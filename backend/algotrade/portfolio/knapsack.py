"""
AlgoTrade Engine — Capital Allocation (0/1 Knapsack)
DAA Paradigm: Dynamic Programming
Brute-force: O(2^n) exhaustive  |  Greedy: O(n log n)  |  DP: O(n·W) optimal
"""

import numpy as np
from itertools import combinations


def knapsack_brute(values: list[float], weights: list[int], capacity: int) -> dict:
    """
    Brute-force 0/1 Knapsack — enumerate all 2^n subsets.
    Time: O(2^n)  — only feasible for n ≤ 20
    """
    n = len(values)
    best_value = 0.0
    best_items = []

    for r in range(n + 1):
        for combo in combinations(range(n), r):
            w = sum(weights[i] for i in combo)
            v = sum(values[i] for i in combo)
            if w <= capacity and v > best_value:
                best_value = v
                best_items = list(combo)

    return {"total_value": best_value, "selected_indices": best_items,
            "total_weight": sum(weights[i] for i in best_items), "method": "brute_force"}


def knapsack_greedy(values: list[float], weights: list[int], capacity: int) -> dict:
    """
    Greedy Knapsack — sort by value/weight ratio, take greedily.
    Time: O(n log n)  — not guaranteed optimal for 0/1 variant
    """
    n = len(values)
    ratios = [(values[i] / weights[i] if weights[i] > 0 else 0, i) for i in range(n)]
    ratios.sort(reverse=True)

    total_value = 0.0
    total_weight = 0
    selected = []

    for ratio, idx in ratios:
        if total_weight + weights[idx] <= capacity:
            selected.append(idx)
            total_value += values[idx]
            total_weight += weights[idx]

    return {"total_value": total_value, "selected_indices": sorted(selected),
            "total_weight": total_weight, "method": "greedy"}


def knapsack_dp(values: list[float], weights: list[int], capacity: int) -> dict:
    """
    0/1 Knapsack DP — bottom-up table fill with backtracking.
    Time: O(n·W)  Space: O(n·W)  — guaranteed optimal
    """
    n = len(values)
    dp = [[0.0] * (capacity + 1) for _ in range(n + 1)]

    # Fill DP table
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]  # Don't take item i
            if weights[i - 1] <= w:
                take = dp[i - 1][w - weights[i - 1]] + values[i - 1]
                dp[i][w] = max(dp[i][w], take)

    # Backtrack to find selected items
    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(i - 1)
            w -= weights[i - 1]

    selected.reverse()
    return {"total_value": dp[n][capacity], "selected_indices": selected,
            "total_weight": sum(weights[i] for i in selected), "method": "knapsack_dp"}


def compare_methods(values: list[float], weights: list[int], capacity: int) -> dict:
    """Run all three methods and compute solution quality gaps."""
    dp_result = knapsack_dp(values, weights, capacity)
    greedy_result = knapsack_greedy(values, weights, capacity)

    dp_val = dp_result["total_value"]
    greedy_val = greedy_result["total_value"]
    greedy_ratio = (greedy_val / dp_val * 100) if dp_val > 0 else 100.0

    result = {"dp": dp_result, "greedy": greedy_result, "quality_gap": {
        "dp_value": dp_val, "greedy_value": greedy_val,
        "greedy_optimality_pct": round(greedy_ratio, 2)}}

    if len(values) <= 20:
        brute_result = knapsack_brute(values, weights, capacity)
        result["brute_force"] = brute_result

    return result
