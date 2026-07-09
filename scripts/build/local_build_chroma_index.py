import json
import networkx as nx
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import shutil
import os

def main():
    print("1. 載入 Graph JSON...")
    json_path = "E:/Project_AGY/11_RAG_GraphRAG_LLMwiki/data/databases/graph_rag_hybrid_export/graph_rag_export.json"
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    G = nx.node_link_graph(data, edges="edges")
    print(f"成功載入圖譜，包含 {G.number_of_nodes()} 個節點。")

    print("2. 載入 Embedding 模型 (BAAI/bge-m3)...")
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    
    entity_docs = []
    for node, attrs in G.nodes(data=True):
        if attrs.get("type") == "Entity":
            entity_docs.append(Document(page_content=str(node), metadata={"node_id": str(node)}))
            
    print(f"共萃取出 {len(entity_docs)} 個實體。準備建立 Chroma 向量庫...")

    persist_directory = "E:/Project_AGY/11_RAG_GraphRAG_LLMwiki/data/databases/graph_rag_hybrid_export/graph_entity_chroma_db"
    
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)

    if entity_docs:
        vectorstore = Chroma.from_documents(
            documents=entity_docs,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        print(f"✅ Chroma 向量資料庫建立完成！已儲存於: {persist_directory}")
    else:
        print("警告：沒有找到任何實體。")

if __name__ == "__main__":
    main()
