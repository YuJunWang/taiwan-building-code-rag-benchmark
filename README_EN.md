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
│       └── benchmark_results_v3.csv
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
> After running, the results will be output to `benchmark/results/benchmark_results_v3.csv`.

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

Based on the initial test results and the V2 architecture evaluations, we have completed the following upgrades in the latest version:
1. **Hybrid RAG**: "Parent-Child Retriever", restores the matched small chunks to their parent regulations to prevent context truncation.
2. **Graph RAG**: "Graph-Document Binding", entity nodes now directly bind the original regulatory text, resolving definition ambiguities from returning only entity names.
3. **OKF LLM Wiki (Large-scale Standardization & Graphification)**:
   - **Standard Markdown Hyperlinking 🔗**: Re-formatted all MOCs and index files to remove emojis, and upgraded the original Obsidian-specific `[[filename]]` wikilinks to standard Markdown relative path links (`[name](./path.md)`). This ensures all links render and resolve correctly in any Markdown viewer, GitHub preview, or AI Agent environment. Agents can now directly pass the link path to `view_file` for cross-file navigation.
   - **Frontmatter Metadata Graph 🏷️**: Leveraged AI to generate `summary` and `tags` metadata for all 700+ articles, and created 56 cross-chapter MOCs under the `主題索引/` folder, achieving thematic topology searches without Vector DBs.
   - **Local Automation & Traditional Chinese Correction**: Integrated One-shot prompting and OpenCC (s2twp) translation into the Colab build script to eradicate simplified Chinese outputs and formatting discrepancies.

> 👉 **[Click here: 15-Question Full V2 Benchmark Ultimate Test Report](docs/benchmark_v2_report.md)**

---

## ⚙️ Experimental Setup & Retrieval Parameters

To ensure the fairness and reproducibility of the evaluation, the following parameters were used during the execution of `local_evaluator.py` and Agent testing in this Benchmark:

1. **Infrastructure**
   *   Embedding Model: `BAAI/bge-m3` was used to process Traditional Chinese legal texts.
   *   Vector DB: `Chroma` was used for vector storage.
   *   LLM: Both the answer extraction phase and the OKF Agent reasoning phase used **Gemini 3.1 Pro (in Antigravity 2.0 environment)** as the underlying model.

2. **Retrieval Parameters per Architecture**
   *   **🟢 Hybrid RAG**
       *   **Retrieval Strategy**: Vector Search + BM25
       *   **Top-K**: Retrieves the top 3 most relevant chunks (`k=3`).
       *   **Post-processing**: Through the Parent-Child Retriever logic, the matched small chunks are restored to their "Parent Text" to ensure the context of the law is not truncated.
   *   **🔵 Graph RAG**
       *   **Entry Point Search**: Performs similarity search on the Entity vector database, taking the Top 3 entities (`k=3`) as entry nodes.
       *   **Graph Expansion**: Performs 1-Hop topology expansion (extracting associated edges and neighbor nodes).
       *   **Context Limit**: Returns a maximum of 15 topology edges (`limit=15`) and attaches the complete original entity text bound to the entry node (Graph-Document Binding).
   *   **🟡 OKF LLM Wiki**
       *   **Retrieval Strategy**: Purely Agentic exploration, completely without Vector DB.
       *   **Tools Provided**: Only `list_dir` (read directory), `view_file` (view file), and `grep_search` (keyword search) are provided.
       *   **Navigation Rules**: Strictly follows `agent_skills/okf-wiki-navigator`, forcing the Agent to read the Map of Content (MOC) first, then follow the breadcrumbs down to the bottom-level Markdown files.

---

## 🏆 Evaluation Results (Benchmark)

We designed 15 questions covering "Fact Retrieval", "Multi-hop Reasoning", and "Global Summarization". We executed `local_evaluator.py` locally and generated `benchmark_results.csv`. Below is the comprehensive performance of the three architectures:

