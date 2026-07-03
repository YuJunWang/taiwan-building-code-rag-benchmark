**繁體中文** | [English](README_EN.md)

# LLM Knowledge Retrieval Benchmark: RAG vs. Graph RAG vs. OKF-Wiki

這是一個針對台灣《建築技術規則建築設計施工編》所建立的進階 AI 知識檢索架構比較專案。
本專案實作並嚴格對比了目前市面上主流的三種 LLM 知識庫架構，提供給開發者與企業作為導入 AI 系統的架構選擇參考。

## 📁 專案目錄結構 (Folder Structure)

為了能順利執行本地端的自動化測試腳本，請確保專案維持以下結構：

```text
RAG_GraphRAG_LLMwiki/
├── data/
│   ├── raw/
│   │   └── building_regulations_v2.json      # 原始法規爬蟲資料
│   └── databases/                            # [已內建] 三大架構的完整法規資料庫
│       ├── rag_hybrid_export/                # Hybrid RAG 資料庫 (包含 Chroma 與 BM25)
│       ├── graph_rag_hybrid_export/          # Graph RAG 資料庫 (包含 GraphML 與 Entity Vector DB)
│       └── okf_knowledge/                    # OKF 本地知識庫 (Markdown 目錄樹)
├── agent_skills/
│   └── okf-wiki-navigator/                   # OKF 專屬 Agent 導航策略 (SKILL)
├── scripts/
│   ├── build/                                # 三大資料庫 Colab 雲端建置腳本
│   │   ├── colab_build_rag.py
│   │   ├── colab_build_graph_rag.py
│   │   └── colab_build_okf_enrichment.py
├── benchmark/                                # 評估與測試區
│   ├── evaluation_questions.json             # 15個基準測試題目 (從 all_contexts.json 萃取)
│   ├── local_evaluator.py                    # 本地端自動化評估主程式
│   ├── compile_report.py                     # 報表生成腳本
│   └── results/                              # 查詢結果與報表
│       ├── hybrid_answers.json
│       ├── graph_answers.json
│       ├── okf_agent_answers.json            # 真實 Agent 測試產出的最終答案
│       └── benchmark_results_v2.csv
├── agent_skills/                             # 存放 Agent 導航技能 (SKILL) 檔案
├── docs/                                     # 文件與 Markdown 報表
│   └── benchmark_v2_report.md
├── archive/                                  # 歷史備份與過渡檔案 (已被 .gitignore 排除)
├── requirements.txt
├── README.md
└── README_EN.md
```

## 🚀 快速開始 (Quick Start)

由於法規純文字資料庫體積不大（MB 等級），本專案已將三大架構的完整資料庫一併包含在 Repo 中，您可以直接 clone 並執行測試，無需重新建置資料庫：

```bash
# 1. 取得專案
git clone https://github.com/YuJunWang/taiwan-building-code-rag-benchmark.git
cd taiwan-building-code-rag-benchmark

# 2. 安裝套件
pip install -r requirements.txt

# 3. 直接執行 V2 評估腳本
python benchmark/local_evaluator.py
```
> 執行後，結果將輸出至 `benchmark/results/benchmark_results_v2.csv`。

## 🛠️ 資料庫建置 (Build from Scratch)

如果您希望從零開始重新建置資料庫，或是將其替換為您自己的資料集，請參考以下步驟：

建議使用 `uv` 或 `pip` 安裝相依套件：

```bash
# 使用 pip
pip install -r requirements.txt

# 使用 uv
uv pip install -r requirements.txt
```

---

## 🧰 核心技術棧 (Tech Stack)

本專案刻意挑選「輕量、開源、適合本地端運行」的框架，確保任何人都能零門檻執行 Benchmark：

- **LangChain**：作為應用層框架，統一串接 LLM、向量檢索與關鍵字檢索機制。
- **ChromaDB**：輕量級本地端向量資料庫 (SQLite based)，無需架設 Docker 伺服器即可「開箱即用」。
- **Rank-BM25**：基於詞頻的關鍵字檢索演算法，完美彌補向量檢索在法規專有名詞與數字比對上的盲點。
- **NetworkX**：Python 原生的圖論網路庫，將 Graph RAG 的實體關聯圖譜載入記憶體中進行極速拓樸擴展 (Graph Traversal)，取代笨重的圖形資料庫。
- **BAAI/bge-m3**：HuggingFace 頂級開源 Embedding 模型，對繁體中文法規與長文本語意有極佳的捕捉能力。

