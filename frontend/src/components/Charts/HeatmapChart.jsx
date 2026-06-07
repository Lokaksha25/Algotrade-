import { useMemo } from 'react';

export default function HeatmapChart({ matrix, labels, height = 360 }) {
  const cellSize = useMemo(() => {
    if (!labels?.length) return 30;
    const maxSize = Math.min(height - 40, 500);
    return Math.max(20, Math.floor(maxSize / labels.length));
  }, [labels, height]);

  if (!matrix?.length || !labels?.length) return null;

  const getColor = (val) => {
    // Map correlation [-1, 1] to color
    const t = (val + 1) / 2; // normalize to [0, 1]
    if (t < 0.3) return `rgba(59, 130, 246, ${0.3 + t})`; // blue = low correlation
    if (t < 0.5) return `rgba(139, 92, 246, ${0.2 + t * 0.6})`; // purple = moderate
    if (t < 0.7) return `rgba(245, 158, 11, ${0.2 + t * 0.6})`; // amber
    return `rgba(239, 68, 68, ${0.3 + t * 0.5})`; // red = high correlation
  };

  const totalW = labels.length * cellSize + 60;
  const totalH = labels.length * cellSize + 60;

  return (
    <div style={{ overflowX: 'auto', overflowY: 'auto', maxHeight: height + 40 }}>
      <svg width={totalW} height={totalH} style={{ display: 'block' }}>
        {/* Column labels */}
        {labels.map((label, i) => (
          <text
            key={`col-${i}`}
            x={60 + i * cellSize + cellSize / 2}
            y={14}
            textAnchor="middle"
            fill="#94a3b8"
            fontSize={Math.min(10, cellSize * 0.45)}
            fontFamily="Inter, sans-serif"
            fontWeight="500"
          >
            {label}
          </text>
        ))}
        {/* Row labels + cells */}
        {matrix.map((row, ri) => (
          <g key={`row-${ri}`}>
            <text
              x={56}
              y={24 + ri * cellSize + cellSize / 2 + 4}
              textAnchor="end"
              fill="#94a3b8"
              fontSize={Math.min(10, cellSize * 0.45)}
              fontFamily="Inter, sans-serif"
              fontWeight="500"
            >
              {labels[ri]}
            </text>
            {row.map((val, ci) => (
              <g key={`cell-${ri}-${ci}`}>
                <rect
                  x={60 + ci * cellSize}
                  y={20 + ri * cellSize}
                  width={cellSize - 2}
                  height={cellSize - 2}
                  rx={3}
                  fill={getColor(val)}
                  stroke="rgba(255,255,255,0.03)"
                  strokeWidth={0.5}
                >
                  <title>{`${labels[ri]} × ${labels[ci]}: ${val.toFixed(3)}`}</title>
                </rect>
                {cellSize >= 28 && (
                  <text
                    x={60 + ci * cellSize + (cellSize - 2) / 2}
                    y={20 + ri * cellSize + (cellSize - 2) / 2 + 4}
                    textAnchor="middle"
                    fill="rgba(255,255,255,0.7)"
                    fontSize={Math.min(9, cellSize * 0.35)}
                    fontFamily="JetBrains Mono, monospace"
                  >
                    {val.toFixed(2)}
                  </text>
                )}
              </g>
            ))}
          </g>
        ))}
      </svg>
    </div>
  );
}
