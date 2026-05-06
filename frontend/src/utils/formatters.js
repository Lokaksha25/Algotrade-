/**
 * AlgoTrade Engine — Formatter Utilities
 */

export const formatCurrency = (value, decimals = 2) => {
  if (value == null || isNaN(value)) return '—';
  const sign = value >= 0 ? '' : '-';
  const abs = Math.abs(value);
  if (abs >= 1_000_000) return `${sign}$${(abs / 1_000_000).toFixed(1)}M`;
  if (abs >= 1_000) return `${sign}$${(abs / 1_000).toFixed(1)}K`;
  return `${sign}$${abs.toFixed(decimals)}`;
};

export const formatPercent = (value, decimals = 2) => {
  if (value == null || isNaN(value)) return '—';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${(value * 100).toFixed(decimals)}%`;
};

export const formatNumber = (value, decimals = 2) => {
  if (value == null || isNaN(value)) return '—';
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

export const formatDate = (dateStr) => {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
};

export const formatCompact = (value) => {
  if (value == null || isNaN(value)) return '—';
  if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
  if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
  if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
  return value.toFixed(1);
};

export const formatDuration = (days) => {
  if (!days) return '—';
  if (days === 1) return '1 day';
  if (days < 30) return `${days} days`;
  if (days < 365) return `${(days / 30).toFixed(1)} mo`;
  return `${(days / 365).toFixed(1)} yr`;
};
