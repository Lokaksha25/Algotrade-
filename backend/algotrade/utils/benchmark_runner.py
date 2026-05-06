"""
AlgoTrade Engine — Benchmark Runner
Generic framework for running log-log complexity benchmarks and extracting slopes.
"""

import time
import numpy as np
from typing import Callable
from algotrade.utils.types import BenchmarkResult


def measure_runtime(func: Callable, *args, repeats: int = 3, **kwargs) -> float:
    """Measure average runtime of a function in milliseconds."""
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        func(*args, **kwargs)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms
    return np.median(times)


def run_benchmark(
    name: str,
    setup_func: Callable,
    test_func: Callable,
    input_sizes: list[int],
    theoretical_complexity: str,
    category: str = "general",
    repeats: int = 3,
) -> BenchmarkResult:
    """
    Run a benchmark across multiple input sizes.

    Args:
        name: Algorithm name
        setup_func: Function that takes n and returns test data (e.g., arrays)
        test_func: Function to benchmark, receives output of setup_func
        input_sizes: List of input sizes to test
        theoretical_complexity: Expected Big-O string
        category: Module name
        repeats: Number of repetitions per size

    Returns:
        BenchmarkResult with runtimes and empirical slope
    """
    runtimes = []

    for n in input_sizes:
        data = setup_func(n)
        if isinstance(data, tuple):
            rt = measure_runtime(test_func, *data, repeats=repeats)
        else:
            rt = measure_runtime(test_func, data, repeats=repeats)
        runtimes.append(rt)

    # Compute log-log slope
    slope = extract_loglog_slope(input_sizes, runtimes)

    return BenchmarkResult(
        algorithm_name=name,
        input_sizes=input_sizes,
        runtimes_ms=runtimes,
        theoretical_complexity=theoretical_complexity,
        empirical_slope=slope,
        category=category,
    )


def extract_loglog_slope(sizes: list[int], runtimes: list[float]) -> float:
    """
    Fit a line to log(runtime) vs log(n) and return the slope.
    Slope ≈ 0 → O(1), ≈ 1 → O(n), ≈ 2 → O(n²), etc.
    """
    log_n = np.log10(np.array(sizes, dtype=float))
    log_t = np.log10(np.array(runtimes, dtype=float))

    # Filter out any invalid values (zero or negative runtimes)
    valid = np.isfinite(log_n) & np.isfinite(log_t)
    if valid.sum() < 2:
        return 0.0

    # Linear regression: log(t) = slope * log(n) + intercept
    coeffs = np.polyfit(log_n[valid], log_t[valid], 1)
    return round(coeffs[0], 3)


def format_benchmark_comparison(brute: BenchmarkResult, optimized: BenchmarkResult) -> dict:
    """Format a benchmark comparison for API response."""
    speedups = []
    for bt, ot in zip(brute.runtimes_ms, optimized.runtimes_ms):
        speedups.append(round(bt / ot, 2) if ot > 0 else float('inf'))

    return {
        "brute_force": {
            "name": brute.algorithm_name,
            "complexity": brute.theoretical_complexity,
            "empirical_slope": brute.empirical_slope,
            "sizes": brute.input_sizes,
            "runtimes_ms": [round(r, 4) for r in brute.runtimes_ms],
        },
        "optimized": {
            "name": optimized.algorithm_name,
            "complexity": optimized.theoretical_complexity,
            "empirical_slope": optimized.empirical_slope,
            "sizes": optimized.input_sizes,
            "runtimes_ms": [round(r, 4) for r in optimized.runtimes_ms],
        },
        "speedup_factors": speedups,
    }
