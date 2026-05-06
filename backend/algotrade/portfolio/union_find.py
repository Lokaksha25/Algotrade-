"""
AlgoTrade Engine — Union-Find (Disjoint Set Union)
DAA Paradigm: Disjoint Set with path compression + union-by-rank → O(α(n)) amortized.
Used by Kruskal's MST for cycle detection and for sector grouping.
"""


class UnionFind:
    """
    Disjoint Set Union with:
      - Path compression in find()
      - Union-by-rank in union()
      - O(α(n)) amortized per operation (α = inverse Ackermann, effectively constant)
    """

    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.num_components = n

    def find(self, x: int) -> int:
        """Find root with path compression — flattens tree on each call."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """Union by rank — attach shorter tree under taller tree. Returns True if merged."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False  # Already in same set (would create cycle in MST)
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.num_components -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)

    def get_components(self) -> dict[int, list[int]]:
        """Return all connected components as {root: [members]}."""
        components = {}
        for i in range(len(self.parent)):
            root = self.find(i)
            components.setdefault(root, []).append(i)
        return components
