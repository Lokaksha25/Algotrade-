"""
AlgoTrade Engine — Weighted Interval Scheduling DP
Selects non-overlapping trade intervals to maximize total return.

DAA Paradigm: Dynamic Programming + Binary Search
Brute-force: O(2^n) subset enumeration
Optimized:   O(n log n) — sort + binary search + bottom-up DP
"""

import bisect


def weighted_interval_scheduling_brute(intervals: list[dict]) -> dict:
    """
    Brute-force: enumerate all 2^n subsets, find max-value non-overlapping set.
    Time: O(2^n · n)  — feasible only for n ≤ 25
    
    Each interval: {"start": int, "end": int, "value": float, ...}
    """
    from itertools import combinations
    n = len(intervals)
    best_value = 0.0
    best_set = []

    for r in range(1, n + 1):
        for combo in combinations(range(n), r):
            selected = sorted(combo, key=lambda i: intervals[i]["end"])
            valid = True
            for k in range(1, len(selected)):
                if intervals[selected[k]]["start"] < intervals[selected[k - 1]]["end"]:
                    valid = False
                    break
            if valid:
                total = sum(intervals[i]["value"] for i in selected)
                if total > best_value:
                    best_value = total
                    best_set = list(selected)

    return {
        "total_value": best_value,
        "selected_indices": best_set,
        "num_selected": len(best_set),
        "method": "brute_force",
    }


def weighted_interval_scheduling_dp(intervals: list[dict]) -> dict:
    """
    Weighted Interval Scheduling via DP + Binary Search.
    Time: O(n log n)

    Algorithm:
      1. Sort intervals by end time
      2. For each interval i, binary search for p(i) = latest interval
         that ends before i starts
      3. DP: opt[i] = max(opt[i-1], value[i] + opt[p(i)])
      4. Backtrack to find selected intervals
    """
    if not intervals:
        return {"total_value": 0, "selected_indices": [], "num_selected": 0, "method": "dp"}

    n = len(intervals)

    # Sort by end time
    indexed = sorted(enumerate(intervals), key=lambda x: x[1]["end"])
    sorted_intervals = [intervals[i] for i, _ in indexed]
    original_indices = [i for i, _ in indexed]
    ends = [iv["end"] for iv in sorted_intervals]

    # Compute p(i): latest interval ending before interval i starts
    def find_latest_compatible(i):
        """Binary search for largest j < i such that end[j] <= start[i]."""
        target = sorted_intervals[i]["start"]
        lo, hi = 0, i - 1
        result = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if ends[mid] <= target:
                result = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return result

    # Build DP table (bottom-up)
    # opt[i] = max total value considering first i intervals
    opt = [0.0] * (n + 1)
    for i in range(1, n + 1):
        # Option 1: skip interval i
        skip = opt[i - 1]
        # Option 2: take interval i + best of compatible intervals
        p = find_latest_compatible(i - 1)
        take = sorted_intervals[i - 1]["value"] + (opt[p + 1] if p >= 0 else 0)
        opt[i] = max(skip, take)

    # Backtrack to find selected intervals
    selected = []
    i = n
    while i > 0:
        p = find_latest_compatible(i - 1)
        take_val = sorted_intervals[i - 1]["value"] + (opt[p + 1] if p >= 0 else 0)
        if take_val >= opt[i - 1]:
            selected.append(original_indices[i - 1])
            i = p + 1
        else:
            i -= 1

    selected.reverse()

    return {
        "total_value": opt[n],
        "selected_indices": selected,
        "num_selected": len(selected),
        "method": "dp",
    }
