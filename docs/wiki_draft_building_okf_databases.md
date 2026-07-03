---
title: "如何建構專業級的 OKF (Open Knowledge Format) 知識庫"
description: "探討如何為高度結構化文件（如法規、SOP、ISO 標準）建立 OKF 架構，利用原生的目錄樹與 LLM YAML 標註，實現 100% 準確率的 Agentic RAG。"
type: "concept"
tags: ["OKF", "Agentic Retrieval", "Data Architecture", "LLM Wiki", "RAG"]
---

# 如何建構專業級的 OKF (Open Knowledge Format) 知識庫

當面對高度結構化、邏輯嚴密且具備跨條文關聯的專業文件（如國家法規、醫療指引、企業 SOP）時，傳統的 RAG (Retrieval-Augmented Generation) 將文本暴力切片 (Chunking) 的做法，往往會導致上下文流失與定義錯置。

為了讓 Agent 能像人類專家一樣「翻閱」知識，我們引入了 **OKF (Open Knowledge Format)** 架構。OKF 的核心思想是將知識庫還原為「作業系統層級的樹狀目錄」與「無損的 Markdown 實體檔案」，並搭配 [[Agent-Readable Formats]] 使其成為極度適合 AI 閱讀的知識網絡。

以下是建構專屬 OKF 知識庫的標準化流程與核心原則：

## 1. 物理化原生架構 (Physicalizing Native Taxonomy)

專業文件（如法規）的「編、章、節、條」本身就是經過數十年淬鍊的最完美分類法。建構 OKF 的第一步，是**完全摒棄 AI 語意分群，直接照搬原生目錄結構**。

*   **作法**：撰寫腳本 (如 Python 爬蟲)，將原始結構轉換為作業系統的實體資料夾。
*   **範例**：
    ```text
    okf_knowledge/
    └── 建築技術規則建築設計施工編/
        ├── 第一章_用語定義/
        │   ├── 第1條.md
        │   └── 第2條.md
        ├── 第二章_一般設計通則/
        │   ├── 第一節_建築基地/
        │   │   ├── 第161條.md
    ```
*   **優勢**：保留了最強大的 Context（資料夾路徑即為前提條件），並確保未來修法時能實現 0 成本的無痛抽換覆蓋。

## 2. 兩階段全自動 YAML 標註 (Two-Stage Enrichment)

純文字的 Markdown 對 Agent 來說導航效率過低。我們需要在每個 `.md` 檔案的頂部注入 YAML Frontmatter，作為 Agent 的「摘要與地圖」。這通常透過兩階段完成：

1.  **階段一 (爬蟲與骨架)**：由程式抓取內容時，自動填寫結構性 Metadata (如 `title`, `chapter`, `section`)。
2.  **階段二 (LLM 語意萃取)**：撰寫背景腳本，讓本地 LLM (如 7B 級別的小模型) 閱讀每一份 Markdown 的完整內文，並自動生成：
    *   `summary`: 一句話的核心總結。
    *   `tags`: 3~5 個口語化關鍵字。
    *   `related_articles`: 掃描內文自動提取的關聯法規條號。
    
完成後的檔案會具備極強的導航性：
```yaml
---
title: "第1條"
chapter: "第一章 用語定義"
summary: "定義了建築技術規則中的關鍵術語及其計算方法，如建築面積、建蔽率等。"
tags: "建築面積, 建蔽率, 基地面積"
---
# 第1條
本編建築技術用語...
```

## 3. 目錄即索引 (Map of Content, MOC)

有了 YAML 標註後，每個資料夾可以動態生成一個 `_index.md`。這個檔案匯集了該資料夾下所有子檔案的 `title` 與 `summary`。
當 Agent 進入一個大章節時，它不再需要逐一打開每一條法規，而是只要閱讀該章節的 MOC 索引，就能瞬間鎖定目標，實現 [[Agentic Retrieval]] 中的 Top-Down 檢索策略。

## 4. 進化藍圖：邁向 Networked Thought

為了將單次檢索時間從數十秒壓縮至毫秒，並解決傳統樹狀結構無法橫向跳躍的痛點，OKF 知識庫可進一步導入以下機制：

*   **雙向連結 (Wiki-Style Hyperlinking)**：將內文中提到的條文直接轉換為 Markdown 連結（如 `[第161條](../第二章/第161條.md)`），允許 Agent 發現連結後直接呼叫 `view_file` 瞬間跳轉。
*   **雙引擎啟動 (Vector Airdrop)**：捨棄由上而下的目錄探索，改由極速的 Vector Search 砸出最接近的 Markdown 路徑作為空投座標，再交由 Agent 接手後續的邏輯跳轉與上下文驗證。
*   **知識蒸餾 (Knowledge Distillation)**：當 Agent 完成一次複雜的跨條文推論後，自動將結果沉澱為一份 `FAQ_xxx.md` 並存回系統。系統將隨著使用次數增加，累積越來越多 O(1) 的捷徑答案。

## 總結

建構 OKF 知識庫，本質上是將「檢索的困難」轉移為「前置的資訊架構工程 (Information Architecture)」。雖然初期建置解析器 (Parser) 成本較高，但能徹底消除 AI 的幻覺空間，是打造高風險專業領域（如法律、醫療）的終極方案。
