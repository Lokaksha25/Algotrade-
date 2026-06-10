"""
AlgoTrade Engine — Technical Indicators (Sliding Window)
SMA, EMA, RSI, and Bollinger Bands computed via O(n) sliding window.

DAA Paradigm: Sliding Window
Brute-force: O(n·k) — recompute entire window at each step
Optimized:   O(n) — maintain running aggregate, slide by 1
"""

import numpy as np
from config import (
    SMA_SHORT_WINDOW, SMA_LONG_WINDOW, EMA_WINDOW,
    RSI_WINDOW, BOLLINGER_WINDOW, BOLLINGER_STD,
)


# ═══════════════════════════════════════════════════════════════════════════════
# BRUTE-FORCE BASELINES — O(n·k) each
# ═══════════════════════════════════════════════════════════════════════════════

def sma_brute(prices: np.ndarray, window: int = SMA_SHORT_WINDOW) -> np.ndarray:
    """
    Simple Moving Average — brute-force.
    At each step, sum the entire window from scratch.
    Time: O(n·k) where k = window size
    """
    n = len(prices)
    result = np.full(n, np.nan)
    for i in range(window - 1, n):
        total = 0.0
        for j in range(i - window + 1, i + 1):
            total += prices[j]
        result[i] = total / window
    return result


def rsi_brute(prices: np.ndarray, window: int = RSI_WINDOW) -> np.ndarray:
    """
    Relative Strength Index — brute-force.
    Recompute gains/losses over the full window at each step.
    Time: O(n·k)
    """
    n = len(prices)
    result = np.full(n, np.nan)
    deltas = np.diff(prices)

    for i in range(window, n):
        window_deltas = deltas[i - window:i]
        gains = np.sum(window_deltas[window_deltas > 0])
        losses = -np.sum(window_deltas[window_deltas < 0])

        avg_gain = gains / window
        avg_loss = losses / window

        if avg_loss == 0:
            result[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[i] = 100 - (100 / (1 + rs))
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# OPTIMIZED — Sliding Window O(n)
# ═══════════════════════════════════════════════════════════════════════════════

def sma(prices: np.ndarray, window: int = SMA_SHORT_WINDOW) -> np.ndarray:
    """
    Simple Moving Average — optimized sliding window.
    Maintains running sum; at each step: sum += new - old.
    Time: O(n)  Space: O(1) extra
    """
    n = len(prices)
    result = np.full(n, np.nan)
    if window <= 0 or n < window:
        return result

    # Initial window sum
    window_sum = np.sum(prices[:window])
    result[window - 1] = window_sum / window

    # Slide: add new element, remove oldest
    for i in range(window, n):
        window_sum += prices[i] - prices[i - window]
        result[i] = window_sum / window

    return result


def ema(prices: np.ndarray, window: int = EMA_WINDOW) -> np.ndarray:
    """
    Exponential Moving Average — single pass O(n).
    Uses exponential decay factor: α = 2 / (window + 1).
    EMA(t) = α * price(t) + (1 - α) * EMA(t-1)
    """
    n = len(prices)
    result = np.full(n, np.nan)
    if window <= 0 or n < window:
        return result
    alpha = 2.0 / (window + 1)

    # Initialize with SMA of first window
    result[window - 1] = np.mean(prices[:window])

    # Single pass with exponential smoothing
    for i in range(window, n):
        result[i] = alpha * prices[i] + (1 - alpha) * result[i - 1]

    return result


def rsi(prices: np.ndarray, window: int = RSI_WINDOW) -> np.ndarray:
    """
    Relative Strength Index — optimized sliding window O(n).
    Maintains running average gain/loss with exponential smoothing.
    RSI = 100 - (100 / (1 + RS)), where RS = avg_gain / avg_loss
    """
    n = len(prices)
    result = np.full(n, np.nan)
    if window <= 0 or n <= window:
        return result
    deltas = np.diff(prices)

    # Initial average gain/loss from first window
    first_gains = deltas[:window]
    avg_gain = np.mean(np.maximum(first_gains, 0))
    avg_loss = np.mean(np.maximum(-first_gains, 0))

    if avg_loss == 0:
        result[window] = 100.0
    else:
        rs = avg_gain / avg_loss
        result[window] = 100 - (100 / (1 + rs))

    # Slide with exponential smoothing
    for i in range(window + 1, n):
        delta = deltas[i - 1]
        gain = max(delta, 0)
        loss = max(-delta, 0)

        avg_gain = (avg_gain * (window - 1) + gain) / window
        avg_loss = (avg_loss * (window - 1) + loss) / window

        if avg_loss == 0:
            result[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[i] = 100 - (100 / (1 + rs))

    return result


def bollinger_bands(
    prices: np.ndarray,
    window: int = BOLLINGER_WINDOW,
    num_std: float = BOLLINGER_STD,
) -> dict[str, np.ndarray]:
    """
    Bollinger Bands — SMA ± k × rolling standard deviation.
    Middle: SMA(window)
    Upper:  SMA + k * σ
    Lower:  SMA - k * σ
    Time: O(n) for the SMA component; std computed via running variance
    """
    n = len(prices)
    middle = sma(prices, window)

    upper = np.full(n, np.nan)
    lower = np.full(n, np.nan)

    for i in range(window - 1, n):
        segment = prices[i - window + 1:i + 1]
        std = np.std(segment)
        upper[i] = middle[i] + num_std * std
        lower[i] = middle[i] - num_std * std

    return {
        "middle": middle,
        "upper": upper,
        "lower": lower,
    }


def generate_sma_crossover_signals(
    prices: np.ndarray,
    short_window: int = SMA_SHORT_WINDOW,
    long_window: int = SMA_LONG_WINDOW,
) -> list[dict]:
    """
    Generate buy/sell signals from SMA crossovers.
    BUY:  when short SMA crosses above long SMA (golden cross)
    SELL: when short SMA crosses below long SMA (death cross)
    """
    short_sma = sma(prices, short_window)
    long_sma = sma(prices, long_window)

    signals = []
    position = None  # Track current position

    for i in range(long_window, len(prices)):
        if np.isnan(short_sma[i]) or np.isnan(long_sma[i]):
            continue

        # Golden cross — BUY
        if short_sma[i] > long_sma[i] and short_sma[i - 1] <= long_sma[i - 1]:
            if position is None:
                position = {"type": "BUY", "entry_idx": i, "entry_price": float(prices[i])}

        # Death cross — SELL
        elif short_sma[i] < long_sma[i] and short_sma[i - 1] >= long_sma[i - 1]:
            if position is not None:
                signals.append({
                    "buy_idx": position["entry_idx"],
                    "sell_idx": i,
                    "buy_price": position["entry_price"],
                    "sell_price": float(prices[i]),
                    "profit_pct": round(((prices[i] - position["entry_price"]) / position["entry_price"]) * 100, 2),
                    "source": "sma_crossover",
                })
                position = None

    return signals


def compute_all_indicators(prices: np.ndarray) -> dict:
    """Compute all indicators for a price series and return as dict."""
    return {
        "sma_short": sma(prices, SMA_SHORT_WINDOW).tolist(),
        "sma_long": sma(prices, SMA_LONG_WINDOW).tolist(),
        "ema": ema(prices, EMA_WINDOW).tolist(),
        "rsi": rsi(prices, RSI_WINDOW).tolist(),
        "bollinger": {
            k: v.tolist() for k, v in bollinger_bands(prices).items()
        },
    }
