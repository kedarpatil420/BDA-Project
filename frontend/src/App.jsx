import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Algorithms from './components/Algorithms';
import Explorer from './components/Explorer';
import Reports from './components/Reports';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [backendOnline, setBackendOnline] = useState(false);

  // Ping backend health
  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await fetch('/api/health');
        if (res.ok) {
          setBackendOnline(true);
        } else {
          setBackendOnline(false);
        }
      } catch (err) {
        setBackendOnline(false);
      }
    }

    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-layout">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendOnline={backendOnline}
      />
      <main className="content-area">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'algorithms' && <Algorithms />}
        {activeTab === 'explorer' && <Explorer />}
        {activeTab === 'reports' && <Reports />}
      </main>
    </div>
  );
}
