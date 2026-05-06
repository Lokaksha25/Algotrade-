import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import Navbar from './components/Layout/Navbar';
import Dashboard from './pages/Dashboard/Dashboard';
import AlgorithmLab from './pages/AlgorithmLab/AlgorithmLab';
import SignalExplorer from './pages/SignalExplorer/SignalExplorer';
import PortfolioAnalysis from './pages/PortfolioAnalysis/PortfolioAnalysis';
import TradeHistory from './pages/TradeHistory/TradeHistory';

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/algorithms" element={<AlgorithmLab />} />
          <Route path="/signals" element={<SignalExplorer />} />
          <Route path="/portfolio" element={<PortfolioAnalysis />} />
          <Route path="/trades" element={<TradeHistory />} />
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  );
}
