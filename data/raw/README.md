# 🥉 Bronze Layer (Raw Data Landing Zone)

This directory serves as the landing zone for all unstructured, legacy, or dirty data. 

**What belongs here?**
*   Legacy Lua configurations (`.lua`)
*   Raw HTML dumps or scraped web pages
*   Unformatted CSVs or broken JSONs
*   System logs

**Philosophy:**
Data here is considered immutable "garbage". It is the job of the ETL pipeline (`ingestion/legacy_parser.py`) to extract value from this chaos, clean it using Regex/Lexers, and promote it to the Silver layer (`data/normalized/`).