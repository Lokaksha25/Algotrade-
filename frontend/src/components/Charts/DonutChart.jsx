import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { CHART_COLORS } from '../../utils/constants';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const { name, value, percent } = payload[0].payload;
  return (
    <div style={{
      background: 'rgba(17,24,39,0.95)',
      border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: '8px',
      padding: '10px 14px',
      fontSize: '0.8rem',
      color: '#f1f5f9',
    }}>
      <div style={{ fontWeight: 600 }}>{name}</div>
      <div style={{ color: '#94a3b8' }}>
        ${value?.toLocaleString()} ({(percent * 100).toFixed(1)}%)
      </div>
    </div>
  );
};

export default function DonutChart({ data, height = 280, centerLabel, centerValue }) {
  if (!data?.length) return null;

  return (
    <div style={{ position: 'relative' }}>
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius="55%"
            outerRadius="80%"
            paddingAngle={3}
            dataKey="value"
            stroke="none"
          >
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.color || CHART_COLORS[i % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
      {(centerLabel || centerValue) && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
          pointerEvents: 'none',
        }}>
          {centerValue && (
            <div style={{ fontSize: '1.375rem', fontWeight: 800, color: '#f1f5f9' }}>
              {centerValue}
            </div>
          )}
          {centerLabel && (
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: 2 }}>
              {centerLabel}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
