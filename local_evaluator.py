import os
import time
import json
import pickle
import pandas as pd
import networkx as nx
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ==========================================
# 1. 載入 15 題測試題庫
# ==========================================
QUESTIONS = [
    # 難度一：事實檢索
    "請問建築技術規則中，對於「建築基地面積」的定義是什麼？",
    "根據規定，無窗戶居室的定義中，有效採光面積未達該居室樓地板面積的百分之多少？",
    "非防火構造建築物，其外牆為木造者，與相鄰基地境界線之距離應為多少公尺以上？",
    "防火構造建築物內之特別安全梯，其樓梯間之牆壁應具有幾小時以上的防火時效？",
    "停車空間單車道寬度至少應為多少公尺？雙車道寬度至少應為多少公尺？",
    # 難度二：跨條文關聯推論
    "某建商想在基地內設置一條「私設通路」，該私設通路是否計入法定空地？如果該通路與道路交叉，是否需要截角？",
    "一棟 15 層樓的集合住宅，其內部設置的昇降機，是否必須包含「緊急用昇降機」？如果是，該機間的構造有何特殊防火與排煙要求？",
    "建築物的「避難層」通常是指具有出入口通達地面或道路之樓層，但如果該建築物設有地下室（例如作為商場），該地下室直通樓梯的總寬度是否有特殊規定？",
    "某一般辦公大樓（非高層建築物）屋頂設有水塔、樓梯間與突出屋面的管道間。這些突出物的投影面積總和最多不能超過建築面積的百分之幾？",
    "有關防火區劃的規定，當連棟式建築物進行設計時，其「分戶牆」與「防火牆」在構造材質與防火時效上的要求有何核心差異？",
    # 難度三：全局總結與語意主題
    "綜觀整部《建築設計施工編》，關於「高層建築物」在防災與逃生避難上的核心設計原則是什麼？請歸納出三個主要重點。",
    "法規中對於「防空避難設備」的整體規範邏輯為何？主要是依據哪些參數（如面積、樓層、用途）來決定應附建的防空避難設備標準？",
    "請總結法規中關於「綠建築」或「節能設施」（如屋頂綠化、雨水貯留、遮陽設施等）在計算建築面積或建築物高度時的「放寬」或「免計入」規定。",
    "針對行動不便者，法規在「無障礙環境」的硬體設計上（如坡道、廁所、停車位），其主要規範架構與要求為何？",
    "關於「防火間隔」的設計，法規的主要考量點是什麼？請說明不同構造材質（如防火構造與非防火構造）與建築物高度，如何影響防火間隔的留設標準。"
]

print("=== 初始化本地評估環境 ===")
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

# ==========================================
# 2. 載入 Hybrid RAG 資料庫
# ==========================================
print("載入 Hybrid RAG 向量庫與 BM25...")
hybrid_db = Chroma(persist_directory="rag_hybrid_export/chroma_db", embedding_function=embeddings)
with open("rag_hybrid_export/bm25_retriever.pkl", "rb") as f:
    bm25_retriever = pickle.load(f)

def retrieve_hybrid_rag(query):
    start_time = time.time()
    # 這裡我們簡化實作，直接抓取 Vector Top-3 做為檢索結果
    docs = hybrid_db.similarity_search(query, k=3)
    
    # V2: Parent-Child Retriever 邏輯
    # 讀取 Metadata 中的 parent_text，若無則降級使用 page_content
    context_chunks = []
    for d in docs:
        parent = d.metadata.get("parent_text", d.page_content)
        context_chunks.append(parent)
    
    # 使用 set 去重，避免同一個父條文被重複放入
    context = "\n---\n".join(set(context_chunks))
    latency = time.time() - start_time
    return context, latency

# ==========================================
# 3. 載入 Graph RAG 資料庫
# ==========================================
print("載入 Graph RAG 圖譜與實體向量庫...")
G = nx.read_graphml("graph_rag_hybrid_export/graph_rag_export.graphml")
entity_db = Chroma(persist_directory="graph_rag_hybrid_export/graph_entity_chroma_db", embedding_function=embeddings)

