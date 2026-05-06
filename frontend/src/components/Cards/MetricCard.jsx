import { motion } from 'framer-motion';
import './MetricCard.css';

export default function MetricCard({
  label,
  value,
  icon,
  color = 'blue',
  trend,
  trendLabel,
  context,
  index = 0,
}) {
  const isPositive = typeof value === 'string'
    ? value.startsWith('+') || (!value.startsWith('-') && !value.startsWith('—'))
    : value >= 0;

  return (
    <motion.div
      className={`glass-card metric-card metric-card--${color}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
    >
      <div className="metric-card-header">
        <span className="metric-card-label">{label}</span>
        {icon && (
          <div className={`metric-card-icon metric-card-icon--${color}`}>
            {icon}
          </div>
        )}
      </div>
      <div className={`metric-card-value ${
        color === 'green' || color === 'red'
          ? isPositive ? 'metric-card-value--positive' : 'metric-card-value--negative'
          : 'metric-card-value--neutral'
      }`}>
        {value}
      </div>
      <div className="metric-card-footer">
        {trend != null && (
          <span className={`metric-card-trend ${trend >= 0 ? 'metric-card-trend--up' : 'metric-card-trend--down'}`}>
            {trend >= 0 ? '▲' : '▼'} {trendLabel || `${Math.abs(trend).toFixed(1)}%`}
          </span>
        )}
        {context && <span className="metric-card-context">{context}</span>}
      </div>
    </motion.div>
  );
}
