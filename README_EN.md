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
│   └── databases/                            # [Download and place from Colab]
│       ├── rag_hybrid_export/                # Hybrid RAG Database (Chroma & BM25)
│       ├── graph_rag_hybrid_export/          # Graph RAG Database (GraphML & Entity Vector DB)
│       └── okf_knowledge/                    # OKF Local Knowledge Base (Markdown Tree)
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
│       ├── okf_answers.json
│       └── benchmark_results_v2.csv
├── docs/                                     # Documentation and Markdown reports
│   └── benchmark_v2_report.md
├── archive/                                  # Historical and temp files (gitignored)
├── requirements.txt
├── README.md
└── README_EN.md
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

To simulate a real-world RAG pipeline, our V2 test report explicitly splits the process into **"[Stage 1] Retrieval"** and **"[Stage 2] AI Generation"**. Below is an excerpt from the actual tests covering three different levels of questions:

#### Case 1: Fact-retrieval
> **Question**: "What is the definition of 'Building Base Area' in the building code?"

*   **🟢 Hybrid RAG**
    *   **[Stage 1] Retrieval**: Perfect hit! Extracts `【Chapter 1 Article 1】 2. Building Base Area: The horizontal projected area of the building base.`
    *   **[Stage 2] AI Generation**: 🤖 *According to Article 1, Paragraph 2, the 'Building Base Area' is clearly defined as the 'horizontal projected area' of the building base.* (✅ Perfect)
*   **🔵 Graph RAG**
    *   **[Stage 1] Retrieval**: Extracts edges like `[Article 161] Base Area -includes-> Statutory Arcade Area`.
    *   **[Stage 2] AI Generation**: 🤖 *The retrieved graph results only indicate that the calculation includes the statutory arcade area, and does not provide the most basic regulatory definition.* (❌ Missed the core definition)
*   **🟡 OKF LLM Wiki**
    *   **[Stage 1] Retrieval**: The Agent successfully hits `Chapter 1_Definitions` and the `Article 1.md` snippet.
    *   **[Stage 2] AI Generation**: 🤖 *According to the retrieved Article 1 thematic index, although it points out that the building area definition is included, because the specific original text was not read, the definition cannot be provided.* (❌ Agent gave up too early)

#### Case 2: Multi-hop Reasoning
> **Question**: "Is a private road counted in the statutory open space? Does it need a cut-off if it intersects a road?"

*   **🟢 Hybrid RAG**
    *   **[Stage 1] Retrieval**: Successfully hits the proviso `the part not exceeding 35 meters may be counted`.
    *   **[Stage 2] AI Generation**: 🤖 *If the length does not exceed 35 meters, it may be counted; regarding the cut-off at the intersection with a road, it is not mentioned in this text.* (⚠️ Half right)
*   **🔵 Graph RAG**
    *   **[Stage 1] Retrieval**: Instantly pulls edges like `Private road -length over 35m-> requires vehicle turning area` and `Intersection of road and turning area -cut-off length is-> 4 meters`.
    *   **[Stage 2] AI Generation**: 🤖 *It does not mention whether it is counted as statutory open space, nor does it state if a cut-off is needed when intersecting a road, it only stipulates a 4-meter cut-off for the intersection with a 'turning area'.* (✅ Accurately points out the blind spot)
*   **🟡 OKF LLM Wiki**
    *   **[Stage 1] Retrieval**: The Agent finds results scattered across dozens of md files after searching.
    *   **[Stage 2] AI Generation**: 🤖 *The intersection of a private road and a road is 'exempt from cut-off'; as for whether it is counted as 'statutory open space', it is not mentioned in the text.* (⚠️ Half right, different part)

#### Case 3: Global Summarization
> **Question**: "Looking at the entire 'Building Design and Construction Chapter', what are the core design principles for disaster prevention and evacuation in 'High-rise Buildings'? Please summarize three main points."

*   **🟢 Hybrid RAG**
    *   **[Stage 1] Retrieval**: Only catches a few scattered articles due to Top-K limits.
    *   **[Stage 2] AI Generation**: 🤖 *1. Vertical space fire zoning. 2. Establish a disaster prevention center. 3. Foundation structural safety (unrelated to evacuation).* (❌ Misses the big picture, off-topic)
*   **🔵 Graph RAG**
    *   **[Stage 1] Retrieval**: Pulls a massive topology of `Disaster Prevention Equipment in High-rise Buildings`.
    *   **[Stage 2] AI Generation**: 🤖 *1. Frame strength and toughness. 2. Fire-resistant wiring for cables. The third point lacks information.* (❌ Has a broad view, but misses the "evacuation" theme)
*   **🟡 OKF LLM Wiki**
    *   **[Stage 1] Retrieval**: Agent directly navigates to the `Chapter 12_High-rise Buildings/Section 3_Fire Prevention and Evacuation Facilities` directory.
    *   **[Stage 2] AI Generation**: 🤖 *1. Install at least two special safety stairs. 2. Corridors form independent fire zones. 3. Gas equipment centralized and equipped with alarms.* (✅ Perfect summary! MOC directory works wonders)

#### Conclusion on the Case
Through the two-stage separation and three different levels of questions, we can clearly see: **"The AI can only cook with the ingredients it is given."**
1. **Hybrid RAG** remains the king of finding "fact definitions" and long regulations.
2. **Graph RAG** performs exceptionally well on "entity relationships and conditional limits (A contains B, 4m cut-off)", but easily loses focus on basic definitions.
3. **OKF LLM Wiki** highly mimics human reading logic, and combined with MOC directories, is extremely good at "cross-chapter summarization" or "global summaries with a specific theme".

---
