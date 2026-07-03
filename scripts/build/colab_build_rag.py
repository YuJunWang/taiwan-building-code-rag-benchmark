# %% [markdown]
# # 進階 RAG 混合檢索資料庫建置腳本 (Google Colab 適用)
# 
# 本腳本將實作：
# 1. **結構化切塊 (Structural Chunking)**：將法規依項/款精細切塊，並綁定章節與條文號碼作為 Metadata。
# 2. **混合檢索準備**：建立 HuggingFace `BAAI/bge-m3` 的向量資料庫 (ChromaDB)，以及關鍵字檢索器 (BM25Retriever)，並將兩者打包匯出。
# 
# **在 Colab 執行前，請確保先將 `building_regulations_v2.json` 上傳到 Colab 的根目錄**。

# %%
# 1. (請在 Colab 另外開一個儲存格安裝套件)

# %%
import json
import os
import shutil
import pickle
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever

# %%
# 2. 讀取 V2 結構化資料
json_path = "building_regulations_v2.json"
if not os.path.exists(json_path):
    raise FileNotFoundError(f"找不到 {json_path}，請確認是否已上傳至 Colab。")

with open(json_path, 'r', encoding='utf-8') as f:
    articles = json.load(f)

print(f"成功載入 {len(articles)} 條法規。")

# %%
# 3. 實作結構化切塊 (Structural Chunking)
# 法規內容中已包含換行符號 (\n)，我們利用換行將條文切分為獨立的「款 / 項」，並為每一塊打上完整的 Metadata
docs = []
for item in articles:
    article_no = item.get("article_no", "").strip()
    chapter = item.get("chapter", "").strip()
    section = item.get("section", "").strip()
    content = item.get("content", "").strip()
    
    # 依換行符號進行切塊
    paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
    
    for i, p in enumerate(paragraphs):
        metadata = {
            "law_title": "建築技術規則建築設計施工編",
            "chapter": chapter,
            "section": section,
            "article_no": article_no,
            "chunk_idx": i,
            "parent_text": content # 寫入完整父文件，實作 Parent-Child Retriever
        }
        
        # 在文本最前面加上語境前綴，避免 Context 稀釋 (Vector Dilution)
        context_prefix = f"【{article_no}】"
        if chapter: context_prefix = f"【{chapter} {article_no}】"
        
        text = f"{context_prefix} {p}"
        docs.append(Document(page_content=text, metadata=metadata))

print(f"結構化切塊完成，共 {len(docs)} 個 Chunks。")

# %%
# 4. 初始化 Embedding 模型
# BAAI/bge-m3 是對繁體中文支援極佳的輕量開源 Embedding 模型
print("載入 Embedding 模型 BAAI/bge-m3...")
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

# %%
# 5. 建立 VectorDB (Chroma)
persist_directory = "./chroma_db"

if os.path.exists(persist_directory):
    shutil.rmtree(persist_directory)

print("開始進行 Embedding 並寫入 ChromaDB，這可能需要幾分鐘的時間...")
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory=persist_directory
)
print("VectorDB 建立完成！")

# %%
# 6. 建立 BM25 Retriever (供 Hybrid Search 使用)
print("開始建立 BM25 關鍵字檢索器...")
bm25_retriever = BM25Retriever.from_documents(docs)
bm25_retriever.k = 10 # 預設檢索筆數

bm25_path = "bm25_retriever.pkl"
with open(bm25_path, "wb") as f:
    pickle.dump(bm25_retriever, f)
print("BM25 Retriever 建立並儲存完成！")

# %%
# 7. 打包並準備下載
import zipfile

zip_filename = "rag_hybrid_export.zip"

print(f"正在打包 {persist_directory} 與 {bm25_path} 為 {zip_filename}...")
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # 打包 ChromaDB
    for root, dirs, files in os.walk(persist_directory):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, persist_directory)
            zipf.write(file_path, os.path.join("chroma_db", arcname))
    # 打包 BM25
    zipf.write(bm25_path, bm25_path)

print("打包完成！")

# %%
# 若在 Colab 中，自動觸發下載
try:
    from google.colab import files
    print("準備下載檔案...")
    files.download(zip_filename)
except ImportError:
    print(f"請手動下載 {zip_filename} 檔案。")
