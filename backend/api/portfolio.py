"""API routes for portfolio construction."""

from fastapi import APIRouter
from pydantic import BaseModel
import numpy as np
from algotrade.data_layer.fetcher import fetch_all
from algotrade.portfolio.knapsack import compare_methods as knapsack_compare
from algotrade.portfolio.mst_diversification import (
    compute_correlation_matrix, kruskal_mst, get_correlation_heatmap_data, select_diversified_stocks
)
from config import DEFAULT_TICKERS, START_DATE, END_DATE, DEFAULT_CAPITAL, CAPITAL_UNIT

router = APIRouter()


@router.get("/optimize")
def optimize_portfolio(capital: float = DEFAULT_CAPITAL):
    """Run knapsack optimization on real stock data."""
    tickers = DEFAULT_TICKERS[:15]
    stock_data = fetch_all(tickers, START_DATE, END_DATE)

    if not stock_data:
        return {"error": "No stock data available"}

    valid_tickers = list(stock_data.keys())
    values = []
    weights = []

    for t in valid_tickers:
        returns = stock_data[t].daily_returns()
        avg_return = float(np.mean(returns) * 252 * 100) if len(returns) > 0 else 0
        values.append(max(0.1, avg_return))
        last_price = float(stock_data[t].close[-1])
        weights.append(max(1, int(last_price / CAPITAL_UNIT)))

    capacity = int(capital / CAPITAL_UNIT)
    result = knapsack_compare(values, weights, capacity)

    # Map indices to tickers
    for method in ["dp", "greedy"]:
        if method in result:
            result[method]["selected_tickers"] = [valid_tickers[i] for i in result[method]["selected_indices"]]

    result["tickers"] = valid_tickers
    result["values"] = [round(v, 2) for v in values]
    result["weights"] = weights
    return result


@router.get("/correlation")
def get_correlation(num_stocks: int = 15):
    """Get correlation matrix and heatmap data."""
    tickers = DEFAULT_TICKERS[:num_stocks]
    stock_data = fetch_all(tickers, START_DATE, END_DATE)
    valid_tickers = [t for t in tickers if t in stock_data and len(stock_data[t].daily_returns()) > 10]

    if len(valid_tickers) < 2:
        return {"error": "Need at least 2 stocks"}

    min_len = min(len(stock_data[t].daily_returns()) for t in valid_tickers)
    returns_matrix = np.column_stack([stock_data[t].daily_returns()[:min_len] for t in valid_tickers])
    corr_matrix = compute_correlation_matrix(returns_matrix)

    return get_correlation_heatmap_data(valid_tickers, corr_matrix)


@router.get("/mst")
def get_mst(num_stocks: int = 15):
    """Get MST diversification graph data."""
    tickers = DEFAULT_TICKERS[:num_stocks]
    stock_data = fetch_all(tickers, START_DATE, END_DATE)
    valid_tickers = [t for t in tickers if t in stock_data and len(stock_data[t].daily_returns()) > 10]

    if len(valid_tickers) < 2:
        return {"error": "Need at least 2 stocks"}

    min_len = min(len(stock_data[t].daily_returns()) for t in valid_tickers)
    returns_matrix = np.column_stack([stock_data[t].daily_returns()[:min_len] for t in valid_tickers])
    corr_matrix = compute_correlation_matrix(returns_matrix)

    mst = kruskal_mst(valid_tickers, corr_matrix)
    diversified = select_diversified_stocks(valid_tickers, corr_matrix, max_stocks=10)
    mst["diversified_selection"] = diversified

    return mst
