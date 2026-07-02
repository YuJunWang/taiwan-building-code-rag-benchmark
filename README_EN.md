[繁體中文](README.md) | **English**

# LLM Knowledge Retrieval Benchmark: RAG vs. Graph RAG vs. OKF-Wiki

This project is an advanced AI knowledge retrieval architecture comparison, using the **Taiwan Building Regulations (Building Design and Construction Chapter)** as the primary dataset.
It implements and strictly benchmarks three mainstream LLM knowledge base architectures, providing a reference for developers and enterprises when choosing an AI architecture. In a sense, the processed data in this repository can also serve as a lightweight database for the Taiwanese building code.

## 📁 Folder Structure

To ensure the local automated testing scripts run smoothly, please maintain the following project structure:

```text
RAG_GraphRAG_LLMwiki/
│
├── building_regulations_v2.json      # Raw crawled regulatory data
├── colab_build_rag.py                # Cloud build script (Hybrid RAG)
├── colab_build_graph_rag.py          # Cloud build script (Graph RAG)
├── colab_build_okf_enrichment.py     # Cloud build script (OKF Tagging)
├── local_evaluator.py                # Local automated evaluation script
├── requirements.txt                  # Python dependencies (supports uv/pip)
│
├── rag_hybrid_export/                # 📥 [Download] Hybrid RAG Database
│   └── chroma_db/                    # Contains Vector and BM25 indexes
│
├── graph_rag_hybrid_export/          # 📥 [Download] Graph RAG Database
│   ├── graph_rag_export.graphml      # NetworkX Knowledge Graph body
│   ├── graph_rag_export.json         # Graph metadata
│   └── entity_vector_db/             # Entity Node (Entry Points) vector DB
│
└── okf_knowledge/                    # 📥 [Download] OKF Local Knowledge Base
    ├── 第一章_用語定義/               # Chapter 1
    ├── 第二章_一般設計通則/             # Chapter 2
    └── ...
```

## 🛠️ Environment Setup

It is recommended to use `uv` or `pip` to install dependencies:

```bash
# Using pip
pip install -r requirements.txt

# Using uv
uv pip install -r requirements.txt
```

---

## 📊 Methodology

### 1. Traditional RAG (Hybrid Search + Structural Chunking)
- **Construction**: Abandons traditional fixed-length chunking in favor of structural chunking based on the law's native "Article/Paragraph" hierarchy. It binds "Chapter and Article Number" to the context.
- **Retrieval (Hybrid Search)**: Uses `BAAI/bge-m3` for semantic search, combined with `BM25` for exact keyword matching, and finally re-ranks with RRF (Reciprocal Rank Fusion). This effectively solves the issue of legal terminology being easily misinterpreted by pure vector retrieval.

### 2. Graph RAG (Two-tiered Indexing)
- **Construction**: Relies on Qwen2.5-7B-Instruct to extract Triplets (Subject-Predicate-Object) from the regulations, generating thousands of interconnected nodes.
- **Retrieval**: A two-tiered architecture. The first tier uses a Vector DB to find "Entity Entry Points" related to the User Query. The second tier traverses the Knowledge Graph via NetworkX from those entry points, pulling a highly correlated web of knowledge simultaneously.

### 3. OKF-based LLM Wiki (Hierarchical MOC + Agent Tools)
- **Construction**: Based on a pure text Markdown folder tree. Internal links are established via Regex, and an LLM appends a `Summary` and `Tags` to each regulation, ultimately generating an `_index.md` (Map of Content) for each folder.
- **Retrieval**: Relies on an AI Agent equipped with `list_dir` and `grep` tools for active navigation and exploration, completely eliminating the need for a massive Vector DB.

## 🚀 V2 Enhancements

Based on the initial test results, we have completed major architecture upgrades in the latest V2 database:
1. **Hybrid RAG**: "Parent-Child Retriever", automatically restores the full regulatory context.
2. **Graph RAG**: "Graph-Document Binding", nodes now carry the full original text.
3. **OKF LLM Wiki**: "Bigram Retrieval & Thematic MOCs", greatly strengthening the Agent's cross-chapter search ability.

> 👉 **[Click here: 15-Question V2 Benchmark Final Report](docs/benchmark_v2_report.md)**

---

## 🏆 Evaluation Results (Benchmark)

We designed 15 questions covering "Fact Retrieval", "Multi-hop Reasoning", and "Global Summarization". We executed `local_evaluator.py` locally and generated `benchmark_results.csv`. Below is the comprehensive performance of the three architectures:

| Evaluation Metric | Hybrid RAG (Vector+BM25) | Graph RAG (Entity+Traversal) | OKF LLM Wiki (Agent Tool) |
| :--- | :--- | :--- | :--- |
| **Compute Cost** | 🟢 Lowest (Embedding only) | 🔴 Extremely High (7B LLM Extraction) | 🟡 Medium (Lightweight LLM Summarization) |
| **Accuracy (Fact)** | 🟢 Extremely High (BM25 helps) | 🟡 Medium (Relies heavily on entry point) | 🟢 Extremely High (Grep precision) |
| **Multi-hop Reasoning** | 🟡 Fair (Misses without word overlap) | 🟢 Excellent (Connects via Edges) | 🟢 Excellent (Jumps via internal links) |
| **Global Summarization**| 🔴 Poor (Top-K limits view) | 🟢 Excellent (Topology shows relations) | 🟢 Excellent (Summarizes via MOC) |
| **Latency** | 🟢 < 0.5 sec | 🟡 0.5 ~ 1.5 sec (Depends on size) | 🔴 > 15 sec (Agent needs multiple tools) |

### 🔍 Case Study: V2 Two-Stage RAG Execution

To simulate a real-world RAG pipeline, our V2 test report explicitly splits the process into **"[Stage 1] Retrieval"** and **"[Stage 2] AI Generation"**. Below is an excerpt from the actual tests:

#### Case 1: Fact-retrieval
> **Question**: "What is the definition of 'Building Base Area' in the building code?"

*   **🟢 Hybrid RAG**
    *   **[Stage 1] Retrieval**: Perfect hit! Extracts `【Chapter 1 Article 1】 2. Building Base Area: The horizontal projected area of the building base.`
    *   **[Stage 2] AI Generation**: 🤖 *According to Article 1, Paragraph 2 of the Building Technical Regulations, the 'Building Base Area' is clearly defined as the 'horizontal projected area' of the building base.*
*   **🔵 Graph RAG**
    *   **[Stage 1] Retrieval**: Extracts edges like `[Article 161] Base Area -includes-> Statutory Arcade Area`.
    *   **[Stage 2] AI Generation**: 🤖 *The retrieved graph results only indicate that the calculation of the base area 'includes the statutory arcade area', and does not provide the most basic regulatory definition.* (The AI accurately points out the graph's lack of a foundational definition)
*   **🟡 OKF LLM Wiki**
    *   **[Stage 1] Retrieval**: The Agent successfully hits `Chapter 1_Definitions` and the `Article 1.md` snippet.
    *   **[Stage 2] AI Generation**: 🤖 *According to the retrieved Article 1 thematic index, although it points out that the building area definition is included, because the specific original text was not read, the definition cannot be provided.*

#### Conclusion on the Case
Through this clear two-stage separation, we can see: **"The AI can only cook with the ingredients it is given."**
1. **Hybrid RAG** remains the king of finding definitions and long regulations.
2. **Graph RAG** performs exceptionally well on entity relationships (A contains B) but easily loses focus on basic definitions.
3. **OKF LLM Wiki** highly mimics human reading logic; with a good Markdown structure, it can effectively narrow down the scope.

---