---

## 📊 三大架構實作原理 (Methodology)

### 1. 傳統 RAG (Hybrid Search + Structural Chunking)
- **建置原理**：放棄傳統的固定字數切塊，改採法規原生的「條/項/款」精細切塊，並強制將「章節名稱與條號」綁定於 Context 中。
- **檢索機制 (Hybrid Search)**：透過 `BAAI/bge-m3` 進行語意搜尋，結合 `BM25` 關鍵字精準匹配，最後以 RRF (Reciprocal Rank Fusion) 重新排序，有效解決法律專有名詞容易因純向量檢索而誤判的問題。

### 2. Graph RAG (Two-tiered Indexing)
- **建置原理**：交由 Qwen2.5-7B-Instruct 萃取法規中的三元組 (Subject-Predicate-Object) 並建立成千上萬個節點。
- **檢索機制**：雙層檢索架構。第一層透過 Vector DB 找到與 User Query 相關的「實體入口節點 (Entry Point)」，第二層從入口節點利用 NetworkX 在知識圖譜中進行擴展 (Graph Traversal)，一次性拉出高度關聯的知識網。

### 3. OKF-based LLM Wiki (Hierarchical MOC + Agent Tools + SKILL)
- **建置原理**：以純文字 Markdown 資料夾樹為基礎。透過 Regex 建立實體內部連結，並由 LLM 為每一條法規補上 `Summary` 與 `Tags`，最終在每個資料夾生成 `_index.md` (Map of Content)。
- **檢索機制**：依賴具有 `list_dir`, `view_file` 等工具的 Agent 進行主動導航與探索。為了解決 Agent 迷失的問題，我們特別開發了 `okf-wiki-navigator` SKILL，賦予 Agent「優先閱讀 MOC (目錄)」與「循線追蹤麵包屑」的能力，使其具備真正的人類翻書邏輯，完全無須建立龐大的 Vector DB。

## 🚀 V2 架構升級重點與成果 (V2 Enhancements)

根據初期的實測結果，我們已在最新的 V2 資料庫中完成了架構升級：
1. **Hybrid RAG**：導入「父子文件檢索 (Parent-Child Retriever)」，綁定完整法規脈絡。
2. **Graph RAG**：導入「圖譜與原文綁定 (Graph-Document Binding)」，節點自帶法條全文。
3. **OKF LLM Wiki**：導入「Bigram 檢索與主題式 MOC」，強化 Agent 的跨章節搜尋能力。

> 👉 **[點此查看：15 題全量 V2 Benchmark 終極測試報告](docs/benchmark_v2_report.md)**

---

## ⚙️ 實驗環境與檢索參數設定 (Experimental Setup)

為了確保評估的公平性與可重現性，本次 Benchmark 在本地端執行 `local_evaluator.py` 與 Agent 測試時，採用以下參數設定：

1. **基礎設施**
   *   Embedding Model：採用 `BAAI/bge-m3` 處理繁體中文法規。
   *   Vector DB：採用 `Chroma` 進行向量儲存。
   *   LLM：答案提取階段與 OKF Agent 推理階段皆使用 **Gemini 3.1 Pro (於 Antigravity 2.0 環境)** 作為底層模型。

2. **各架構檢索參數 (Retrieval Parameters)**
   *   **🟢 Hybrid RAG**
       *   **檢索策略**：Vector Search + BM25
       *   **Top-K**：取最相關的前 3 個 Chunk (`k=3`)。
       *   **後處理**：透過 Parent-Child Retriever 邏輯，將命中的小 Chunk 還原回所屬的「完整父條文 (Parent Text)」，以確保法規脈絡不被切斷。
   *   **🔵 Graph RAG**
       *   **入口搜尋**：對實體 (Entity) 向量庫進行相似度檢索，取 Top 3 實體 (`k=3`) 作為入口節點。
       *   **圖譜擴展**：進行 1-Hop 拓樸擴展 (提取關聯邊與鄰居節點)。
       *   **上下文限制**：最多回傳 15 筆拓樸邊 (`limit=15`)，並一併附上入口節點所綁定的完整實體原文 (Graph-Document Binding)。
   *   **🟡 OKF LLM Wiki**
       *   **檢索策略**：純 Agentic 探索，完全不用 Vector DB。
       *   **賦予工具**：僅提供 `list_dir` (讀取目錄)、`view_file` (檢視文件)、`grep_search` (關鍵字搜尋)。
       *   **導航守則**：嚴格遵守 `agent_skills/okf-wiki-navigator`，強制 Agent 先閱讀目錄 (MOC)，再循線鑽取至底層 Markdown 檔案。

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

