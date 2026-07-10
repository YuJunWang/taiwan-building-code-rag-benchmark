import json
import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

class EvalResult(BaseModel):
    score: float = Field(description="The correctness score from 0.0 to 1.0")
    reasoning: str = Field(description="The explanation for the score")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert evaluator. The 'Ground Truth' provided is an objective SCORING RUBRIC (給分標準).\n"
                "You must evaluate the 'Student Answer' STRICTLY based on whether it contains the facts required by the Ground Truth rubric.\n"
                "Ignore conversational tone or extra information. If the student answer includes the required facts, it is correct.\n"
                "Score 1.0 if the student answer meets all requirements in the Ground Truth rubric.\n"
                "Score 0.5 if it meets only some of the requirements.\n"
                "Score 0.0 if it fails to meet any of the requirements.\n"
                "Provide your output as a JSON object with 'score' and 'reasoning' fields in Traditional Chinese."),
    ("user", "Question: {input_text}\n\nScoring Rubric (Ground Truth): {reference}\n\nStudent Answer: {prediction}")
])

chain = prompt | llm.with_structured_output(EvalResult)

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load data
with open('benchmark/questions.txt', 'r', encoding='utf-8') as f:
    questions = [line.strip() for line in f if line.strip()]

references = load_json('benchmark/results/semantic_answers.json')

# Load answers
h_ans = load_json('benchmark/results/hybrid_answers_timed.json').get('results', [])
g_ans = load_json('benchmark/results/graph_answers_timed.json').get('results', [])
o_ans = load_json('benchmark/results/okf_agent_answers_timed.json').get('results', [])

eval_results = []

print("Evaluating Hybrid, Graph, OKF locally...")
for i in range(15):
    q = questions[i]
    ref = references[i]
    
    ha = h_ans[i]['answer'] if i < len(h_ans) else "N/A"
    ga = g_ans[i]['answer'] if i < len(g_ans) else "N/A"
    oa = o_ans[i]['answer'] if i < len(o_ans) else "N/A"
    
    # Evaluate Hybrid
    try:
        h_eval = chain.invoke({"input_text": q, "reference": ref, "prediction": ha})
        h_score, h_reason = h_eval.score, h_eval.reasoning
    except Exception as e:
        h_score, h_reason = 0.0, str(e)
    time.sleep(1)
        
    # Evaluate Graph
    try:
        g_eval = chain.invoke({"input_text": q, "reference": ref, "prediction": ga})
        g_score, g_reason = g_eval.score, g_eval.reasoning
    except Exception as e:
        g_score, g_reason = 0.0, str(e)
    time.sleep(1)

    # Evaluate OKF
    try:
        o_eval = chain.invoke({"input_text": q, "reference": ref, "prediction": oa})
        o_score, o_reason = o_eval.score, o_eval.reasoning
    except Exception as e:
        o_score, o_reason = 0.0, str(e)
    time.sleep(1)

    eval_results.append({
        "question": q,
        "hybrid": {"score": h_score, "reasoning": h_reason},
        "graph": {"score": g_score, "reasoning": g_reason},
        "okf": {"score": o_score, "reasoning": o_reason}
    })
    print(f"Evaluated Q{i+1}")

with open('benchmark/results/eval_results.json', 'w', encoding='utf-8') as f:
    json.dump(eval_results, f, ensure_ascii=False, indent=2)

print("Evaluation complete!")
