"""
AlgoTrade Engine — Data Layer Benchmarks
Compares Brute-Force O(n) vs Segment Tree O(log n) vs Sparse Table O(1) queries.
"""

import numpy as np
from algotrade.data_layer.segment_tree import SegmentTree, batch_queries_brute
from algotrade.data_layer.sparse_table import SparseTable
from algotrade.utils.benchmark_runner import run_benchmark, format_benchmark_comparison


NUM_QUERIES = 500  # Number of queries per benchmark run


def _generate_data_and_queries(n: int):
    """Setup function: generate random array and random query pairs."""
    arr = np.random.rand(n) * 1000  # Simulate price data
    queries = []
    for _ in range(NUM_QUERIES):
        l = np.random.randint(0, n)
        r = np.random.randint(l, n)
        queries.append((l, r))
    return arr, queries


def _brute_force_bench(arr: np.ndarray, queries: list):
    """Run brute-force range max queries."""
    return batch_queries_brute(arr, queries, "max")


def _segment_tree_bench(arr: np.ndarray, queries: list):
    """Build segment tree + run queries."""
    st = SegmentTree(arr, "max")
    return st.batch_query(queries)


def _sparse_table_bench(arr: np.ndarray, queries: list):
    """Build sparse table + run queries."""
    sp = SparseTable(arr, "max")
    return sp.batch_query(queries)


# ── Query-only benchmarks (pre-built structures) ──────────────────────────

def _setup_segment_tree_queries(n: int):
    """Build segment tree ahead of time, return (tree, queries)."""
    arr = np.random.rand(n) * 1000
    st = SegmentTree(arr, "max")
    queries = [(np.random.randint(0, n), np.random.randint(0, n)) for _ in range(NUM_QUERIES)]
    queries = [(min(l, r), max(l, r)) for l, r in queries]
    return st, queries


def _setup_sparse_table_queries(n: int):
    """Build sparse table ahead of time, return (table, queries)."""
    arr = np.random.rand(n) * 1000
    sp = SparseTable(arr, "max")
    queries = [(np.random.randint(0, n), np.random.randint(0, n)) for _ in range(NUM_QUERIES)]
    queries = [(min(l, r), max(l, r)) for l, r in queries]
    return sp, queries


def _run_st_queries(st: SegmentTree, queries: list):
    return st.batch_query(queries)


def _run_sp_queries(sp: SparseTable, queries: list):
    return sp.batch_query(queries)


def _setup_brute_queries(n: int):
    arr = np.random.rand(n) * 1000
    queries = [(np.random.randint(0, n), np.random.randint(0, n)) for _ in range(NUM_QUERIES)]
    queries = [(min(l, r), max(l, r)) for l, r in queries]
    return arr, queries


def run_data_layer_benchmarks(sizes: list[int] = None) -> dict:
    """
    Run all data layer benchmarks and return results for the API.

    Returns dict with:
      - segment_tree_vs_brute: comparison data
      - sparse_table_vs_brute: comparison data
      - all_three: combined comparison data
    """
    if sizes is None:
        sizes = [1_000, 5_000, 10_000, 50_000, 100_000, 500_000]

    # Brute-force benchmark
    brute = run_benchmark(
        name="Brute-Force Linear Scan",
        setup_func=_setup_brute_queries,
        test_func=lambda arr, q: batch_queries_brute(arr, q, "max"),
        input_sizes=sizes,
        theoretical_complexity="O(n)",
        category="Data Layer",
    )

    # Segment Tree benchmark (query only)
    seg_tree = run_benchmark(
        name="Segment Tree",
        setup_func=_setup_segment_tree_queries,
        test_func=_run_st_queries,
        input_sizes=sizes,
        theoretical_complexity="O(log n)",
        category="Data Layer",
    )

    # Sparse Table benchmark (query only)
    sparse = run_benchmark(
        name="Sparse Table",
        setup_func=_setup_sparse_table_queries,
        test_func=_run_sp_queries,
        input_sizes=sizes,
        theoretical_complexity="O(1)",
        category="Data Layer",
    )

    return {
        "segment_tree_vs_brute": format_benchmark_comparison(brute, seg_tree),
        "sparse_table_vs_brute": format_benchmark_comparison(brute, sparse),
        "all_three": {
            "brute_force": {
                "name": brute.algorithm_name,
                "complexity": brute.theoretical_complexity,
                "slope": brute.empirical_slope,
                "sizes": brute.input_sizes,
                "runtimes_ms": [round(r, 4) for r in brute.runtimes_ms],
            },
            "segment_tree": {
                "name": seg_tree.algorithm_name,
                "complexity": seg_tree.theoretical_complexity,
                "slope": seg_tree.empirical_slope,
                "sizes": seg_tree.input_sizes,
                "runtimes_ms": [round(r, 4) for r in seg_tree.runtimes_ms],
            },
            "sparse_table": {
                "name": sparse.algorithm_name,
                "complexity": sparse.theoretical_complexity,
                "slope": sparse.empirical_slope,
                "sizes": sparse.input_sizes,
                "runtimes_ms": [round(r, 4) for r in sparse.runtimes_ms],
            },
        },
    }


if __name__ == "__main__":
    print("Running data layer benchmarks...")
    results = run_data_layer_benchmarks()
    for key, val in results["all_three"].items():
        print(f"  {val['name']}: slope={val['slope']}, complexity={val['complexity']}")
    print("Done.")
