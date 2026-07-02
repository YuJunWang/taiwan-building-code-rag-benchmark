import json
import os

with open(r'E:\Project_AGY\11_RAG_GraphRAG_LLMwiki\all_contexts.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for i, item in enumerate(data):
    q = item.get('Question', '')
    c = item.get('Graph_RAG_Context', '')
    with open(fr'E:\Project_AGY\11_RAG_GraphRAG_LLMwiki\q{i+1}.txt', 'w', encoding='utf-8') as out:
        out.write(f"Question:\n{q}\n\nContext:\n{c}")
