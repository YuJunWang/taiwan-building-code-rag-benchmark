[繁體中文](README.md) | **English**

# LLM Knowledge Retrieval Benchmark: RAG vs. Graph RAG vs. OKF-Wiki

This project is an advanced AI knowledge retrieval architecture comparison, using the **Taiwan Building Regulations (Building Design and Construction Chapter)** as the primary dataset.
It implements and strictly benchmarks three mainstream LLM knowledge base architectures, providing a reference for developers and enterprises when choosing an AI architecture. In a sense, the processed data in this repository can also serve as a lightweight database for the Taiwanese building code.

## 📁 Folder Structure

To ensure the local automated testing scripts run smoothly, please maintain the following project structure:

```text
RAG_GraphRAG_LLMwiki/
├── data/
│   ├── raw/
│   │   └── building_regulations_v2.json      # Raw crawled regulatory data
│   └── databases/                            # [Built-in] Complete databases for the 3 architectures
│       ├── rag_hybrid_export/                # Hybrid RAG Database (Chroma & BM25)
│       ├── graph_rag_hybrid_export/          # Graph RAG Database (GraphML & Entity Vector DB)
│       └── okf_knowledge/                    # OKF Local Knowledge Base (Markdown Tree)
├── agent_skills/
│   └── okf-wiki-navigator/                   # OKF Agent Navigation Strategy (SKILL)
├── scripts/
│   ├── build/                                # Colab build scripts for the 3 databases
│   │   ├── colab_build_rag.py
│   │   ├── colab_build_graph_rag.py
│   │   └── colab_build_okf_enrichment.py
├── benchmark/                                # Evaluation and Testing
│   ├── evaluation_questions.json             # 15 benchmark questions
│   ├── local_evaluator.py                    # Local automated evaluation script
│   ├── compile_report.py                     # Report generation script
│   └── results/                              # Query results and CSV
│       ├── hybrid_answers.json
│       ├── graph_answers.json
│       ├── okf_agent_answers.json            # Final answers produced by the real Agent test
│       └── benchmark_results_v2.csv
├── agent_skills/                             # Agent navigation skills (SKILL)
├── docs/                                     # Documentation and Markdown reports
│   └── benchmark_v2_report.md
├── archive/                                  # Historical and temp files (gitignored)
├── requirements.txt
├── README.md
└── README_EN.md
```

## 🚀 Quick Start

Since the text-based databases are small in size (MB scale), the complete databases for all three architectures are already included in this repository. You can clone and test directly without rebuilding them:

```bash
# 1. Clone the project
git clone https://github.com/YuJunWang/taiwan-building-code-rag-benchmark.git
cd taiwan-building-code-rag-benchmark

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the V2 evaluation script
python benchmark/local_evaluator.py
```
> After running, the results will be output to `benchmark/results/benchmark_results_v2.csv`.

## 🛠️ Build from Scratch

If you wish to rebuild the databases from scratch, or replace them with your own dataset, please refer to the following steps:

It is recommended to use `uv` or `pip` to install dependencies:

```bash
# Using pip
pip install -r requirements.txt

# Using uv
uv pip install -r requirements.txt
```

---

## 🧰 Tech Stack

This project deliberately selects lightweight, open-source, and local-friendly frameworks to ensure a zero-barrier execution of the benchmark:

- **LangChain**: Serves as the orchestration framework, unifying the logic for LLMs, vector search, and keyword search.
- **ChromaDB**: A lightweight, local vector database (SQLite based) that provides an "out-of-the-box" experience without needing Docker.
- **Rank-BM25**: A keyword retrieval algorithm based on term frequency, perfectly compensating for the blind spots of vector search in matching exact legal terms and numbers.
- **NetworkX**: A native Python graph theory library used to load Graph RAG's entity relationship graphs into memory for rapid graph traversal, bypassing the need for heavy graph databases.
- **BAAI/bge-m3**: A top-tier open-source embedding model from HuggingFace, offering excellent semantic capture for Traditional Chinese legal and long-context texts.

---

## 📊 Methodology

### 1. Traditional RAG (Hybrid Search + Structural Chunking)
- **Construction**: Abandons traditional fixed-length chunking in favor of structural chunking based on the law's native "Article/Paragraph" hierarchy. It binds "Chapter and Article Number" to the context.
- **Retrieval (Hybrid Search)**: Uses `BAAI/bge-m3` for semantic search, combined with `BM25` for exact keyword matching, and finally re-ranks with RRF (Reciprocal Rank Fusion). This effectively solves the issue of legal terminology being easily misinterpreted by pure vector retrieval.

### 2. Graph RAG (Two-tiered Indexing)
- **Construction**: Relies on Qwen2.5-7B-Instruct to extract Triplets (Subject-Predicate-Object) from the regulations, generating thousands of interconnected nodes.
- **Retrieval**: A two-tiered architecture. The first tier uses a Vector DB to find "Entity Entry Points" related to the User Query. The second tier traverses the Knowledge Graph via NetworkX from those entry points, pulling a highly correlated web of knowledge simultaneously.

### 3. OKF-based LLM Wiki (Hierarchical MOC + Agent Tools + SKILL)
- **Construction**: Based on a pure text Markdown folder tree. Internal links are established via Regex, and an LLM appends a `Summary` and `Tags` to each regulation, ultimately generating an `_index.md` (Map of Content) for each folder.
- **Retrieval**: Relies on an AI Agent equipped with `list_dir` and `view_file` tools for active navigation and exploration. To prevent the Agent from getting lost, we specifically developed the `okf-wiki-navigator` SKILL. This grants the Agent the ability to "prioritize reading the MOC (directory)" and "follow breadcrumbs", giving it true human-like book-flipping logic, completely eliminating the need for a massive Vector DB.

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

