# %% [markdown]
# # Graph RAG 知識圖譜建置腳本 (Google Colab 適用)
# 
# 這個腳本將讀取建築法規 JSON，並使用開源的中小型 LLM（例如 Qwen2.5-7B-Instruct 4-bit 量化版）來進行實體與關聯抽取 (Entity Extraction)。
# 由於抽取過程非常耗費算力，建議在 Colab 的 T4 GPU (或更好的硬體) 上運行。
# 
# **在 Colab 執行前，請確保先將 `building_regulations.json` 上傳到 Colab 的根目錄**。

# %%
# 1. (請在 Colab 另外開一個儲存格安裝套件)

# %%
import json
import os
import networkx as nx
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from tqdm.auto import tqdm

# %%
# 2. 讀取資料
json_path = "building_regulations_v2.json"
if not os.path.exists(json_path):
    raise FileNotFoundError(f"找不到 {json_path}，請確認是否已上傳至 Colab。")

with open(json_path, 'r', encoding='utf-8') as f:
    articles = json.load(f)

print(f"成功載入 {len(articles)} 條法規。")

# %%
# 3. 載入 4-bit 模型 (LLM) (適用於 15GB VRAM 以下環境)
# 使用 bitsandbytes 即時進行 4-bit 量化，這比 GPTQ 更穩定且不需額外編譯套件
model_id = "Qwen/Qwen2.5-7B-Instruct"

print(f"正在載入模型 {model_id} ... (這可能需要幾分鐘下載)")
tokenizer = AutoTokenizer.from_pretrained(model_id)

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    quantization_config=quantization_config
)
print("模型載入完成！")

# %%
# 4. 定義萃取函數
def extract_triplets(text):
    prompt = f"""請閱讀以下建築法規條文，並從中萃取出實體(Entities)之間的關聯(Relationships)與法規條件(Conditions)。
輸出的格式必須是嚴格的 JSON 陣列，每個元素包含 "subject", "predicate", "object", "condition" 四個欄位。
如果沒有明顯關聯，請輸出空陣列 []。不要輸出任何其他解釋或文字。

欄位定義：
- subject (主詞): 規範主體，如「防火牆」、「避難層」。
- predicate (關聯/動作): 規範動作，如「退縮距離」、「防火時效」、「不得超過」。
- object (受詞/數值): 規範客體或數值限制，如「6公尺」、「1小時」、「12.5%」。
- condition (條件): 該規定適用的前提條件，如「若外牆為木造」、「無窗戶居室」。若無特定條件請填寫 "無"。

法規條文：
{text}

JSON 輸出：
"""
    
    messages = [
        {"role": "system", "content": "你是一個精準的知識萃取系統，專門將法律文本轉換為法規條件知識圖譜。請只輸出 JSON 格式。"},
        {"role": "user", "content": prompt}
    ]
    
    text_input = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    model_inputs = tokenizer([text_input], return_tensors="pt").to(model.device)
    
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=2048,
        temperature=0.1, # 降低溫度以確保格式穩定
        do_sample=True,  # 必須開啟採樣，temperature 才會生效
        repetition_penalty=1.15 # 加入重複懲罰，避免模型陷入無窮迴圈
    )
    
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    # 嘗試解析 JSON
    try:
        # 清理可能被 Markdown code block 包圍的情況
        cleaned_response = response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
            
        triplets = json.loads(cleaned_response.strip())
        if isinstance(triplets, list):
            return triplets
    except Exception as e:
        print(f"JSON 解析失敗，略過此條文。回應內容：{response}")
    
    return []

# %%
# 5. 執行關係萃取
# 實際執行全部法規
G = nx.DiGraph()

print(f"即將對 {len(articles)} 條法規實體關聯...")
for item in tqdm(articles):
    article_no = item.get("article_no", "未知條文")
    content = item.get("content", "")
    
    # 為了圖譜查詢，將法規本身也當作一個節點
    G.add_node(article_no, type="Regulation", content=content)
    
    triplets = extract_triplets(content)
    for triplet in triplets:
        if not isinstance(triplet, dict):
            continue
            
        sub = triplet.get("subject")
        pred = triplet.get("predicate")
        obj = triplet.get("object")
        cond = triplet.get("condition", "無")
        
        if sub and pred and obj:
            # 加入實體節點 (並綁定法規原文)
            if sub not in G:
                G.add_node(sub, type="Entity", raw_text=content)
            else:
                existing_text = G.nodes[sub].get("raw_text", "")
                if content not in existing_text:
                    G.nodes[sub]["raw_text"] = existing_text + "\n---\n" + content
            
            if obj not in G:
                G.add_node(obj, type="Entity", raw_text=content)
            else:
                existing_text = G.nodes[obj].get("raw_text", "")
                if content not in existing_text:
                    G.nodes[obj]["raw_text"] = existing_text + "\n---\n" + content
                    
            # 加入關係邊 (同時記錄來源條文與條件)
            G.add_edge(sub, obj, relation=pred, condition=cond, source_article=article_no)
            
            # 將法規節點與該條文的主體連結起來
            G.add_edge(article_no, sub, relation="規範了")

print(f"抽取完成！知識圖譜共包含 {G.number_of_nodes()} 個節點與 {G.number_of_edges()} 條邊。")

# %%
# 6. [升級] 建立雙層實體向量索引 (Entity Entry Point Vector Index)
# Graph RAG 檢索的痛點是無法直接透過字串匹配找到圖譜入口。
# 我們將圖譜中的「實體 (Entity)」萃取出來建立向量索引，當作檢索時的 Entry Points。
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import shutil

print("載入 Embedding 模型 BAAI/bge-m3 以建立實體索引...")
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

entity_docs = []
for node, attrs in G.nodes(data=True):
    if attrs.get("type") == "Entity":
        # 節點名稱就是實體名稱
        entity_docs.append(Document(page_content=str(node), metadata={"node_id": str(node)}))

print(f"共萃取出 {len(entity_docs)} 個實體，準備建立向量索引...")

persist_directory = "./graph_entity_chroma_db"
if os.path.exists(persist_directory):
    shutil.rmtree(persist_directory)

if entity_docs:
    vectorstore = Chroma.from_documents(
        documents=entity_docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print("雙層實體向量索引 (Entity Vector Index) 建立完成！")
else:
    print("警告：沒有萃取出任何實體，跳過建立向量索引。")

# %%
# 7. 匯出 GraphML, JSON 與 Entity Vector Index
# GraphML 格式可以用 Gephi 等視覺化軟體開啟
graphml_filename = "graph_rag_export.graphml"
nx.write_graphml(G, graphml_filename)

# 也匯出 Node-Link JSON 格式供後續應用讀取
json_filename = "graph_rag_export.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(nx.node_link_data(G), f, ensure_ascii=False, indent=2)

print(f"圖譜已儲存為 {graphml_filename} 與 {json_filename}")

# %%
# 打包所有檔案
import zipfile

zip_filename = "graph_rag_hybrid_export.zip"

print(f"正在打包圖譜與實體向量索引為 {zip_filename}...")
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # 打包圖譜檔案
    zipf.write(graphml_filename, graphml_filename)
    zipf.write(json_filename, json_filename)
    
    # 打包 ChromaDB
    if os.path.exists(persist_directory):
        for root, dirs, files in os.walk(persist_directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, persist_directory)
                zipf.write(file_path, os.path.join("graph_entity_chroma_db", arcname))

print("打包完成！")

# %%
# 若在 Colab 中，自動觸發下載
try:
    from google.colab import files
    print("準備下載檔案...")
    files.download(zip_filename)
except ImportError:
    print(f"請手動下載 {zip_filename}。")
