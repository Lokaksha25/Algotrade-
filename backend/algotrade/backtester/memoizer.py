"""
AlgoTrade Engine — Memoization Layer
Caches indicator computations to avoid redundant recalculation.

DAA Paradigm: Top-Down DP / Memoization
Without cache: O(k) recomputation per indicator per timestep
With cache:    O(1) lookup for previously computed values
"""


class Memoizer:
    """
    Dictionary-based memoization for indicator computations.
    Key: (indicator_name, timestep, window_size)
    Tracks cache hit/miss ratio for benchmarking.
    """

    def __init__(self):
        self._cache = {}
        self._hits = 0
        self._misses = 0

    def get(self, indicator: str, timestep: int, window: int):
        """Lookup cached value. Returns None on miss."""
        key = (indicator, timestep, window)
        if key in self._cache:
            self._hits += 1
            return self._cache[key]
        self._misses += 1
        return None

    def put(self, indicator: str, timestep: int, window: int, value):
        """Store computed value in cache."""
        self._cache[(indicator, timestep, window)] = value

    def get_or_compute(self, indicator: str, timestep: int, window: int, compute_fn):
        """Get from cache or compute and store."""
        val = self.get(indicator, timestep, window)
        if val is not None:
            return val
        val = compute_fn()
        self.put(indicator, timestep, window, val)
        return val

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return (self._hits / total * 100) if total > 0 else 0.0

    @property
    def stats(self) -> dict:
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total": self._hits + self._misses,
            "hit_rate_pct": round(self.hit_rate, 2),
            "cache_size": len(self._cache),
        }

    def clear(self):
        self._cache.clear()
        self._hits = 0
        self._misses = 0
