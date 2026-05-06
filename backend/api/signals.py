"""API routes for trade signals and indicators."""

from fastapi import APIRouter, HTTPException
from algotrade.data_layer.fetcher import fetch_single
from algotrade.signal_engine.indicators import compute_all_indicators, generate_sma_crossover_signals
from algotrade.signal_engine.profit_finder import find_all_profitable_windows, max_profit_kadane
from algotrade.signal_engine.pattern_matcher import find_all_patterns, encode_candlesticks
from algotrade.signal_engine.fft_cycles import extract_cycles
from config import START_DATE, END_DATE

router = APIRouter()


@router.get("/{ticker}")
def get_signals(ticker: str, start: str = START_DATE, end: str = END_DATE):
    """Get all signals and indicators for a ticker."""
    try:
        data = fetch_single(ticker.upper(), start, end)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

    indicators = compute_all_indicators(data.close)
    crossover_signals = generate_sma_crossover_signals(data.close)
    profit_windows = find_all_profitable_windows(data.close, min_profit_pct=3.0)
    patterns = find_all_patterns(data.open, data.close, method="kmp")
    cycles = extract_cycles(data.close)
    best_trade = max_profit_kadane(data.close)

    return {
        "ticker": data.ticker,
        "dates": data.dates,
        "ohlcv": {
            "open": data.open.tolist(), "high": data.high.tolist(),
            "low": data.low.tolist(), "close": data.close.tolist(),
            "volume": data.volume.tolist(),
        },
        "indicators": indicators,
        "signals": {
            "crossover": crossover_signals,
            "profit_windows": profit_windows[:20],
            "patterns": patterns,
        },
        "fft_cycles": cycles,
        "best_trade": best_trade,
        "encoded_candlesticks": encode_candlesticks(data.open, data.close)[:100],
    }
