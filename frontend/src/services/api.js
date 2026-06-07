/**
 * AlgoTrade Engine — API Service Layer
 * Axios client configured for FastAPI backend
 * Uses Vite dev proxy (/api -> localhost:8000/api)
 */

import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

export const DEFAULT_BACKTEST_CONFIG = {
  tickers: ['AAPL', 'MSFT', 'NVDA', 'META', 'JPM'],
  start_date: '2024-01-01',
  end_date: '2024-12-31',
  capital: 100000,
};

// ── Data Endpoints ────────────────────────────────────────────
export const fetchTickers = () => api.get('/data/tickers');
export const fetchOHLCV = (ticker) => api.get(`/data/${ticker}`);

// ── Backtest Endpoints ────────────────────────────────────────
export const runBacktest = (config = {}) => api.post('/backtest/run', config);

// ── Signal Endpoints ──────────────────────────────────────────
export const fetchSignals = (ticker) => api.get(`/signals/${ticker}`);

// ── Algorithm Benchmark Endpoints ─────────────────────────────
export const fetchBenchmarks = (forceRerun = false) =>
  api.get(`/algorithms/benchmarks${forceRerun ? '?force_rerun=true' : ''}`);

// ── Portfolio Endpoints ───────────────────────────────────────
export const fetchPortfolioOptimize = (config = {}) =>
  api.get('/portfolio/optimize', { params: config });
export const fetchCorrelation = () => api.get('/portfolio/correlation');
export const fetchMST = () => api.get('/portfolio/mst');

export default api;
