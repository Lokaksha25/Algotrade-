"""
AlgoTrade Engine — Signal Engine Benchmarks
Compares brute-force vs optimized for: Profit Finder, FFT, KMP.
"""

import numpy as np
from algotrade.signal_engine.profit_finder import max_profit_brute, max_profit_divide_conquer, max_profit_kadane
from algotrade.signal_engine.fft_cycles import dft_brute, fft_optimized
from algotrade.signal_engine.pattern_matcher import search_brute, search_kmp, search_rabin_karp
from algotrade.utils.benchmark_runner import run_benchmark, format_benchmark_comparison


def run_signal_engine_benchmarks(sizes: list[int] = None) -> dict:
    """Run all signal engine benchmarks."""
    if sizes is None:
        sizes = [500, 1_000, 2_000, 5_000, 10_000, 50_000]

    # ── Profit Finder ──
    profit_sizes = [s for s in sizes if s <= 10_000]  # Brute is O(n²)

    brute_profit = run_benchmark("Brute-Force O(n²)", lambda n: np.random.rand(n) * 100 + 50,
        max_profit_brute, profit_sizes, "O(n²)", "Signal Engine")
    dc_profit = run_benchmark("Divide & Conquer O(n log n)", lambda n: np.random.rand(n) * 100 + 50,
        max_profit_divide_conquer, profit_sizes, "O(n log n)", "Signal Engine")
    kadane_profit = run_benchmark("Kadane's O(n)", lambda n: np.random.rand(n) * 100 + 50,
        max_profit_kadane, profit_sizes, "O(n)", "Signal Engine")

    # ── FFT vs DFT ──
    fft_sizes = [512, 1024, 2048, 4096, 8192]

    dft_bench = run_benchmark("DFT Brute O(n²)", lambda n: np.random.rand(n),
        dft_brute, [s for s in fft_sizes if s <= 4096], "O(n²)", "Signal Engine")
    fft_bench = run_benchmark("FFT O(n log n)", lambda n: np.random.rand(n),
        fft_optimized, fft_sizes, "O(n log n)", "Signal Engine")

    # ── KMP vs Brute ──
    def setup_pattern(n):
        text = "".join(np.random.choice(["U", "D", "S"], n))
        pattern = "UUU"
        return text, pattern

    kmp_sizes = [s for s in sizes if s <= 100_000]
    brute_kmp = run_benchmark("Naive Match O(n·m)", setup_pattern,
        lambda t, p: search_brute(t, p), kmp_sizes, "O(n·m)", "Signal Engine")
    kmp_bench = run_benchmark("KMP O(n+m)", setup_pattern,
        lambda t, p: search_kmp(t, p), kmp_sizes, "O(n+m)", "Signal Engine")

    return {
        "profit_finder": {
            "brute_force": {"name": brute_profit.algorithm_name, "complexity": brute_profit.theoretical_complexity,
                "slope": brute_profit.empirical_slope, "sizes": brute_profit.input_sizes,
                "runtimes_ms": [round(r, 4) for r in brute_profit.runtimes_ms]},
            "divide_conquer": {"name": dc_profit.algorithm_name, "complexity": dc_profit.theoretical_complexity,
                "slope": dc_profit.empirical_slope, "sizes": dc_profit.input_sizes,
                "runtimes_ms": [round(r, 4) for r in dc_profit.runtimes_ms]},
            "kadane": {"name": kadane_profit.algorithm_name, "complexity": kadane_profit.theoretical_complexity,
                "slope": kadane_profit.empirical_slope, "sizes": kadane_profit.input_sizes,
                "runtimes_ms": [round(r, 4) for r in kadane_profit.runtimes_ms]},
        },
        "fft_vs_dft": format_benchmark_comparison(dft_bench, fft_bench),
        "kmp_vs_brute": format_benchmark_comparison(brute_kmp, kmp_bench),
    }
