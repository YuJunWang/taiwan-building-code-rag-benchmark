# Benchmark 測試標準作業流程 (Standard Testing Methodology)

為了確保專案未來所有的測試都能夠達到「客觀、擬真、且不受外部 API 影響」的嚴格標準，本專案一律採用以下「全動態真 Agentic 測試方案」。

## 核心理念 (Core Philosophy)
1. **零 LLM API 依賴進行檢索與生成**：在作答階段，嚴禁使用帶有 API Key (如 OpenAI, Groq) 的 Python 腳本來直接生成答案。生成任務必須交由具備獨立思考能力的 Antigravity Gemini Native Agent (Subagent) 親自執行。
2. **檢索與生成分離 (Separation of Retrieval and Generation)**：測試必須真實還原各系統的「檢索流程」，Agent 不能只是靜態地讀取預先抓好的 JSON，而必須親自在終端機下達檢索指令或操作資料夾。
3. **時間測量 (Latency Tracking)**：每一次作答都必須精準紀錄從「接獲題目」到「給出解答」的總耗時（秒），以反映系統的真實運作延遲。
4. **頂級法官評分 (Top-tier LLM-as-a-judge)**：答案產出後，統一交由最高等級的模型（如 `llama-3.3-70b-versatile` 或 GPT-4o）透過 LangSmith 進行雙盲給分。

## 角色與執行方式 (Agent Roles & Execution)

### 1. Hybrid RAG 測試 (Chroma + BM25)
- **檢索工具**：本機端檢索腳本 `benchmark/retrieve_hybrid.py`。
- **Agent 行為**：Agent 針對每道題目，必須在終端機執行 `python benchmark/retrieve_hybrid.py "題目"`。
- **作答邏輯**：Agent 閱讀終端機印出的 Context 後，結合自身的理解給出精簡答案。

### 2. Graph RAG 測試 (NetworkX + Entity Vector)
- **檢索工具**：本機端檢索腳本 `benchmark/retrieve_graph.py`。
- **Agent 行為**：Agent 針對每道題目，必須在終端機執行 `python benchmark/retrieve_graph.py "題目"`。
- **作答邏輯**：Agent 閱讀終端機印出的 Graph Traversal Context 後，結合自身的理解給出精簡答案。

### 3. OKF LLM Wiki 測試 (純 Agentic Navigator)
- **檢索工具**：無。僅依賴基礎指令 (`list_dir`, `view_file`)。
- **Agent 行為**：Agent 直接進入 `data/databases/okf_knowledge` 目錄，模擬人類翻書。先閱讀 `_MOC.md` 目錄，再層層深入查找具體的 Markdown 條文。
- **作答邏輯**：Agent 結合自己在檔案堆中挖掘到的所有資訊，給出精簡答案。

## 評分與輸出 (Evaluation & Output)

1. **紀錄答案與時間**：
   三位 Agent 執行完 15 題後，必須將結果統一寫入對應的 JSON 中（如 `benchmark/results/hybrid_answers_timed.json`），格式必須包含 `answers` 陣列與 `total_time_seconds`。
   
2. **LangSmith LLM-as-a-judge**：
   執行 `evals/run_evals.py`，該腳本會讀取答案，並對照 `evaluation_questions.json` 中的 `expected_answer` 進行嚴格給分。

3. **報告產出**：
   執行 `benchmark/fetch_scores.py` 獲取最終分數，並將時間與分數對照表更新進 `README.md`。
