"""
AlgoTrade Engine — Main Backtester Simulation Engine
Ties all modules together: Data → Signals → Portfolio → Execution → P&L.
"""

import numpy as np
from algotrade.utils.types import OHLCVData, BacktestResult
from algotrade.data_layer.segment_tree import SegmentTree
from algotrade.signal_engine.indicators import sma, ema, rsi, bollinger_bands, generate_sma_crossover_signals
from algotrade.signal_engine.profit_finder import find_all_profitable_windows
from algotrade.signal_engine.pattern_matcher import find_all_patterns
from algotrade.signal_engine.fft_cycles import extract_cycles
from algotrade.portfolio.knapsack import knapsack_dp
from algotrade.portfolio.mst_diversification import compute_correlation_matrix, kruskal_mst, select_diversified_stocks
from algotrade.execution.activity_selection import activity_selection_greedy, format_trades_as_activities
from algotrade.execution.priority_queue import MaxHeap
from algotrade.backtester.memoizer import Memoizer
from algotrade.backtester.interval_scheduler import weighted_interval_scheduling_dp
from config import DEFAULT_CAPITAL, CAPITAL_UNIT


class BacktestEngine:
    """
    Main simulation engine that orchestrates the full backtest pipeline.

    Pipeline:
      1. Load OHLCV data + build Segment Trees
      2. Generate trade signals (indicators, patterns, profit windows)
      3. Allocate capital (Knapsack DP + MST diversification)
      4. Schedule trades (Activity Selection + Interval Scheduling)
      5. Simulate day-by-day execution
      6. Compute performance metrics
    """

    def __init__(self, stock_data: dict[str, OHLCVData], capital: float = DEFAULT_CAPITAL):
        self.stock_data = stock_data
        self.initial_capital = capital
        self.memo = Memoizer()
        self.segment_trees = {}  # ticker -> SegmentTree

    def _build_segment_trees(self):
        """Build segment trees for range queries on all stocks."""
        for ticker, data in self.stock_data.items():
            self.segment_trees[ticker] = {
                "high": SegmentTree(data.high, "max"),
                "low": SegmentTree(data.low, "min"),
                "close": SegmentTree(data.close, "max"),
            }

    def _generate_signals(self, ticker: str) -> list[dict]:
        """Generate all trade signals for a single stock."""
        data = self.stock_data[ticker]
        prices = data.close
        signals = []

        # SMA crossover signals
        crossover_signals = generate_sma_crossover_signals(prices)
        for sig in crossover_signals:
            sig["ticker"] = ticker
            sig["source"] = "sma_crossover"
            signals.append(sig)

        # Profitable windows
        window_signals = find_all_profitable_windows(prices, min_profit_pct=3.0)
        for sig in window_signals:
            sig["ticker"] = ticker
            sig["source"] = "profit_window"
            signals.append(sig)

        # Pattern-based signals
        patterns = find_all_patterns(data.open, data.close, method="kmp")
        for pat in patterns:
            if pat["signal"] == "BUY" and pat["position"] + 5 < len(prices):
                entry = pat["position"]
                exit_idx = min(entry + 10, len(prices) - 1)
                profit_pct = ((prices[exit_idx] - prices[entry]) / prices[entry]) * 100
                signals.append({
                    "buy_idx": entry, "sell_idx": exit_idx,
                    "buy_price": float(prices[entry]), "sell_price": float(prices[exit_idx]),
                    "profit_pct": round(float(profit_pct), 2),
                    "ticker": ticker, "source": f"pattern_{pat['pattern']}",
                })

        return signals

    def run(self) -> BacktestResult:
        """Execute the full backtest pipeline."""
        # Step 1: Build segment trees
        self._build_segment_trees()

        # Step 2: Generate signals for all stocks
        all_signals = []
        signals_by_ticker = {}
        for ticker in self.stock_data:
            sigs = self._generate_signals(ticker)
            signals_by_ticker[ticker] = sigs
            all_signals.extend(sigs)

        # Step 3: Portfolio construction
        # Compute correlation matrix for diversification
        tickers = list(self.stock_data.keys())
        if len(tickers) >= 3:
            returns_matrix = np.column_stack([
                self.stock_data[t].daily_returns() for t in tickers
                if len(self.stock_data[t].daily_returns()) > 0
            ])
            valid_tickers = [t for t in tickers if len(self.stock_data[t].daily_returns()) > 0]
            if returns_matrix.shape[1] >= 2:
                min_len = min(returns_matrix.shape[0], len(valid_tickers))
                if min_len > 10:
                    corr_matrix = compute_correlation_matrix(returns_matrix[:min_len])
                    diversified = select_diversified_stocks(valid_tickers, corr_matrix, max_stocks=15)
                else:
                    diversified = valid_tickers
            else:
                diversified = valid_tickers
        else:
            diversified = tickers

        # Knapsack allocation
        # Value = avg profit_pct, Weight = capital units needed
        ticker_values = []
        ticker_weights = []
        for t in diversified:
            sigs = signals_by_ticker.get(t, [])
            if sigs:
                avg_profit = np.mean([s.get("profit_pct", 0) for s in sigs])
                ticker_values.append(max(0.1, float(avg_profit)))
            else:
                ticker_values.append(0.1)
            ticker_weights.append(max(1, int(self.stock_data[t].close[-1] / CAPITAL_UNIT)))

        capacity = int(self.initial_capital / CAPITAL_UNIT)
        allocation = knapsack_dp(ticker_values, ticker_weights, capacity)
        selected_tickers = [diversified[i] for i in allocation["selected_indices"]]

        if not selected_tickers:
            selected_tickers = diversified[:5]

        # Step 4: Schedule trades using Interval Scheduling DP
        scheduled_signals = []
        for t in selected_tickers:
            sigs = signals_by_ticker.get(t, [])
            if sigs:
                activities = format_trades_as_activities(sigs)
                non_overlapping = activity_selection_greedy(activities)
                intervals = [{"start": a["start"], "end": a["end"],
                              "value": abs(a.get("value", 1))} for a in non_overlapping]
                if intervals:
                    result = weighted_interval_scheduling_dp(intervals)
                    for idx in result["selected_indices"]:
                        if idx < len(sigs):
                            scheduled_signals.append(sigs[idx])

        # Step 5: Simulate trades
        return self._simulate(selected_tickers, scheduled_signals)

    def _simulate(self, tickers: list[str], signals: list[dict]) -> BacktestResult:
        """Simulate trading day-by-day and compute P&L."""
        # Use first stock's dates as timeline
        ref_ticker = tickers[0] if tickers else list(self.stock_data.keys())[0]
        ref_data = self.stock_data[ref_ticker]
        n_days = ref_data.n
        dates = ref_data.dates

        cash = self.initial_capital
        portfolio_values = [self.initial_capital]
        cash_values = [self.initial_capital]
        executed_trades = []

        # Sort signals by entry time
        sorted_signals = sorted(signals, key=lambda s: s.get("buy_idx", 0))

        # Priority queue for pending signals
        heap = MaxHeap()
        for sig in sorted_signals:
            heap.insert(sig.get("profit_pct", 0), sig)

        # Execute top signals
        positions = {}
        while heap:
            priority, sig = heap.extract_max()
            ticker = sig.get("ticker", "")
            buy_idx = sig.get("buy_idx", 0)
            sell_idx = sig.get("sell_idx", 0)
            buy_price = sig.get("buy_price", 0)
            sell_price = sig.get("sell_price", 0)

            # Position sizing: allocate equally
            position_size = min(cash * 0.1, self.initial_capital * 0.05)
            if position_size < buy_price or buy_price <= 0:
                continue

            shares = int(position_size / buy_price)
            if shares <= 0:
                continue

            cost = shares * buy_price
            revenue = shares * sell_price
            profit = revenue - cost

            cash -= cost
            cash += revenue

            executed_trades.append({
                "ticker": ticker,
                "entry_date": dates[buy_idx] if buy_idx < len(dates) else "",
                "exit_date": dates[sell_idx] if sell_idx < len(dates) else "",
                "entry_price": round(buy_price, 2),
                "exit_price": round(sell_price, 2),
                "shares": shares,
                "profit": round(profit, 2),
                "profit_pct": round((profit / cost) * 100, 2) if cost > 0 else 0,
                "duration": sell_idx - buy_idx,
                "source": sig.get("source", ""),
            })

        # Build equity curve
        final_value = self.initial_capital + sum(t["profit"] for t in executed_trades)
        # Interpolate equity curve
        for i in range(1, n_days):
            pv = self.initial_capital
            for trade in executed_trades:
                buy_idx = next((j for j, d in enumerate(dates) if d == trade["entry_date"]), 0)
                sell_idx = next((j for j, d in enumerate(dates) if d == trade["exit_date"]), 0)
                if i >= sell_idx and sell_idx > 0:
                    pv += trade["profit"]
                elif buy_idx <= i < sell_idx:
                    # Mark-to-market
                    ticker = trade["ticker"]
                    if ticker in self.stock_data and i < self.stock_data[ticker].n:
                        current_price = self.stock_data[ticker].close[i]
                        unrealized = (current_price - trade["entry_price"]) * trade["shares"]
                        pv += unrealized
            portfolio_values.append(round(pv, 2))
            cash_values.append(round(cash, 2))

        # Buy-and-hold baseline
        bnh_values = []
        if ref_ticker in self.stock_data:
            ref_prices = self.stock_data[ref_ticker].close
            bnh_shares = self.initial_capital / ref_prices[0] if ref_prices[0] > 0 else 0
            bnh_values = [round(bnh_shares * p, 2) for p in ref_prices]

        # Compute metrics
        total_return = ((final_value - self.initial_capital) / self.initial_capital) * 100
        winning = [t for t in executed_trades if t["profit"] > 0]
        win_rate = (len(winning) / len(executed_trades) * 100) if executed_trades else 0

        # Sharpe ratio
        if len(portfolio_values) > 1:
            pv_arr = np.array(portfolio_values)
            daily_returns = np.diff(pv_arr) / pv_arr[:-1]
            sharpe = (np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)) if np.std(daily_returns) > 0 else 0
        else:
            sharpe = 0

        # Max drawdown
        pv_arr = np.array(portfolio_values)
        peak = np.maximum.accumulate(pv_arr)
        drawdown = (peak - pv_arr) / peak * 100
        max_dd = float(np.max(drawdown)) if len(drawdown) > 0 else 0

        avg_duration = np.mean([t["duration"] for t in executed_trades]) if executed_trades else 0
        bnh_return = ((bnh_values[-1] - self.initial_capital) / self.initial_capital * 100) if bnh_values else 0

        return BacktestResult(
            dates=dates,
            portfolio_values=portfolio_values,
            cash_values=cash_values,
            trades=executed_trades,
            total_return_pct=round(total_return, 2),
            sharpe_ratio=round(sharpe, 4),
            max_drawdown_pct=round(max_dd, 2),
            win_rate_pct=round(win_rate, 2),
            total_trades=len(executed_trades),
            avg_trade_duration=round(avg_duration, 1),
            bnh_return_pct=round(bnh_return, 2),
            bnh_values=bnh_values,
        )
