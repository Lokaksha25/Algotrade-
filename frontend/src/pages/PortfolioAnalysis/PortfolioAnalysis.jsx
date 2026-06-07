import { useState, useEffect } from 'react';
import PageWrapper from '../../components/Layout/PageWrapper';
import DonutChart from '../../components/Charts/DonutChart';
import HeatmapChart from '../../components/Charts/HeatmapChart';
import NetworkGraph from '../../components/Charts/NetworkGraph';
import LoadingSpinner from '../../components/Common/LoadingSpinner';
import { fetchPortfolioOptimize, fetchCorrelation, fetchMST } from '../../services/api';
import { CHART_COLORS } from '../../utils/constants';
import { formatCurrency } from '../../utils/formatters';
import { motion } from 'framer-motion';
import './PortfolioAnalysis.css';

function generateDemoPortfolio() {
  const tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'JPM', 'V', 'UNH'];
  const n = tickers.length;

  // Knapsack results
  const dpValue = 42500 + Math.random() * 5000;
  const greedyValue = dpValue * (0.88 + Math.random() * 0.08);
  const bruteValue = dpValue; // brute should find optimal for small n

  // Allocation
  const selected = tickers.slice(0, 6);
  const allocation = selected.map((t, i) => ({
    name: t,
    value: 10000 + Math.random() * 20000,
    color: CHART_COLORS[i],
  }));

  // Correlation matrix
  const matrix = [];
  for (let i = 0; i < n; i++) {
    const row = [];
    for (let j = 0; j < n; j++) {
      if (i === j) row.push(1);
      else if (j < i) row.push(matrix[j][i]); // symmetric
      else row.push(-0.2 + Math.random() * 1.0);
    }
    matrix.push(row);
  }

  // MST graph
  const nodes = tickers.map(t => ({ id: t, label: t }));
  const edges = [];
  for (let i = 0; i < n - 1; i++) {
    const j = i + 1 + Math.floor(Math.random() * Math.min(3, n - i - 1));
    edges.push({
      source: tickers[i],
      target: tickers[Math.min(j, n - 1)],
      weight: Math.abs(matrix[i][Math.min(j, n - 1)]),
    });
  }

  return {
    knapsack: { dp: dpValue, greedy: greedyValue, brute: bruteValue },
    allocation,
    correlation: { matrix, labels: tickers },
    mst: { nodes, edges, total_weight: edges.reduce((s, e) => s + e.weight, 0) },
  };
}

export default function PortfolioAnalysis() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchPortfolioOptimize().catch(() => null),
      fetchCorrelation().catch(() => null),
      fetchMST().catch(() => null),
    ]).then(([optRes, corrRes, mstRes]) => {
      if (optRes?.data && corrRes?.data && mstRes?.data) {
        setData({
          knapsack: optRes.data.knapsack,
          allocation: optRes.data.allocation,
          correlation: corrRes.data,
          mst: mstRes.data,
        });
      } else {
        setData(generateDemoPortfolio());
      }
      setLoading(false);
    });
  }, []);

  if (loading) return <PageWrapper><LoadingSpinner message="Optimizing portfolio..." /></PageWrapper>;

  const k = data?.knapsack || {};
  const greedyPct = k.dp > 0 ? ((k.greedy / k.dp) * 100) : 0;
  const alloc = data?.allocation || [];
  const totalAlloc = alloc.reduce((s, a) => s + a.value, 0);

  return (
    <PageWrapper>
      <div className="page-header">
        <h1 className="page-title" id="portfolio-title">Portfolio Analysis</h1>
        <p className="page-subtitle">
          Capital allocation via 0/1 Knapsack DP and MST diversification with Kruskal's algorithm
        </p>
      </div>

      {/* Top: Knapsack + Allocation */}
      <div className="portfolio-top">
        <motion.div
          className="glass-card glass-card--static knapsack-section"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h3 className="section-title">0/1 Knapsack — Capital Allocation</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 16 }}>
            Comparing O(2ⁿ) brute-force, O(n log n) greedy, and O(n·W) DP approaches
          </p>

          <div className="knapsack-comparison">
            <div className="knapsack-method">
              <div className="knapsack-method-name">Brute-Force</div>
              <div className="knapsack-method-value" style={{ color: 'var(--accent-red)' }}>
                {formatCurrency(k.brute)}
              </div>
              <div className="knapsack-method-pct">O(2ⁿ) — 100%</div>
            </div>
            <div className="knapsack-method">
              <div className="knapsack-method-name">Greedy</div>
              <div className="knapsack-method-value" style={{ color: 'var(--accent-amber)' }}>
                {formatCurrency(k.greedy)}
              </div>
              <div className="knapsack-method-pct">O(n log n) — {greedyPct.toFixed(1)}%</div>
            </div>
            <div className="knapsack-method">
              <div className="knapsack-method-name">DP Optimal</div>
              <div className="knapsack-method-value" style={{ color: 'var(--accent-green)' }}>
                {formatCurrency(k.dp)}
              </div>
              <div className="knapsack-method-pct">O(n·W) — 100%</div>
            </div>
          </div>

          <div className="quality-bar-container">
            <div className="quality-bar-label">
              <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Greedy Quality Gap</span>
              <span style={{ color: 'var(--accent-amber)', fontWeight: 600, fontSize: '0.8rem' }}>
                {greedyPct.toFixed(1)}% of optimal
              </span>
            </div>
            <div className="quality-bar-track">
              <motion.div
                className="quality-bar-fill"
                style={{ background: 'var(--gradient-blue)', width: `${greedyPct}%` }}
                initial={{ width: 0 }}
                animate={{ width: `${greedyPct}%` }}
                transition={{ delay: 0.3, duration: 0.8 }}
              />
            </div>
          </div>
        </motion.div>

        <motion.div
          className="glass-card glass-card--static allocation-section"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h3 className="section-title">Optimal Allocation</h3>
          <DonutChart
            data={alloc}
            height={220}
            centerValue={formatCurrency(totalAlloc)}
            centerLabel="Total Capital"
          />
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 12, justifyContent: 'center' }}>
            {alloc.map((a, i) => (
              <span key={i} className="badge" style={{
                background: `${a.color}20`,
                color: a.color,
                border: `1px solid ${a.color}40`,
              }}>
                {a.name}: {formatCurrency(a.value)}
              </span>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Bottom: MST + Heatmap */}
      <div className="portfolio-bottom">
        <motion.div
          className="glass-card glass-card--static mst-section"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h3 className="section-title">MST Diversification Graph</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 12 }}>
            Kruskal's MST on correlation graph — drag nodes to explore
          </p>
          <NetworkGraph graphData={data?.mst} height={360} />
          <div className="mst-stats">
            <div className="mst-stat">
              <span className="mst-stat-label">Nodes</span>
              <span className="mst-stat-value">{data?.mst?.nodes?.length || 0}</span>
            </div>
            <div className="mst-stat">
              <span className="mst-stat-label">MST Edges</span>
              <span className="mst-stat-value">{data?.mst?.edges?.length || 0}</span>
            </div>
            <div className="mst-stat">
              <span className="mst-stat-label">Total Weight</span>
              <span className="mst-stat-value">{data?.mst?.total_weight?.toFixed(3) || '—'}</span>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="glass-card glass-card--static heatmap-section"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h3 className="section-title">Correlation Heatmap</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 12 }}>
            Pearson correlation matrix — blue (low) → red (high)
          </p>
          <HeatmapChart
            matrix={data?.correlation?.matrix || []}
            labels={data?.correlation?.labels || []}
            height={380}
          />
        </motion.div>
      </div>
    </PageWrapper>
  );
}
