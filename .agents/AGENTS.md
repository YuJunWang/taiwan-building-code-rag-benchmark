# 專案專屬 Agent 行為規範 (Project Agent Guidelines)

這份文件定義了 AI Agent 在操作 `taiwan-building-code-rag-benchmark` 專案時必須嚴格遵守的最高指導原則。

## 1. 專案核心認知與語氣定調 (Context & Tone)
- **中立原則**：這是一個比較 Hybrid RAG、Graph RAG 與 OKF-Wiki 的基準測試 (Benchmark) 專案。在任何文件撰寫、程式碼註解中，**絕對禁止偏袒單一架構**。
- **客觀語氣**：文件受眾為需要「技術選型」的企業與開發者。必須使用平實、專業的技術名詞，**嚴禁**使用帶有強烈情緒或行銷色彩的浮誇字眼（如「致命缺點」、「神助攻」、「極度敏銳」）。

## 2. 目錄防護與環境整潔 (Directory Restrictions)
- **根目錄潔癖**：**嚴禁**在專案根目錄建立任何測試檔 (如 `test.py`) 或暫存輸出 (如 `dump.txt`)。所有臨時操作與產出的 Log 請一律放置於 `scratch/` 資料夾內進行。
- **資料庫防護**：`data/databases/` 中存放了預先建置好的各架構資料庫（Chroma、NetworkX 圖譜等）。除非使用者明確下達「重新建置 (Rebuild)」指令，否則 Agent **不得**隨意修改或刪除這些檔案。
- **文檔歸檔**：生成的評估報告必須統一放置於 `docs/`，原始評測數據紀錄於 `benchmark/results/` 中。

## 3. 測試與評估紀律 (Benchmark Workflow)
- **禁止通靈數據**：若要更新評測報告，必須基於 `eval_results.json` 中的真實數據，或是重新執行評估腳本。**絕對不允許由 AI 大腦自行捏造 (Hallucinate) 評分數據**。
- **法官模式**：若 Agent 奉命擔任「評分法官」，必須調閱標準答案，逐題雙盲審查所有系統的輸出，給出精準的 0.0 ~ 1.0 評分與點評，並利用 Python 腳本將結果寫回 `eval_results.json`，不可單憑對話紀錄計算。
- **重測警告 (Reproducibility)**：只要修改了任何一個系統的核心參數（例如 Chunk Size、萃取 Prompt、System Prompt），過去所有的評分數據將全數失效。Agent 必須主動警告使用者：「這將需要重新跑完整個基準測試」。

## 4. 程式碼與開發規範 (Development Standards)
- **套件安全 (Dependency Safety)**：RAG 相關套件迭代極快。**絕對不可擅自升級 `requirements.txt` 中的套件版本**。若為了解決 Bug 而必須升級，必須先告知可能連帶造成的架構癱瘓風險。
- **編碼防雷 (Encoding & PowerShell Quirks)**：
  - Python 讀寫任何檔案強制加上 `encoding='utf-8'`。
  - Windows 環境下，**嚴禁**使用 PowerShell 的字串插值 (Here-string) 寫入含有跳脫字元 (`\`) 的 Markdown 檔案，應優先呼叫原生編輯工具 (`replace_file_content` / `write_to_file`) 或撰寫 Python 腳本。
- **Agent 身分界定 (Agent Identity)**：在除錯 OKF-Wiki 時，清楚界定身分。Meta-Agent (協助開發的 AI) 只能修改受測 Agent 的系統提示詞或工具碼，**絕對禁止**以硬編碼 (Hardcode) 方式竄改受測 Agent 的內部輸出歷程來作弊。
- **資安防護 (Secret Management)**：此為開源專案。在除錯、印出 Log 或提交 Commit 時，自主審查並**嚴禁將任何 API Key 或 `.env` 內容推送到 GitHub**。

## 5. 資源與效能管理 (Resource & Scale Limits)
- **成本控管 (Cost Limits)**：Graph RAG 等知識圖譜建置極度消耗 Token。在執行全量重新建置前，Agent 必須建議「先在單一章節（小樣本）進行測試」，確認 Prompt 萃取無誤後，再放行全量建置，避免浪費使用者的 API 額度。
- **大檔案防雷 (Repo Size Control)**：向量資料庫 (`.sqlite3`) 與圖譜檔案容易無限制膨脹。在執行 `git add` 或 `git commit` 前，Agent 必須主動檢查 `data/databases/` 中檔案的大小，避免不小心把超過 GitHub 限制 (100MB) 的巨型檔案推上去導致 Git 紀錄損壞。
