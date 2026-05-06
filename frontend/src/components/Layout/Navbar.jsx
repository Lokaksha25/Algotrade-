import { NavLink } from 'react-router-dom';
import './Navbar.css';

const navItems = [
  { path: '/',           label: 'Dashboard',     icon: '📊' },
  { path: '/algorithms', label: 'Algorithm Lab',  icon: '⚡' },
  { path: '/signals',    label: 'Signals',        icon: '📈' },
  { path: '/portfolio',  label: 'Portfolio',      icon: '💼' },
  { path: '/trades',     label: 'Trades',         icon: '📋' },
];

export default function Navbar() {
  return (
    <nav className="navbar" id="main-navbar">
      <NavLink to="/" className="navbar-brand">
        <div className="navbar-logo">AT</div>
        <div className="navbar-title">
          <span>AlgoTrade</span> Engine
        </div>
      </NavLink>

      <ul className="navbar-nav">
        {navItems.map(({ path, label, icon }) => (
          <li key={path}>
            <NavLink
              to={path}
              end={path === '/'}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              id={`nav-${label.toLowerCase().replace(/\s+/g, '-')}`}
            >
              <span className="nav-icon">{icon}</span>
              {label}
            </NavLink>
          </li>
        ))}
      </ul>

      <div className="navbar-status">
        <div className="status-dot" />
        <span className="status-text">Engine Ready</span>
      </div>
    </nav>
  );
}
