---
name: okf-wiki-navigator
description: A navigation strategy for LLM Agents to accurately and efficiently explore OKF (Open Knowledge Format) Markdown repositories.
---

# OKF Wiki Navigator (OKF 導航指南)

You are equipped with the OKF Wiki Navigator skill. This skill allows you to efficiently find answers within an OKF (Open Knowledge Format) database, which is structured like a Markdown Wiki with Maps of Content (MOC). 

Your goal is to answer the user's questions by exploring the `data/databases/okf_knowledge/` directory.

## 🧭 Core Navigation Strategy (Top-Down Approach)

Instead of blinding searching for keywords across all files, you MUST use the following strategic flow:

### 1. Identify the Topic (MOC Routing)
- Always start by listing the directories at the root of the OKF database using the `list_dir` tool on `data/databases/okf_knowledge/`.
- Look at the folder names. They are usually chapters or major categories (e.g., `第一章_用語定義`, `第四章_防火避難設施`).
- **Reasoning**: Based on the user's question, deduce which chapter/folder is most likely to contain the answer. 

### 2. Read the Map of Content (`_index.md`)
- Once you enter a suspected folder, use `view_file` to read the `_index.md` file inside it.
- The `_index.md` file contains a summary of all articles (regulations) in that folder.
- **Reasoning**: Read the index to find the exact file name (e.g., `第90條.md`) that matches the specific detail the user is asking about.

### 3. Targeted Reading & Breadcrumb Tracking
- Use `view_file` to read the specific markdown file you identified.
- Read the content carefully. 
- **CRITICAL**: If the text contains references to other articles (e.g., "除符合第96條規定外..."), and those articles are necessary to fully answer the question, **DO NOT GUESS**. 
- Check the YAML `related_articles` array at the top of the markdown file. It contains the exact relative paths to related articles (e.g., `["第三章_建築物之防火/第一節_出入口_走廊_樓梯/第96條"]`).
- Append `.md` to the relative path and use `view_file` to open that referenced file (e.g., `第三章_建築物之防火/第一節_出入口_走廊_樓梯/第96條.md`).
- If an article is referenced in the text but NOT listed in `related_articles`, use the `grep_search` tool to search for its filename (e.g. `第96條.md`) inside the `data/databases/okf_knowledge/` directory to find its exact path before calling `view_file`.

### 4. Fallback (Grep Search)
- If you have checked the `_index.md` files of the logical chapters but still cannot find the relevant article, or if the user's question uses very specific jargon that spans multiple chapters, you may use the `grep_search` tool.
- When using `grep_search`, search for highly specific, unique keywords within `data/databases/okf_knowledge/`. 
- After `grep_search` returns file paths, ALWAYS use `view_file` to read the full context of those files to ensure you understand the rules correctly.

## ⚠️ Constraints & Guidelines
1. **Never Hallucinate**: Only provide answers based on the text you have explicitly read using `view_file`. If the regulation does not mention something, explicitly state that it is not covered in the retrieved text.
2. **Be Efficient**: Avoid reading files that are obviously irrelevant based on their titles in `_index.md`.
3. **Cite Your Sources**: When providing the final answer, explicitly state which file(s) (e.g., `第四章_.../第90條.md`) you derived the answer from.

Execute your navigation now.
