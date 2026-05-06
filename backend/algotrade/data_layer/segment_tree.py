"""
AlgoTrade Engine — Segment Tree
Supports range min, max, and sum queries in O(log n) after O(n) build.
Includes brute-force O(n) baseline for benchmarking.

DAA Paradigm: Tree-based Data Structure
Brute-force: O(n) per query → O(n²) over full backtest
Optimized:   O(n) build + O(log n) per query
"""

import numpy as np
from typing import Callable


# ═══════════════════════════════════════════════════════════════════════════════
# BRUTE-FORCE BASELINE — O(n) per query
# ═══════════════════════════════════════════════════════════════════════════════

def range_query_brute(arr: np.ndarray, left: int, right: int, operation: str = "max") -> float:
    """
    Brute-force range query: linear scan from left to right.
    Time: O(n) per query where n = right - left + 1
    """
    segment = arr[left:right + 1]
    if operation == "max":
        return float(np.max(segment))
    elif operation == "min":
        return float(np.min(segment))
    elif operation == "sum":
        return float(np.sum(segment))
    else:
        raise ValueError(f"Unknown operation: {operation}")


def batch_queries_brute(arr: np.ndarray, queries: list[tuple[int, int]], operation: str = "max") -> list[float]:
    """Run multiple brute-force range queries. Total: O(n * Q)."""
    return [range_query_brute(arr, l, r, operation) for l, r in queries]


# ═══════════════════════════════════════════════════════════════════════════════
# OPTIMIZED — Segment Tree O(log n) per query
# ═══════════════════════════════════════════════════════════════════════════════

class SegmentTree:
    """
    Segment Tree for range queries (min, max, sum).

    Build:  O(n)
    Query:  O(log n)
    Update: O(log n) (point update)

    Uses a 1-indexed array representation:
    - tree[1] = root (full range aggregate)
    - tree[2i] = left child, tree[2i+1] = right child
    """

    # Operation function map
    _OPS = {
        "max": max,
        "min": min,
        "sum": lambda a, b: a + b,
    }

    # Identity elements for each operation
    _IDENTITY = {
        "max": float("-inf"),
        "min": float("inf"),
        "sum": 0.0,
    }

    def __init__(self, arr: np.ndarray, operation: str = "max"):
        """
        Build a segment tree over the given array.

        Args:
            arr: Input array of numeric values
            operation: "max", "min", or "sum"
        """
        self.n = len(arr)
        self.operation = operation
        self._op = self._OPS[operation]
        self._identity = self._IDENTITY[operation]
        self.tree = [self._identity] * (4 * self.n)  # 4n is safe upper bound
        self._arr = arr
        self._build(1, 0, self.n - 1)

    def _build(self, node: int, start: int, end: int):
        """Recursively build the segment tree. O(n)."""
        if start == end:
            self.tree[node] = float(self._arr[start])
            return

        mid = (start + end) // 2
        self._build(2 * node, start, mid)
        self._build(2 * node + 1, mid + 1, end)
        self.tree[node] = self._op(self.tree[2 * node], self.tree[2 * node + 1])

    def query(self, left: int, right: int) -> float:
        """
        Range query on [left, right] (inclusive).
        Time: O(log n) — traverses at most 2 * log(n) nodes.
        """
        return self._query(1, 0, self.n - 1, left, right)

    def _query(self, node: int, start: int, end: int, left: int, right: int) -> float:
        """Recursive range query."""
        # No overlap
        if right < start or end < left:
            return self._identity

        # Complete overlap
        if left <= start and end <= right:
            return self.tree[node]

        # Partial overlap — recurse both children
        mid = (start + end) // 2
        left_result = self._query(2 * node, start, mid, left, right)
        right_result = self._query(2 * node + 1, mid + 1, end, left, right)
        return self._op(left_result, right_result)

    def update(self, idx: int, value: float):
        """
        Point update: set arr[idx] = value.
        Time: O(log n)
        """
        self._update(1, 0, self.n - 1, idx, value)

    def _update(self, node: int, start: int, end: int, idx: int, value: float):
        """Recursive point update."""
        if start == end:
            self.tree[node] = value
            return

        mid = (start + end) // 2
        if idx <= mid:
            self._update(2 * node, start, mid, idx, value)
        else:
            self._update(2 * node + 1, mid + 1, end, idx, value)

        self.tree[node] = self._op(self.tree[2 * node], self.tree[2 * node + 1])

    def batch_query(self, queries: list[tuple[int, int]]) -> list[float]:
        """Run multiple range queries."""
        return [self.query(l, r) for l, r in queries]
