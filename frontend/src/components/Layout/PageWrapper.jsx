import { motion } from 'framer-motion';

const pageVariants = {
  initial:  { opacity: 0, y: 16 },
  animate:  { opacity: 1, y: 0 },
  exit:     { opacity: 0, y: -12 },
};

const pageTransition = {
  type: 'tween',
  ease: [0.4, 0, 0.2, 1],
  duration: 0.35,
};

export default function PageWrapper({ children }) {
  return (
    <motion.div
      className="page"
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={pageTransition}
    >
      {children}
    </motion.div>
  );
}
