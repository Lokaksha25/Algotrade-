"""AlgoTrade Engine — Execution Engine Benchmarks"""

import numpy as np
from algotrade.execution.activity_selection import activity_selection_brute, activity_selection_greedy
from algotrade.execution.priority_queue import build_heap_repeated_insertion, build_heap_heapify
from algotrade.execution.order_book import AVLTree, SortedListOrderBook
from algotrade.utils.benchmark_runner import run_benchmark, format_benchmark_comparison


def run_execution_benchmarks() -> dict:
    """Run all execution engine benchmarks."""

    # ── Activity Selection ──
    act_sizes = [5, 8, 10, 12, 15, 18, 20]

    def setup_activities(n):
        acts = []
        for i in range(n):
            s = np.random.randint(0, 200)
            e = s + np.random.randint(5, 50)
            acts.append({"id": i, "start": s, "end": e, "value": np.random.rand() * 10})
        return (acts,)

    brute_act = run_benchmark("Brute O(2^n)", setup_activities,
        lambda a: activity_selection_brute(a), act_sizes, "O(2^n)", "Execution")
    greedy_act = run_benchmark("Greedy O(n log n)", setup_activities,
        lambda a: activity_selection_greedy(a), act_sizes, "O(n log n)", "Execution")

    # ── Heap Build ──
    heap_sizes = [1_000, 5_000, 10_000, 50_000, 100_000, 500_000]

    def setup_heap(n):
        items = [(np.random.rand() * 100, {"id": i}) for i in range(n)]
        return (items,)

    insert_heap = run_benchmark("Repeated Insert O(n log n)", setup_heap,
        lambda items: build_heap_repeated_insertion(items), heap_sizes, "O(n log n)", "Execution")
    heapify_bench = run_benchmark("Heapify O(n)", setup_heap,
        lambda items: build_heap_heapify(items), heap_sizes, "O(n)", "Execution")

    # ── AVL vs Sorted List ──
    avl_sizes = [500, 1_000, 2_000, 5_000, 10_000]

    def bench_avl(n):
        tree = AVLTree()
        prices = np.random.rand(n) * 1000
        for p in prices:
            tree.insert(float(p))
        for _ in range(n // 2):
            tree.find_max()
            tree.find_min()

    def bench_sorted(n):
        book = SortedListOrderBook()
        prices = np.random.rand(n) * 1000
        for p in prices:
            book.insert(float(p))
        for _ in range(n // 2):
            book.find_max()
            book.find_min()

    avl_bench = run_benchmark("AVL Tree O(log n)", lambda n: (n,),
        lambda n: bench_avl(n), avl_sizes, "O(n log n)", "Execution")
    sorted_bench = run_benchmark("Sorted List O(n²)", lambda n: (n,),
        lambda n: bench_sorted(n), avl_sizes, "O(n²)", "Execution")

    return {
        "activity_selection": format_benchmark_comparison(brute_act, greedy_act),
        "heap_build": format_benchmark_comparison(insert_heap, heapify_bench),
        "order_book": format_benchmark_comparison(sorted_bench, avl_bench),
    }
