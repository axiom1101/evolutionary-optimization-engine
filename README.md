# 🧬 EOE: Evolutionary Optimization Engine

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Architecture](https://img.shields.io/badge/Architecture-Multi--Agent-success.svg)
![Algorithms](https://img.shields.io/badge/Algorithms-Genetic%20%2F%20Evolutionary-orange.svg)
![Status](https://img.shields.io/badge/Status-R&D_Prototype-purple.svg)

*Read this in [Russian](README_RU.md)*

**Evolutionary Optimization Engine (EOE)** is a domain-agnostic AI framework designed to solve NP-hard topology optimization problems, discover hidden synergies in complex systems, and perform quantitative arbitrage using Multi-Agent LLM orchestration and Genetic Algorithms.

## 🎯 Vision & Domain-Agnostic Architecture

While the core engine was initially prototyped to evaluate complex mathematical models with millions of permutations, its architecture is strictly **Domain-Agnostic**. The system maps abstract graph nodes, modifiers, and fitness functions to real-world business verticals.

| Abstract Concept | 📈 FinTech / Quant Trading (Primary) | ☁️ Cloud / MLOps | 🚚 Supply Chain & Logistics |
| :--- | :--- | :--- | :--- |
| **Topology Graph** | Asset Correlation & Dependency Graph | Microservice / Network Topology | Logistics & Distribution Network |
| **Nodes / Components** | Financial Instruments (Derivatives, Equities) | Compute Nodes (EC2, GPU, DBs) | Transport Hubs, Warehouses |
| **Modifiers (Rules)** | Market Volatility, Taxes, Fees | SLA Constraints, Network Latency | Customs, Weather, Fuel Costs |
| **Fitness Function** | Expected Yield (Alpha) vs. Max Drawdown | Throughput vs. Fault Tolerance | Delivery Volume vs. OPEX |
| **Arbitrage Discovery** | Finding Undervalued Asset Combinations | Spot Instance Pricing Arbitrage | Route Cost Inefficiencies |

## 🏗️ System Architecture: LLM-Driven Multi-Agent Workflow

The core value of the project is the robust integration between raw data, local/cloud LLMs, and specialized agentic workflows.

### 1. ETL & Data Ingestion Layer (`/ingestion`)
*   **Legacy Data Parsing:** Safe extraction of unstructured data from legacy Lua/XML configurations using regular expressions and lexical analysis (`slpp`) without arbitrary code execution risks.
*   **Data Reconciliation:** Deep validation scripts (`validate_lossless.py`) ensuring zero data loss during transformation from raw formats to normalized JSON Data Lakes.

### 2. LLM Integration & MLOps (`/agents/llm_client.py`)
*   **Local & Cloud Inference:** Hybrid model execution. Integration with local models via **Ollama** (Qwen, Mistral) for private data, and **Google Gemini API** for multimodal tasks (Computer Vision).
*   **Prompt Engineering:** Strict System Prompts enforcing structured data returns (JSON) and preventing hallucinations.

### 3. Multi-Agent Orchestration (`/agents`)
*   **Intent Router:** NLP-based analysis of user queries to determine Intent and extract Entities before invoking heavy models.
*   **Specialized Agents:** Role separation (Strategy Scout, Architect, Validator). Each agent operates within an isolated context and prompt.

### 4. Evolutionary Core (`/core/evolution_engine.py`)
*   **Genetic Algorithms:** Implements population initialization, crossover, and targeted mutations to evolve system topologies.
*   **Elitism & Wildcards:** Protects top-performing configurations while maintaining genetic diversity (10-15% wildcards) to escape local optima and discover "Hidden Mechanic Abuse".

### 5. In-Memory Data Grid & Evaluation (`/core`)
*   **Metrics Aggregation Engine:** A robust `ModDB` class handling complex modifier math (Base, Additive, Multiplicative) across thousands of nodes.
*   **Simulation Bridge:** Uses `lupa` (Lua-Python FFI) to bridge the Python orchestrator with a high-performance C/Lua simulation engine (Digital Twin).

### 6. Quantitative Arbitrage & RPA (`/automation`)
*   **Real-Time Signal Monitor:** RPA and Computer Vision integration (`follower.py`) for automated data gathering and execution in legacy terminal environments.

## 🛠️ Tech Stack
*   **Backend:** Python 3.11+
*   **Data Processing:** Regex, JSON Schema, XML ElementTree
*   **FFI / Simulation:** `lupa` (Lua in Python)
*   **AI / NLP:** `ollama` (Local LLM execution), `google-genai` (Multimodal Vision)
*   **Automation:** `pyautogui`, `pygetwindow`

## 📁 Repository Structure

```text
evolutionary-optimization-engine/
├── core/                       # Core algorithms and metric aggregation
│   ├── evolution_engine.py     # Genetic algorithm for topology optimization
│   ├── metrics_db.py           # Modifiers and metrics aggregation engine
│   ├── in_memory_index.py      # Sub-millisecond inverted indexing
│   └── simulation_bridge.py    # FFI bridge to high-performance C/Lua simulator
├── ingestion/                  # ETL pipelines and data extraction
│   ├── legacy_parser.py        # Safe extraction from unstructured legacy configs
│   ├── data_reconciliation.py  # Zero-data-loss validation scripts
│   └── pipeline.py             # Data Lake assembly pipeline
├── agents/                     # Multi-Agent LLM orchestration
│   ├── intent_router.py        # NLP-based query router
│   ├── response_formatter.py   # Analytical report generator
│   ├── arbitrage_scout.py      # Quantitative arbitrage logic
│   └── llm_client.py           # Wrapper for local/cloud LLMs
├── automation/                 # RPA and Computer Vision
│   ├── signal_monitor.py       # CV-based automation for legacy terminals
│   └── stream_analyzer.py      # Real-time log and clipboard analysis
└── data/                       # Data Lake (Raw & Normalized)
```