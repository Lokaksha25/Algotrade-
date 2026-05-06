import { motion } from 'framer-motion';
import './AlgorithmCard.css';

export default function AlgorithmCard({ algo, selected, onClick, index = 0 }) {
  return (
    <motion.div
      className={`glass-card algo-card ${selected ? 'selected' : ''}`}
      onClick={onClick}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.35 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="algo-card-header">
        <div className="algo-card-dot" style={{ background: algo.color }} />
        <span className="algo-card-name">{algo.name}</span>
        <span className={`badge badge-${
          algo.module === 'Data Layer' ? 'blue'
          : algo.module === 'Signal Engine' ? 'green'
          : algo.module === 'Portfolio' ? 'purple'
          : algo.module === 'Execution' ? 'amber'
          : 'blue'
        } algo-card-paradigm`}>
          {algo.paradigm}
        </span>
      </div>
      <p className="algo-card-description">{algo.description}</p>
      <div className="algo-card-complexity">
        <div className="complexity-item">
          <span className="complexity-label">Brute-Force</span>
          <span className="complexity-value complexity-value--brute">{algo.brute}</span>
        </div>
        <div className="complexity-item">
          <span className="complexity-label">Optimized</span>
          <span className="complexity-value complexity-value--optimized">{algo.optimized}</span>
        </div>
      </div>
    </motion.div>
  );
}
