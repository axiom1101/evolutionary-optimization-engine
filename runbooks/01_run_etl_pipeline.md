# 📘 Runbook: ETL Pipeline Execution (Data Ingestion)

*Read this in [Russian](01_run_etl_pipeline_RU.md)*

This module demonstrates the Extract, Transform, and Load (ETL) process for unstructured legacy data (Lua/XML) into a normalized Data Lake.

## ⚙️ Prerequisites
1. Ensure the lexical analysis library is installed:
`pip install -r requirements.txt`
2. Place raw files (e.g., legacy config dumps) into the `data/raw/` directory.
3. If `DEMO_MODE = True` in `settings.ini`, the pipeline will automatically generate Mock data even if the `raw/` folder is empty.

## 🚀 CLI Usage
Run the script with the `--etl` flag:
`python main.py --etl`

## 🧠 Expected Behavior
1. **Extract:** `legacy_parser.py` reads the raw file from `data/raw/`.
2. **Transform:** Regular expressions strip comments and fix syntax errors. `slpp` converts the string into a Python dictionary.
3. **Load:** Normalized data is saved as strict JSON in `data/normalized/`, ready for In-Memory indexing.