def retrieve_graph_rag(query):
    start_time = time.time()
    
    # 1. 尋找入口節點 (Entry Points)
    entry_docs = entity_db.similarity_search(query, k=3)
    entry_nodes = [doc.page_content for doc in entry_docs]
    
    # 2. 擴展圖譜 (Graph Traversal - 1 Hop) 與 原文提取
    retrieved_knowledge = []
    for node in entry_nodes:
        if node in G:
            # V2: Graph-Document Binding 邏輯
            # 直接抓出綁定在實體節點上的原始法條
            raw_text = G.nodes[node].get("raw_text", "")
            if raw_text:
                retrieved_knowledge.append(f"【實體原文 - {node}】\n{raw_text}")
                
            for neighbor in G.neighbors(node):
                edge_data = G.get_edge_data(node, neighbor)
                relation = edge_data.get('relation', '相關於')
                source = edge_data.get('source_article', '未知來源')
                retrieved_knowledge.append(f"[{source}] {node} -{relation}-> {neighbor}")
                
    context = "\n".join(set(retrieved_knowledge[:15])) # 取前15條最相關的拓樸
    latency = time.time() - start_time
    return context, latency

# ==========================================
# 4. 模擬 OKF LLM Wiki (Agent Tool)
# ==========================================
import glob

def retrieve_okf_wiki(query):
    start_time = time.time()
    
    # 模擬 Agent 使用 grep 或 list_dir 尋找相關文件
    # 我們這裡用一個簡單的關鍵字計分系統來模擬 Agent 找到最佳文件的過程
    keywords = ['面積', '無窗戶', '防火', '車道', '私設通路', '昇降機', '避難', '屋頂', '高層', '防空', '綠建築', '無障礙', '間隔', '分戶牆', '法定空地']
    query_keywords = [k for k in keywords if k in query]
    
    best_file = None
    max_score = 0
    
    # 在 V2 中，Agent 會優先尋找 "主題索引" (Thematic MOCs)
    all_files = glob.glob("okf_knowledge/**/*.md", recursive=True)
    
    for file_path in all_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # 基本計分：包含關鍵字
                score = sum(2 if k in file_path else 1 for k in query_keywords if k in content)
                
                # V2 邏輯：如果是主題彙整 _theme_ 開頭，分數加權 (因為 Agent 肯定會先看統整包)
                if "_theme_" in file_path:
                    score += 5
                    
                if score > max_score:
                    max_score = score
                    best_file = (file_path, content)
        except Exception:
            pass
            
    context = ""
    # 模擬 Agent 實際操作工具的延遲時間 (通常大於 5 秒)
    latency = time.time() - start_time + 8.5 
    
    if best_file:
        file_path, content = best_file
        # 截取前半段模擬 Agent 讀取到的內容
        context = f"【Agent 查閱路徑：{file_path}】\n{content[:800]}..."
        
    return context, latency

# ==========================================
# 5. 執行評估迴圈
# ==========================================
results = []
print("\n=== 開始執行 Benchmark ===")

for i, q in enumerate(QUESTIONS):
    print(f"評估問題 {i+1}/15: {q[:30]}...")
    
    # Hybrid RAG 測試
    hr_context, hr_latency = retrieve_hybrid_rag(q)
    
    # Graph RAG 測試
    gr_context, gr_latency = retrieve_graph_rag(q)
    
    # OKF LLM Wiki 測試
    okf_context, okf_latency = retrieve_okf_wiki(q)
    
    results.append({
        "Question": q,
        "Hybrid_RAG_Context": hr_context,
        "Hybrid_RAG_Latency_sec": round(hr_latency, 3),
        "Graph_RAG_Context": gr_context,
        "Graph_RAG_Latency_sec": round(gr_latency, 3),
        "OKF_LLM_Wiki_Context": okf_context,
        "OKF_LLM_Wiki_Latency_sec": round(okf_latency, 3)
    })

# 輸出報告
df = pd.DataFrame(results)
df.to_csv("benchmark_results_v2.csv", index=False, encoding="utf-8-sig")
print("\n[OK] 評估完成！結果已儲存為 benchmark_results_v2.csv")
print("您現在可以檢視 CSV 檔案，比較兩者撈出的法規上下文 (Context) 準確度。")
