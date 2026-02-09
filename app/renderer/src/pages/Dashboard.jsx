import React, { useState, useEffect } from 'react';
import { Settings, Zap, Cpu, HardDrive, Activity, Archive, MessageSquare, Power, Shield, Clock } from 'lucide-react';
import '../styles/Dashboard.css';

function Dashboard() {
  const [resources, setResources] = useState({cpu: {}, gpu: {}, memory: {}, disk: {}});
  const [settings, setSettings] = useState({
    device: 'cpu',
    cpu_threads: 4,
    memory_limit: 8,
    max_threads: 8,
    total_memory_gb: 16,
    context_size: 4096,
    max_tokens: 0,
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
  const [toolStats, setToolStats] = useState({
    total_executions: 0,
    today: 0,
    success_rate: 0,
    most_used: [],
    by_category: {},
    recent_executions: []
  });
  const [recentSessions, setRecentSessions] = useState([]);
  const [expandedSession, setExpandedSession] = useState(null);

  useEffect(() => {
    loadResources();
    loadSessions();
    loadToolStats();
    
    // Update resources every 3 seconds (reduced from 1s)
    const resourceInterval = setInterval(loadResources, 3000);
    
    // Update sessions every 15 seconds (reduced from 10s)
    const sessionInterval = setInterval(loadSessions, 15000);
    
    // Update tool stats every 30 seconds
    const toolInterval = setInterval(loadToolStats, 30000);
    
    return () => {
      clearInterval(resourceInterval);
      clearInterval(sessionInterval);
      clearInterval(toolInterval);
    };
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

  const loadToolStats = () => {
    try {
      // Load tool execution statistics from localStorage
      const storedStats = localStorage.getItem('toolExecutionStats');
      if (storedStats) {
        const stats = JSON.parse(storedStats);
        
        // Calculate aggregate statistics
        const totalExecutions = stats.executions?.length || 0;
        const today = new Date().toDateString();
        const todayExecutions = stats.executions?.filter(e => 
          new Date(e.timestamp).toDateString() === today
        ).length || 0;
        
        const successCount = stats.executions?.filter(e => e.success).length || 0;
        const successRate = totalExecutions > 0 ? (successCount / totalExecutions * 100).toFixed(1) : 0;
        
        // Count by tool
        const toolCounts = {};
        const categoryCount = {};
        stats.executions?.forEach(exec => {
          toolCounts[exec.tool] = (toolCounts[exec.tool] || 0) + 1;
          categoryCount[exec.category] = (categoryCount[exec.category] || 0) + 1;
        });
        
        // Sort and get top 5
        const mostUsed = Object.entries(toolCounts)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 5)
          .map(([tool, count]) => ({ tool, count }));
        
        setToolStats({
          total_executions: totalExecutions,
          today: todayExecutions,
          success_rate: successRate,
          most_used: mostUsed,
          by_category: categoryCount,
          recent_executions: stats.executions?.slice(-10).reverse() || []
        });
      } else {
        // Initialize empty stats
        setToolStats({
          total_executions: 0,
          today: 0,
          success_rate: 0,
          most_used: [],
          by_category: {},
          recent_executions: []
        });
      }
    } catch (error) {
      console.error('Failed to load tool stats:', error);
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
      console.log(`updateSetting called: ${key} = ${value}`);
      
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
      
      console.log('Sending payload:', payload);
      
      // Don't reload settings immediately - wait for user to finish adjusting
      const response = await fetch('http://localhost:5174/api/resources/configure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const result = await response.json();
      console.log('Response:', result);
      
      if (result.success) {
        console.log(`✅ ${key} updated successfully`);
      } else {
        console.error('Update failed:', result);
      }
    } catch (error) {
      console.error('Error updating setting:', error);
    }
  };

  const saveAllSettings = async () => {
    try {
      console.log('💾 Saving all settings...');
      
      const payload = {
        cpu_threads: parseInt(settings.cpu_threads),
        memory_limit: parseFloat(settings.memory_limit),
        context_size: parseInt(settings.context_size ?? 4096),
        max_tokens: parseInt(settings.max_tokens ?? 0),
        gpu_usage_percent: parseInt(settings.gpu_usage_percent),
        cpu_usage_percent: parseInt(settings.cpu_usage_percent),
        usage_limiter_enabled: settings.usage_limiter_enabled,
        safety_buffer_enabled: settings.safety_buffer_enabled
      };
      
      console.log('Sending payload:', payload);
      
      const response = await fetch('http://localhost:5174/api/resources/configure', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const result = await response.json();
      console.log('Response:', result);
      
      if (result.success) {
        alert('✅ All settings saved successfully!');
      } else {
        alert('❌ Failed to save settings');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      alert(`❌ Error: ${error.message}`);
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
                {resources.gpu?.available && resources.gpu?.devices?.[0] 
                  ? `${resources.gpu.devices[0].usage_percent?.toFixed(1)}%` 
                  : 'N/A'}
              </div>
              {resources.gpu?.available && resources.gpu?.devices?.[0] && (
                <div style={{fontSize: '10px', color: '#666', marginTop: '4px'}}>
                  {resources.gpu.devices[0].name?.substring(0, 20)} • {resources.gpu.devices[0].temperature_c}°C
                </div>
              )}
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
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px'}}>
            <h3 style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
              <Settings size={20} />
              Performance Settings
            </h3>
            <button 
              onClick={saveAllSettings}
              style={{
                padding: '8px 16px',
                backgroundColor: '#00ff88',
                color: '#000',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 'bold'
              }}
            >
              💾 Save All Settings
            </button>
          </div>

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
              <span style={{color: settings.device === 'gpu' ? '#00ff88' : '#4a9eff', fontWeight: 'bold'}}>
                {settings.device === 'gpu' ? (settings.gpu_usage_percent || 90) : (settings.cpu_usage_percent || 95)}%
              </span>
            </h4>
            <input
              type="range"
              min="0"
              max="100"
              step="1"
              value={settings.device === 'gpu' ? (settings.gpu_usage_percent || 90) : (settings.cpu_usage_percent || 95)}
              onChange={(e) => {
                const value = parseInt(e.target.value);
                const key = settings.device === 'gpu' ? 'gpu_usage_percent' : 'cpu_usage_percent';
                console.log(`${settings.device.toUpperCase()} Usage: ${value}%`);
                setSettings(prev => ({...prev, [key]: value}));
                updateSetting(key, value);
              }}
              disabled={!settings.usage_limiter_enabled}
              style={{
                width: '100%',
                height: '8px',
                borderRadius: '4px',
                background: settings.usage_limiter_enabled 
                  ? `linear-gradient(to right, ${settings.device === 'gpu' ? '#00ff88' : '#4a9eff'} 0%, ${settings.device === 'gpu' ? '#00ff88' : '#4a9eff'} ${settings.device === 'gpu' ? (settings.gpu_usage_percent || 90) : (settings.cpu_usage_percent || 95)}%, #2a2a40 ${settings.device === 'gpu' ? (settings.gpu_usage_percent || 90) : (settings.cpu_usage_percent || 95)}%, #2a2a40 100%)`
                  : '#2a2a40',
                outline: 'none',
                cursor: settings.usage_limiter_enabled ? 'pointer' : 'not-allowed',
                opacity: settings.usage_limiter_enabled ? 1 : 0.5,
                WebkitAppearance: 'none',
                appearance: 'none'
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
                onClick={() => {
                  const newValue = !settings.usage_limiter_enabled;
                  console.log(`Toggle Usage Limiter: ${newValue}`);
                  setSettings(prev => ({...prev, usage_limiter_enabled: newValue}));
                  updateSetting('usage_limiter_enabled', newValue);
                }}
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
                onClick={() => {
                  const newValue = !settings.safety_buffer_enabled;
                  console.log(`Toggle Safety Buffer: ${newValue}`);
                  setSettings(prev => ({...prev, safety_buffer_enabled: newValue}));
                  updateSetting('safety_buffer_enabled', newValue);
                }}
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

          {/* Performance Sliders - 2x2 Grid */}
          <div style={{ 
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '12px',
            marginBottom: '20px'
          }}>
            {/* CPU Threads */}
            <div style={{ 
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
                max={settings.max_threads || 8}
                step="1"
                value={settings.cpu_threads || 4}
                onChange={(e) => {
                  const value = parseInt(e.target.value);
                  setSettings(prev => ({...prev, cpu_threads: value}));
                }}
                style={{
                  width: '100%',
                  height: '8px',
                  borderRadius: '4px',
                  background: `linear-gradient(to right, #4a9eff 0%, #6bb8ff ${((settings.cpu_threads || 4) / (settings.max_threads || 8)) * 100}%, #2a2a40 ${((settings.cpu_threads || 4) / (settings.max_threads || 8)) * 100}%, #2a2a40 100%)`,
                  outline: 'none',
                  cursor: 'pointer',
                  WebkitAppearance: 'none',
                  appearance: 'none'
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
                <span>{settings.max_threads || 8}</span>
              </div>
            </div>

            {/* Memory Limit */}
            <div style={{ 
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
                min="1"
                max={Math.floor(settings.total_memory_gb) || 16}
                step="0.5"
                value={settings.memory_limit || 8}
                onChange={(e) => {
                  const value = parseFloat(e.target.value);
                  setSettings(prev => ({...prev, memory_limit: value}));
                }}
                style={{
                  width: '100%',
                  height: '8px',
                  borderRadius: '4px',
                  background: `linear-gradient(to right, #ff6b6b 0%, #ffdd57 ${((settings.memory_limit || 8) / (settings.total_memory_gb || 16)) * 100}%, #2a2a40 ${((settings.memory_limit || 8) / (settings.total_memory_gb || 16)) * 100}%, #2a2a40 100%)`,
                  outline: 'none',
                  cursor: 'pointer',
                  WebkitAppearance: 'none',
                  appearance: 'none'
                }}
              />
              <div style={{
                marginTop: '8px',
                fontSize: '11px',
                color: '#666',
                display: 'flex',
                justifyContent: 'space-between'
              }}>
                <span>1 GB</span>
                <span>{settings.total_memory_gb?.toFixed(1) || 16} GB</span>
              </div>
            </div>

            {/* Context Size */}
            <div style={{ 
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
                <span>📝 Context Size</span>
                <span style={{color: '#a855f7', fontWeight: 'bold'}}>{settings.context_size || 2048}</span>
              </h4>
              <input
                type="range"
                min="512"
                max="8192"
                step="512"
                value={settings.context_size || 2048}
                onChange={(e) => {
                  const value = parseInt(e.target.value);
                  setSettings(prev => ({...prev, context_size: value}));
                }}
                style={{
                  width: '100%',
                  height: '8px',
                  borderRadius: '4px',
                  background: `linear-gradient(to right, #a855f7 0%, #c084fc ${((settings.context_size || 2048) - 512) / (8192 - 512) * 100}%, #2a2a40 ${((settings.context_size || 2048) - 512) / (8192 - 512) * 100}%, #2a2a40 100%)`,
                  outline: 'none',
                  cursor: 'pointer',
                  WebkitAppearance: 'none',
                  appearance: 'none'
                }}
              />
              <div style={{
                marginTop: '8px',
                fontSize: '11px',
                color: '#666',
                display: 'flex',
                justifyContent: 'space-between'
              }}>
                <span>512</span>
                <span>8192</span>
              </div>
            </div>

            {/* Max Tokens */}
            <div style={{ 
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
                <span>✨ Max Tokens</span>
                <span style={{color: '#ec4899', fontWeight: 'bold'}}>
                  {settings.max_tokens === 0 ? '∞' : settings.max_tokens}
                </span>
              </h4>
              <input
                type="range"
                min="0"
                max="4096"
                step="256"
                value={settings.max_tokens ?? 0}
                onChange={(e) => {
                  const value = parseInt(e.target.value);
                  setSettings(prev => ({...prev, max_tokens: value}));
                }}
                style={{
                  width: '100%',
                  height: '8px',
                  borderRadius: '4px',
                  background: `linear-gradient(to right, #ec4899 0%, #f472b6 ${((settings.max_tokens ?? 0) / 4096) * 100}%, #2a2a40 ${((settings.max_tokens ?? 0) / 4096) * 100}%, #2a2a40 100%)`,
                  outline: 'none',
                  cursor: 'pointer',
                  WebkitAppearance: 'none',
                  appearance: 'none'
                }}
              />
              <div style={{
                marginTop: '8px',
                fontSize: '11px',
                color: '#666',
                display: 'flex',
                justifyContent: 'space-between'
              }}>
                <span>0 (Unlimited)</span>
                <span>4096</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tool Statistics Panel */}
        <div className="card" style={{gridColumn: 'span 2'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px'}}>
            <h3 style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
              <Settings size={20} />
              🛠️ Tool Execution Statistics
            </h3>
            <button 
              onClick={loadToolStats}
              style={{
                padding: '6px 12px',
                backgroundColor: '#ffa500',
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

          {/* Tool Stats Overview */}
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '16px'}}>
            <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#888', marginBottom: '4px'}}>
                🛠️ Total Executions
              </div>
              <div style={{fontSize: '24px', fontWeight: 'bold', color: '#ffa500'}}>{toolStats.total_executions}</div>
            </div>
            <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#888', marginBottom: '4px'}}>
                📅 Today
              </div>
              <div style={{fontSize: '24px', fontWeight: 'bold', color: '#4a9eff'}}>{toolStats.today}</div>
            </div>
            <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#888', marginBottom: '4px'}}>
                ✅ Success Rate
              </div>
              <div style={{fontSize: '24px', fontWeight: 'bold', color: '#00ff88'}}>{toolStats.success_rate}%</div>
            </div>
            <div style={{padding: '12px', backgroundColor: '#1a1a2e', borderRadius: '6px', textAlign: 'center'}}>
              <div style={{fontSize: '11px', color: '#888', marginBottom: '4px'}}>
                📊 Categories
              </div>
              <div style={{fontSize: '24px', fontWeight: 'bold', color: '#ff6b6b'}}>{Object.keys(toolStats.by_category).length}</div>
            </div>
          </div>

          {/* Most Used Tools */}
          {toolStats.most_used.length > 0 && (
            <div style={{marginBottom: '16px'}}>
              <h4 style={{fontSize: '14px', color: '#888', marginBottom: '12px'}}>
                🏆 Most Used Tools
              </h4>
              <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '8px'}}>
                {toolStats.most_used.map((item, idx) => (
                  <div key={idx} style={{
                    padding: '10px',
                    backgroundColor: '#0f0f1e',
                    borderRadius: '6px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <span style={{fontSize: '13px', color: '#ccc'}}>{item.tool}</span>
                    <span style={{
                      fontSize: '14px',
                      fontWeight: 'bold',
                      color: idx === 0 ? '#ffa500' : '#4a9eff',
                      padding: '2px 8px',
                      backgroundColor: idx === 0 ? 'rgba(255, 165, 0, 0.2)' : 'rgba(74, 158, 255, 0.2)',
                      borderRadius: '4px'
                    }}>
                      {item.count}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Category Breakdown */}
          {Object.keys(toolStats.by_category).length > 0 && (
            <div style={{marginBottom: '16px'}}>
              <h4 style={{fontSize: '14px', color: '#888', marginBottom: '12px'}}>
                📁 Usage by Category
              </h4>
              <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '8px'}}>
                {Object.entries(toolStats.by_category).map(([category, count]) => (
                  <div key={category} style={{
                    padding: '8px',
                    backgroundColor: '#0f0f1e',
                    borderRadius: '6px',
                    textAlign: 'center'
                  }}>
                    <div style={{fontSize: '12px', color: '#888', marginBottom: '4px'}}>{category}</div>
                    <div style={{fontSize: '18px', fontWeight: 'bold', color: '#4a9eff'}}>{count}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No Data State */}
          {toolStats.total_executions === 0 && (
            <div style={{textAlign: 'center', padding: '40px', color: '#666'}}>
              <div style={{fontSize: '48px', marginBottom: '16px'}}>🛠️</div>
              <div style={{fontSize: '16px', marginBottom: '8px'}}>No tools executed yet</div>
              <div style={{fontSize: '13px', opacity: 0.7}}>
                Enable Commander or Web Search mode and use tools to see statistics here!
              </div>
            </div>
          )}
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
