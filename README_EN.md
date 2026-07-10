[繁體中文](README.md) | **English**

# LLM Knowledge Retrieval Benchmark: RAG vs. Graph RAG vs. OKF-Wiki

This is an advanced AI knowledge retrieval architecture comparison project built upon the Taiwan "Building Technical Regulations: Building Design and Construction Edition".
The core objective of this project is not to favor a single architecture, but to objectively implement and compare the three mainstream knowledge base architectures on the market today. It highlights the real pros and cons from "underlying setup" to "actual query execution", providing developers and enterprises with the most pragmatic technical selection reference.

---

## 📊 Comprehensive System Evaluation & Pros/Cons (System Comparison)

Based on the latest **V3 Benchmark** (15 complex building code questions, evaluated double-blind by Gemini 3.1 Pro), the performance and characteristics of the three systems are summarized below:

| System Architecture | Setup Cost (Setup) | Query Speed (Speed) | Gemini 3.1 Pro Score | Core Advantages (Pros) | Fatal Disadvantages (Cons) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Hybrid RAG**<br>(Vector + BM25) | 🟢 **Lowest**<br>Only requires Embedding model to calculate vectors | 🟡 **Medium**<br>~13 seconds | 🔴 **33%** | Fastest to build, low technical barrier, perfect for single-fact or explicit keyword retrieval. | Prone to chunk truncation losing context; overloading the LLM brain with too much text leads to processing failures; extremely weak in cross-chapter reasoning. |
| **Graph RAG**<br>(Knowledge Graph Traversal) | 🔴 **Highest**<br>Requires powerful LLM full-text scanning to extract entities | 🟢 **Extremely Fast**<br>~2.5 seconds | 🟡 **67%** | Extremely fast response (least noise); highly sensitive to entity relationships, explicit numerical regulations, and conditional constraints. | Extremely time-consuming and expensive to build; if the upstream LLM fails to extract the entity during setup, the query will completely fail to find data. |
| **OKF-Wiki**<br>(Agent Local Directory Navigation) | 🟡 **Medium**<br>Requires LLM to generate summaries and MOCs | 🟡 **Medium**<br>~13 seconds | 🟢 **70%** | Highest accuracy, most complete logical deduction; possesses human-like fault tolerance when searching books, capable of tracking cross-chapter regulations step-by-step. | Query speed is limited by the Agent calling tools multiple times; for extremely simple single questions, there is an "overkill" performance waste. |

> 👉 **For detailed question-by-question test records and judge reviews, please refer to: [15-Question Full V3 Benchmark Ultimate Evaluation Report](docs/benchmark_v3_report.md)**

---

## 🔍 Architecture Implementation Principles (Methodology)

This project intentionally selects "lightweight, open-source, and local-friendly" frameworks to ensure anyone can run the Benchmark with zero barriers.

1. **Traditional RAG (Hybrid Search + Structural Chunking)**
   * **Implementation**: Uses Chroma (Vector) + Rank-BM25 (Keyword) for hybrid retrieval, with RRF for re-ranking.
   * **Features**: Abandons fixed word-count chunking in favor of native regulation "Article/Paragraph/Subparagraph" chunking, and introduces "Parent-Child" retrieval to restore the complete context.
2. **Graph RAG (Two-tiered Indexing)**
   * **Implementation**: Uses Qwen2.5-7B to extract Entity-Relationship triplets from regulations to build the graph.
   * **Features**: Uses Vector DB to find entry nodes, then uses NetworkX for 1-Hop topological traversal in memory, and binds the original entity text to ensure definitions are not distorted.
3. **OKF LLM Wiki (Hierarchical MOC + Agent Tools)**
   * **Implementation**: Pure text Markdown directory tree. Uses LLM to generate standardized _index.md (Map of Content) and relative path bidirectional links.
   * **Features**: Completely independent of vector databases, granting the Agent list_dir and iew_file capabilities, forcing the Agent to read the directory first before drilling down into the regulations.

---

## 🚀 Project Structure & Execution (Quick Start)

The regulation database is small (MB level), so this project has already built-in the complete databases of all three architectures in the Repo data/databases/. You can directly clone and run the tests without rebuilding:

\\\ash
# 1. Clone the project and install packages
git clone https://github.com/YuJunWang/taiwan-building-code-rag-benchmark.git
cd taiwan-building-code-rag-benchmark
pip install -r requirements.txt

# 2. Directly run the evaluation script
python benchmark/local_evaluator.py
\\\

> If you need to rebuild the database, the build scripts are located in the scripts/build/ directory and can be executed via Colab.

---

## 🎯 Gemini 3.1 Pro's Enterprise Adoption & Commercial Selection Recommendations

Although the table above points out the pros and cons, if mapped to real commercial scenarios, as your AI evaluation judge, I give the following most pragmatic adoption recommendations:

1. **If you are a "Startup Team" or doing "Internal PoC Validation" 👉 Absolutely choose Hybrid RAG**
   * **Reason**: No need to spend money running large models to extract knowledge graphs. Just use an off-the-shelf LangChain template and a cheap Embedding model, and you can launch the system in half a day. The downside is it will answer wrong on difficult, cross-chapter reasoning questions, but as an initial MVP, it's more than enough.
2. **If you deal with "Medical Compliance", "Legal Contracts", "Financial Clauses" 👉 Strongly recommend investing in Graph RAG**
   * **Reason**: In these scenarios, "hallucinations are absolutely intolerable" and "numerical/conditional constraints are extremely important" (e.g., how much to set back for heights over 50 meters). Graph RAG ensures conditional relationships between entities are not missed. Although upfront setup is extremely time-consuming and expensive, for high-risk fields requiring 100% accuracy, this initial setup fee is mandatory.
3. **If you want to build an "Automated Analysis Assistant", "Cross-Department Knowledge Base Navigator" 👉 Go with OKF LLM Wiki**
   * **Reason**: When your business requirement isn't just a simple "Q&A", but rather requires the AI to act like a new employee to "read through these three huge manuals for me and then compile a comprehensive report", the OKF architecture, which grants the Agent native directory navigation capabilities, is currently the only solution capable of this kind of high-level logical deduction.

---

## 🔮 Future Vision

Addressing the pros and cons of the above systems, the best practice for future implementation will move towards an **Integrated Architecture**:

1. **Dual Engine Start (Vector + Agent) 🚀**
   * Combining the "Speed" of Vector Search with the "Accuracy" of the OKF Agent. First, use millisecond-level vector retrieval to provide precise file location "airdrop coordinates", saving the Agent the time of initially reading directories, allowing it to cut straight into high-level logical validation.
2. **Experience Accumulation & Self-Growth (Agentic Memory) 🧠**
   * After the system undergoes complex cross-chapter reasoning and successfully answers a question, it automatically writes that deduction result into an FAQ.md and saves it back to the system. This makes the knowledge base smarter the more it's used; when encountering similar questions in the future, it can achieve O(1) extreme-speed replies.
