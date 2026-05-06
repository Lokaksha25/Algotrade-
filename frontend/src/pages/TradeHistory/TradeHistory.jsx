import { useState, useEffect, useMemo } from 'react';
import PageWrapper from '../../components/Layout/PageWrapper';
import LoadingSpinner from '../../components/Common/LoadingSpinner';
import { runBacktest } from '../../services/api';
import { formatCurrency, formatPercent, formatDate, formatDuration } from '../../utils/formatters';
import { motion } from 'framer-motion';
import './TradeHistory.css';

function generateDemoTrades() {
  const tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'UNH'];
  const signals = ['SMA Cross', 'KMP Pattern', 'FFT Cycle', 'Kadane Signal', 'RSI Reversal'];
  const trades = [];

  for (let i = 0; i < 80; i++) {
    const ticker = tickers[Math.floor(Math.random() * tickers.length)];
    const entryDate = new Date(2023, Math.floor(Math.random() * 12), 1 + Math.floor(Math.random() * 28));
    const holdDays = 2 + Math.floor(Math.random() * 30);
    const exitDate = new Date(entryDate);
    exitDate.setDate(exitDate.getDate() + holdDays);

    const entryPrice = 50 + Math.random() * 400;
    const exitPrice = entryPrice * (0.85 + Math.random() * 0.35);
    const pnl = exitPrice - entryPrice;
    const pnlPct = pnl / entryPrice;

    trades.push({
      id: i + 1,
      ticker,
      entry_date: entryDate.toISOString().split('T')[0],
      exit_date: exitDate.toISOString().split('T')[0],
      entry_price: entryPrice,
      exit_price: exitPrice,
      pnl,
      pnl_pct: pnlPct,
      duration: holdDays,
      signal: signals[Math.floor(Math.random() * signals.length)],
    });
  }

  return trades.sort((a, b) => b.entry_date.localeCompare(a.entry_date));
}

const PAGE_SIZE = 15;

