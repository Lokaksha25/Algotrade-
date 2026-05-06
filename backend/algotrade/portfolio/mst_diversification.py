"""
AlgoTrade Engine — MST Diversification (Kruskal's Algorithm)
Uses correlation-based MST for portfolio diversification.

DAA Paradigm: Greedy + Graph (Kruskal's MST with Union-Find)
Builds MST on correlation graph → low-correlation stocks = diversified portfolio.
"""

import numpy as np
from algotrade.portfolio.union_find import UnionFind


def compute_correlation_matrix(returns_matrix: np.ndarray) -> np.ndarray:
    """
    Compute Pearson correlation matrix between all stock return series.
    returns_matrix: shape (n_days, n_stocks)
    """
    return np.corrcoef(returns_matrix.T)


def build_correlation_edges(tickers: list[str], corr_matrix: np.ndarray) -> list[tuple]:
    """
    Build edge list from correlation matrix.
    Edge weight = |correlation| (lower = more diversified).
    Returns list of (weight, i, j) sorted by weight.
    """
    n = len(tickers)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            weight = abs(corr_matrix[i][j])
            edges.append((weight, i, j))
    edges.sort()  # Sort by weight (ascending = least correlated first)
    return edges


def kruskal_mst(tickers: list[str], corr_matrix: np.ndarray) -> dict:
    """
    Kruskal's MST on the correlation graph.
    Greedily adds edges with lowest |correlation| while avoiding cycles.
    Time: O(E log E) for sorting + O(E · α(V)) for Union-Find operations

    Returns MST edges, total weight, and graph data for visualization.
    """
    n = len(tickers)
    edges = build_correlation_edges(tickers, corr_matrix)
    uf = UnionFind(n)

    mst_edges = []
    total_weight = 0.0

    for weight, u, v in edges:
        if uf.union(u, v):
            mst_edges.append({
                "source": tickers[u], "target": tickers[v],
                "source_idx": u, "target_idx": v,
                "correlation": round(float(corr_matrix[u][v]), 4),
                "weight": round(weight, 4),
            })
            total_weight += weight
            if len(mst_edges) == n - 1:
                break

    return {
        "edges": mst_edges,
        "total_weight": round(total_weight, 4),
        "num_vertices": n,
        "num_edges": len(mst_edges),
        "nodes": [{"id": t, "index": i} for i, t in enumerate(tickers)],
    }


def select_diversified_stocks(tickers: list[str], corr_matrix: np.ndarray, max_stocks: int = 10) -> list[str]:
    """
    Select a diversified subset using MST.
    Strategy: Pick stocks that are leaves or low-degree nodes in the MST
    (they have least correlation with the rest).
    """
    mst = kruskal_mst(tickers, corr_matrix)

    # Count degree of each node in MST
    degree = {t: 0 for t in tickers}
    for edge in mst["edges"]:
        degree[edge["source"]] += 1
        degree[edge["target"]] += 1

    # Sort by degree (ascending) — leaf nodes first
    sorted_tickers = sorted(tickers, key=lambda t: degree[t])
    return sorted_tickers[:max_stocks]


def get_correlation_heatmap_data(tickers: list[str], corr_matrix: np.ndarray) -> dict:
    """Format correlation matrix for frontend heatmap visualization."""
    return {
        "tickers": tickers,
        "matrix": [[round(float(corr_matrix[i][j]), 4) for j in range(len(tickers))] for i in range(len(tickers))],
    }
