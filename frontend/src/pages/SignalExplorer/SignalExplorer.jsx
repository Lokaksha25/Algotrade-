import { useState, useEffect, useMemo } from 'react';
import PageWrapper from '../../components/Layout/PageWrapper';
import CandlestickChart from '../../components/Charts/CandlestickChart';
import LoadingSpinner from '../../components/Common/LoadingSpinner';
import { fetchOHLCV, fetchSignals, fetchTickers } from '../../services/api';
import { motion } from 'framer-motion';
import './SignalExplorer.css';

// Generate demo OHLCV + signals
function generateDemoSignals(ticker) {
  const days = 250;
  const start = new Date('2023-01-03');
  let price = ticker === 'AAPL' ? 130 : ticker === 'MSFT' ? 250 : ticker === 'GOOGL' ? 90 : 150;
  const ohlcv = [];
  const signals = [];

  for (let i = 0; i < days; i++) {
    const date = new Date(start);
    date.setDate(date.getDate() + Math.floor(i * 1.4));
    if (date.getDay() === 0 || date.getDay() === 6) continue;
    const dayStr = date.toISOString().split('T')[0];

    const change = (Math.random() - 0.48) * price * 0.03;
    const open = price;
    const close = price + change;
    const high = Math.max(open, close) + Math.random() * price * 0.01;
    const low = Math.min(open, close) - Math.random() * price * 0.01;
    const volume = Math.floor(20000000 + Math.random() * 50000000);

    ohlcv.push({ time: dayStr, open, high, low, close, volume });
    price = close;

    if (Math.random() < 0.04) {
      signals.push({ time: dayStr, type: 'buy', price: close });
    } else if (Math.random() < 0.04) {
      signals.push({ time: dayStr, type: 'sell', price: close });
    }
  }

  // Compute SMA-20
  const sma = ohlcv.map((d, i) => {
    if (i < 19) return null;
    const avg = ohlcv.slice(i - 19, i + 1).reduce((s, x) => s + x.close, 0) / 20;
    return { time: d.time, value: avg };
  }).filter(Boolean);

  // Compute EMA-12
  const ema = [];
  const multiplier = 2 / 13;
  ohlcv.forEach((d, i) => {
    if (i === 0) { ema.push({ time: d.time, value: d.close }); return; }
    const prev = ema[ema.length - 1].value;
    ema.push({ time: d.time, value: d.close * multiplier + prev * (1 - multiplier) });
  });

  // Demo FFT cycles
  const cycles = [
    { period: 5, label: '~1 Week', strength: 0.85 },
    { period: 21, label: '~1 Month', strength: 0.72 },
    { period: 63, label: '~1 Quarter', strength: 0.56 },
    { period: 126, label: '~6 Months', strength: 0.38 },
  ];

  // Demo patterns
  const patterns = [
    { name: 'Bullish Engulfing', day: ohlcv[45]?.time, type: 'bullish' },
    { name: 'Three White Soldiers', day: ohlcv[78]?.time, type: 'bullish' },
    { name: 'Bearish Harami', day: ohlcv[112]?.time, type: 'bearish' },
    { name: 'Morning Star', day: ohlcv[156]?.time, type: 'bullish' },
    { name: 'Evening Star', day: ohlcv[189]?.time, type: 'bearish' },
    { name: 'Hammer', day: ohlcv[210]?.time, type: 'bullish' },
  ];

  return { ohlcv, signals, sma, ema, cycles, patterns };
}

const DEMO_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM'];

