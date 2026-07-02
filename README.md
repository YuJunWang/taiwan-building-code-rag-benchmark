**繁體中文** | [English](README_EN.md)

# LLM Knowledge Retrieval Benchmark: RAG vs. Graph RAG vs. OKF-Wiki

這是一個針對台灣《建築技術規則建築設計施工編》所建立的進階 AI 知識檢索架構比較專案。
本專案實作並嚴格對比了目前市面上主流的三種 LLM 知識庫架構，提供給開發者與企業作為導入 AI 系統的架構選擇參考。

## 📁 專案目錄結構 (Folder Structure)

為了能順利執行本地端的自動化測試腳本，請確保專案維持以下結構：

```text
RAG_GraphRAG_LLMwiki/
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

## 🚀 V2 架構升級重點與成果 (V2 Enhancements)

根據初期的實測結果，我們已在最新的 V2 資料庫中完成了架構升級：
1. **Hybrid RAG**：導入「父子文件檢索 (Parent-Child Retriever)」，綁定完整法規脈絡。
2. **Graph RAG**：導入「圖譜與原文綁定 (Graph-Document Binding)」，節點自帶法條全文。
3. **OKF LLM Wiki**：導入「Bigram 檢索與主題式 MOC」，強化 Agent 的跨章節搜尋能力。

> 👉 **[點此查看：15 題全量 V2 Benchmark 終極測試報告](docs/benchmark_v2_report.md)**

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

### 🔍 實際案例解析：V2 雙階段 RAG 實測 (Case Study)

為了符合真實世界的 RAG 運作邏輯，我們的 V2 測試報告將流程明確切割為**「[第一階段] 檢索查閱」**與**「[第二階段] AI 答案提取」**。以下截取自真實執行的測試紀錄：

#### 案例一：事實定義檢索 (Fact-retrieval)
> **問題**：「請問建築技術規則中，對於『建築基地面積』的定義是什麼？」

*   **🟢 Hybrid RAG**
    *   **[第一階段] 檢索查閱**：精準命中！直接擷取出 `【第一章 第1條】 二、建築基地面積：建築基地之水平投影面積。`
    *   **[第二階段] 答案提取**：🤖 *「根據建築技術規則第1條第2款，明確定義為：建築基地之『水平投影面積』。」*
*   **🔵 Graph RAG**
    *   **[第一階段] 檢索查閱**：抓出 `[第161條] 基地面積 -包括-> 法定騎樓面積` 等關聯邊。
    *   **[第二階段] 答案提取**：🤖 *「檢索到的圖譜結果僅指出基地面積的計算『包括法定騎樓面積』，並未提供最基礎的法規定義。」* (AI 如實指出圖譜缺乏基礎定義)
*   **🟡 OKF LLM Wiki**
    *   **[第一階段] 檢索查閱**：Agent 成功命中 `第一章_用語定義` 以及 `第1條.md` 的片段。
    *   **[第二階段] 答案提取**：🤖 *「根據檢索到的第1條主題導覽，雖然指出包含建築面積定義，但因未讀取到具體原文，未能給出定義。」*

#### 案例分析結論
透過明確的雙階段切割，我們可以清楚看到：**「給 AI 什麼料，它就只能炒什麼菜」**。
1. **Hybrid RAG** 仍是找尋定義題與長篇幅規範的王者。
2. **Graph RAG** 在實體關聯（A 包含 B）上表現極佳，但在基礎定義上容易失焦。
3. **OKF LLM Wiki** 高度還原人類翻書邏輯，搭配優良的 Markdown 結構，能有效定位範圍。

---
