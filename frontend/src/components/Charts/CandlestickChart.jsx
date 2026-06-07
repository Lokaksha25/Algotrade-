import { useEffect, useRef } from 'react';
import {
  CandlestickSeries,
  ColorType,
  createChart,
  createSeriesMarkers,
  HistogramSeries,
  LineSeries,
} from 'lightweight-charts';

export default function CandlestickChart({ data, signals = [], height = 400, indicators = {} }) {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    if (!chartContainerRef.current || !data?.length) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#94a3b8',
        fontFamily: "'Inter', sans-serif",
        fontSize: 12,
      },
      grid: {
        vertLines: { color: 'rgba(255,255,255,0.04)' },
        horzLines: { color: 'rgba(255,255,255,0.04)' },
      },
      crosshair: {
        mode: 0,
        vertLine: { color: 'rgba(59,130,246,0.3)', width: 1, style: 2 },
        horzLine: { color: 'rgba(59,130,246,0.3)', width: 1, style: 2 },
      },
      width: chartContainerRef.current.clientWidth,
      height,
      rightPriceScale: {
        borderColor: 'rgba(255,255,255,0.08)',
        scaleMargins: { top: 0.1, bottom: 0.2 },
      },
      timeScale: {
        borderColor: 'rgba(255,255,255,0.08)',
        timeVisible: true,
      },
    });

    chartRef.current = chart;

    // Candlestick series
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#10b981',
      downColor: '#ef4444',
      borderDownColor: '#ef4444',
      borderUpColor: '#10b981',
      wickDownColor: '#ef4444',
      wickUpColor: '#10b981',
    });
    candleSeries.setData(data);

    // Volume histogram
    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
    });
    chart.priceScale('volume').applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });
    if (data[0]?.volume !== undefined) {
      volumeSeries.setData(
        data.map(d => ({
          time: d.time,
          value: d.volume,
          color: d.close >= d.open ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)',
        }))
      );
    }

    // SMA overlay
    if (indicators.sma?.length) {
      const smaSeries = chart.addSeries(LineSeries, {
        color: '#06b6d4',
        lineWidth: 1.5,
        title: 'SMA',
      });
      smaSeries.setData(indicators.sma);
    }

    // EMA overlay
    if (indicators.ema?.length) {
      const emaSeries = chart.addSeries(LineSeries, {
        color: '#f59e0b',
        lineWidth: 1.5,
        title: 'EMA',
      });
      emaSeries.setData(indicators.ema);
    }

    // Buy/Sell markers
    if (signals.length) {
      const markers = signals.map(s => ({
        time: s.time,
        position: s.type === 'buy' ? 'belowBar' : 'aboveBar',
        color: s.type === 'buy' ? '#10b981' : '#ef4444',
        shape: s.type === 'buy' ? 'arrowUp' : 'arrowDown',
        text: s.type === 'buy' ? 'B' : 'S',
      }));
      createSeriesMarkers(candleSeries, markers);
    }

    chart.timeScale().fitContent();

    // Resize handler
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
  }, [data, signals, height, indicators]);

  return (
    <div
      ref={chartContainerRef}
      id="candlestick-chart"
      style={{ width: '100%', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}
    />
  );
}