export default function SignalExplorer() {
  const [ticker, setTicker] = useState('AAPL');
  const [tickers, setTickers] = useState(DEMO_TICKERS);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showSMA, setShowSMA] = useState(true);
  const [showEMA, setShowEMA] = useState(false);

  useEffect(() => {
    fetchTickers()
      .then(res => setTickers(res.data?.tickers || DEMO_TICKERS))
      .catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetchOHLCV(ticker).catch(() => null),
      fetchSignals(ticker).catch(() => null),
    ]).then(([ohlcvRes, sigRes]) => {
      if (ohlcvRes?.data && sigRes?.data) {
        setData({ ...ohlcvRes.data, ...sigRes.data });
      } else {
        setData(generateDemoSignals(ticker));
      }
      setLoading(false);
    });
  }, [ticker]);

  const indicators = useMemo(() => ({
    sma: showSMA ? data?.sma : undefined,
    ema: showEMA ? data?.ema : undefined,
  }), [data, showSMA, showEMA]);

  return (
    <PageWrapper>
      <div className="page-header">
        <h1 className="page-title" id="signal-explorer-title">Signal Explorer</h1>
        <p className="page-subtitle">
          Interactive trading signals with FFT cycle detection and KMP pattern matching
        </p>
      </div>

      {/* Controls */}
      <div className="signals-controls">
        <select
          className="select-input"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          id="ticker-selector"
        >
          {tickers.map(t => <option key={t} value={t}>{t}</option>)}
        </select>

        <div className="indicator-toggles">
          <button
            className={`indicator-toggle sma ${showSMA ? 'active' : ''}`}
            onClick={() => setShowSMA(!showSMA)}
            id="toggle-sma"
          >
            <span style={{ width: 10, height: 3, background: '#06b6d4', borderRadius: 2, display: 'inline-block' }} />
            SMA-20
          </button>
          <button
            className={`indicator-toggle ema ${showEMA ? 'active' : ''}`}
            onClick={() => setShowEMA(!showEMA)}
            id="toggle-ema"
          >
            <span style={{ width: 10, height: 3, background: '#f59e0b', borderRadius: 2, display: 'inline-block' }} />
            EMA-12
          </button>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message={`Loading ${ticker} data...`} />
      ) : (
        <>
          {/* Candlestick Chart */}
          <div className="glass-card glass-card--static signals-chart-section">
            <h3 className="section-title" style={{ marginBottom: 12 }}>
              {ticker} — OHLCV Chart
              <span style={{ float: 'right', fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 400 }}>
                {data?.ohlcv?.length || 0} trading days
              </span>
            </h3>
            <CandlestickChart
              data={data?.ohlcv || []}
              signals={data?.signals || []}
              height={420}
              indicators={indicators}
            />
          </div>

          {/* FFT Cycles + Pattern Matches */}
          <div className="signals-bottom">
            <motion.div
              className="glass-card glass-card--static fft-section"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <h3 className="section-title">
                🔬 FFT Dominant Cycles
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8 }}>
                Extracted via O(n log n) Fast Fourier Transform
              </p>
              <div className="fft-cycles-list">
                {(data?.cycles || []).map((c, i) => (
                  <div className="fft-cycle-item" key={i}>
                    <span className="fft-cycle-period">{c.period}d</span>
                    <div className="fft-bar-container">
                      <motion.div
                        className="fft-bar"
                        initial={{ width: 0 }}
                        animate={{ width: `${c.strength * 100}%` }}
                        transition={{ delay: 0.2 + i * 0.1, duration: 0.5 }}
                      />
                    </div>
                    <span className="fft-cycle-strength">{c.label}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div
              className="glass-card glass-card--static patterns-section"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <h3 className="section-title">
                🔍 KMP Pattern Matches
              </h3>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8 }}>
                Candlestick patterns detected via O(n+m) KMP algorithm
              </p>
              <div className="pattern-list">
                {(data?.patterns || []).map((p, i) => (
                  <div className="pattern-item" key={i}>
                    <span className={`badge ${p.type === 'bullish' ? 'badge-green' : 'badge-red'}`}>
                      {p.type === 'bullish' ? '▲' : '▼'}
                    </span>
                    <span className="pattern-name">{p.name}</span>
                    <span className="pattern-day">{p.day}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </>
      )}
    </PageWrapper>
  );
}
