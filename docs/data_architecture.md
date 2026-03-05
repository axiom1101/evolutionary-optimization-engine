# 🗄️ Data Architecture & ETL Pipeline

This project implements a simplified **Medallion Architecture** for data processing, ensuring a clear separation between raw ingestion, normalization, and business logic.

## 1. Bronze Layer: `data/raw/` (Landing Zone)
*   **Purpose:** The dumping ground for all unstructured, legacy, or external data.
*   **Contents:** Legacy Lua configurations, raw HTML dumps, CSVs, or API JSON responses.
*   **Ingestion:** Data can be placed here manually, or fetched via dedicated scraper/extractor scripts (e.g., `ingestion/extractors/`). We treat this data as immutable (append-only).

## 2. Silver Layer: `data/normalized/` (Cleansed Data)
*   **Purpose:** Cleaned, filtered, and strictly typed data ready for algorithmic processing.
*   **Process:** The `ingestion/legacy_parser.py` script reads from the Bronze layer, strips comments/syntax errors using Regex, parses the data, and saves it here as strict JSON.
*   **Usage:** This is the "Single Source of Truth" for the AI Agents and the Core Engine.

## 3. Gold Layer: In-Memory Data Grid (`core/metrics_db.py`)
*   **Purpose:** Highly optimized, business-level aggregations.
*   **Process:** The system loads Silver JSONs into memory, builds inverted indexes (`in_memory_index.py`), and calculates complex metrics (e.g., ROI, Drawdown, Throughput).