To simulate a real-world RAG pipeline, our V2 test report explicitly splits the process into **"[Stage 1] Retrieval"** and **"[Stage 2] AI Generation"**. Below is an excerpt from the actual tests covering three different levels of questions:

#### Case 1: Fact-retrieval
> **Question**: "What is the definition of 'Building Base Area' in the building code?"

*   **🟢 Hybrid RAG**
    *   **[Stage 1] Retrieval**: Extracted `【Chapter 1 Article 1】 2. Building base area: the horizontal projection area of the building base.`
    *   **[Stage 2] Answer Extraction**: 🤖 *"Clearly defined as: the 'horizontal projection area' of the building base."*
        *   ✅ **Complete Answer**
*   **🔵 Graph RAG**
    *   **[Stage 1] Retrieval**: Extracted `【Entity Text - Building Base Area】 Building base area: the horizontal projection area of the building base.`
    *   **[Stage 2] Answer Extraction**: 🤖 *"According to the context, the definition of the building base area is 'the horizontal projection area of the building base (hereinafter referred to as the base)'."*
        *   ✅ **Complete Answer** (Successfully answered after introducing entity text binding in V2)
*   **🟡 OKF LLM Wiki**
    *   **[Stage 1] Agent Retrieval**: The Agent successfully matched `Chapter 1_Terminology` and snippets of `Article 1.md`.
    *   **[Stage 2] Answer Extraction**: 🤖 *"According to the Building Technical Regulations, the definition of 'building site area' is: the horizontal projection area of the building site (hereinafter referred to as the site)."*
        *   ✅ **Complete Answer**

#### Case 2: Multi-hop Reasoning
> **Question**: "Is a private road counted in the statutory open space? Does it need a cut-off if it intersects a road?"

*   **🟢 Hybrid RAG**
    *   **[Stage 1] Retrieval**: Hit the contradiction and exception of `the part not exceeding 35 meters can be included`.
    *   **[Stage 2] Answer Extraction**: 🤖 *"If the part not exceeding 35 meters can be included in the statutory open space area; regarding whether a cut-off is needed when intersecting a road, this text does not mention it."*
        *   ⚠️ **Partially Correct** (Did not cover the corner cutoff rule)
*   **🔵 Graph RAG**
    *   **[Stage 1] Retrieval**: Instantly pulls edges like `Private road -length over 35m-> requires vehicle turning area` and `Intersection of road and turning area -cut-off length is-> 4 meters`.
    *   **[Stage 2] Answer Extraction**: 🤖 *"It does not mention whether it is counted as statutory open space, nor does it state if a cut-off is needed when intersecting a road, it only stipulates a 4-meter cut-off for the intersection with a 'turning area'."*
        *   ⚠️ **Partially Correct** (Pointed out the cutoff blind spot, but missed the open space rule)
*   **🟡 OKF LLM Wiki**
    *   **[Stage 1] Agent Retrieval**: After searching for `private passage`, the Agent read the MOC to quickly lock onto the relevant regulations.
    *   **[Stage 2] Answer Extraction**: 🤖 *"1. Regarding statutory open space: the part not exceeding 35 meters can be included. 2. Regarding corner cutoff: the intersection is exempt from corner cutoff."*
        *   ✅ **Complete Answer** (Correctly integrated cross-article and exception rules)

#### Case 3: Global Summarization
> **Question**: "Looking at the entire 'Building Design and Construction Chapter', what are the core design principles for disaster prevention and evacuation in 'High-rise Buildings'? Please summarize three main points."

*   **🟢 Hybrid RAG**
    *   **[Stage 1] Retrieval**: Only caught a few sporadic articles about high-rise buildings due to Top-K limitation.
    *   **[Stage 2] Answer Extraction**: 🤖 *"1. Vertical space fire compartments. 2. Establish a disaster prevention center. 3. Foundation structure safety (non-evacuation related)."*
        *   ❌ **Off-topic** (Did not cover the main theme of evacuation)
*   **🔵 Graph RAG**
    *   **[Stage 1] Retrieval**: Pulled a massive topology of `Disaster Prevention Equipment in High-rise Buildings`.
    *   **[Stage 2] Answer Extraction**: 🤖 *"1. Frame strength and toughness. 2. Fire-resistant wiring for cables. The third point lacks information."*
        *   ❌ **Missed Core Theme** (Lacked evacuation focus)
*   **🟡 OKF LLM Wiki**
    *   **[Stage 1] Agent Retrieval**: The Agent directly navigated to the `Chapter 12_High-Rise Buildings/Section 3_Fire Safety and Evacuation Facilities` directory.
    *   **[Stage 2] Answer Extraction**: 🤖 *"1. Independent protection for two-direction evacuation routes. 2. Strict fire compartments for vertical shafts and gas equipment. 3. Installation of emergency elevators and a centralized disaster prevention center."*
        *   ✅ **Complete Answer** (Correctly summarized the three core points)

#### Conclusion on the Case
Through the two-stage separation and three different levels of questions, we can clearly see: **"The AI can only cook with the ingredients it is given."**
1. **Hybrid RAG** remains the king of finding "fact definitions" and long regulations.
2. **Graph RAG** performs exceptionally well on "entity relationships and conditional limits (A contains B, 4m cut-off)", but easily loses focus on basic definitions.
3. **OKF LLM Wiki** highly mimics human reading logic, and combined with MOC directories, is extremely good at "cross-chapter summarization" or "global summaries with a specific theme".

---
