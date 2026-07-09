import json

with open('E:\\Project_AGY\\11_RAG_GraphRAG_LLMwiki\\all_contexts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
for i, d in enumerate(data):
    q = d.get('Question', '')
    c = d.get('Graph_RAG_Context', '')
    out.append(f"Q{i+1}: {q}\nContext: {c}\n---")

with open('E:\\Project_AGY\\11_RAG_GraphRAG_LLMwiki\\extract.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
