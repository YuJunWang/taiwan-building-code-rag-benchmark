import json
import os

data = json.load(open('E:\\Project_AGY\\11_RAG_GraphRAG_LLMwiki\\all_contexts.json', encoding='utf-8'))
os.makedirs('E:\\Project_AGY\\11_RAG_GraphRAG_LLMwiki\\scratch', exist_ok=True)

for i, d in enumerate(data):
    question = d.get('Question', '')
    context = d.get('OKF_LLM_Wiki_Context', '')
    content = f"Question: {question}\n\nContext: {context}"
    with open(f'E:\\Project_AGY\\11_RAG_GraphRAG_LLMwiki\\scratch\\q{i}.md', 'w', encoding='utf-8') as f:
        f.write(content)
