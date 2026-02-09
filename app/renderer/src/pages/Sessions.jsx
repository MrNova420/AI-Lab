import React, { useState, useEffect } from 'react';
import sessionManager from '../utils/sessionManager';

function Sessions() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all'); // 'all', 'chat', 'voice'

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await sessionManager.listSessions(200, 0);
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewSession = async (sessionId) => {
    try {
      const session = await sessionManager.loadSession(sessionId);
      setSelectedSession(session);
    } catch (error) {
      console.error('Failed to load session:', error);
      alert('Failed to load session details');
    }
  };

  const deleteSession = async (sessionId) => {
    if (!confirm('Are you sure you want to delete this session?')) {
      return;
    }
    
    try {
      await sessionManager.deleteSession(sessionId);
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));
      if (selectedSession && selectedSession.session_id === sessionId) {
        setSelectedSession(null);
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
      alert('Failed to delete session');
    }
  };

  const exportSession = async (sessionId) => {
    try {
      const session = sessions.find(s => s.session_id === sessionId) || selectedSession;
      if (!session && !selectedSession) {
        const loaded = await sessionManager.loadSession(sessionId);
        downloadSessionJSON(loaded);
      } else {
        if (selectedSession && selectedSession.session_id === sessionId) {
          downloadSessionJSON(selectedSession);
        } else {
          const loaded = await sessionManager.loadSession(sessionId);
          downloadSessionJSON(loaded);
        }
      }
    } catch (error) {
      console.error('Failed to export session:', error);
      alert('Failed to export session');
    }
  };

  const downloadSessionJSON = (session) => {
    // Enhanced export with full tool information
    const exportData = {
      session_id: session.session_id,
      user_name: session.user_name,
      started_at: session.started_at,
      last_updated: session.last_updated,
      metadata: session.metadata,
      stats: session.stats,
      messages: session.messages.map(msg => ({
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp,
        metadata: msg.metadata,
        // Extract tool information if present
        tools_used: extractToolsFromMessage(msg),
        modes: msg.metadata?.modes || {},
        has_tools: msg.metadata?.hasTools || false
      }))
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `session_${session.session_id}_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    console.log(`📥 Exported session: ${session.session_id}`);
  };

  const extractToolsFromMessage = (msg) => {
    if (msg.role !== 'assistant' || !msg.content) return [];
    
    const tools = [];
    const toolPattern = /🛠️\s*(\w+)(?:\(([^)]*)\))?/g;
    let match;
    
    while ((match = toolPattern.exec(msg.content)) !== null) {
      tools.push({
        name: match[1],
        params: match[2] || '',
        context: msg.content.substring(Math.max(0, match.index - 50), Math.min(msg.content.length, match.index + 100))
      });
    }
    
    return tools;
  };

  const exportAllSessions = async () => {
    try {
      const allData = {
        exported_at: new Date().toISOString(),
        total_sessions: sessions.length,
        sessions: []
      };

      // Load full data for each session
      for (const session of sessions.slice(0, 50)) { // Limit to 50 for performance
        try {
          const fullSession = await sessionManager.loadSession(session.session_id);
          allData.sessions.push({
            session_id: fullSession.session_id,
            user_name: fullSession.user_name,
            started_at: fullSession.started_at,
            stats: fullSession.stats,
            messages: fullSession.messages.map(msg => ({
              role: msg.role,
              content: msg.content,
              timestamp: msg.timestamp,
              tools_used: extractToolsFromMessage(msg),
              modes: msg.metadata?.modes || {}
            }))
          });
        } catch (error) {
          console.error(`Failed to load session ${session.session_id}:`, error);
        }
      }

      const blob = new Blob([JSON.stringify(allData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `all_sessions_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      alert(`Exported ${allData.sessions.length} sessions`);
    } catch (error) {
      console.error('Failed to export all sessions:', error);
      alert('Failed to export sessions');
    }
  };

  const filteredSessions = sessions.filter(session => {
    const matchesSearch = !searchTerm || 
      session.session_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      session.preview?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      session.user_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = filterType === 'all' || 
      session.metadata?.type === filterType ||
      (!session.metadata?.type && filterType === 'chat');
    
    return matchesSearch && matchesType;
  });

  return (
    <div style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{ marginBottom: '20px' }}>
        <h1 className="page-title">📚 Sessions & Conversations</h1>
        <p className="page-description">Browse, view, and manage all your past conversations</p>
      </div>

      {/* Controls */}
      <div style={{ 
        display: 'flex', 
        gap: '12px', 
        marginBottom: '20px',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <input
          type="text"
          placeholder="🔍 Search sessions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            flex: 1,
            minWidth: '200px',
            padding: '10px 14px',
            backgroundColor: '#1a1a2e',
            color: 'white',
            border: '1px solid #333',
            borderRadius: '6px',
            fontSize: '14px'
          }}
        />
        
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          style={{
            padding: '10px 14px',
            backgroundColor: '#1a1a2e',
            color: 'white',
            border: '1px solid #333',
            borderRadius: '6px',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          <option value="all">All Types</option>
          <option value="chat">Chat Only</option>
          <option value="voice">Voice Only</option>
        </select>

        <button
          onClick={loadSessions}
          style={{
            padding: '10px 16px',
            backgroundColor: '#4a9eff',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 'bold'
          }}
        >
          🔄 Refresh
        </button>

        <button
          onClick={exportAllSessions}
          style={{
            padding: '10px 16px',
            backgroundColor: '#00d9ff',
            color: '#000',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 'bold'
          }}
        >
          📥 Export All
        </button>
      </div>

      {/* Stats */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
        gap: '12px',
        marginBottom: '20px'
      }}>
        <div style={{
          padding: '12px',
          backgroundColor: '#1a1a2e',
          borderRadius: '6px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Total Sessions</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4a9eff' }}>
            {sessions.length}
          </div>
        </div>
        
        <div style={{
          padding: '12px',
          backgroundColor: '#1a1a2e',
          borderRadius: '6px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Filtered</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#00d9ff' }}>
            {filteredSessions.length}
          </div>
        </div>
        
        <div style={{
          padding: '12px',
          backgroundColor: '#1a1a2e',
          borderRadius: '6px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>Total Messages</div>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#00ff88' }}>
            {sessions.reduce((sum, s) => sum + (s.message_count || 0), 0)}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ 
        flex: 1, 
        display: 'grid', 
        gridTemplateColumns: selectedSession ? '1fr 1.5fr' : '1fr',
        gap: '20px',
        minHeight: 0
      }}>
        {/* Sessions List */}
        <div style={{
          backgroundColor: '#0a0a0f',
          border: '1px solid #333',
          borderRadius: '8px',
          padding: '16px',
          overflowY: 'auto'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '16px', color: '#00d9ff' }}>
            Sessions ({filteredSessions.length})
          </h3>
          
          {loading ? (
            <div style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
              Loading sessions...
            </div>
          ) : filteredSessions.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
              <p>No sessions found</p>
              {searchTerm && <p style={{ fontSize: '12px' }}>Try a different search term</p>}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {filteredSessions.map(session => (
                <div
                  key={session.session_id}
                  onClick={() => viewSession(session.session_id)}
                  style={{
                    padding: '12px',
                    backgroundColor: selectedSession?.session_id === session.session_id ? '#2a2a40' : '#1a1a2e',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    border: selectedSession?.session_id === session.session_id ? '2px solid #00d9ff' : '1px solid #333',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={e => e.currentTarget.style.backgroundColor = '#2a2a40'}
                  onMouseLeave={e => e.currentTarget.style.backgroundColor = 
                    selectedSession?.session_id === session.session_id ? '#2a2a40' : '#1a1a2e'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ 
                        fontSize: '13px', 
                        fontWeight: 'bold', 
                        color: '#4a9eff',
                        marginBottom: '4px'
                      }}>
                        {session.metadata?.type === 'voice' ? '🎤' : '💬'} {session.session_id.substring(0, 8)}
                      </div>
                      <div style={{ fontSize: '11px', color: '#888', marginBottom: '6px' }}>
                        {new Date(session.started_at).toLocaleString()}
                      </div>
                      <div style={{ fontSize: '11px', color: '#aaa', marginBottom: '6px' }}>
                        {session.message_count} messages • {session.user_messages} user • {session.assistant_messages} AI
                      </div>
                      {session.preview && (
                        <div style={{ 
                          fontSize: '12px', 
                          color: '#ccc', 
                          fontStyle: 'italic',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>
                          "{session.preview}"
                        </div>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: '4px', marginLeft: '8px' }}>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          exportSession(session.session_id);
                        }}
                        style={{
                          padding: '4px 8px',
                          backgroundColor: '#00d9ff',
                          color: '#000',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '11px',
                          fontWeight: 'bold'
                        }}
                        title="Export session"
                      >
                        📥
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteSession(session.session_id);
                        }}
                        style={{
                          padding: '4px 8px',
                          backgroundColor: '#ff4444',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '11px'
                        }}
                        title="Delete session"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Session Details */}
        {selectedSession && (
          <div style={{
            backgroundColor: '#0a0a0f',
            border: '1px solid #333',
            borderRadius: '8px',
            padding: '16px',
            overflowY: 'auto'
          }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '16px'
            }}>
              <h3 style={{ margin: 0, color: '#00d9ff' }}>
                Session Details
              </h3>
              <button
                onClick={() => setSelectedSession(null)}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#333',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '12px'
                }}
              >
                Close
              </button>
            </div>

            {/* Session Info */}
            <div style={{
              padding: '12px',
              backgroundColor: '#1a1a2e',
              borderRadius: '6px',
              marginBottom: '16px'
            }}>
              <div style={{ fontSize: '12px', marginBottom: '8px' }}>
                <strong>ID:</strong> {selectedSession.session_id}
              </div>
              <div style={{ fontSize: '12px', marginBottom: '8px' }}>
                <strong>Started:</strong> {new Date(selectedSession.started_at).toLocaleString()}
              </div>
              <div style={{ fontSize: '12px', marginBottom: '8px' }}>
                <strong>Last Updated:</strong> {new Date(selectedSession.last_updated || selectedSession.started_at).toLocaleString()}
              </div>
              <div style={{ fontSize: '12px', marginBottom: '8px' }}>
                <strong>Messages:</strong> {selectedSession.messages.length}
              </div>
              <div style={{ fontSize: '12px' }}>
                <strong>Type:</strong> {selectedSession.metadata?.type || 'chat'}
              </div>
            </div>

            {/* Messages */}
            <h4 style={{ color: '#888', marginBottom: '12px' }}>Conversation</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {selectedSession.messages.map((msg, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '12px',
                    backgroundColor: msg.role === 'user' ? '#1a1a2e' : '#0f3460',
                    borderRadius: '8px',
                    borderLeft: `4px solid ${msg.role === 'user' ? '#4a9eff' : '#00d9ff'}`
                  }}
                >
                  <div style={{ 
                    fontSize: '11px', 
                    color: '#888', 
                    marginBottom: '6px',
                    display: 'flex',
                    justifyContent: 'space-between'
                  }}>
                    <span>
                      {msg.role === 'user' ? '👤 You' : '🤖 Assistant'}
                      {msg.metadata?.hasTools && (
                        <span style={{
                          marginLeft: '8px',
                          padding: '2px 6px',
                          backgroundColor: 'rgba(255, 165, 0, 0.2)',
                          borderRadius: '3px',
                          color: '#ffa500',
                          fontSize: '10px'
                        }}>🛠️ TOOLS</span>
                      )}
                      {msg.metadata?.modes?.commander && (
                        <span style={{
                          marginLeft: '8px',
                          padding: '2px 6px',
                          backgroundColor: 'rgba(255, 68, 68, 0.2)',
                          borderRadius: '3px',
                          color: '#ff4444',
                          fontSize: '10px'
                        }}>⚡ CMD</span>
                      )}
                      {msg.metadata?.modes?.webSearch && (
                        <span style={{
                          marginLeft: '8px',
                          padding: '2px 6px',
                          backgroundColor: 'rgba(68, 255, 68, 0.2)',
                          borderRadius: '3px',
                          color: '#44ff44',
                          fontSize: '10px'
                        }}>🌐 WEB</span>
                      )}
                    </span>
                    <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div style={{ 
                    fontSize: '13px', 
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word'
                  }}>
                    {msg.content}
                  </div>
                  {/* Show extracted tools */}
                  {msg.role === 'assistant' && extractToolsFromMessage(msg).length > 0 && (
                    <div style={{ 
                      marginTop: '8px',
                      padding: '8px',
                      backgroundColor: 'rgba(255, 165, 0, 0.1)',
                      borderRadius: '4px',
                      fontSize: '11px'
                    }}>
                      <div style={{ fontWeight: 'bold', marginBottom: '4px', color: '#ffa500' }}>
                        🛠️ Tools Used:
                      </div>
                      {extractToolsFromMessage(msg).map((tool, tidx) => (
                        <div key={tidx} style={{ marginLeft: '8px', color: '#ccc' }}>
                          • {tool.name}{tool.params ? `(${tool.params})` : ''}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Sessions;
