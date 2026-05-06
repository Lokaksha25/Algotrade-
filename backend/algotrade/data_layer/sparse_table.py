"""
AlgoTrade Engine — Sparse Table (Range Minimum/Maximum Query)
O(n log n) preprocessing, O(1) per query for idempotent operations (min/max).

DAA Paradigm: Precomputation / Binary Lifting
Brute-force: O(n) per query
Optimized:   O(n log n) build + O(1) per query (for min/max only)

Trade-off vs Segment Tree:
  - Sparse Table: O(1) query but STATIC (no updates), more space O(n log n)
  - Segment Tree: O(log n) query but supports updates, less space O(n)
  → Classic space-time trade-off in DAA
"""

import math
import numpy as np


class SparseTable:
    """
    Sparse Table for Range Minimum/Maximum Query (RMQ).

    Uses overlapping sub-arrays of length 2^k (binary lifting).
    For idempotent functions (min, max), overlapping intervals give
    correct answers, enabling O(1) query time.

    Build:  O(n log n)
    Query:  O(1)
    Space:  O(n log n)
    Update: NOT SUPPORTED (static structure)
    """

    def __init__(self, arr: np.ndarray, operation: str = "max"):
        """
        Build sparse table over the given array.

        Args:
            arr: Input array of numeric values
            operation: "max" or "min" (must be idempotent)
        """
        if operation not in ("max", "min"):
            raise ValueError("Sparse Table only supports idempotent ops: 'max', 'min'")

        self.n = len(arr)
        self.operation = operation
        self._op = max if operation == "max" else min

        # K = floor(log2(n)) + 1 — number of levels
        self.K = max(1, int(math.log2(self.n)) + 1)

        # table[k][i] = op(arr[i], arr[i+1], ..., arr[i + 2^k - 1])
        self.table = [[0.0] * self.n for _ in range(self.K)]

        # Base case: intervals of length 1 (2^0 = 1)
        for i in range(self.n):
            self.table[0][i] = float(arr[i])

        # Fill using recurrence: table[k][i] = op(table[k-1][i], table[k-1][i + 2^(k-1)])
        for k in range(1, self.K):
            half = 1 << (k - 1)   # 2^(k-1)
            for i in range(self.n - (1 << k) + 1):
                self.table[k][i] = self._op(
                    self.table[k - 1][i],
                    self.table[k - 1][i + half]
                )

        # Precompute floor(log2(x)) for all x up to n
        self._log = [0] * (self.n + 1)
        for i in range(2, self.n + 1):
            self._log[i] = self._log[i // 2] + 1

    def query(self, left: int, right: int) -> float:
        """
        Range query on [left, right] (inclusive).
        Time: O(1) — single lookup using two overlapping intervals.

        Method: Find largest k such that 2^k ≤ (right - left + 1),
        then answer = op(table[k][left], table[k][right - 2^k + 1]).
        The two intervals [left, left+2^k-1] and [right-2^k+1, right]
        overlap but cover the full range — valid because min/max are idempotent.
        """
        length = right - left + 1
        k = self._log[length]
        return self._op(
            self.table[k][left],
            self.table[k][right - (1 << k) + 1]
        )

    def batch_query(self, queries: list[tuple[int, int]]) -> list[float]:
        """Run multiple range queries."""
        return [self.query(l, r) for l, r in queries]
