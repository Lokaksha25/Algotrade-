"""
AlgoTrade Engine — Candlestick Pattern Matcher (KMP + Rabin-Karp)
Encodes candlesticks as characters and searches for known patterns.

DAA Paradigm: String Matching
Brute-force: O(n·m) naive matching  |  KMP: O(n+m)  |  Rabin-Karp: O(n+m) avg
"""

import numpy as np
from config import DOJI_THRESHOLD

# Known candlestick patterns (encoded as strings)
PATTERNS = {
    "UUU": {"name": "Three White Soldiers", "signal": "BUY", "strength": 0.8},
    "DDD": {"name": "Three Black Crows", "signal": "SELL", "strength": 0.8},
    "DSU": {"name": "Morning Star", "signal": "BUY", "strength": 0.7},
    "USD": {"name": "Evening Star", "signal": "SELL", "strength": 0.7},
    "DU":  {"name": "Bullish Engulfing", "signal": "BUY", "strength": 0.6},
    "UD":  {"name": "Bearish Engulfing", "signal": "SELL", "strength": 0.6},
    "SU":  {"name": "Doji Star Bullish", "signal": "BUY", "strength": 0.5},
    "SD":  {"name": "Doji Star Bearish", "signal": "SELL", "strength": 0.5},
}


def encode_candlesticks(open_prices: np.ndarray, close_prices: np.ndarray, threshold: float = DOJI_THRESHOLD) -> str:
    """Encode each candlestick as U (bullish), D (bearish), S (doji)."""
    encoded = []
    for o, c in zip(open_prices, close_prices):
        pct = abs(c - o) / o if o != 0 else 0
        if pct < threshold:
            encoded.append("S")
        elif c > o:
            encoded.append("U")
        else:
            encoded.append("D")
    return "".join(encoded)


# ═══════════════════════════════════════════════════════════════════════════════
# BRUTE-FORCE — O(n·m) naive string matching
# ═══════════════════════════════════════════════════════════════════════════════

def search_brute(text: str, pattern: str) -> list[int]:
    """Naive string matching — O(n·m)."""
    n, m = len(text), len(pattern)
    matches = []
    for i in range(n - m + 1):
        match = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            matches.append(i)
    return matches


# ═══════════════════════════════════════════════════════════════════════════════
# KMP — O(n + m)
# ═══════════════════════════════════════════════════════════════════════════════

def _build_failure_function(pattern: str) -> list[int]:
    """Build KMP failure/prefix function in O(m)."""
    m = len(pattern)
    fail = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and pattern[k] != pattern[i]:
            k = fail[k - 1]
        if pattern[k] == pattern[i]:
            k += 1
        fail[i] = k
    return fail


def search_kmp(text: str, pattern: str) -> list[int]:
    """KMP string matching — O(n + m)."""
    n, m = len(text), len(pattern)
    if m == 0:
        return []
    fail = _build_failure_function(pattern)
    matches = []
    j = 0
    for i in range(n):
        while j > 0 and text[i] != pattern[j]:
            j = fail[j - 1]
        if text[i] == pattern[j]:
            j += 1
        if j == m:
            matches.append(i - m + 1)
            j = fail[j - 1]
    return matches


# ═══════════════════════════════════════════════════════════════════════════════
# RABIN-KARP — O(n + m) average
# ═══════════════════════════════════════════════════════════════════════════════

def search_rabin_karp(text: str, pattern: str, base: int = 256, mod: int = 101) -> list[int]:
    """Rabin-Karp with rolling hash — O(n + m) average case."""
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []

    matches = []
    p_hash = 0
    t_hash = 0
    h = pow(base, m - 1, mod)

    for i in range(m):
        p_hash = (base * p_hash + ord(pattern[i])) % mod
        t_hash = (base * t_hash + ord(text[i])) % mod

    for i in range(n - m + 1):
        if p_hash == t_hash:
            if text[i:i + m] == pattern:
                matches.append(i)
        if i < n - m:
            t_hash = (base * (t_hash - ord(text[i]) * h) + ord(text[i + m])) % mod
            if t_hash < 0:
                t_hash += mod

    return matches


def find_all_patterns(open_prices: np.ndarray, close_prices: np.ndarray, method: str = "kmp") -> list[dict]:
    """Find all known candlestick patterns in the price data."""
    text = encode_candlesticks(open_prices, close_prices)
    search_fn = {"kmp": search_kmp, "rabin_karp": search_rabin_karp, "brute": search_brute}[method]

    results = []
    for pattern_str, info in PATTERNS.items():
        positions = search_fn(text, pattern_str)
        for pos in positions:
            results.append({
                "pattern": info["name"],
                "signal": info["signal"],
                "position": pos,
                "length": len(pattern_str),
                "strength": info["strength"],
            })

    results.sort(key=lambda x: x["position"])
    return results
