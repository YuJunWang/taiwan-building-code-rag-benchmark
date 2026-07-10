import os
import sys
import time
import pickle
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

import warnings
warnings.filterwarnings("ignore")

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

def retrieve(query):
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3", model_kwargs={"device": "cpu"})
    hybrid_db = Chroma(persist_directory=os.path.join(PROJECT_ROOT, "data/databases/rag_hybrid_export/chroma_db"), embedding_function=embeddings)
    
    docs = hybrid_db.similarity_search(query, k=3)
    
    context_chunks = []
    for d in docs:
        parent = d.metadata.get("parent_text", d.page_content)
        context_chunks.append(parent)
    
    context = "\n---\n".join(set(context_chunks))
    return context

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python retrieve_hybrid.py <query>")
        sys.exit(1)
        
    query = sys.argv[1]
    start_time = time.time()
    context = retrieve(query)
    retrieval_time = time.time() - start_time
    
    print(context)
    print(f"\n=== [SYSTEM] Retrieval Time: {retrieval_time:.4f} seconds ===")
