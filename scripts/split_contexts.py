import json
import os

def main():
    base_dir = r"E:\Project_AGY\11_RAG_GraphRAG_LLMwiki"
    json_path = os.path.join(base_dir, "benchmark", "evaluation_questions.json")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    hybrid_text = ""
    graph_text = ""
    okf_text = ""
    
    for idx, row in enumerate(data):
        q = row['Question']
        hybrid_text += f"Question {idx+1}: {q}\nContext:\n{row.get('Hybrid_RAG_Context', '')}\n\n{'='*40}\n\n"
        graph_text += f"Question {idx+1}: {q}\nContext:\n{row.get('Graph_RAG_Context', '')}\n\n{'='*40}\n\n"
        okf_text += f"Question {idx+1}: {q}\nContext:\n{row.get('OKF_LLM_Wiki_Context', '')}\n\n{'='*40}\n\n"
        
    os.makedirs(os.path.join(base_dir, "scratch"), exist_ok=True)
    with open(os.path.join(base_dir, "scratch", "hybrid_tasks.md"), 'w', encoding='utf-8') as f:
        f.write(hybrid_text)
    with open(os.path.join(base_dir, "scratch", "graph_tasks.md"), 'w', encoding='utf-8') as f:
        f.write(graph_text)
    with open(os.path.join(base_dir, "scratch", "okf_tasks.md"), 'w', encoding='utf-8') as f:
        f.write(okf_text)
        
if __name__ == "__main__":
    main()
