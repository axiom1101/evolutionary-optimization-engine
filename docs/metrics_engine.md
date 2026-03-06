# 🧮 Core Metrics Aggregation Engine

The `core/metrics_db.py` module is the mathematical heart of the Evolutionary Optimization Engine. It handles the complex aggregation of modifiers applied to system components (assets, nodes, microservices).

## The Problem
In complex systems (like financial markets or RPG skill trees), modifiers do not simply add up. They interact in three distinct ways:
1.  **Flat additions** (e.g., +$1000 to base capital).
2.  **Additive percentages** (e.g., +10% yield and +5% yield = +15% total).
3.  **Multiplicative percentages** (e.g., a 1.5x margin leverage applies to the *entire* accumulated sum).

## The Solution: BASE / INC / MORE Architecture
We implemented a deterministic aggregation engine based on the `ModifierType` enum:

*   `BASE`: Flat values added together.
*   `INC` (Increased): Additive percentages summed together before application.
*   `MORE`: Multiplicative percentages that compound exponentially.

### The Mathematical Formula
The `calculate_total_metric(metric_name)` method computes the final value using the following strict order of operations:

```text
Total Value = ( SUM(Base Values) + SUM(Base Values) * SUM(INC Values / 100) ) * PRODUCT(1 + MORE Value / 100)
```

### Example: Financial Portfolio
If a portfolio has:
*   Initial Deposit (`BASE`): $1000
*   Market Trend Bonus (`INC`): +20%
*   Broker Fee (`INC`): -5%
*   Margin Leverage (`MORE`): 50% (1.5x)

The engine calculates:
`Total Capital = ($1000 * (1 + 0.15)) * 1.5 = $1150 * 1.5 = $1725`

This architecture allows O(1) complexity when adding new modifiers and O(N) complexity when calculating the final state, making it highly efficient for the Genetic Algorithm's fitness function evaluations.