為了符合真實世界的 RAG 運作邏輯，我們的 V2 測試報告將流程明確切割為**「[第一階段] 檢索查閱」**與**「[第二階段] AI 答案提取」**。以下截取自真實測試紀錄的三個不同層次問題：

#### 案例一：事實定義檢索 (Fact-retrieval)
> **問題**：「請問建築技術規則中，對於『建築基地面積』的定義是什麼？」

*   **🟢 Hybrid RAG**
    *   **[第一階段] 檢索查閱**：擷取出 `【第一章 第1條】 二、建築基地面積：建築基地之水平投影面積。`
    *   **[第二階段] 答案提取**：🤖 *「明確定義為：建築基地之『水平投影面積』。」*
        *   ✅ **完整回答**
*   **🔵 Graph RAG**
    *   **[第一階段] 檢索查閱**：擷取出 `【實體原文 - 建築基地面積】 建築基地面積：建築基地（以下簡稱基地）之水平投影面積。`
    *   **[第二階段] 答案提取**：🤖 *「根據上下文，建築基地面積的定義為『建築基地（以下簡稱基地）之水平投影面積』。」*
        *   ✅ **完整回答** (V2 導入實體原文綁定後已能成功回答)
*   **🟡 OKF LLM Wiki**
    *   **[第一階段] Agent 檢索查閱**：Agent 成功命中 `第一章_用語定義` 以及 `第1條.md` 的片段。
    *   **[第二階段] 答案提取**：🤖 *「依據建築技術規則，對於『建築基地面積』的定義為：建築基地（以下簡稱基地）之水平投影面積。」*
        *   ✅ **完整回答**

#### 案例二：跨條文關聯推論 (Multi-hop Reasoning)
> **問題**：「某建商想在基地內設置一條『私設通路』，該私設通路是否計入法定空地？如果與道路交叉是否需要截角？」

*   **🟢 Hybrid RAG**
    *   **[第一階段] 檢索查閱**：命中 `未超過三十五公尺部分得計入` 的矛盾與但書。
    *   **[第二階段] 答案提取**：🤖 *「若未超過35公尺部分得計入法定空地面積；關於與道路交叉是否需要截角，此段文本中未提及。」*
        *   ⚠️ **部分正確** (未涵蓋截角規定)
*   **🔵 Graph RAG**
    *   **[第一階段] 檢索查閱**：擷取出包含 `私設通路 -長度超過三十五公尺-> 應設置汽車迴車道`、`通路與迴車道交叉口 -截角長度為-> 四公尺` 的關聯邊。
    *   **[第二階段] 答案提取**：🤖 *「未提及是否計入法定空地，也未說明與道路交叉是否截角，僅規定與『迴車道』交叉口截角為四公尺。」*
        *   ⚠️ **部分正確** (指出截角盲點，但未回答法定空地)
*   **🟡 OKF LLM Wiki**
    *   **[第一階段] Agent 檢索查閱**：Agent 搜尋 `私設通路` 後，透過閱讀 MOC 導覽頁快速鎖定關聯法規。
    *   **[第二階段] 答案提取**：🤖 *「1. 關於法定空地：未超過35公尺的部分得計入。2. 關於截角：該交叉口免截角。」*
        *   ✅ **完整回答** (正確統整跨條文與例外規範)

#### 案例三：全局總結 (Global Summarization)
> **問題**：「綜觀整部《建築設計施工編》，關於『高層建築物』在防災與逃生避難上的核心設計原則是什麼？請歸納出三個主要重點。」

*   **🟢 Hybrid RAG**
    *   **[第一階段] 檢索查閱**：因 Top-K 限制，僅取得高層建築物某幾個零星條文。
    *   **[第二階段] 答案提取**：🤖 *「1. 垂直空間防火區劃。2. 設置防災中心。3. 基礎結構安全 (非避難相關)。」*
        *   ❌ **內容偏題** (未涵蓋逃生避難主軸)
