import React, { useState, useEffect } from 'react';
import { Settings, Zap, Cpu, HardDrive, Activity, Archive, MessageSquare, Power, Shield } from 'lucide-react';
import '../styles/Dashboard.css';

function Dashboard() {
  const [resources, setResources] = useState({cpu: {}, gpu: {}, memory: {}, disk: {}});
  const [settings, setSettings] = useState({
    device: 'cpu',
    cpu_threads: 4,
    memory_limit: 8,
    max_threads: 8,
    total_memory_gb: 16,
    // NEW: Usage controls
    gpu_usage_percent: 100,
    cpu_usage_percent: 100,
    usage_limiter_enabled: false,
    safety_buffer_enabled: true,
    actual_gpu_usage: 90,
    actual_cpu_usage: 95
  });
  const [sessionStats, setSessionStats] = useState({
    total: 0,
    today: 0,
    this_week: 0,
    total_messages: 0
  });
  const [recentSessions, setRecentSessions] = useState([]);
  const [expandedSession, setExpandedSession] = useState(null);

  useEffect(() => {
    loadResources();
    loadSessions();
    
    // Update resources every 1 second for better accuracy
    const interval = setInterval(loadResources, 1000);
    return () => clearInterval(interval);
  }, []);

  const loadResources = async () => {
    try {
      // Load resource stats
      const statsResponse = await fetch('http://localhost:5174/api/resources/stats');
      const statsData = await statsResponse.json();
      setResources(statsData);
      
      // Load settings including usage limits
      const settingsResponse = await fetch('http://localhost:5174/api/resources/settings');
      const settingsData = await settingsResponse.json();
      setSettings(prev => ({...prev, ...settingsData}));
    } catch (error) {
      // Silent fail - don't spam console
    }
  };

  const loadSessions = async () => {
    try {
      const response = await fetch('http://localhost:5174/api/sessions/list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await response.json();
      
      if (data.sessions) {
        setRecentSessions(data.sessions.slice(0, 10)); // Show last 10
        setSessionStats({
          total: data.total_sessions || 0,
          today: data.sessions_today || 0,
          this_week: data.sessions_this_week || 0,
          total_messages: data.total_messages || 0
        });
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    }
  };

  const switchDevice = async (device) => {
    try {
      console.log(`🔄 Switching to ${device}...`);
      
      const response = await fetch('http://localhost:5174/api/resources/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          device: device,
          num_gpu: device === 'gpu' ? 1 : 0 
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        console.log('✅ Device switched successfully');
        alert(`✅ Switched to ${device.toUpperCase()}\n\nAll future AI responses will use ${device.toUpperCase()}.`);
        loadResources();
      } else {
        alert(`❌ Failed to switch to ${device.toUpperCase()}`);
      }
    } catch (error) {
      console.error('Error switching device:', error);
      alert(`❌ Error: ${error.message}`);
    }
  };

  const updateSetting = async (key, value) => {
    try {
      const payload = {};
      
      if (key === 'cpu_threads') {
        payload.cpu_threads = parseInt(value);
      } else if (key === 'memory_limit') {
        payload.memory_limit = parseFloat(value);
      } else if (key === 'gpu_usage_percent') {
        payload.gpu_usage_percent = parseInt(value);
      } else if (key === 'cpu_usage_percent') {
        payload.cpu_usage_percent = parseInt(value);
      } else if (key === 'usage_limiter_enabled') {
        payload.usage_limiter_enabled = value;
      } else if (key === 'safety_buffer_enabled') {
        payload.safety_buffer_enabled = value;
      }
      
      const response = await fetch('http://localhost:5174/api/resources/configure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const result = await response.json();
      
      if (result.success) {
        console.log(`✅ ${key} updated successfully`);
        setSettings(prev => ({...prev, [key]: value}));
        
        // Reload to get actual values with buffer applied
        setTimeout(loadResources, 500);
      }
    } catch (error) {
      console.error('Error updating setting:', error);
    }
  };

  const toggleSession = (sessionId) => {
    setExpandedSession(expandedSession === sessionId ? null : sessionId);
  };

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">System overview and controls</p>
      </div>

      <div className="dashboard-grid">
        {/* Resource Stats */}
        <div className="card">
          <h3 style={{marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px'}}>
            <Activity size={20} />
            Live Resource Stats
          </h3>
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px'}}>
            <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#888', marginBottom: '6px'}}>
                <Cpu size={14} style={{display: 'inline', marginRight: '4px'}} />
                CPU
              </div>
              <div style={{fontSize: '24px', fontWeight: 'bold', color: '#4a9eff'}}>
                {resources.cpu?.usage_percent?.toFixed(1) || '0'}%
              </div>
            </div>
            <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#888', marginBottom: '6px'}}>
                <Zap size={14} style={{display: 'inline', marginRight: '4px'}} />
                GPU
              </div>
              <div style={{fontSize: '24px', fontWeight: 'bold', color: '#00ff88'}}>
                {resources.gpu?.available ? `${resources.gpu?.usage_percent?.toFixed(1)}%` : 'N/A'}
              </div>
            </div>
            <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#888', marginBottom: '6px'}}>
                <HardDrive size={14} style={{display: 'inline', marginRight: '4px'}} />
                Memory
              </div>
              <div style={{fontSize: '24px', fontWeight: 'bold', color: '#ff9500'}}>
                {resources.memory?.percent?.toFixed(1) || '0'}%
              </div>
            </div>
            <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#888', marginBottom: '6px'}}>
                <HardDrive size={14} style={{display: 'inline', marginRight: '4px'}} />
                Disk
              </div>
              <div style={{fontSize: '24px', fontWeight: 'bold', color: '#ff4444'}}>
                {resources.disk?.percent?.toFixed(1) || '0'}%
              </div>
            </div>
          </div>
        </div>

        {/* Performance Controls */}
        <div className="card">
          <h3 style={{marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px'}}>
            <Settings size={20} />
            Performance Controls
          </h3>

          {/* Device Selection */}
          <div style={{ 
            marginBottom: '20px',
            padding: '15px',
            backgroundColor: '#1a1a2e',
            borderRadius: '8px'
          }}>
            <h4 style={{ 
              fontSize: '14px', 
              marginBottom: '12px',
              color: '#888',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <Power size={16} />
              Device Selection
            </h4>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={() => switchDevice('cpu')}
                style={{
                  flex: 1,
                  padding: '12px',
                  backgroundColor: settings.device === 'cpu' ? '#4a9eff' : '#2a2a40',
                  color: 'white',
                  border: settings.device === 'cpu' ? '2px solid #4a9eff' : '2px solid transparent',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  transition: 'all 0.2s'
                }}
              >
                🖥️ CPU {settings.device === 'cpu' && '✓'}
              </button>
              <button
                onClick={() => switchDevice('gpu')}
                style={{
                  flex: 1,
                  padding: '12px',
                  backgroundColor: settings.device === 'gpu' ? '#00ff88' : '#2a2a40',
                  color: settings.device === 'gpu' ? '#000' : 'white',
                  border: settings.device === 'gpu' ? '2px solid #00ff88' : '2px solid transparent',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  transition: 'all 0.2s'
                }}
              >
                🎮 GPU {settings.device === 'gpu' && '✓'}
              </button>
            </div>
            <div style={{
              marginTop: '10px',
              padding: '8px',
              backgroundColor: '#0f0f1e',
              borderRadius: '4px',
              fontSize: '12px',
              color: '#888',
              textAlign: 'center'
            }}>
              Current Device: <strong style={{ color: settings.device === 'gpu' ? '#00ff88' : '#4a9eff' }}>
                {settings.device?.toUpperCase() || 'CPU'}
              </strong>
            </div>
          </div>

          {/* NEW: GPU/CPU Usage Percentage Slider */}
          <div style={{ 
            marginBottom: '20px',
            padding: '15px',
            backgroundColor: '#1a1a2e',
            borderRadius: '8px'
          }}>
            <h4 style={{ 
              fontSize: '14px', 
              marginBottom: '8px',
              color: '#888',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <span>
                {settings.device === 'gpu' ? '🎮' : '🖥️'} {settings.device?.toUpperCase()} Usage Limit
              </span>
              <span style={{color: '#4a9eff', fontWeight: 'bold'}}>
                {settings.device === 'gpu' ? settings.gpu_usage_percent : settings.cpu_usage_percent}%
              </span>
            </h4>
            <input
              type="range"
              min="0"
              max="100"
              value={settings.device === 'gpu' ? settings.gpu_usage_percent : settings.cpu_usage_percent}
              onChange={(e) => updateSetting(
                settings.device === 'gpu' ? 'gpu_usage_percent' : 'cpu_usage_percent', 
                e.target.value
              )}
              disabled={!settings.usage_limiter_enabled}
              style={{
                width: '100%',
                height: '6px',
                borderRadius: '3px',
                background: settings.usage_limiter_enabled 
                  ? `linear-gradient(to right, ${settings.device === 'gpu' ? '#00ff88' : '#4a9eff'} 0%, ${settings.device === 'gpu' ? '#00ff88' : '#4a9eff'} ${settings.device === 'gpu' ? settings.gpu_usage_percent : settings.cpu_usage_percent}%, #2a2a40 ${settings.device === 'gpu' ? settings.gpu_usage_percent : settings.cpu_usage_percent}%, #2a2a40 100%)`
                  : '#2a2a40',
                outline: 'none',
                cursor: settings.usage_limiter_enabled ? 'pointer' : 'not-allowed',
                opacity: settings.usage_limiter_enabled ? 1 : 0.5
              }}
            />
            <div style={{
              marginTop: '8px',
              fontSize: '11px',
              color: '#666',
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <span>0%</span>
              <span>100%</span>
            </div>
            {settings.safety_buffer_enabled && settings.usage_limiter_enabled && (
              <div style={{
                marginTop: '8px',
                padding: '6px',
                backgroundColor: '#0f0f1e',
                borderRadius: '4px',
                fontSize: '11px',
                color: '#888',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <Shield size={12} />
                Actual usage: <strong style={{color: '#00ff88'}}>
                  {settings.device === 'gpu' ? settings.actual_gpu_usage : settings.actual_cpu_usage}%
                </strong>
                <span style={{color: '#666'}}>
                  ({settings.device === 'gpu' ? settings.gpu_safety_buffer : settings.cpu_safety_buffer}% reserved for system)
                </span>
              </div>
            )}
          </div>

          {/* NEW: Toggle Buttons */}
          <div style={{ 
            marginBottom: '20px',
            padding: '15px',
            backgroundColor: '#1a1a2e',
            borderRadius: '8px'
          }}>
            <h4 style={{ 
              fontSize: '14px', 
              marginBottom: '12px',
              color: '#888'
            }}>
              Safety & Limits
            </h4>
            <div style={{display: 'flex', flexDirection: 'column', gap: '10px'}}>
              <button
                onClick={() => updateSetting('usage_limiter_enabled', !settings.usage_limiter_enabled)}
                style={{
                  padding: '10px',
                  backgroundColor: settings.usage_limiter_enabled ? '#00ff88' : '#2a2a40',
                  color: settings.usage_limiter_enabled ? '#000' : 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <span>Usage Limiter</span>
                <span>{settings.usage_limiter_enabled ? '✓ ON' : '✗ OFF'}</span>
              </button>
              <button
                onClick={() => updateSetting('safety_buffer_enabled', !settings.safety_buffer_enabled)}
                style={{
                  padding: '10px',
                  backgroundColor: settings.safety_buffer_enabled ? '#4a9eff' : '#2a2a40',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: 'bold',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <span style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
                  <Shield size={14} />
                  Safety Buffer
                </span>
                <span>{settings.safety_buffer_enabled ? '✓ ON' : '✗ OFF'}</span>
              </button>
            </div>
          </div>

          {/* CPU Threads */}
          <div style={{ 
            marginBottom: '20px',
            padding: '15px',
            backgroundColor: '#1a1a2e',
            borderRadius: '8px'
          }}>
            <h4 style={{ 
              fontSize: '14px', 
              marginBottom: '12px',
              color: '#888',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <span>🔧 CPU Threads</span>
              <span style={{color: '#4a9eff', fontWeight: 'bold'}}>{settings.cpu_threads || 4}</span>
            </h4>
            <input
              type="range"
              min="1"
              max="16"
              value={settings.cpu_threads || 4}
              onChange={(e) => updateSetting('cpu_threads', e.target.value)}
              style={{
                width: '100%',
                height: '6px',
                borderRadius: '3px',
                background: `linear-gradient(to right, #4a9eff 0%, #4a9eff ${(settings.cpu_threads || 4) * 6.25}%, #2a2a40 ${(settings.cpu_threads || 4) * 6.25}%, #2a2a40 100%)`,
                outline: 'none',
                cursor: 'pointer'
              }}
            />
            <div style={{
              marginTop: '8px',
              fontSize: '11px',
              color: '#666',
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <span>1</span>
              <span>16</span>
            </div>
          </div>

          {/* Memory Limit */}
          <div style={{ 
            marginBottom: '20px',
            padding: '15px',
            backgroundColor: '#1a1a2e',
            borderRadius: '8px'
          }}>
            <h4 style={{ 
              fontSize: '14px', 
              marginBottom: '12px',
              color: '#888',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <span>💾 Memory Limit</span>
              <span style={{color: '#ff6b6b', fontWeight: 'bold'}}>{settings.memory_limit || 8} GB</span>
            </h4>
            <input
              type="range"
              min="2"
              max="32"
              step="0.5"
              value={settings.memory_limit || 8}
              onChange={(e) => updateSetting('memory_limit', e.target.value)}
              style={{
                width: '100%',
                height: '6px',
                borderRadius: '3px',
                background: `linear-gradient(to right, #ff6b6b 0%, #ff6b6b ${((settings.memory_limit || 8) - 2) * 3.33}%, #2a2a40 ${((settings.memory_limit || 8) - 2) * 3.33}%, #2a2a40 100%)`,
                outline: 'none',
                cursor: 'pointer'
              }}
            />
            <div style={{
              marginTop: '8px',
              fontSize: '11px',
              color: '#666',
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <span>2 GB</span>
              <span>32 GB</span>
            </div>
          </div>
        </div>

        {/* Sessions Panel - NOW INTEGRATED */}
        <div className="card" style={{gridColumn: 'span 2'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px'}}>
            <h3 style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
              <MessageSquare size={20} />
              Recent Chat Sessions
            </h3>
            <button 
              onClick={loadSessions}
              style={{
                padding: '6px 12px',
                backgroundColor: '#4a9eff',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              🔄 Refresh
            </button>
          </div>

          {/* Session Stats */}
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px'}}>
            <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#888', marginBottom: '4px'}}>
                <Archive size={14} style={{display: 'inline', marginRight: '4px'}} />
                Total
              </div>
              <div style={{fontSize: '24px', fontWeight: 'bold', color: '#4a9eff'}}>{sessionStats.total}</div>
            </div>
            <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#888', marginBottom: '4px'}}>
                <Clock size={14} style={{display: 'inline', marginRight: '4px'}} />
                Today
              </div>
              <div style={{fontSize: '24px', fontWeight: 'bold', color: '#00ff88'}}>{sessionStats.today}</div>
            </div>
            <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#888', marginBottom: '4px'}}>
                <Activity size={14} style={{display: 'inline', marginRight: '4px'}} />
                This Week
              </div>
              <div style={{fontSize: '24px', fontWeight: 'bold', color: '#ff9500'}}>{sessionStats.this_week}</div>
            </div>
            <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#888', marginBottom: '4px'}}>
                <MessageSquare size={14} style={{display: 'inline', marginRight: '4px'}} />
                Messages
              </div>
              <div style={{fontSize: '24px', fontWeight: 'bold', color: '#ff6b6b'}}>{sessionStats.total_messages}</div>
            </div>
          </div>

          {/* Recent Sessions List */}
          <div style={{maxHeight: '400px', overflowY: 'auto'}}>
            {recentSessions.length > 0 ? (
              recentSessions.map((session) => (
                <div 
                  key={session.session_id}
                  style={{
                    padding: '12px',
                    backgroundColor: expandedSession === session.session_id ? '#1a1a2e' : '#0f0f1e',
                    borderRadius: '6px',
                    marginBottom: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onClick={() => toggleSession(session.session_id)}
                >
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                    <div>
                      <div style={{fontSize: '14px', fontWeight: 'bold', color: '#4a9eff'}}>
                        Session {session.session_id.substring(0, 8)}
                      </div>
                      <div style={{fontSize: '12px', color: '#888', marginTop: '4px'}}>
                        {new Date(session.started_at).toLocaleString()} • {session.total_messages} messages
                      </div>
                    </div>
                    <div style={{fontSize: '18px', color: '#666'}}>
                      {expandedSession === session.session_id ? '▼' : '▶'}
                    </div>
                  </div>
                  
                  {expandedSession === session.session_id && (
                    <div style={{
                      marginTop: '12px',
                      paddingTop: '12px',
                      borderTop: '1px solid #2a2a40'
                    }}>
                      <div style={{fontSize: '12px', color: '#888', marginBottom: '8px'}}>
                        User: {session.user_name || 'Unknown'}
                      </div>
                      {session.messages && session.messages.slice(0, 3).map((msg, idx) => (
                        <div key={idx} style={{
                          padding: '8px',
                          backgroundColor: '#0a0a1e',
                          borderRadius: '4px',
                          marginBottom: '6px',
                          fontSize: '12px'
                        }}>
                          <div style={{color: msg.role === 'user' ? '#4a9eff' : '#00ff88', fontWeight: 'bold', marginBottom: '4px'}}>
                            {msg.role === 'user' ? '👤 You' : '🤖 AI'}
                          </div>
                          <div style={{color: '#ccc'}}>
                            {msg.content.substring(0, 100)}{msg.content.length > 100 ? '...' : ''}
                          </div>
                        </div>
                      ))}
                      {session.messages && session.messages.length > 3 && (
                        <div style={{fontSize: '11px', color: '#666', marginTop: '8px'}}>
                          ... and {session.messages.length - 3} more messages
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div style={{textAlign: 'center', padding: '40px', color: '#666'}}>
                No sessions yet. Start chatting to create sessions!
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
