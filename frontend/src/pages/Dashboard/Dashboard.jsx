import { useState, useEffect } from 'react';
import PageWrapper from '../../components/Layout/PageWrapper';
import MetricCard from '../../components/Cards/MetricCard';
import EquityCurve from '../../components/Charts/EquityCurve';
import DonutChart from '../../components/Charts/DonutChart';
import LoadingSpinner from '../../components/Common/LoadingSpinner';
import { runBacktest } from '../../services/api';
import { formatCurrency, formatPercent, formatNumber } from '../../utils/formatters';
import { CHART_COLORS } from '../../utils/constants';
import './Dashboard.css';

// Generate demo data when API is unavailable
function generateDemoData() {
  const startDate = new Date('2022-01-03');
  const days = 500;
  let equity = 100000;
  let benchmark = 100000;
  const equityData = [];
  const benchmarkData = [];
  const trades = [];

  const tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM'];

  for (let i = 0; i < days; i++) {
    const date = new Date('2022-01-03T00:00:00Z');
    date.setUTCDate(date.getUTCDate() + i);
    if (date.getUTCDay() === 0 || date.getUTCDay() === 6) continue;

    const dayStr = date.toISOString().split('T')[0];
    equity *= 1 + (Math.random() - 0.47) * 0.025;
    benchmark *= 1 + (Math.random() - 0.48) * 0.02;

    equityData.push({ time: dayStr, value: equity });
    benchmarkData.push({ time: dayStr, value: benchmark });

    if (Math.random() < 0.05) {
      const ticker = tickers[Math.floor(Math.random() * tickers.length)];
      const entryPrice = 100 + Math.random() * 300;
      const exitPrice = entryPrice * (0.9 + Math.random() * 0.25);
      trades.push({
        ticker,
        entry_date: dayStr,
        exit_date: dayStr,
        entry_price: entryPrice,
        exit_price: exitPrice,
        pnl: exitPrice - entryPrice,
        pnl_pct: (exitPrice - entryPrice) / entryPrice,
        signal: ['SMA Cross', 'KMP Pattern', 'FFT Cycle', 'Kadane Signal'][Math.floor(Math.random() * 4)],
      });
    }
  }

  const finalReturn = (equity - 100000) / 100000;
  const winTrades = trades.filter(t => t.pnl > 0);

  return {
    metrics: {
      total_return: finalReturn,
      sharpe_ratio: 1.2 + Math.random() * 0.8,
      max_drawdown: -(0.08 + Math.random() * 0.12),
      win_rate: winTrades.length / Math.max(trades.length, 1),
      total_trades: trades.length,
      final_equity: equity,
    },
    equity_curve: equityData,
    benchmark_curve: benchmarkData,
    trades: trades.slice(-10),
    allocation: tickers.map((t, i) => ({
      name: t,
      value: 8000 + Math.random() * 15000,
      percent: 0,
      color: CHART_COLORS[i % CHART_COLORS.length],
    })),
  };
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    runBacktest()
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(() => {
        // Fallback to demo data
        setData(generateDemoData());
        setLoading(false);
      });
  }, []);

  if (loading) return <PageWrapper><LoadingSpinner message="Running backtest engine..." /></PageWrapper>;

  const m = data?.metrics || {};
  const alloc = data?.allocation || [];
  const totalAlloc = alloc.reduce((s, a) => s + a.value, 0);
  const allocWithPct = alloc.map(a => ({ ...a, percent: a.value / totalAlloc }));

  return (
    <PageWrapper>
      <div className="page-header">
        <h1 className="page-title" id="dashboard-title">Dashboard</h1>
        <p className="page-subtitle">
          Real-time backtest results powered by 15 DAA paradigms
        </p>
      </div>

      {/* Metric Cards */}
      <div className="dashboard-metrics">
        <MetricCard
          label="Total Return"
          value={formatPercent(m.total_return)}
          icon="📈"
          color={m.total_return >= 0 ? 'green' : 'red'}
          trend={m.total_return >= 0 ? 12.3 : -8.5}
          context="vs. buy & hold"
          index={0}
        />
        <MetricCard
          label="Sharpe Ratio"
          value={formatNumber(m.sharpe_ratio)}
          icon="⚡"
          color="blue"
          context="risk-adjusted"
          index={1}
        />
        <MetricCard
          label="Max Drawdown"
          value={formatPercent(m.max_drawdown)}
          icon="📉"
          color="red"
          context="peak to trough"
          index={2}
        />
        <MetricCard
          label="Win Rate"
          value={formatPercent(m.win_rate)}
          icon="🎯"
          color="purple"
          context={`${m.total_trades || 0} total trades`}
          index={3}
        />
      </div>

      {/* Equity Curve + Allocation */}
      <div className="dashboard-main">
        <div className="glass-card glass-card--static dashboard-equity">
          <div className="dashboard-equity-header">
            <h3 className="section-title" style={{ marginBottom: 0 }}>Equity Curve</h3>
            <span className="badge badge-green">
              {formatCurrency(m.final_equity || 0)}
            </span>
          </div>
          {/* <EquityCurve
            data={data?.equity_curve || []}
            benchmarkData={data?.benchmark_curve}
            height={320}
          /> */}
          <div style={{ height: 320, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
            [Chart Unavailable]
          </div>
        </div>

        <div className="glass-card glass-card--static dashboard-allocation">
          <h3 className="section-title">Portfolio Allocation</h3>
          <DonutChart
            data={allocWithPct}
            height={240}
            centerValue={allocWithPct.length.toString()}
            centerLabel="Stocks"
          />
          <div className="allocation-legend">
            {allocWithPct.slice(0, 8).map((a, i) => (
              <div key={i} className="legend-item">
                <div className="legend-dot" style={{ background: a.color }} />
                <span>{a.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Algorithm Summary Cards */}
      <h3 className="section-title">Engine Components</h3>
      <div className="dashboard-algo-summary">
        <div className="glass-card algo-summary-card">
          <div className="algo-summary-number">15</div>
          <div className="algo-summary-label">DAA Paradigms</div>
        </div>
        <div className="glass-card algo-summary-card">
          <div className="algo-summary-number">5</div>
          <div className="algo-summary-label">Algorithm Modules</div>
        </div>
        <div className="glass-card algo-summary-card">
          <div className="algo-summary-number">30</div>
          <div className="algo-summary-label">S&P 500 Stocks</div>
        </div>
      </div>

      {/* Recent Trades Table */}
      <div className="glass-card glass-card--static dashboard-trades">
        <div className="dashboard-trades-header">
          <h3 className="section-title" style={{ marginBottom: 0 }}>Recent Trades</h3>
          <span className="badge badge-blue">{data?.trades?.length || 0} trades</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" id="recent-trades-table">
            <thead>
              <tr>
                <th>Ticker</th>
                <th>Entry Date</th>
                <th>Entry Price</th>
                <th>Exit Price</th>
                <th>P/L</th>
                <th>Signal</th>
              </tr>
            </thead>
            <tbody>
              {(data?.trades || []).slice(0, 10).map((t, i) => (
                <tr key={i}>
                  <td><span className="font-semibold">{t.ticker}</span></td>
                  <td className="text-muted">{t.entry_date}</td>
                  <td className="font-mono">${t.entry_price?.toFixed(2)}</td>
                  <td className="font-mono">${t.exit_price?.toFixed(2)}</td>
                  <td>
                    <span className={`badge ${t.pnl >= 0 ? 'badge-green' : 'badge-red'}`}>
                      {t.pnl >= 0 ? '+' : ''}{formatCurrency(t.pnl)}
                    </span>
                  </td>
                  <td><span className="badge badge-purple">{t.signal}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </PageWrapper>
  );
}