| Evaluation Metric | Hybrid RAG (Vector+BM25) | Graph RAG (Entity+Traversal) | OKF LLM Wiki (Agent Tool) |
| :--- | :--- | :--- | :--- |
| **Compute Cost** | 🟢 Lowest (Embedding only) | 🔴 Extremely High (7B LLM Extraction) | 🟡 Medium (Lightweight LLM Summarization) |
| **Accuracy (Fact)** | 🟢 Extremely High (BM25 helps) | 🟡 Medium (Relies heavily on entry point) | 🟢 Extremely High (Grep precision) |
| **Multi-hop Reasoning** | 🟡 Fair (Misses without word overlap) | 🟢 Excellent (Connects via Edges) | 🟢 Excellent (Jumps via internal links) |
| **Global Summarization**| 🔴 Poor (Top-K limits view) | 🟢 Excellent (Topology shows relations) | 🟢 Excellent (Summarizes via MOC) |
| **Latency** | 🟢 < 0.5 sec | 🟡 0.5 ~ 1.5 sec (Depends on size) | 🔴 ~30-40 sec (Agent multi-step reasoning & tool calls) |
| **LangSmith Eval (Strict Metric)** | 🟡 0.57 (57%) | 🔴 0.07 (7%) | 🟢 0.90 (90%) |

### 🔍 Case Study: V2 Two-Stage RAG Execution

To simulate a real-world RAG pipeline, our V2 test report explicitly splits the process for Hybrid RAG and Graph RAG into **"[Stage 1] Retrieval"** and **"[Stage 2] AI Generation"**. OKF LLM Wiki, due to its autonomous agentic nature, uses a **"[Single Stage] Autonomous Agent Retrieval & Reasoning"** evaluation model. Below is an excerpt from the actual tests covering three different levels of questions:

#### Case 1: Fact-retrieval
> **Question**: "What is the definition of 'Building Base Area' in the building code?"

*   **🟢 Hybrid RAG**
    *   **[Stage 1] Retrieval**: Extracted `【Chapter 1 Article 1】 2. Building base area: the horizontal projection area of the building base.`
    *   **[Stage 2] Answer Extraction**: 🤖 *"The horizontal projection area of the building site."*
        *   ✅ **Complete Answer**
*   **🔵 Graph RAG**
    *   **[Stage 1] Retrieval**: Extracted entity relationship edges and entity source text related to `site area` and `arcade` (but failed to retrieve Article 1 from Terminology containing the base definition of "horizontal projection area").
    *   **[Stage 2] Answer Extraction**: 🤖 *"The calculation of the building site area includes the statutory arcade area. However, the area occupied by arcades in commercial zones... is not included in the site area."*
        *   ❌ **Incomplete Answer** (Failed to hit the core definition of "horizontal projection area", showing that entity entry point retrieval can still have blind spots without keyword assistance)
*   **🟡 OKF LLM Wiki**
    *   **[Single Stage] Autonomous Agent Retrieval & Reasoning**: The Agent successfully located and read the original text of `Chapter 1_Terminology/Article 1.md`.
    *   **Answer**: 🤖 *"The horizontal projection area of the building site (hereinafter referred to as the site)."*
        *   ✅ **Complete Answer**

#### Case 2: Multi-hop Reasoning
> **Question**: "Is a private road counted in the statutory open space? Does it need a cut-off if it intersects a road?"

*   **🟢 Hybrid RAG**
    *   **[Stage 1] Retrieval**: Hit the contradiction and exception of `the part not exceeding 35 meters can be included`.
    *   **[Stage 2] Answer Extraction**: 🤖 *"The portion of a private passage whose length, calculated from the building line, does not exceed 35 meters may be included in the statutory open space area... as for whether a corner cutoff is required when intersecting a road, this context lacks information."*
        *   ⚠️ **Partially Correct** (Did not cover the corner cutoff rule)
*   **🔵 Graph RAG**
    *   **[Stage 1] Retrieval**: Instantly pulls edges like `Private road -length over 35m-> requires vehicle turning area` and `Intersection of road and turning area -cut-off length is-> 4 meters`.
    *   **[Stage 2] Answer Extraction**: 🤖 *"Information regarding whether a private passage counts as statutory open space is missing in the context; for passage intersection cutoff, the context only specifies a 4-meter cutoff for the intersection with a 'turning area', and does not mention cutoff rules for intersection with a 'road'."*
        *   ⚠️ **Partially Correct** (Pointed out the cutoff blind spot, but missed the open space rule)
