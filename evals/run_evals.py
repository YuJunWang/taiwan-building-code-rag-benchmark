import os
import json
from dotenv import load_dotenv
from langsmith import Client
from langsmith.evaluation import evaluate
from langchain_groq import ChatGroq

# 載入環境變數
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "benchmark")

# 初始化 LangSmith 客戶端與評測用 LLM
client = Client()
eval_llm = ChatGroq(model="openai/gpt-oss-120b")

# ==========================================
# 1. 建立 / 取得 LangSmith Dataset
# ==========================================
dataset_name = "Taiwan_Building_Code_Benchmark_V3"

if not client.has_dataset(dataset_name=dataset_name):
    print(f"Creating dataset '{dataset_name}' in LangSmith...")
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="台灣建築技術規則 15 題基準測試"
    )
    
    # 讀取剛剛加上 expected_answer 的題目檔
    with open(os.path.join(DATA_DIR, "evaluation_questions.json"), "r", encoding="utf-8") as f:
        questions_data = json.load(f)
        
    inputs = []
    outputs = []
    for row in questions_data:
        inputs.append({"question": row["Question"]})
        outputs.append({"expected_answer": row["expected_answer"]})
        
    client.create_examples(inputs=inputs, outputs=outputs, dataset_id=dataset.id)
    print("Dataset created successfully.")
else:
    print(f"Dataset '{dataset_name}' already exists.")


from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class EvalResult(BaseModel):
    score: float = Field(description="The correctness score from 0.0 to 1.0")
    reasoning: str = Field(description="The explanation for the score")

def custom_qa_evaluator(run, example):
    prediction = run.outputs.get("answer", "")
    reference = example.outputs.get("expected_answer", "")
    input_text = example.inputs.get("question", "")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert evaluator. The 'Ground Truth' provided is an objective SCORING RUBRIC (給分標準).\n"
                   "You must evaluate the 'Student Answer' STRICTLY based on whether it contains the facts required by the Ground Truth rubric.\n"
                   "Ignore conversational tone or extra information. If the student answer includes the required facts, it is correct.\n"
                   "Score 1.0 if the student answer meets all requirements in the Ground Truth rubric.\n"
                   "Score 0.5 if it meets only some of the requirements.\n"
                   "Score 0.0 if it fails to meet any of the requirements.\n"
                   "Provide your output as a JSON object with 'score' and 'reasoning' fields."),
        ("user", f"Question: {input_text}\n\nScoring Rubric (Ground Truth): {reference}\n\nStudent Answer: {prediction}")
    ])
    
    chain = prompt | eval_llm.with_structured_output(EvalResult)
    
    try:
        result = chain.invoke({})
        return {
            "key": "Correctness",
            "score": result.score,
            "comment": result.reasoning
        }
    except Exception as e:
        return {
            "key": "Correctness",
            "score": 0.0,
            "comment": f"Eval failed: {str(e)}"
        }

# 可選：自訂評分器 (Faithfulness 忠實度)
# 這邊為了簡化示範，我們先針對 Correctness 進行打分

# ==========================================
# 3. 準備靜態測試結果 (Target Functions)
# ==========================================
# 讀取三個系統的生成結果
with open(os.path.join(DATA_DIR, "results", "hybrid_answers_timed.json"), "r", encoding="utf-8") as f:
    hybrid_ans = json.load(f)
with open(os.path.join(DATA_DIR, "results", "graph_answers_timed.json"), "r", encoding="utf-8") as f:
    graph_ans = json.load(f)
with open(os.path.join(DATA_DIR, "results", "okf_agent_answers_timed.json"), "r", encoding="utf-8") as f:
    okf_ans = json.load(f)
    
# 為了讓 evaluate 函式能靜態讀取，我們使用閉包函數搭配一個 index 計數器
def create_static_target(answers_list):
    # 因為 evaluate() 會針對 dataset 內的每一個 example 呼叫 target function，
    # 而我們剛好確保資料集的順序與 answers_list 的順序一致。
    def target_func(inputs: dict):
        # 尋找該問題在題庫中的 Index，並對應到 answers_list
        with open(os.path.join(DATA_DIR, "evaluation_questions.json"), "r", encoding="utf-8") as f:
            qs = json.load(f)
        idx = next((i for i, row in enumerate(qs) if row["Question"] == inputs["question"]), 0)
        
        answer = answers_list["results"][idx]["answer"] if "results" in answers_list and idx < len(answers_list["results"]) else "生成失敗"
        return {"answer": answer}
    return target_func


# ==========================================
# 4. 執行評測並上傳
# ==========================================
print("\n=== 開始評估 Hybrid RAG ===")
evaluate(
    create_static_target(hybrid_ans),
    data=dataset_name,
    evaluators=[custom_qa_evaluator],
    experiment_prefix="Hybrid-RAG-Eval",
)

print("\n=== 開始評估 Graph RAG ===")
evaluate(
    create_static_target(graph_ans),
    data=dataset_name,
    evaluators=[custom_qa_evaluator],
    experiment_prefix="Graph-RAG-Eval",
)

print("\n=== 開始評估 OKF LLM Wiki ===")
evaluate(
    create_static_target(okf_ans),
    data=dataset_name,
    evaluators=[custom_qa_evaluator],
    experiment_prefix="OKF-Agent-Eval",
)

print("\n[OK] 評測完成！請至 LangSmith 儀表板的 'Datasets & Testing' 查看完整比較報表。")
