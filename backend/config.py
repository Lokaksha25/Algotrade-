"""
AlgoTrade Engine — Global Configuration
"""

# ── Stock Universe (Top 30 S&P 500 by market cap) ──────────────────────────
DEFAULT_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "BRK-B", "LLY", "AVGO", "JPM",
    "TSLA", "V", "UNH", "XOM", "MA",
    "JNJ", "PG", "COST", "HD", "ABBV",
    "MRK", "CRM", "AMD", "NFLX", "PEP",
    "KO", "TMO", "ADBE", "WMT", "BAC",
]

# ── Date Range ──────────────────────────────────────────────────────────────
START_DATE = "2019-01-01"
END_DATE = "2024-12-31"

# ── Capital Budget ──────────────────────────────────────────────────────────
DEFAULT_CAPITAL = 100_000        # $100,000 total budget
CAPITAL_UNIT = 1_000             # $1,000 per unit (W = 100 in Knapsack DP)

# ── Technical Indicator Defaults ────────────────────────────────────────────
SMA_SHORT_WINDOW = 20
SMA_LONG_WINDOW = 50
EMA_WINDOW = 20
RSI_WINDOW = 14
BOLLINGER_WINDOW = 20
BOLLINGER_STD = 2

# ── Candlestick Pattern Encoding ────────────────────────────────────────────
DOJI_THRESHOLD = 0.001           # |close - open| / open < threshold → doji

# ── Benchmark Sizes ─────────────────────────────────────────────────────────
BENCHMARK_SIZES = [1_000, 5_000, 10_000, 50_000, 100_000, 500_000, 1_000_000]
BENCHMARK_SMALL_SIZES = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]  # For Knapsack

# ── FFT ─────────────────────────────────────────────────────────────────────
FFT_SIZES = [512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
TOP_K_FREQUENCIES = 5

# ── Data Cache ──────────────────────────────────────────────────────────────
DATA_DIR = "data"
