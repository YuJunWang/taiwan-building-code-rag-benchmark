import os
import sys
import time
import networkx as nx
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

import warnings
warnings.filterwarnings("ignore")

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

def retrieve(query):
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3", model_kwargs={"device": "cpu"})
    G = nx.read_graphml(os.path.join(PROJECT_ROOT, "data/databases/graph_rag_hybrid_export/graph_rag_export.graphml"))
    entity_db = Chroma(persist_directory=os.path.join(PROJECT_ROOT, "data/databases/graph_rag_hybrid_export/graph_entity_chroma_db"), embedding_function=embeddings)
    
    entry_docs = entity_db.similarity_search(query, k=3)
    entry_nodes = [doc.page_content for doc in entry_docs]
    
    retrieved_knowledge = []
    for node in entry_nodes:
        if node in G:
            raw_text = G.nodes[node].get("raw_text", "")
            if raw_text:
                retrieved_knowledge.append(f"【實體原文】 - {node}\n{raw_text}")
                
            for neighbor in G.neighbors(node):
                edge_data = G.get_edge_data(node, neighbor)
                relation = edge_data.get('relation', '未知關聯')
                source = edge_data.get('source_article', '未知來源')
                
                n_text = G.nodes[neighbor].get("raw_text", "")
                
                fact = f"- 節點 ({node}) [{relation}] 節點 ({neighbor}) 來源：{source}"
                if n_text:
                    fact += f"\n  (節點原文：{n_text})"
                retrieved_knowledge.append(fact)
    
    context = "\n".join(retrieved_knowledge)
    return context

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python retrieve_graph.py <query>")
        sys.exit(1)
        
    query = sys.argv[1]
    start_time = time.time()
    context = retrieve(query)
    retrieval_time = time.time() - start_time
    
    print(context)
    print(f"\n=== [SYSTEM] Retrieval Time: {retrieval_time:.4f} seconds ===")
