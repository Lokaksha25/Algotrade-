"""API routes for algorithm benchmarks."""

from fastapi import APIRouter

router = APIRouter()

# Cache benchmark results (they take time to compute)
_benchmark_cache = {}


@router.get("/benchmarks")
def get_all_benchmarks(force_rerun: bool = False):
    """Run and return all algorithm benchmarks across all modules."""
    if _benchmark_cache and not force_rerun:
        return _benchmark_cache

    from algotrade.data_layer.benchmarks import run_data_layer_benchmarks
    from algotrade.signal_engine.benchmarks import run_signal_engine_benchmarks
    from algotrade.portfolio.benchmarks import run_portfolio_benchmarks
    from algotrade.execution.benchmarks import run_execution_benchmarks
    from algotrade.backtester.benchmarks import run_backtester_benchmarks

    results = {
        "data_layer": run_data_layer_benchmarks([1_000, 5_000, 10_000, 50_000, 100_000]),
        "signal_engine": run_signal_engine_benchmarks([500, 1_000, 2_000, 5_000]),
        "portfolio": run_portfolio_benchmarks(),
        "execution": run_execution_benchmarks(),
        "backtester": run_backtester_benchmarks(),
    }

    _benchmark_cache.update(results)
    return results


@router.get("/benchmarks/{module}")
def get_module_benchmarks(module: str):
    """Get benchmarks for a specific module."""
    all_benchmarks = get_all_benchmarks()
    if module not in all_benchmarks:
        return {"error": f"Module '{module}' not found. Available: {list(all_benchmarks.keys())}"}
    return all_benchmarks[module]


@router.get("/info")
def get_algorithm_info():
    """Return metadata about all 15+ algorithms implemented."""
    return {
        "algorithms": [
            {"id": 1, "name": "Segment Tree", "paradigm": "Tree DS", "module": "Data Layer",
             "brute_complexity": "O(n)", "optimized_complexity": "O(log n)", "description": "Range min/max/sum queries over OHLCV price arrays"},
            {"id": 2, "name": "Sparse Table", "paradigm": "Precomputation", "module": "Data Layer",
             "brute_complexity": "O(n)", "optimized_complexity": "O(1)", "description": "Static RMQ for support/resistance detection"},
            {"id": 3, "name": "Divide & Conquer", "paradigm": "D&C", "module": "Signal Engine",
             "brute_complexity": "O(n²)", "optimized_complexity": "O(n log n)", "description": "Maximum profit buy-sell window detection"},
            {"id": 4, "name": "Kadane's Algorithm", "paradigm": "Dynamic Programming", "module": "Signal Engine",
             "brute_complexity": "O(n²)", "optimized_complexity": "O(n)", "description": "Optimal max subarray / max profit finder"},
            {"id": 5, "name": "Sliding Window", "paradigm": "Sliding Window", "module": "Signal Engine",
             "brute_complexity": "O(n·k)", "optimized_complexity": "O(n)", "description": "SMA, EMA, RSI, Bollinger Bands computation"},
            {"id": 6, "name": "FFT", "paradigm": "Transform", "module": "Signal Engine",
             "brute_complexity": "O(n²)", "optimized_complexity": "O(n log n)", "description": "Cycle detection in price time series"},
            {"id": 7, "name": "KMP", "paradigm": "String Matching", "module": "Signal Engine",
             "brute_complexity": "O(n·m)", "optimized_complexity": "O(n+m)", "description": "Candlestick pattern matching"},
            {"id": 8, "name": "Rabin-Karp", "paradigm": "Hashing", "module": "Signal Engine",
             "brute_complexity": "O(n·m)", "optimized_complexity": "O(n+m) avg", "description": "Rolling hash pattern matching"},
            {"id": 9, "name": "0/1 Knapsack DP", "paradigm": "Dynamic Programming", "module": "Portfolio",
             "brute_complexity": "O(2^n)", "optimized_complexity": "O(n·W)", "description": "Optimal capital allocation across stocks"},
            {"id": 10, "name": "Kruskal's MST", "paradigm": "Greedy + Graph", "module": "Portfolio",
             "brute_complexity": "O(V²)", "optimized_complexity": "O(E log E)", "description": "Correlation-based portfolio diversification"},
            {"id": 11, "name": "Union-Find (DSU)", "paradigm": "Disjoint Set", "module": "Portfolio",
             "brute_complexity": "O(n)", "optimized_complexity": "O(α(n))", "description": "Cycle detection for MST + sector grouping"},
            {"id": 12, "name": "Activity Selection", "paradigm": "Greedy", "module": "Execution",
             "brute_complexity": "O(2^n)", "optimized_complexity": "O(n log n)", "description": "Max non-overlapping trade selection"},
            {"id": 13, "name": "Max-Heap", "paradigm": "Heap", "module": "Execution",
             "brute_complexity": "O(n log n)", "optimized_complexity": "O(n) heapify", "description": "Trade signal prioritization"},
            {"id": 14, "name": "AVL Tree", "paradigm": "Balanced BST", "module": "Execution",
             "brute_complexity": "O(n)", "optimized_complexity": "O(log n)", "description": "Simulated limit order book"},
            {"id": 15, "name": "Weighted Interval Scheduling", "paradigm": "DP + Binary Search", "module": "Backtester",
             "brute_complexity": "O(2^n)", "optimized_complexity": "O(n log n)", "description": "Multi-period return maximization"},
            {"id": 16, "name": "Memoization", "paradigm": "Top-Down DP", "module": "Backtester",
             "brute_complexity": "O(k) recompute", "optimized_complexity": "O(1) cached", "description": "Indicator computation caching"},
        ]
    }
