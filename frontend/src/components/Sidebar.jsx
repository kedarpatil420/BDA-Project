import React from 'react';
import { LayoutDashboard, Cpu, Database, FileText } from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, backendOnline }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'algorithms', label: 'Algorithms', icon: Cpu },
    { id: 'explorer', label: 'Content Explorer', icon: Database },
    { id: 'reports', label: 'Reports & PDF', icon: FileText },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-badge">BIG DATA ANALYTICS</div>
        <div className="brand-title">
          NETFLIX CONTENT ANALYTICS
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon size={18} strokeWidth={2.5} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="server-status">
          <span className={`status-dot ${backendOnline ? '' : 'offline'}`}></span>
          <span>{backendOnline ? 'SYS_STATUS: ONLINE' : 'SYS_STATUS: CONNECTING...'}</span>
        </div>
      </div>
    </aside>
  );
}
