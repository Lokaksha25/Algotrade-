"""API routes for running backtests."""

from fastapi import APIRouter
from pydantic import BaseModel
from algotrade.data_layer.fetcher import fetch_all
from algotrade.backtester.engine import BacktestEngine
from config import DEFAULT_TICKERS, START_DATE, END_DATE, DEFAULT_CAPITAL

router = APIRouter()


class BacktestRequest(BaseModel):
    tickers: list[str] = DEFAULT_TICKERS[:10]
    start_date: str = START_DATE
    end_date: str = END_DATE
    capital: float = DEFAULT_CAPITAL


@router.post("/run")
def run_backtest(req: BacktestRequest):
    """Run a full backtest with given parameters."""
    stock_data = fetch_all(req.tickers, req.start_date, req.end_date)

    if not stock_data:
        return {"error": "No data fetched for given tickers"}

    engine = BacktestEngine(stock_data, req.capital)
    result = engine.run()

    return {
        "dates": result.dates,
        "portfolio_values": result.portfolio_values,
        "cash_values": result.cash_values,
        "trades": result.trades,
        "metrics": {
            "total_return_pct": result.total_return_pct,
            "sharpe_ratio": result.sharpe_ratio,
            "max_drawdown_pct": result.max_drawdown_pct,
            "win_rate_pct": result.win_rate_pct,
            "total_trades": result.total_trades,
            "avg_trade_duration": result.avg_trade_duration,
            "buy_hold_return_pct": result.bnh_return_pct,
        },
        "buy_hold_values": result.bnh_values,
        "memo_stats": engine.memo.stats,
    }
