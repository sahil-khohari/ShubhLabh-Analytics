import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ShoppingCart, Package, Bot, TrendingUp, LineChart, Receipt, LogOut, Settings } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = () => {
  const { logout } = useAuth();
  
  const navLinks = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/sales', icon: ShoppingCart, label: 'Sales' },
    { to: '/inventory', icon: Package, label: 'Inventory' },
    { to: '/expenses', icon: Receipt, label: 'Expenses' },
    { to: '/analytics', icon: LineChart, label: 'Analytics' },
    { to: '/assistant', icon: Bot, label: 'AI Assistant' },
    { to: '/profile', icon: Settings, label: 'Profile' },
  ];

  return (
    <aside className="w-64 h-screen bg-sidebar text-slate-100 flex flex-col fixed left-0 top-0 border-r border-slate-700/50">
      <div className="p-6 border-b border-slate-700/50 flex items-center gap-3">
        <TrendingUp className="text-accent" size={28} />
        <h1 className="text-xl font-bold tracking-wide">ShubhLabh360</h1>
      </div>
      
      <nav className="flex-1 p-4 space-y-2">
        {navLinks.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                isActive 
                  ? 'bg-accent text-sidebar font-bold shadow-md' 
                  : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'
              }`
            }
          >
            <link.icon size={20} />
            <span>{link.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-700/50">
        <button 
          onClick={logout}
          className="flex items-center gap-3 px-4 py-3 w-full text-left rounded-lg text-slate-300 hover:bg-red-500/10 hover:text-red-400 transition-colors"
        >
          <LogOut size={20} />
          <span>Sign Out</span>
        </button>
      </div>
      
      <div className="p-4 text-xs text-slate-500 text-center border-t border-slate-700/50">
        &copy; 2026 ShubhLabh Analytics
      </div>
    </aside>
  );
};

export default Sidebar;
