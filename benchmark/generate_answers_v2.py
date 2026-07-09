import json
import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from tqdm import tqdm

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# 載入前面萃取好的上下文
with open(os.path.join(os.path.dirname(BASE_DIR), "all_contexts.json"), "r", encoding="utf-8") as f:
    contexts_data = json.load(f)

# 初始化生成答案用的 LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你是一個嚴謹的台灣建築法規專家。請『完全只根據』以下提供的參考文獻（Context）來回答問題。\n"
               "1. 如果參考文獻中沒有提到相關資訊，請明確回答「根據提供的參考文獻，缺乏相關資訊」。\n"
               "2. 請盡量精簡扼要，直接回答問題的核心，不需要贅述。"),
    ("user", "【參考文獻】\n{context}\n\n【問題】\n{question}")
])

chain = prompt_template | llm

hybrid_answers = []
graph_answers = []
okf_answers = []

print("=== 開始為 15 題基準測試生成 LLM 答案 ===")
for i, row in enumerate(tqdm(contexts_data)):
    q = row["Question"]
    
    # 1. Hybrid RAG
    try:
        hybrid_ans = chain.invoke({"context": row.get("Hybrid_RAG_Context", ""), "question": q}).content
    except Exception as e:
        hybrid_ans = f"Error: {e}"
        
    # 2. Graph RAG
    try:
        graph_ans = chain.invoke({"context": row.get("Graph_RAG_Context", ""), "question": q}).content
    except Exception as e:
        graph_ans = f"Error: {e}"
        
    # 3. OKF LLM Wiki
    try:
        okf_ans = chain.invoke({"context": row.get("OKF_LLM_Wiki_Context", ""), "question": q}).content
    except Exception as e:
        okf_ans = f"Error: {e}"
        
    hybrid_answers.append(hybrid_ans)
    graph_answers.append(graph_ans)
    okf_answers.append(okf_ans)
    
    # 避免 API Rate Limit
    time.sleep(1)

# 寫入檔案，準備供 run_evals.py 與 compile_report.py 使用
with open(os.path.join(RESULTS_DIR, "hybrid_answers.json"), "w", encoding="utf-8") as f:
    json.dump(hybrid_answers, f, ensure_ascii=False, indent=2)
with open(os.path.join(RESULTS_DIR, "graph_answers.json"), "w", encoding="utf-8") as f:
    json.dump(graph_answers, f, ensure_ascii=False, indent=2)
with open(os.path.join(RESULTS_DIR, "okf_agent_answers.json"), "w", encoding="utf-8") as f:
    json.dump(okf_answers, f, ensure_ascii=False, indent=2)

print(f"\n[OK] 答案生成完畢！已儲存至 {RESULTS_DIR}")
