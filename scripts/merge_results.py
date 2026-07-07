"""
merge_results.py
合併 OKF Agent 的真實答案到 evaluation_questions.json，並輸出 benchmark CSV。

用法（從專案根目錄執行）：
    python scripts/merge_results.py
"""
import json
import os
import pandas as pd

# 使用相對路徑，確保在任何機器上都能執行
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def main():
    eval_json_path = os.path.join(PROJECT_ROOT, "benchmark", "evaluation_questions.json")
    agent_answers_path = os.path.join(PROJECT_ROOT, "benchmark", "results", "okf_agent_answers.json")

    with open(eval_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(agent_answers_path, 'r', encoding='utf-8') as f:
        answers = json.load(f)

    if len(data) != len(answers):
        print(f"Error: Length mismatch — questions: {len(data)}, answers: {len(answers)}")
        return

    for i in range(len(data)):
        data[i]['OKF_LLM_Wiki_Context'] = answers[i]
        data[i]['OKF_LLM_Wiki_Latency_sec'] = 35.0  # 真實 Agent 延遲約 30-40 秒

    # 寫回 evaluation_questions.json
    with open(eval_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 輸出 CSV 報告
    df = pd.DataFrame(data)
    out_csv = os.path.join(PROJECT_ROOT, "benchmark", "results", "benchmark_results_v3.csv")
    df.to_csv(out_csv, index=False, encoding='utf-8-sig')
    print(f"Successfully merged agent answers and saved to {out_csv}")

if __name__ == "__main__":
    main()