*   **🔵 Graph RAG**
    *   **[第一階段] 檢索查閱**：擷取出 `高層建築物之防災設備` 的龐大拓樸。
    *   **[第二階段] 答案提取**：🤖 *「1. 構架強度與韌性。2. 電線電纜防火配線。第三個重點缺乏資訊。」*
        *   ❌ **未命中核心主軸** (缺乏逃生避難重點)
*   **🟡 OKF LLM Wiki**
    *   **[第一階段] Agent 檢索查閱**：Agent 直接導航至 `第十二章_高層建築物/第三節_防火避難設施` 目錄。
    *   **[第二階段] 答案提取**：🤖 *「1. 二方向避難與逃生動線獨立防護。2. 垂直管道與燃氣設備的嚴格防火區劃。3. 設置緊急昇降機與集中指揮之防災中心。」*
        *   ✅ **完整回答** (正確歸納三大核心重點)

#### 案例分析結論
透過雙階段切割與三種不同層次的問題，我們可以清楚看到：**「給 AI 什麼料，它就只能炒什麼菜」**。
1. **Hybrid RAG** 仍是找尋「事實定義」與長篇幅規範的王者。
2. **Graph RAG** 在「實體關聯、條件限制（A 包含 B、截角四公尺）」上表現極佳，但在基礎定義上容易失焦。
3. **OKF LLM Wiki** 高度還原人類翻書邏輯，搭配 MOC 目錄，極度擅長「跨章節尋找大意」或「有明確主題域的全局總結」。

---

## 🔮 未來展望：OKF 架構的進化藍圖 (Future Vision)

本次 Benchmark 驗證了 OKF (Open Knowledge Format) 在「全局理解」與「跨條文推論」上的壓倒性優勢，證明了讓 Agent 讀取無損的 Markdown 完整檔案與 MOC (Map of Content) 目錄，能徹底解決傳統 RAG 破碎上下文的問題。

然而，純 Agent 導航仍面臨檢索速度較慢、Token 消耗較高的挑戰。為了將 OKF 的效益極大化，未來可針對以下四個維度進行增強，使其從「靜態檔案庫」進化為「會自我生長的神經網路大腦」：

1. **導入雙向連結 (Wiki-Style Hyperlinking) 🔗**
   * **概念**：如同 Obsidian 或 Wikipedia，在 Markdown 內文中直接標註關聯法規的超連結（如：`依據 [第十一條](第一章/第11條.md) 辦理`）。
   * **效益**：Agent 閱讀到連結時，無須退回根目錄搜尋，可直接呼叫工具瞬間跳轉。這能將跨章節檢索的時間從十幾秒壓縮至 1 秒內，實現高速的神經突觸跳轉。

2. **OKF + Vector 混合動力 (雙引擎啟動) 🚀**
   * **概念**：結合傳統 Vector Search 的「快」與 OKF 的「準」。
   * **效益**：當接收到提問時，先以毫秒級的向量檢索找出 Top-1 的實體 Markdown 檔案路徑作為「空投座標」，直接交給 Agent 作為起點。Agent 藉此省去前期閱讀目錄的摸索時間，直接進入高階邏輯驗證與跳轉階段。

3. **Frontmatter 屬性標籤化 (Metadata Graph) 🏷️**
   * **概念**：利用現有的 YAML Frontmatter（如 `tags:`, `related_articles:`），在背景建立輕量級的屬性圖譜 (Property Graph)。
   * **效益**：讓 Agent 擁有上帝視角，能透過工具瞬間取得特定標籤的檔案清單，以極低成本白嫖 Graph RAG 的拓樸能力，且無須維護昂貴的圖資料庫。

4. **經驗沉澱與自我生長 (Agentic Memory & Distillation) 🧠**
   * **概念**：當 Agent 經歷複雜的跨章節推論並成功解答後（例如耗時 30 秒統整了高層建築的消防規範），自動將該推論結果生成為一份 `FAQ_高層建築消防總結.md`，並存回 OKF 系統中。
   * **效益**：**讓系統越用越聰明、越用越快**。未來遇到類似問題時，Agent 在閱讀目錄時便能直接發現這份 FAQ 檔案，實現 O(1) 的極速回覆（Knowledge Distillation）。
