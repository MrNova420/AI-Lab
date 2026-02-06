import React, { useState, useEffect } from 'react';
import { Activity, Zap } from 'lucide-react';

function Dashboard() {
  const [models, setModels] = useState([]);
  const [config, setConfig] = useState({});

  useEffect(() => {
    loadData();
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
    </div>
  );
}

export default Dashboard;
