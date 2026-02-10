import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink, useNavigate } from 'react-router-dom';
import { Home, MessageSquare, Mic, Download, FolderOpen, Settings } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Models from './pages/Models';
import Chat from './pages/Chat';
import Voice from './pages/Voice';
import Projects from './pages/Projects';
import SettingsPage from './pages/Settings';
import Sessions from './pages/Sessions';
import { ThemeProvider } from './contexts/ThemeContext';
import CommandPalette from './components/ui/CommandPalette';
import ShortcutHelp from './components/ui/ShortcutHelp';
import useGlobalShortcuts from './hooks/useGlobalShortcuts';

function AppContent() {
  const navigate = useNavigate();
  const [config, setConfig] = useState({ project_name: 'default', active_model_tag: null });
  
  // PERSIST CHAT STATE AT APP LEVEL
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  
  // UI state for modals
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [showShortcutHelp, setShowShortcutHelp] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  
  // Global keyboard shortcuts
  useGlobalShortcuts({
    openCommandPalette: () => setShowCommandPalette(true),
    showShortcuts: () => setShowShortcutHelp(true),
    newChat: () => {
      setChatMessages([]);
      navigate('/chat');
    },
    saveSession: () => {
      // TODO: Implement save session
      console.log('Save session triggered');
    },
    toggleSidebar: () => setSidebarCollapsed(prev => !prev),
    openSettings: () => navigate('/settings'),
    toggleCommander: () => {
      // TODO: Implement commander mode toggle
      console.log('Toggle commander mode');
    },
    toggleWebSearch: () => {
      // TODO: Implement web search toggle
      console.log('Toggle web search');
    },
    createBranch: () => {
      // TODO: Implement branch creation
      console.log('Create branch');
    },
    createArtifact: () => {
      // TODO: Implement artifact creation
      console.log('Create artifact');
    }
  });
  
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

  
  // Execute command from command palette
  const executeCommand = (commandId) => {
    switch (commandId) {
      case 'newChat':
        setChatMessages([]);
        navigate('/chat');
        break;
      case 'openSession':
        navigate('/sessions');
        break;
      case 'saveSession':
        console.log('Save session');
        break;
      case 'openSettings':
        navigate('/settings');
        break;
      case 'toggleTheme':
        // Theme toggling not yet implemented - user can change in Settings
        console.log('Toggle theme command is not yet implemented');
        break;
      case 'toggleCommander':
        console.log('Toggle commander');
        break;
      case 'toggleWebSearch':
        console.log('Toggle web search');
        break;
      default:
        console.log('Unknown command:', commandId);
    }
  };

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
    <>
      <div className="app-container">
        <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
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
      
      {/* Global Modals */}
      <CommandPalette
        isOpen={showCommandPalette}
        onClose={() => setShowCommandPalette(false)}
        onExecuteCommand={executeCommand}
      />
      <ShortcutHelp
        isOpen={showShortcutHelp}
        onClose={() => setShowShortcutHelp(false)}
      />
    </>
  );
}

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