export default function TradeHistory() {
  const [allTrades, setAllTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterTicker, setFilterTicker] = useState('All');
  const [filterSignal, setFilterSignal] = useState('All');
  const [filterPnL, setFilterPnL] = useState('All');
  const [sortKey, setSortKey] = useState('entry_date');
  const [sortDir, setSortDir] = useState('desc');
  const [page, setPage] = useState(1);

  useEffect(() => {
    setLoading(true);
    runBacktest()
      .then(res => {
        setAllTrades(res.data?.trades || generateDemoTrades());
        setLoading(false);
      })
      .catch(() => {
        setAllTrades(generateDemoTrades());
        setLoading(false);
      });
  }, []);

  const tickers = useMemo(() => ['All', ...new Set(allTrades.map(t => t.ticker))].sort(), [allTrades]);
  const signals = useMemo(() => ['All', ...new Set(allTrades.map(t => t.signal))].sort(), [allTrades]);

  const filteredTrades = useMemo(() => {
    let result = [...allTrades];
    if (filterTicker !== 'All') result = result.filter(t => t.ticker === filterTicker);
    if (filterSignal !== 'All') result = result.filter(t => t.signal === filterSignal);
    if (filterPnL === 'Profit') result = result.filter(t => t.pnl >= 0);
    if (filterPnL === 'Loss') result = result.filter(t => t.pnl < 0);

    result.sort((a, b) => {
      let va = a[sortKey], vb = b[sortKey];
      if (typeof va === 'string') return sortDir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
      return sortDir === 'asc' ? va - vb : vb - va;
    });
    return result;
  }, [allTrades, filterTicker, filterSignal, filterPnL, sortKey, sortDir]);

  const totalPages = Math.ceil(filteredTrades.length / PAGE_SIZE);
  const paginatedTrades = filteredTrades.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const stats = useMemo(() => {
    const wins = allTrades.filter(t => t.pnl >= 0);
    const totalPnL = allTrades.reduce((s, t) => s + t.pnl, 0);
    const avgDuration = allTrades.length > 0
      ? allTrades.reduce((s, t) => s + (t.duration || 0), 0) / allTrades.length : 0;
    return {
      total: allTrades.length,
      profitable: wins.length,
      totalPnL,
      avgDuration: Math.round(avgDuration),
    };
  }, [allTrades]);

  const handleSort = (key) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortKey(key); setSortDir('desc'); }
  };

  const handleExport = () => {
    const header = 'Ticker,Entry Date,Exit Date,Entry Price,Exit Price,P/L,P/L %,Duration,Signal\n';
    const rows = filteredTrades.map(t =>
      `${t.ticker},${t.entry_date},${t.exit_date},${t.entry_price.toFixed(2)},${t.exit_price.toFixed(2)},${t.pnl.toFixed(2)},${(t.pnl_pct * 100).toFixed(2)}%,${t.duration}d,${t.signal}`
    ).join('\n');
    const blob = new Blob([header + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'trades.csv'; a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) return <PageWrapper><LoadingSpinner message="Loading trade history..." /></PageWrapper>;

  const SortArrow = ({ col }) => sortKey === col ? <span className="sort-arrow">{sortDir === 'asc' ? '▲' : '▼'}</span> : null;

  return (
    <PageWrapper>
      <div className="page-header">
        <h1 className="page-title" id="trade-history-title">Trade History</h1>
        <p className="page-subtitle">
          Detailed trade log with filtering, sorting, and CSV export
        </p>
      </div>

      {/* Stats Bar */}
      <div className="trades-stats-bar">
        {[
          { value: stats.total, label: 'Total Trades' },
          { value: stats.profitable, label: 'Profitable' },
          { value: formatCurrency(stats.totalPnL), label: 'Total P/L' },
          { value: formatDuration(stats.avgDuration), label: 'Avg Hold Time' },
        ].map((s, i) => (
          <motion.div
            key={i}
            className="glass-card trades-stat"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
          >
            <div className="trades-stat-value">{s.value}</div>
            <div className="trades-stat-label">{s.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Filters */}
      <div className="trades-filters">
        <select className="select-input" value={filterTicker} onChange={e => { setFilterTicker(e.target.value); setPage(1); }} id="filter-ticker">
          {tickers.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <select className="select-input" value={filterSignal} onChange={e => { setFilterSignal(e.target.value); setPage(1); }} id="filter-signal">
          {signals.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select className="select-input" value={filterPnL} onChange={e => { setFilterPnL(e.target.value); setPage(1); }} id="filter-pnl">
          <option value="All">All Trades</option>
          <option value="Profit">Profits Only</option>
          <option value="Loss">Losses Only</option>
        </select>
        <div className="trades-search" style={{ display: 'flex', gap: 8 }}>
          <span className="badge badge-blue">{filteredTrades.length} matches</span>
          <button className="btn btn-secondary btn-sm" onClick={handleExport} id="export-csv-btn">
            📥 Export CSV
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="glass-card glass-card--static trades-table-container">
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" id="trades-table">
            <thead>
              <tr>
                <th className="sort-header" onClick={() => handleSort('ticker')}>Ticker<SortArrow col="ticker" /></th>
                <th className="sort-header" onClick={() => handleSort('entry_date')}>Entry Date<SortArrow col="entry_date" /></th>
                <th className="sort-header" onClick={() => handleSort('exit_date')}>Exit Date<SortArrow col="exit_date" /></th>
                <th className="sort-header" onClick={() => handleSort('entry_price')}>Entry<SortArrow col="entry_price" /></th>
                <th className="sort-header" onClick={() => handleSort('exit_price')}>Exit<SortArrow col="exit_price" /></th>
                <th className="sort-header" onClick={() => handleSort('pnl')}>P/L<SortArrow col="pnl" /></th>
                <th className="sort-header" onClick={() => handleSort('pnl_pct')}>P/L %<SortArrow col="pnl_pct" /></th>
                <th className="sort-header" onClick={() => handleSort('duration')}>Duration<SortArrow col="duration" /></th>
                <th>Signal</th>
              </tr>
            </thead>
            <tbody>
              {paginatedTrades.map((t, i) => (
                <tr key={t.id || i}>
                  <td><span className="font-semibold">{t.ticker}</span></td>
                  <td className="text-muted">{formatDate(t.entry_date)}</td>
                  <td className="text-muted">{formatDate(t.exit_date)}</td>
                  <td className="font-mono">${t.entry_price?.toFixed(2)}</td>
                  <td className="font-mono">${t.exit_price?.toFixed(2)}</td>
                  <td className={`pnl-cell ${t.pnl >= 0 ? 'pnl-positive' : 'pnl-negative'}`}>
                    {t.pnl >= 0 ? '+' : ''}{formatCurrency(t.pnl)}
                  </td>
                  <td className={`pnl-cell ${t.pnl_pct >= 0 ? 'pnl-positive' : 'pnl-negative'}`}>
                    {formatPercent(t.pnl_pct)}
                  </td>
                  <td className="text-muted">{formatDuration(t.duration)}</td>
                  <td><span className="badge badge-purple">{t.signal}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="pagination">
            <button className="page-btn" disabled={page === 1} onClick={() => setPage(p => p - 1)}>‹</button>
            {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
              const p = i + 1;
              return (
                <button key={p} className={`page-btn ${page === p ? 'active' : ''}`} onClick={() => setPage(p)}>
                  {p}
                </button>
              );
            })}
            {totalPages > 7 && <span style={{ color: 'var(--text-muted)' }}>…</span>}
            <button className="page-btn" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>›</button>
          </div>
        )}
      </div>
    </PageWrapper>
  );
}
