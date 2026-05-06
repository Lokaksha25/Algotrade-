import { motion } from 'framer-motion';

export default function LoadingSpinner({ message = 'Loading...', size = 'md' }) {
  const dims = size === 'sm' ? 32 : size === 'lg' ? 56 : 40;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 16,
        padding: '48px 24px',
        minHeight: 200,
      }}
    >
      <svg width={dims} height={dims} viewBox="0 0 40 40" style={{ animation: 'spin 1s linear infinite' }}>
        <circle cx="20" cy="20" r="16" fill="none" stroke="rgba(59,130,246,0.15)" strokeWidth="3" />
        <circle
          cx="20" cy="20" r="16" fill="none"
          stroke="url(#spinner-gradient)" strokeWidth="3"
          strokeLinecap="round"
          strokeDasharray="70 30"
        />
        <defs>
          <linearGradient id="spinner-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#3b82f6" />
            <stop offset="100%" stopColor="#8b5cf6" />
          </linearGradient>
        </defs>
      </svg>
      <span style={{ fontSize: '0.875rem', color: '#94a3b8', fontWeight: 500 }}>{message}</span>
    </motion.div>
  );
}
