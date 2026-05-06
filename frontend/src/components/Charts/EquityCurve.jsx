import { useEffect, useRef } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

export default function EquityCurve({ data, benchmarkData, height = 320 }) {
  const chartContainerRef = useRef(null);

  useEffect(() => {
    if (!chartContainerRef.current || !data?.length) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: 'solid', color: 'transparent' },
        textColor: '#94a3b8',
        fontFamily: "'Inter', sans-serif",
        fontSize: 12,
      },
      grid: {
        vertLines: { color: 'rgba(255,255,255,0.03)' },
        horzLines: { color: 'rgba(255,255,255,0.03)' },
      },
      width: chartContainerRef.current.clientWidth,
      height,
      rightPriceScale: { borderColor: 'rgba(255,255,255,0.08)' },
      timeScale: { borderColor: 'rgba(255,255,255,0.08)' },
      crosshair: {
        vertLine: { color: 'rgba(59,130,246,0.3)', width: 1, style: 2 },
        horzLine: { color: 'rgba(59,130,246,0.3)', width: 1, style: 2 },
      },
    });

    // Strategy equity curve
    const areaSeries = chart.addAreaSeries({
      lineColor: '#10b981',
      topColor: 'rgba(16, 185, 129, 0.3)',
      bottomColor: 'rgba(16, 185, 129, 0.02)',
      lineWidth: 2,
      title: 'Strategy',
    });
    areaSeries.setData(data);

    // Benchmark overlay
    if (benchmarkData?.length) {
      const benchSeries = chart.addLineSeries({
        color: '#64748b',
        lineWidth: 1.5,
        lineStyle: 2,
        title: 'Buy & Hold',
      });
      benchSeries.setData(benchmarkData);
    }

    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, benchmarkData, height]);

  return (
    <div
      ref={chartContainerRef}
      id="equity-curve"
      style={{ width: '100%', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}
    />
  );
}
