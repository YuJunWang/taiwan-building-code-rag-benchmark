**繁體中文** | [English](README_EN.md)

# LLM Knowledge Retrieval Benchmark: RAG vs. Graph RAG vs. OKF-Wiki

這是一個針對台灣《建築技術規則建築設計施工編》所建立的進階 AI 知識檢索架構比較專案。
專案核心目標並非獨厚單一架構，而是客觀實作並對比目前主流的三種知識庫架構，點出從「底層建置」到「實際查詢」的真實優缺點，提供開發者與企業最務實的技術選型參考。

---

## 📊 三大系統綜合評測與優缺點 (System Comparison)

基於最新的 **V3 基準測試**（15 題複雜法規考題，由 Gemini 3.1 Pro 進行雙盲客觀評估），三大系統的表現與特性統整如下：

| 系統架構 | 建置成本 (Setup) | 查詢速度 (Speed) | Gemini 3.1 Pro 評分 | 核心優點 (Pros) | 致命缺點 (Cons) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Hybrid RAG**<br>(Vector + BM25) | 🟢 **最低**<br>僅需 Embedding 模型計算向量 | 🟡 **中等**<br>~13 秒 | 🔴 **33%** | 建置最快、技術門檻低、非常適合單一事實或明確關鍵字的檢索。 | 容易發生 Chunk 截斷丟失上下文；一次塞入過多文本導致大腦處理過載；跨章節推論能力極弱。 |
| **Graph RAG**<br>(知識圖譜擴展) | 🔴 **極高**<br>需使用強大 LLM 全文掃描萃取實體 | 🟢 **極快**<br>~2.5 秒 | 🟡 **67%** | 回答速度極快（雜訊最少）；對於實體關聯、明確的數字規定與條件限制極度敏銳。 | 建置極度耗時且昂貴；若前置作業 LLM 沒有萃取出該實體，查詢時會直接找不到資料。 |
| **OKF-Wiki**<br>(Agent 本地目錄導航) | 🟡 **中等**<br>需使用 LLM 生成摘要與 MOC | 🟡 **中等**<br>~13 秒 | 🟢 **70%** | 準確率最高、邏輯推演最完整；具備類似人類查書的容錯率，能循線追蹤跨章節法規。 | 查詢速度受限於 Agent 多次呼叫工具的過程；對於極簡單的單一問題會有「牛刀小試」的效能浪費。 |

> 👉 **詳細的逐題測試紀錄與法官點評，請參閱：[15 題全量 V3 Benchmark 終極測試報告](docs/benchmark_v3_report.md)**

---

## 🔍 架構實作原理 (Methodology)

本專案刻意挑選「輕量、開源、適合本地端運行」的框架，確保任何人都能零門檻執行 Benchmark。

1. **傳統 RAG (Hybrid Search + Structural Chunking)**
   * **實作**：使用 Chroma (向量) + Rank-BM25 (關鍵字) 進行混合檢索，並採用 RRF 重新排序。
   * **特色**：放棄固定字數切塊，改採法規原生「條/項/款」切塊，並導入「父子文件 (Parent-Child)」檢索還原完整脈絡。
2. **Graph RAG (Two-tiered Indexing)**
   * **實作**：交由 Qwen2.5-7B 萃取法規中的三元組 (Entity-Relationship) 建立圖譜。
   * **特色**：以 Vector DB 尋找入口節點，再利用 NetworkX 於記憶體中進行 1-Hop 拓樸擴展，並綁定實體原文確保定義不失真。
3. **OKF LLM Wiki (Hierarchical MOC + Agent Tools)**
   * **實作**：純文字 Markdown 目錄樹。利用 LLM 生成標準化的 _index.md (Map of Content) 與相對路徑雙向連結。
   * **特色**：完全不依賴向量庫，賦予 Agent list_dir 與 iew_file 能力，強制 Agent 先閱讀目錄再循線鑽取法規。

---

## 🚀 專案結構與執行 (Quick Start)

法規資料庫體積小（MB 等級），本專案已將三大架構的完整資料庫內建於 Repo data/databases/ 中，您可以直接 clone 並執行測試，無需重新建置：

\\\ash
# 1. 取得專案並安裝套件
git clone https://github.com/YuJunWang/taiwan-building-code-rag-benchmark.git
cd taiwan-building-code-rag-benchmark
pip install -r requirements.txt

# 2. 直接執行評估腳本
python benchmark/local_evaluator.py
\\\

> 若需重新建置資料庫，建置腳本存放於 scripts/build/ 目錄下，可透過 Colab 執行。

---

## 🔮 未來展望 (Future Vision)

針對上述系統的優缺點，未來落地的最佳實踐將朝向**整合架構**發展：

1. **雙引擎啟動 (Vector + Agent) 🚀**
   * 結合 Vector Search 的「快」與 OKF Agent 的「準」。先以毫秒級向量檢索給出精準的檔案位置「空投座標」，省去 Agent 前期看目錄的時間，直接切入高階邏輯驗證。
2. **經驗沉澱與自我生長 (Agentic Memory) 🧠**
   * 當系統經歷複雜的跨章節推論並解答成功後，自動將該推論結果寫成一份 FAQ.md 存回系統。讓知識庫越用越聰明，未來遇到類似問題即可實現 O(1) 的極速回覆。
