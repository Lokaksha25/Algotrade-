"""
AlgoTrade Engine — Data Fetcher
Downloads OHLCV data from Yahoo Finance and caches locally as CSV.
"""

import os
import numpy as np
import pandas as pd
import yfinance as yf
from pathlib import Path
from algotrade.utils.types import OHLCVData
from config import DEFAULT_TICKERS, START_DATE, END_DATE, DATA_DIR


def _safe_cache_part(value: str) -> str:
    return value.replace("/", "-").replace(":", "-")


def _get_cache_path(ticker: str, start: str = START_DATE, end: str = END_DATE) -> Path:
    """Get the cache file path for a ticker."""
    cache_dir = Path(DATA_DIR)
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / f"{ticker}_{_safe_cache_part(start)}_{_safe_cache_part(end)}.csv"


def fetch_single(ticker: str, start: str = START_DATE, end: str = END_DATE, use_cache: bool = True) -> OHLCVData:
    """
    Fetch OHLCV data for a single ticker.
    Uses local CSV cache if available to avoid repeated API calls.
    """
    cache_path = _get_cache_path(ticker, start, end)

    if use_cache and cache_path.exists():
        df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
    else:
        df = yf.download(ticker, start=start, end=end, progress=False)
        if df.empty:
            raise ValueError(f"No data returned for ticker: {ticker}")
        # Flatten multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.to_csv(cache_path)

    parsed_dates = pd.to_datetime(df.index, errors="coerce")
    df = df.loc[~parsed_dates.isna()].copy()
    parsed_dates = parsed_dates[~parsed_dates.isna()]
    dates = parsed_dates.strftime("%Y-%m-%d").tolist()

    return OHLCVData(
        ticker=ticker,
        dates=dates,
        open=df["Open"].values.astype(float),
        high=df["High"].values.astype(float),
        low=df["Low"].values.astype(float),
        close=df["Close"].values.astype(float),
        volume=df["Volume"].values.astype(float),
    )


def fetch_all(
    tickers: list[str] = None,
    start: str = START_DATE,
    end: str = END_DATE,
    use_cache: bool = True,
) -> dict[str, OHLCVData]:
    """
    Fetch OHLCV data for all tickers.
    Returns a dict mapping ticker -> OHLCVData.
    """
    tickers = tickers or DEFAULT_TICKERS
    data = {}

    for ticker in tickers:
        try:
            data[ticker] = fetch_single(ticker, start, end, use_cache)
        except Exception as e:
            print(f"[WARN] Failed to fetch {ticker}: {e}")

    return data


def get_close_prices_matrix(
    stock_data: dict[str, OHLCVData],
) -> tuple[list[str], np.ndarray]:
    """
    Build a matrix of close prices (rows = days, cols = stocks).
    Only includes dates common to all stocks.
    """
    tickers = list(stock_data.keys())

    # Find common date range (intersection of all date sets)
    date_sets = [set(d.dates) for d in stock_data.values()]
    common_dates = sorted(set.intersection(*date_sets))

    matrix = np.zeros((len(common_dates), len(tickers)))
    for j, ticker in enumerate(tickers):
        d = stock_data[ticker]
        date_to_idx = {date: i for i, date in enumerate(d.dates)}
        for i, date in enumerate(common_dates):
            matrix[i, j] = d.close[date_to_idx[date]]

    return tickers, matrix
