"""AlgoTrade Engine — Portfolio Construction Benchmarks"""

import numpy as np
from algotrade.portfolio.knapsack import knapsack_brute, knapsack_greedy, knapsack_dp
from algotrade.utils.benchmark_runner import run_benchmark, format_benchmark_comparison


def run_portfolio_benchmarks() -> dict:
    """Run Knapsack DP vs Greedy vs Brute-force benchmarks."""
    small_sizes = [5, 8, 10, 12, 15, 18, 20]
    dp_sizes = [5, 10, 15, 20, 25, 30, 40, 50]

    def setup(n):
        values = (np.random.rand(n) * 20 + 1).tolist()
        weights = (np.random.randint(1, 10, n)).tolist()
        capacity = int(sum(weights) * 0.5)
        return values, weights, capacity

    brute = run_benchmark("Brute-Force O(2^n)", setup,
        lambda v, w, c: knapsack_brute(v, w, c), small_sizes, "O(2^n)", "Portfolio")
    greedy = run_benchmark("Greedy O(n log n)", setup,
        lambda v, w, c: knapsack_greedy(v, w, c), dp_sizes, "O(n log n)", "Portfolio")
    dp = run_benchmark("Knapsack DP O(n·W)", setup,
        lambda v, w, c: knapsack_dp(v, w, c), dp_sizes, "O(n·W)", "Portfolio")

    # Quality gap across sizes
    quality_gaps = []
    for n in dp_sizes:
        values = (np.random.rand(n) * 20 + 1).tolist()
        weights = (np.random.randint(1, 10, n)).tolist()
        capacity = int(sum(weights) * 0.5)
        dp_val = knapsack_dp(values, weights, capacity)["total_value"]
        gr_val = knapsack_greedy(values, weights, capacity)["total_value"]
        quality_gaps.append({
            "n": n, "dp_value": round(dp_val, 2), "greedy_value": round(gr_val, 2),
            "optimality_pct": round(gr_val / dp_val * 100, 2) if dp_val > 0 else 100,
        })

    return {
        "knapsack_brute_vs_dp": format_benchmark_comparison(brute, dp),
        "knapsack_greedy": {"name": greedy.algorithm_name, "slope": greedy.empirical_slope,
            "sizes": greedy.input_sizes, "runtimes_ms": [round(r, 4) for r in greedy.runtimes_ms]},
        "quality_gaps": quality_gaps,
    }
