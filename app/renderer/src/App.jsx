import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { Home, MessageSquare, Mic, Download, FolderOpen, Settings } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Models from './pages/Models';
import Chat from './pages/Chat';
import Voice from './pages/Voice';
import Projects from './pages/Projects';
import SettingsPage from './pages/Settings';
import Sessions from './pages/Sessions';
import { ThemeProvider } from './contexts/ThemeContext';

function App() {
  const [config, setConfig] = useState({ project_name: 'default', active_model_tag: null });
  
  // PERSIST CHAT STATE AT APP LEVEL
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  
  // Load config on mount and poll for updates
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const response = await fetch('http://localhost:5174/api/project/config');
        const data = await response.json();
        setConfig(data);
      } catch (error) {
        // Silent - config will retry
      }
    };
    
    // Load immediately
    loadConfig();
    
    // Poll every 5 seconds to catch model changes
    const interval = setInterval(loadConfig, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/models', icon: Download, label: 'Models' },
    { path: '/chat', icon: MessageSquare, label: 'Chat' },
    { path: '/voice', icon: Mic, label: 'Voice' },
    { path: '/sessions', icon: FolderOpen, label: 'Sessions' },
    { path: '/projects', icon: FolderOpen, label: 'Projects' },
    { path: '/settings', icon: Settings, label: 'Settings' }
  ];

  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="app-container">
          <aside className="sidebar">
            <div className="sidebar-header">
              <h1 className="logo">⚡ AI-Lab</h1>
            </div>
            <nav className="nav-menu">
              {navItems.map(item => (
                <NavLink key={item.path} to={item.path} className="nav-item">
                  <item.icon size={20} />
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>
            <div className="sidebar-footer">
              <div className="config-item">
                <span className="config-label">Project:</span>
                <span className="config-value">{config.project_name}</span>
              </div>
              <div className="config-item">
                <span className="config-label">Model:</span>
                <span className="config-value">{config.active_model_tag || 'None'}</span>
              </div>
            </div>
          </aside>
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/models" element={<Models />} />
              <Route path="/chat" element={
                <Chat 
                  messages={chatMessages} 
                  setMessages={setChatMessages}
                  input={chatInput}
                  setInput={setChatInput}
                />
              } />
              <Route path="/voice" element={<Voice />} />
              <Route path="/sessions" element={<Sessions />} />
              <Route path="/projects" element={<Projects />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
