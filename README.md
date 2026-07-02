**繁體中文** | [English](README_EN.md)

# LLM Knowledge Retrieval Benchmark: RAG vs. Graph RAG vs. OKF-Wiki

這是一個針對台灣《建築技術規則建築設計施工編》所建立的進階 AI 知識檢索架構比較專案。
本專案實作並嚴格對比了目前市面上主流的三種 LLM 知識庫架構，提供給開發者與企業作為導入 AI 系統的架構選擇參考。

## 📁 專案目錄結構 (Folder Structure)

為了能順利執行本地端的自動化測試腳本，請確保專案維持以下結構：

```text
11_RAG_GraphRAG_LLMwiki/
│
├── building_regulations_v2.json      # 原始法規爬蟲資料
├── colab_build_rag.py                # 雲端建置腳本 (Hybrid RAG)
├── colab_build_graph_rag.py          # 雲端建置腳本 (Graph RAG)
├── colab_build_okf_enrichment.py     # 雲端建置腳本 (OKF 標註)
├── local_evaluator.py                # 本地端自動化評估腳本
├── requirements.txt                  # Python 相依套件清單 (支援 uv/pip)
│
├── rag_hybrid_export/                # 📥 [下載] Hybrid RAG 資料庫
│   └── chroma_db/                    # 包含 Vector 與 BM25 索引
│
├── graph_rag_hybrid_export/          # 📥 [下載] Graph RAG 資料庫
│   ├── graph_rag_export.graphml      # NetworkX 知識圖譜本體
│   ├── graph_rag_export.json         # 圖譜元資料
│   └── entity_vector_db/             # 實體節點 (Entry Points) 向量庫
│
└── okf_knowledge/                    # 📥 [下載] OKF 本地知識庫
    ├── 第一章_用語定義/
    ├── 第二章_一般設計通則/
    └── ...
```

## 🛠️ 環境建置 (Environment Setup)

建議使用 `uv` 或 `pip` 安裝相依套件：

```bash
# 使用 pip
pip install -r requirements.txt

# 使用 uv
uv pip install -r requirements.txt
```

---

## 📊 三大架構實作原理 (Methodology)

### 1. 傳統 RAG (Hybrid Search + Structural Chunking)
- **建置原理**：放棄傳統的固定字數切塊，改採法規原生的「條/項/款」精細切塊，並強制將「章節名稱與條號」綁定於 Context 中。
- **檢索機制 (Hybrid Search)**：透過 `BAAI/bge-m3` 進行語意搜尋，結合 `BM25` 關鍵字精準匹配，最後以 RRF (Reciprocal Rank Fusion) 重新排序，有效解決法律專有名詞容易因純向量檢索而誤判的問題。

### 2. Graph RAG (Two-tiered Indexing)
- **建置原理**：交由 Qwen2.5-7B-Instruct 萃取法規中的三元組 (Subject-Predicate-Object) 並建立成千上萬個節點。
- **檢索機制**：雙層檢索架構。第一層透過 Vector DB 找到與 User Query 相關的「實體入口節點 (Entry Point)」，第二層從入口節點利用 NetworkX 在知識圖譜中進行擴展 (Graph Traversal)，一次性拉出高度關聯的知識網。

### 3. OKF-based LLM Wiki (Hierarchical MOC + Agent Tools)
- **建置原理**：以純文字 Markdown 資料夾樹為基礎。透過 Regex 建立實體內部連結，並由 LLM 為每一條法規補上 `Summary` 與 `Tags`，最終在每個資料夾生成 `_index.md` (Map of Content)。
- **檢索機制**：依賴具有 `list_dir`, `grep` 工具的 Agent 進行主動導航與探索，完全無須建立龐大的 Vector DB。

---

## 🏆 Benchmark 測試報告 (Evaluation Results)

我們設計了 15 題涵蓋「事實檢索」、「跨條文推論」、「全局總結」的問題，在本地端執行 `local_evaluator.py`，產生出 `benchmark_results.csv`。以下是三大架構在我們測試下的綜合表現：

| 評估維度 | Hybrid RAG (Vector+BM25) | Graph RAG (Entity+Traversal) | OKF LLM Wiki (Agent Tool) |
| :--- | :--- | :--- | :--- |
| **建置成本與算力** | 🟢 最低 (僅需 Embedding) | 🔴 極高 (需 7B LLM 全文掃描萃取) | 🟡 中 (需輕量 LLM 生成摘要) |
| **檢索精準度 (事實)** | 🟢 極高 (BM25 神助攻) | 🟡 中 (高度依賴入口節點抓取) | 🟢 極高 (Grep 精準打擊) |
| **跨文件推理能力** | 🟡 尚可 (若無重疊字詞易漏接) | 🟢 優秀 (透過 Edge 連結不同法規) | 🟢 優秀 (透過內部連結跳躍) |
| **全局總結能力** | 🔴 差 (Top-K 限制導致見樹不見林) | 🟢 優秀 (拓樸結構直接呈現關聯) | 🟢 優秀 (透過 MOC 目錄總結) |
| **查詢延遲 (Latency)** | 🟢 < 0.5 秒 | 🟡 0.5 ~ 1.5 秒 (取決於圖譜大小) | 🔴 > 15 秒 (Agent 需逐步使用工具) |

