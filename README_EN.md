[繁體中文](README.md) | **English**

# LLM Knowledge Retrieval Benchmark: RAG vs. Graph RAG vs. OKF-Wiki

This project is an advanced AI knowledge retrieval architecture comparison, using the **Taiwan Building Regulations (Building Design and Construction Chapter)** as the primary dataset.
It implements and strictly benchmarks three mainstream LLM knowledge base architectures, providing a reference for developers and enterprises when choosing an AI architecture. In a sense, the processed data in this repository can also serve as a lightweight database for the Taiwanese building code.

## 📁 Folder Structure

To ensure the local automated testing scripts run smoothly, please maintain the following project structure:

```text
11_RAG_GraphRAG_LLMwiki/
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

### 🔍 Case Study

To illustrate, here are excerpts from our actual `benchmark_results.csv`:

#### Case 1: Fact-retrieval
> **Question**: "What is the definition of 'Building Base Area' in the building code?"
- **Hybrid RAG**: Perfect hit! Extracts the exact definition clause. BM25 exerts strong keyword binding.
- **Graph RAG**: Extracts nodes like `Base Area -includes-> Statutory Arcade Area`. Provides useful peripheral knowledge but misses the core definitional sentence (because LLM extraction favors conditional relationships over noun explanations).
- **OKF LLM Wiki**: The Agent uses `grep` or reads `_index.md`, finding the exact file in 2~3 seconds and reading the full Markdown text for a 100% accurate definition. Highly accurate without vector DB overhead.

#### Case 2: Multi-hop Reasoning
> **Question**: "Is a private road counted in the statutory open space? Does it need a cut-off if it intersects a road?"
- **Hybrid RAG**: Successfully hits the contradictions and provisos in Article 118 and 163.
- **Graph RAG**: Instantly pulls a network of over a dozen design specifications related to private roads (e.g., `width -> at least 2m`, `length -> over 35m`). This demonstrates Graph RAG's overwhelming advantage in providing a global view when asking for all regulations concerning a specific entity.
- **OKF LLM Wiki**: The Agent finds results scattered across dozens of md files. While the Agent can filter by tags, piecing together the full answer requires multiple tool calls (>15 seconds). It is less efficient than Graph RAG for expansive knowledge gathering.

### Conclusion
1. **For Extreme Speed & Exact Clauses (Definitions)**: **Hybrid RAG** is the first choice. Low cost, great results.
2. **For Highly Correlated, Multi-hop Reasoning (Design Specs)**: **Graph RAG** is recommended. High build cost, but exceptional at finding hidden correlations.
3. **No Compute Budget, Requires Human-AI Collab**: **OKF LLM Wiki** is extremely friendly to both AI Agents and humans (using tools like Obsidian).

---

## 🚀 V2 Enhancements

Based on the Phase 1 Benchmark, we have successfully implemented the following major architecture upgrades in the latest V2 database:

### 1. Hybrid RAG: "Parent-Child Retriever"
Without changing the Vector DB chunk size, we bound the "Full Article (parent_text)" in the MetaData. Now, when a small chunk is retrieved, the system automatically restores the entire regulation, completely resolving the context fragmentation issue caused by Top-K retrieval.

### 2. Graph RAG: "Graph-Document Binding"
When creating Entity Nodes in the knowledge graph, we now write the original "Raw Regulation Text (raw_text)" directly into the node's properties. During Graph Traversal, the LLM not only sees the relational edges between nodes but also reads the most detailed original text of the regulation.

### 3. OKF LLM Wiki: "Thematic Indexes (MOCs)"
In addition to the existing chapter hierarchy, the system now automatically aggregates **cross-chapter Thematic MOCs** (e.g., `_theme_fire_compartment.md`) based on global YAML Tags. Agents can now access all related links with a single click when dealing with complex queries scattered across various chapters!

> 💡 **Want to see the stunning results of the V2 upgrade?**
> We re-tested the upgraded system against the 15 rigorous questions. Please see:
> 👉 **[V2 Architecture Benchmark Detailed Report](docs/benchmark_v2_report.md)**
