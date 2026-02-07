import React, { useState, useEffect } from 'react';
import { Activity, Zap, MessageSquare, Clock, Archive } from 'lucide-react';

function Dashboard() {
  const [models, setModels] = useState([]);
  const [config, setConfig] = useState({});
  const [sessions, setSessions] = useState([]);
  const [sessionStats, setSessionStats] = useState({ total: 0, messages: 0 });

  useEffect(() => {
    loadData();
    loadSessions();
  }, []);

  const loadData = async () => {
    const isElectron = !!window.electron?.models;
    
    if (isElectron) {
      window.electron.models.list().then(setModels);
      window.electron.project.getConfig().then(setConfig);
    } else {
      // Browser mode - use HTTP API
      try {
        const modelsResponse = await fetch('http://localhost:5174/api/models');
        const modelsData = await modelsResponse.json();
        setModels(modelsData);
        
        const configResponse = await fetch('http://localhost:5174/api/project/config');
        const configData = await configResponse.json();
        setConfig({
          project_name: configData.project_name,
          active_model_tag: configData.active_model
        });
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      }
    }
  };

  const loadSessions = async () => {
    try {
      const response = await fetch('http://localhost:5174/api/sessions/list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await response.json();
      const sessionList = data.sessions || [];
      setSessions(sessionList.slice(0, 5)); // Show last 5
      
      const totalMessages = sessionList.reduce((sum, s) => sum + s.message_count, 0);
      setSessionStats({
        total: sessionList.length,
        messages: totalMessages
      });
    } catch (err) {
      console.error('Failed to load sessions:', err);
    }
  };

  const viewSession = async (sessionId) => {
    try {
      const response = await fetch('http://localhost:5174/api/sessions/load', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
      const session = await response.json();
      alert(`Session: ${session.session_id}\nMessages: ${session.messages.length}\n\nView full conversation in Sessions page!`);
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  };

  const exportAllSessions = async () => {
    try {
      const response = await fetch('http://localhost:5174/api/sessions/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format: 'jsonl' })
      });
      const result = await response.json();
      alert(`✅ All sessions exported for training!\n\nPath: ${result.export_path}`);
    } catch (err) {
      alert(`❌ Export failed: ${err.message}`);
    }
  };

  return (
    <div>
      <h1 className="page-title">Dashboard</h1>
      <p className="page-description">Welcome to NovaForge AI Lab</p>

      <div className="card">
        <h2 style={{marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px'}}>
          <Zap size={24} />
          Quick Status
        </h2>
        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px'}}>
          <div>
            <div className="config-label">Active Project</div>
            <div className="config-value" style={{fontSize: '18px'}}>{config.project_name || 'default'}</div>
          </div>
          <div>
            <div className="config-label">Active Model</div>
            <div className="config-value" style={{fontSize: '18px'}}>{config.active_model_tag || 'None selected'}</div>
          </div>
          <div>
            <div className="config-label">Downloaded Models</div>
            <div className="config-value" style={{fontSize: '18px'}}>{models.length}</div>
          </div>
          <div>
            <div className="config-label">Status</div>
            <div className="config-value" style={{fontSize: '18px', color: config.active_model_tag ? '#10b981' : '#f59e0b'}}>
              <Activity size={16} style={{display: 'inline', marginRight: '4px'}} />
              {config.active_model_tag ? 'Ready' : 'No Model Selected'}
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 style={{marginBottom: '16px'}}>Getting Started</h3>
        <ul style={{lineHeight: '1.8', color: 'var(--text-secondary)'}}>
          <li>📥 <strong>Models</strong> - Download Ollama models to get started</li>
          <li>💬 <strong>Chat</strong> - Have text conversations with AI</li>
          <li>🎙️ <strong>Voice</strong> - Hands-free AI assistant (native audio!)</li>
          <li>📁 <strong>Projects</strong> - Organize your AI workspaces</li>
        </ul>
      </div>

      {/* Sessions Panel */}
      <div className="card">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px'}}>
          <h3 style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
            <MessageSquare size={20} />
            Recent Sessions
          </h3>
          <button 
            onClick={exportAllSessions}
            style={{
              padding: '6px 12px',
              backgroundColor: '#4CAF50',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            📦 Export All
          </button>
        </div>

        <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px'}}>
          <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px'}}>
            <div style={{fontSize: '12px', color: '#888', marginBottom: '4px'}}>
              <Archive size={14} style={{display: 'inline', marginRight: '4px'}} />
              Total Sessions
            </div>
            <div style={{fontSize: '24px', fontWeight: 'bold', color: '#4a9eff'}}>{sessionStats.total}</div>
          </div>
          <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px'}}>
            <div style={{fontSize: '12px', color: '#888', marginBottom: '4px'}}>
              <MessageSquare size={14} style={{display: 'inline', marginRight: '4px'}} />
              Total Messages
            </div>
            <div style={{fontSize: '24px', fontWeight: 'bold', color: '#00d9ff'}}>{sessionStats.messages}</div>
          </div>
        </div>

        {sessions.length === 0 ? (
          <div style={{textAlign: 'center', padding: '20px', color: '#666'}}>
            No sessions yet. Start chatting to create your first session!
          </div>
        ) : (
          <div style={{maxHeight: '300px', overflowY: 'auto'}}>
            {sessions.map((session) => (
              <div
                key={session.session_id}
                onClick={() => viewSession(session.session_id)}
                style={{
                  padding: '12px',
                  marginBottom: '8px',
                  backgroundColor: '#0f3460',
                  borderRadius: '6px',
                  borderLeft: '4px solid #4a9eff',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#1a4d7a'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#0f3460'}
              >
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: '6px'}}>
                  <span style={{fontSize: '12px', fontWeight: 'bold', color: '#4a9eff'}}>
                    👤 {session.user_name}
                  </span>
                  <span style={{fontSize: '11px', color: '#888'}}>
                    <Clock size={12} style={{display: 'inline', marginRight: '4px'}} />
                    {new Date(session.started_at).toLocaleString()}
                  </span>
                </div>
                <div style={{fontSize: '11px', color: '#aaa'}}>
                  💬 {session.message_count} messages
                </div>
              </div>
            ))}
          </div>
        )}

        <div style={{marginTop: '12px', textAlign: 'center'}}>
          <a 
            href="/sessions.html" 
            target="_blank"
            style={{color: '#4a9eff', textDecoration: 'none', fontSize: '12px'}}
          >
            View All Sessions →
          </a>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