### 🔍 實際案例解析 (Case Study)

為了更具體說明，以下截取自我們真實執行的 `benchmark_results.csv` 測試紀錄：

#### 案例一：事實檢索 (Fact-retrieval)
> **問題**：「請問建築技術規則中，對於『建築基地面積』的定義是什麼？」
- **Hybrid RAG 表現**：完美命中！直接擷取出 `【第一章 用語定義 第1條】 二、建築基地面積：建築基地（以下簡稱基地）之水平投影面積。`。因為 BM25 發揮了強大的關鍵字綁定能力。
- **Graph RAG 表現**：抓出 `[第161條] 基地面積 -包括-> 法定騎樓面積` 與 `[第24條] 基地面積 -需大於等於-> 一千五百平方公尺` 等節點關聯。雖然提供了有用的周邊知識，但卻錯失了最核心的「定義句」（因為 LLM 萃取時偏向抓取條件關係，而非單純的名詞解釋）。
- **OKF LLM Wiki 表現**：Agent 透過 `grep` 全域搜尋或直接查閱 `第一章_用語定義/_index.md`，花費約 2~3 秒精準定位到 `第1條.md`，並閱讀完整 Markdown 內文獲得百分之百正確的定義。不僅準確，且無須耗費算力維持 Vector DB。

#### 案例二：跨條文關聯推論 (Multi-hop)
> **問題**：「私設通路是否計入法定空地？如果與道路交叉是否需要截角？」
- **Hybrid RAG 表現**：成功命中 `第118條 (不得計入)` 與 `第163條 (得計入)` 的矛盾與但書。
- **Graph RAG 表現**：瞬間拉出包含 `寬度不得小於-> 二公尺`、`因地形無法供車輛通行-> 得免設迴車道`、`長度-> 超過三十五公尺` 等十幾條關於私設通路的設計規範網絡。這展示了 Graph RAG 在面對「我想了解某個實體的所有相關規定」時，能提供比傳統 RAG 完整數倍的全局視野。
- **OKF LLM Wiki 表現**：Agent 搜尋 `私設通路` 後，會看到結果散佈在數十個 md 檔案中。此時 Agent 可進一步過濾含有 `#法定空地` 或 `#截角` 標籤的檔案。雖然最終也能拼湊出完整答案，但需要 Agent 執行多次工具呼叫（花費 15 秒以上），相較於 Graph RAG 一次性拉出拓樸圖，OKF 架構在盤點這類發散性知識時，處理效率較低。

### 結論與建議 (Conclusion)
1. **追求極致速度與精準條文 (定義/法條背誦)**：首選 **Hybrid RAG**，成本低且效果好。
2. **面對高度關聯、需跨條文推理的複雜知識庫 (設計規範盤點)**：推薦 **Graph RAG**，雖然建置成本高，但對於找出隱含關聯與整體限制有奇效。
3. **無算力預算、需要人類與 AI 協作**：使用 **OKF LLM Wiki**，它不僅對 Agent 友善，人類用 Obsidian 閱讀體驗也非常棒！

---

## 🔮 未來優化方向 (Future Work)

根據第一階段的 Benchmark 實測結果，我們歸納出在「下一版迭代」中，針對這三個系統可以進行的重大升級：

### 1. Hybrid RAG：導入「父子文件檢索 (Parent-Child Retriever)」
- **痛點**：目前的 Top-3 切塊往往過於細碎，導致缺乏前後文脈絡。
- **優化方案**：不改變 Vector DB 的切塊大小，但在 MetaData 中綁定「父層級 (如整條法規)」。當小切塊被檢索到時，系統自動將完整的父層級文本送給 LLM，兼顧精準度與完整度。

### 2. Graph RAG：導入「圖譜與原文綁定 (Graph-Document Binding)」
- **痛點**：LLM 萃取三元組時，容易把詳盡的名詞定義給「抽象化」成短短的關係邊 (Edge)，導致回答定義題時缺乏細節。
- **優化方案**：在建立實體節點 (Node) 的同時，將原始的「法規原文 Text」直接寫入該節點的 `Properties` 之中。當 Graph Traversal 抓取到該節點時，一併輸出原始法規，達到「見骨（關聯）也見肉（原文）」的終極型態。

### 3. OKF LLM Wiki：建立「主題式 MOC (Thematic Indexes)」
- **痛點**：當問題涉及散佈各處的零碎法條（如私設通路），Agent 必須花費大量時間來回呼叫 grep 與閱讀，嚴重拖慢回答速度。
- **優化方案**：除了原有的「章節階層 MOC」之外，定期讓 LLM 根據現有的 YAML Tags，自動彙整出**跨章節的主題式 MOC**（例如建立一個 `私設通路_統整.md`），讓 Agent 未來遇到這類問題時，能夠一鍵調閱所有相關連結！
