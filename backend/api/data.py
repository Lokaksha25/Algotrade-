"""API routes for market data."""

from fastapi import APIRouter, HTTPException
from algotrade.data_layer.fetcher import fetch_single, fetch_all
from config import DEFAULT_TICKERS, START_DATE, END_DATE

router = APIRouter()


@router.get("/tickers")
def get_tickers():
    """Get list of available tickers."""
    return {"tickers": DEFAULT_TICKERS}


@router.get("/{ticker}")
def get_ticker_data(ticker: str, start: str = START_DATE, end: str = END_DATE):
    """Get OHLCV data for a single ticker."""
    try:
        data = fetch_single(ticker.upper(), start, end)
        return {
            "ticker": data.ticker,
            "dates": data.dates,
            "open": data.open.tolist(),
            "high": data.high.tolist(),
            "low": data.low.tolist(),
            "close": data.close.tolist(),
            "volume": data.volume.tolist(),
            "num_points": data.n,
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
