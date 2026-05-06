"""AlgoTrade Engine — Backtester Core Benchmarks"""

import numpy as np
from algotrade.backtester.memoizer import Memoizer
from algotrade.backtester.interval_scheduler import weighted_interval_scheduling_brute, weighted_interval_scheduling_dp
from algotrade.utils.benchmark_runner import run_benchmark, format_benchmark_comparison


def run_backtester_benchmarks() -> dict:
    """Run memoization and interval scheduling benchmarks."""

    # ── Memoization ──
    def bench_with_memo(n):
        memo = Memoizer()
        for i in range(n):
            memo.get_or_compute("sma", i % 100, 20, lambda: np.random.rand())
        return memo.stats

    def bench_without_memo(n):
        results = {}
        for i in range(n):
            key = ("sma", i % 100, 20)
            results[key] = np.random.rand()  # Always recompute
        return results

    memo_sizes = [1_000, 5_000, 10_000, 50_000, 100_000]
    with_memo = run_benchmark("With Memoization", lambda n: (n,),
        lambda n: bench_with_memo(n), memo_sizes, "O(1) cached", "Backtester")
    without_memo = run_benchmark("Without Memoization", lambda n: (n,),
        lambda n: bench_without_memo(n), memo_sizes, "O(k) recompute", "Backtester")

    # ── Interval Scheduling ──
    sched_small = [5, 8, 10, 12, 15, 18]
    sched_large = [100, 500, 1_000, 5_000, 10_000]

    def setup_intervals(n):
        intervals = []
        for _ in range(n):
            s = np.random.randint(0, 500)
            e = s + np.random.randint(5, 50)
            intervals.append({"start": s, "end": e, "value": float(np.random.rand() * 20)})
        return (intervals,)

    brute_sched = run_benchmark("Brute O(2^n)", setup_intervals,
        lambda iv: weighted_interval_scheduling_brute(iv), sched_small, "O(2^n)", "Backtester")
    dp_sched = run_benchmark("DP O(n log n)", setup_intervals,
        lambda iv: weighted_interval_scheduling_dp(iv), sched_large, "O(n log n)", "Backtester")

    return {
        "memoization": format_benchmark_comparison(without_memo, with_memo),
        "interval_scheduling": {
            "brute_force": {
                "name": brute_sched.algorithm_name, "slope": brute_sched.empirical_slope,
                "sizes": brute_sched.input_sizes,
                "runtimes_ms": [round(r, 4) for r in brute_sched.runtimes_ms],
            },
            "dp": {
                "name": dp_sched.algorithm_name, "slope": dp_sched.empirical_slope,
                "sizes": dp_sched.input_sizes,
                "runtimes_ms": [round(r, 4) for r in dp_sched.runtimes_ms],
            },
        },
    }