*   **🟡 OKF LLM Wiki**
    *   **[Single Stage] Autonomous Agent Retrieval & Reasoning**: After searching for `private passage`, the Agent read the Section 1_Building Site `_index.md` MOC, then drilled into specific articles to correctly extract both the open space rule and the road intersection exemption.
    *   **Answer**: 🤖 *"1. Counted in statutory open space: Yes. The portion of the private passage, calculated from the building line, that does not exceed 35 meters may be included. 2. Corner cutoff required: No. A private road's intersection with a public road is exempt from the cutoff requirement."*
        *   ✅ **Complete Answer** (Correct and precise judgment based on the provided context)

#### Case 3: Global Summarization
> **Question**: "Looking at the entire 'Building Design and Construction Chapter', what are the core design principles for disaster prevention and evacuation in 'High-rise Buildings'? Please summarize three main points."

*   **🟢 Hybrid RAG**
    *   **[Stage 1] Retrieval**: Only caught a few sporadic articles about high-rise buildings due to Top-K limitation.
    *   **[Stage 2] Answer Extraction**: 🤖 *"1. Setup centralized monitoring in disaster prevention centers... 2. Structural safety protection for foundations... 3. Strict fire/smoke compartments..."*
        *   ⚠️ **Partially Correct** (Foundation structural safety is off-topic regarding evacuation)
*   **🔵 Graph RAG**
    *   **[Stage 1] Retrieval**: Pulled a massive topology of `Disaster Prevention Equipment in High-rise Buildings`.
    *   **[Stage 2] Answer Extraction**: 🤖 *"1. Fire-resistant wiring for cables (30 mins for heavy power, 15 mins for light power); 2. Structural strength and toughness... However, the context lacks the third main point regarding evacuation and escape."*
        *   ❌ **Missed Core Theme** (Lacked evacuation focus)
*   **🟡 OKF LLM Wiki**
    *   **[Single Stage] Autonomous Agent Retrieval & Reasoning**: The Agent navigated to the MOC index and associated sections of `Chapter 12_High-Rise Buildings/Section 4_Building Equipment/_index.md`, then synthesized the core themes.
    *   **Answer**: 🤖 *"1. Enforce two-direction evacuation principles with dedicated emergency access facilities (special safety staircases, emergency elevators, emergency entrances). 2. Strict independent fire and smoke compartments (with smoke-blocking performance) and mandatory active alarm and suppression systems. 3. Establish a 'Disaster Prevention Center' with centralized monitoring and command hub functions."*
        *   ✅ **Complete Answer** (Correctly summarized the three core points)

#### Conclusion on the Case
Through the two-stage separation and three different levels of questions, we can clearly see: **"The AI can only cook with the ingredients it is given."**
1. **Hybrid RAG** remains the king of finding "fact definitions" and long regulations.
2. **Graph RAG** performs exceptionally well on "entity relationships and conditional limits (A contains B, 4m cut-off)", but easily loses focus on basic definitions.
3. **OKF LLM Wiki** highly mimics human reading logic, and combined with MOC directories, is extremely good at "cross-chapter summarization" or "global summaries with a specific theme".

---

## 🔮 Future Vision: The Evolution of OKF

The V2 Benchmark confirms the overwhelming advantages of OKF (Open Knowledge Format) after our major upgrades. By migrating to standard Markdown relative path links (`[name](./path.md)`), the Agent's navigation efficiency during cross-chapter traversal has been greatly improved. This approach is also fully compatible with GitHub, any Markdown viewer, and all LLM environments — no longer relying on Obsidian-specific formats.

To further maximize the benefits of OKF, the future vision focuses on the following two key dimensions:

1. **Hybrid Power: OKF + Vector (Dual-Engine Start) 🚀**
   * **Concept**: Combine the "speed" of traditional Vector Search with the "accuracy" of OKF.
   * **Benefit**: Upon receiving a query, use millisecond-level vector search to find the Top-1 relevant Markdown file path as a "drop zone coordinate," passing it directly to the Agent. This skips the initial directory exploration phase, allowing the Agent to jump straight into high-level logical validation and navigation.

2. **Agentic Memory & Knowledge Distillation 🧠**
   * **Concept**: When an Agent successfully answers a complex query after multi-hop reasoning (e.g., spending 30 seconds summarizing fire safety for high-rises), it automatically generates a new file like `FAQ_HighRiseFireSafety.md` and saves it back into the OKF system.
   * **Benefit**: **The system becomes smarter and faster the more it's used.** When similar questions arise in the future, the Agent spots this FAQ directly in the MOC, achieving O(1) response times (Knowledge Distillation).
