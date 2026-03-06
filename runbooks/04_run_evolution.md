# 📘 Runbook: Evolutionary Optimization Engine (Genetic Algorithm)

This module demonstrates the core algorithmic capability of the project: using Genetic Algorithms to find optimal asset combinations (portfolios) in a high-dimensional search space.

## ⚙️ Prerequisites
Check `configs/settings.ini`:
*   `DEMO_MODE = True` — The algorithm will run using in-memory Mock data and bypass real LLM API calls for the final analysis, returning a simulated JSON response.
*   `DEMO_MODE = False` — The algorithm will attempt to use real LLM endpoints to generate a human-readable explanation of why the winning portfolio is effective.

## 🚀 CLI Usage
Run the script with the `--evolve` flag:
```bash
python main.py --evolve
```

## 🧠 Expected Behavior
1. **Initialization:** Generates an initial population of 30 random portfolios.
2. **Evaluation:** Scores each portfolio using a heuristic fitness function (`yield_potential`, `alpha_generation`, `liquidity`, `risk_mitigation`).
3. **Evolution:** Applies Elitism (keeping the top 6), Wildcards (keeping 15% of low-scoring portfolios to maintain genetic diversity), Crossover, and Mutation over 25 generations.
4. **Output:** Prints the Top-3 unique portfolios and requests an LLM to analyze the hidden synergies of the winning combination.