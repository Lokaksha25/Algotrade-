"""
AlgoTrade Engine — Profit Finder
Finds the maximum profit buy-sell window in a price array using three approaches.

DAA Paradigms:
  1. Brute-Force:       O(n²) — check all (buy, sell) pairs
  2. Divide & Conquer:  O(n log n) — recursive midpoint split
  3. Kadane's Algorithm: O(n) — DP-based max subarray adapted for max profit
"""

import numpy as np


# ═══════════════════════════════════════════════════════════════════════════════
# BRUTE-FORCE — O(n²)
# ═══════════════════════════════════════════════════════════════════════════════

def max_profit_brute(prices: np.ndarray) -> dict:
    """
    Find maximum profit by checking all (buy, sell) pairs.
    Time: O(n²)  Space: O(1)

    Returns dict with: profit, buy_idx, sell_idx
    """
    n = len(prices)
    best_profit = 0
    buy_idx, sell_idx = 0, 0

    for i in range(n):
        for j in range(i + 1, n):
            profit = prices[j] - prices[i]
            if profit > best_profit:
                best_profit = profit
                buy_idx, sell_idx = i, j

    return {
        "profit": float(best_profit),
        "buy_idx": int(buy_idx),
        "sell_idx": int(sell_idx),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# DIVIDE & CONQUER — O(n log n)
# ═══════════════════════════════════════════════════════════════════════════════

def max_profit_divide_conquer(prices: np.ndarray) -> dict:
    """
    Find maximum profit using Divide & Conquer.
    Time: O(n log n)  Space: O(log n) recursion stack

    Approach:
      - Split array at midpoint
      - Max profit is either:
        (a) entirely in left half
        (b) entirely in right half
        (c) buy in left half, sell in right half (crossing)
      - Case (c): buy at min of left, sell at max of right → O(n) per level
      - Recurrence: T(n) = 2T(n/2) + O(n) → O(n log n)
    """
    if len(prices) <= 1:
        return {"profit": 0.0, "buy_idx": 0, "sell_idx": 0}

    result = _dc_helper(prices, 0, len(prices) - 1)
    return {
        "profit": float(result[0]),
        "buy_idx": int(result[1]),
        "sell_idx": int(result[2]),
    }


def _dc_helper(prices: np.ndarray, low: int, high: int) -> tuple:
    """Returns (max_profit, buy_idx, sell_idx)."""
    if low >= high:
        return (0.0, low, low)

    mid = (low + high) // 2

    # Solve left and right halves
    left = _dc_helper(prices, low, mid)
    right = _dc_helper(prices, mid + 1, high)

    # Find crossing case: min in left half, max in right half
    min_left_idx = low
    for i in range(low, mid + 1):
        if prices[i] < prices[min_left_idx]:
            min_left_idx = i

    max_right_idx = mid + 1
    for i in range(mid + 1, high + 1):
        if prices[i] > prices[max_right_idx]:
            max_right_idx = i

    cross_profit = prices[max_right_idx] - prices[min_left_idx]

    # Return the best of three cases
    if left[0] >= right[0] and left[0] >= cross_profit:
        return left
    elif right[0] >= left[0] and right[0] >= cross_profit:
        return right
    else:
        return (cross_profit, min_left_idx, max_right_idx)


# ═══════════════════════════════════════════════════════════════════════════════
# KADANE'S ALGORITHM — O(n)
# ═══════════════════════════════════════════════════════════════════════════════

def max_profit_kadane(prices: np.ndarray) -> dict:
    """
    Find maximum profit using Kadane's algorithm (DP approach).
    Time: O(n)  Space: O(1)

    Approach:
      - Track the minimum price seen so far
      - At each step, compute profit = current_price - min_price_so_far
      - Update best profit if current profit is higher
      - This is equivalent to max subarray sum on the daily differences array
    """
    n = len(prices)
    if n <= 1:
        return {"profit": 0.0, "buy_idx": 0, "sell_idx": 0}

    min_price = prices[0]
    min_idx = 0
    best_profit = 0.0
    buy_idx, sell_idx = 0, 0

    for i in range(1, n):
        profit = prices[i] - min_price
        if profit > best_profit:
            best_profit = profit
            buy_idx = min_idx
            sell_idx = i

        if prices[i] < min_price:
            min_price = prices[i]
            min_idx = i

    return {
        "profit": float(best_profit),
        "buy_idx": int(buy_idx),
        "sell_idx": int(sell_idx),
    }


def find_all_profitable_windows(prices: np.ndarray, min_profit_pct: float = 2.0) -> list[dict]:
    """
    Find all buy-sell windows with profit > min_profit_pct%.
    Used by the signal engine to generate trade signals.

    Uses a modified approach: track local minima/maxima to find profitable swings.
    """
    n = len(prices)
    signals = []

    i = 0
    while i < n - 1:
        # Find local minimum (potential buy)
        while i < n - 1 and prices[i] >= prices[i + 1]:
            i += 1
        buy_idx = i

        # Find local maximum (potential sell)
        while i < n - 1 and prices[i] <= prices[i + 1]:
            i += 1
        sell_idx = i

        if buy_idx < sell_idx:
            profit_pct = ((prices[sell_idx] - prices[buy_idx]) / prices[buy_idx]) * 100
            if profit_pct >= min_profit_pct:
                signals.append({
                    "buy_idx": int(buy_idx),
                    "sell_idx": int(sell_idx),
                    "buy_price": float(prices[buy_idx]),
                    "sell_price": float(prices[sell_idx]),
                    "profit_pct": round(float(profit_pct), 2),
                })

    return signals
