# 📘 Runbook: AI Agents Execution (NLP & LLM Orchestration)

This module demonstrates a hybrid pipeline: a deterministic NLP Intent Router combined with an LLM (Ollama/Gemini) fallback mechanism.

## ⚙️ Prerequisites
Ensure the correct mode is set in `configs/settings.ini`:
*   `DEMO_MODE = True` — Safe execution without consuming API tokens or requiring a local Ollama instance (returns Mock responses).
*   `DEMO_MODE = False` — Production mode (requires a valid `GEMINI_API_KEY` and a running Ollama service).

## 🚀 CLI Usage
The single entry point for all modules is `main.py`.

### Option 1: Interactive Mode
Run the script with the `--agent` flag without parameters. The system will prompt you for input.
```bash
python main.py --agent
```
*Example input:* `Will the portfolio survive a crisis with a 30 drawdown and 50% hedge?`

### Option 2: One-shot Execution
Useful for automation and CI/CD pipelines. Pass the query string directly after the flag.
```bash
python main.py --agent "what assets are on the crypto market"
```

## 🧠 Expected Behavior
1. **Intent Router** intercepts the text and uses regular expressions to extract financial Entities and determine the Intent.
2. If the intent is recognized (e.g., `check_risk`), the **Response Formatter** generates an analytical Markdown report based on a mathematical model, **bypassing the LLM** (saving resources/tokens).
3. If the intent is not recognized (`unknown`), the query is routed to the **LLM Client** for natural language processing (Fallback).