import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, Line, ComposedChart,
} from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: 'rgba(17,24,39,0.95)',
      border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: '8px',
      padding: '10px 14px',
      fontSize: '0.8rem',
    }}>
      {payload.map((entry, i) => (
        <div key={i} style={{ color: entry.color, marginBottom: 2 }}>
          {entry.name}: log₁₀(n)={entry.payload.logN?.toFixed(2)}, log₁₀(t)={entry.value?.toFixed(3)}
        </div>
      ))}
    </div>
  );
};

export default function LogLogPlot({ data, series = [], height = 350, title }) {
  /*
    data: [{ logN, brute, optimized, ... }]
    series: [{ dataKey: 'brute', name: 'Brute-Force', color: '#ef4444', slope: 2.0 }]
  */
  if (!data?.length) return null;

  return (
    <div>
      {title && <h4 style={{ marginBottom: 12, color: '#f1f5f9', fontSize: '0.95rem' }}>{title}</h4>}
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={data} margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
          <CartesianGrid stroke="rgba(255,255,255,0.04)" strokeDasharray="3 3" />
          <XAxis
            dataKey="logN"
            type="number"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            label={{ value: 'log₁₀(n)', position: 'insideBottom', offset: -10, fill: '#64748b', fontSize: 12 }}
          />
          <YAxis
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            label={{ value: 'log₁₀(time)', angle: -90, position: 'insideLeft', offset: 10, fill: '#64748b', fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            wrapperStyle={{ fontSize: '0.8rem', paddingBottom: 10 }}
          />
          {series.map((s) => (
            <Scatter
              key={s.dataKey}
              dataKey={s.dataKey}
              name={`${s.name}${s.slope != null ? ` (slope=${s.slope.toFixed(2)})` : ''}`}
              fill={s.color}
              r={4}
            />
          ))}
          {series.map((s) => (
            s.slope != null && (
              <Line
                key={`line-${s.dataKey}`}
                dataKey={s.dataKey}
                stroke={s.color}
                strokeWidth={1.5}
                strokeDasharray="6 3"
                dot={false}
                name={`fit (${s.name})`}
                legendType="none"
              />
            )
          ))}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
