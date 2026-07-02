# 研究計畫：RAG vs. Graph RAG vs. OKF-based LLM Wiki 比較測試

這個專案的目標是針對目前主流的三種 AI 知識檢索架構進行實作與比較，了解它們在準確度、建置成本及推論能力上的優劣。

> [!NOTE]
> 考量到算力限制 (Colab 免費版 T4 GPU)，我們在設計進階檢索機制時，將優先採用高效且不消耗額外 VRAM 的方案（例如 BM25 混合檢索、輕量級 Embedding 模型 BAAI/bge-m3，以及 4-bit 量化的 LLM）。

---

## 測試資料集：【台灣建築法規】
- **特性**：約 400 條法規，具備高度的跨條文參照、專有名詞及層次結構（編、章、節、條、項、款）。
- **取得方式**：已使用 Python 爬蟲至全國法規資料庫抓取最新「建築技術規則建築設計施工編」條文，共 389 條。

---

## 架構與實作方法 (Methodology)

為了確保比較基準達到企業級 Production-ready 的水準，我們導入了針對法律文本最佳化的進階架構：

### 1. 傳統 RAG (Hybrid Search + Structural Chunking)
- **建置原理 (結構化切塊)**：不使用暴力的固定字數切塊。我們將法規依「項 / 款」精細切塊，並將「法規名稱、章節、條號」強制綁定在每個 Chunk 的 Metadata 與前綴中，避免 Context 稀釋。
- **建置環境 (Colab)**：使用 HuggingFace `BAAI/bge-m3` 進行 Vector Embedding，建立 ChromaDB。
- **本地/應用端檢索 (Hybrid Search)**：實作**混合檢索**。同時結合「Vector 相似度」與「BM25 關鍵字精確匹配」，最後透過 RRF (Reciprocal Rank Fusion) 重新排序。這解決了法律專有名詞完全依賴向量容易誤判的問題，且 BM25 幾乎不耗費額外算力。

### 2. Graph RAG (Two-tiered Indexing)
- **建置原理 (實體萃取與雙層索引)**：
  1. 將法規依「句子/項」切塊，補上前文參照後，交由 LLM 萃取三元組 (Subject-Predicate-Object)。
  2. 建立**雙層索引 (Two-tiered Indexing)**：將抽出來的「實體節點 (Entities)」額外做一次 Vector Embedding，作為檢索的入口。
- **雲端建置 (Colab)**：使用 `Qwen2.5-7B-Instruct 4-bit` 量化版本萃取圖譜，並使用 `bge-m3` 對節點做輕量 Embedding。最後匯出 NetworkX GraphML 與 VectorDB。
- **本地/應用端檢索**：當使用者提問時，先透過 Vector 找到最相關的實體節點 (Entry Point)，再從該節點往外擴展 (Traversal) 抓取關聯知識送給 LLM。

### 3. OKF-based LLM Wiki (Hierarchical MOC + Agent Tools)
- **建置原理 (階層目錄與前期標註)**：
  - **分組與 MOC**：依照法規原生的「章 -> 節」建立階層式實體資料夾。並為每個資料夾建立 `_index.md` (Map of Content)，統整該節的核心條文。
  - **確定性連結**：用 Regex 強制將內文提及的「第 X 條」轉換為 Markdown 內部連結與 YAML `related_articles`。
  - **語意標註**：透過 LLM 為每條法規補上簡短的 `summary` 與 `tags`。
- **建置環境**：結合本地與輕量 LLM 批次處理轉換。
- **本地/應用端檢索 (Agent Tools)**：賦予 Agent 強大的檔案操作工具：包含 `list_dir`, `view_file`，以及最重要的 **`search_keyword_in_files` (等同 grep)**。讓 Agent 能全域搜尋專有名詞，再透過 MOC 摘要與內部連結精準跳躍閱讀。

---

## 評估計畫 (Evaluation Plan)

我們將設計 10~15 個測試問題，涵蓋三種難度層級：
1. **事實檢索 (Fact-retrieval)**：例如「排煙室的門寬度規定是多少？」
2. **跨文件推理 (Multi-hop reasoning)**：例如「如果要在易淹水地區蓋高腳屋，容積率的計算與一般建築有何不同？」
3. **全局總結 (Global summarization)**：例如「本編法規中，對於『法定空地』的規定主要散布在哪些章節？核心精神為何？」

### 預期比較維度

| 評估項目 | 說明 |
| :--- | :--- |
| **建置成本** | 時間、API Token 花費、算力需求（考量 Colab T4 限制） |
| **準確度與幻覺** | 提供正確答案且不胡說八道的能力 |
| **跨文件推理能力** | 解決 Multi-hop 問題的表現 |
| **全局總結能力** | 處理龐大脈絡問題的表現 |
| **反應延遲 (Latency)**| 從提問到給出最終答案的時間 |
