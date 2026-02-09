import React, { useState, useEffect, useRef } from 'react';
import { trackToolsFromResponse } from '../utils/toolTracking';
import { saveModePreferences, loadModePreferences } from '../utils/statePersistence';
import sessionManager from '../utils/sessionManager';

function Chat({ messages, setMessages, input, setInput }) {
  const [isLoading, setIsLoading] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [commanderMode, setCommanderMode] = useState(false);
  const [webSearchMode, setWebSearchMode] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [showSessionList, setShowSessionList] = useState(false);
  const messagesEndRef = useRef(null);
  const sessionInitialized = useRef(false);

  // Initialize session on mount
  useEffect(() => {
    const initializeSession = async () => {
      if (sessionInitialized.current) return;
      sessionInitialized.current = true;
      
      const prefs = loadModePreferences();
      setCommanderMode(prefs.commanderMode);
      setWebSearchMode(prefs.webSearchMode);
      
      // Smart session resumption: check if last session is still fresh
      const isFresh = sessionManager.isSessionFresh();
      const timeSince = sessionManager.getTimeSinceActivity();
      
      try {
        if (isFresh) {
          // Resume last session (< 30 minutes old)
          const sessionData = await sessionManager.listSessions(1, 0);
          if (sessionData.sessions && sessionData.sessions.length > 0) {
            const lastSession = sessionData.sessions[0];
            const loaded = await sessionManager.loadSession(lastSession.session_id);
            setMessages(loaded.messages || []);
            setCurrentSessionId(loaded.session_id);
            console.log(`📥 Resumed fresh session (last activity: ${timeSince}): ${loaded.session_id}`);
          } else {
            // No sessions exist, start new
            const sessionId = await sessionManager.startNewSession();
            setCurrentSessionId(sessionId);
            console.log(`✨ Started new session (no history)`);
          }
        } else {
          // Session is stale (>= 30 minutes), start fresh
          const sessionId = await sessionManager.startNewSession();
          setCurrentSessionId(sessionId);
          if (timeSince !== 'Never') {
            console.log(`✨ Started fresh session (last activity: ${timeSince})`);
          } else {
            console.log(`✨ Started new session (first time)`);
          }
        }
      } catch (error) {
        console.error('Session initialization error:', error);
        // Fallback: start new session
        try {
          const sessionId = await sessionManager.startNewSession();
          setCurrentSessionId(sessionId);
        } catch (e) {
          console.error('Failed to start new session:', e);
        }
      }
    };
    
    initializeSession();
  }, []);

  // Save mode preferences whenever they change
  useEffect(() => {
    saveModePreferences(commanderMode, webSearchMode);
  }, [commanderMode, webSearchMode]);

  // Sync messages with session manager whenever they change
  useEffect(() => {
    if (messages.length > 0 && currentSessionId) {
      // Update session manager's message list
      const session = sessionManager.getCurrentSession();
      if (session && session.session_id === currentSessionId) {
        session.messages = messages;
      }
    }
  }, [messages, currentSessionId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentResponse]);

  useEffect(() => {
    // Listen for streaming tokens
    if (window.electron?.chat?.onToken) {
      const unsubscribe = window.electron.chat.onToken((token) => {
        setCurrentResponse(prev => prev + token);
      });
      
      return () => unsubscribe?.();
    }
  }, []);

  const startNewSession = async () => {
    try {
      const sessionId = await sessionManager.startNewSession('User');
      setCurrentSessionId(sessionId);
      setMessages([]);
      setCurrentResponse('');
      console.log(`✨ Started new session: ${sessionId}`);
    } catch (error) {
      console.error('Failed to start new session:', error);
    }
  };

  const loadSessionFromList = async (sessionId) => {
    try {
      const loaded = await sessionManager.loadSession(sessionId);
      setMessages(loaded.messages || []);
      setCurrentSessionId(loaded.session_id);
      setShowSessionList(false);
      console.log(`📥 Loaded session: ${sessionId}`);
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  };

  const loadSessionsList = async () => {
    try {
      const data = await sessionManager.listSessions(50, 0);
      setSessions(data.sessions || []);
      setShowSessionList(true);
    } catch (error) {
      console.error('Failed to load sessions list:', error);
    }
  };

  const deleteSessionFromList = async (sessionId, event) => {
    event.stopPropagation();
    if (!confirm('Are you sure you want to delete this session?')) {
      return;
    }
    
    try {
      await sessionManager.deleteSession(sessionId);
      // Refresh the list
      const data = await sessionManager.listSessions(50, 0);
      setSessions(data.sessions || []);
      
      // If we deleted the current session, start a new one
      if (sessionId === currentSessionId) {
        await startNewSession();
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    const messageText = input;
    setMessages(prev => [...prev, userMessage]);
    
    // Add to session manager
    if (currentSessionId) {
      sessionManager.addMessage('user', input);
    }
    
    setInput('');
    setIsLoading(true);
    setCurrentResponse('');

    try {
      // Build history (last 10 messages for context)
      const history = messages.slice(-10);
      
      let fullResponse = '';
      let responseModel = 'unknown'; // Track model used for this response
      let responseMode; // Track mode
      
      // Check if running in Electron or browser
      const isElectron = window.electron?.chat?.send;
      
      if (isElectron) {
        // Electron IPC mode
        fullResponse = await window.electron.chat.send(messageText, history);
        
      } else {
        // Browser mode - HTTP API
        
        // Use HTTP API for browser
        const response = await fetch('http://localhost:5174/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            message: messageText, 
            history,
            commander_mode: commanderMode,
            web_search_mode: webSearchMode
          })
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        // Read streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value);
          const lines = chunk.split('\n').filter(Boolean);
          
          for (const line of lines) {
            try {
              const data = JSON.parse(line);
              
              if (data.type === 'token') {
                setCurrentResponse(prev => prev + data.token);
              } else if (data.type === 'done') {
                fullResponse = data.full_response;
                responseModel = data.model || 'unknown';
                responseMode = data.mode || 'normal';
              } else if (data.type === 'error') {
                throw new Error(data.message);
              }
            } catch (e) {
              // Silent - ignore parse errors
            }
          }
        }
      }
      
      // Add assistant message with mode indicators and model info
      const assistantMessage = { 
        role: 'assistant', 
        content: fullResponse || currentResponse,
        modes: {
          commander: commanderMode,
          webSearch: webSearchMode
        },
        model: responseModel,
        timestamp: new Date().toISOString()
      };
      
      // Check if response contains tool executions
      if (assistantMessage.content && assistantMessage.content.includes('🛠️')) {
        assistantMessage.hasTools = true;
        // Track tool usage for statistics
        trackToolsFromResponse(assistantMessage.content);
      }
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Add to session manager with model info
      if (currentSessionId) {
        sessionManager.addMessage('assistant', assistantMessage.content, {
          modes: assistantMessage.modes,
          hasTools: assistantMessage.hasTools,
          model: assistantMessage.model,
          timestamp: assistantMessage.timestamp
        });
      }
      
      setCurrentResponse('');
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Error: ${error.message}` 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    // This now starts a new session instead of just clearing
    startNewSession();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 className="page-title">Chat</h1>
          <p className="page-description">
            Text conversation with AI
            {currentSessionId && (
              <span style={{ marginLeft: '10px', fontSize: '12px', color: '#888' }}>
                Session: {currentSessionId.substring(0, 8)}
              </span>
            )}
          </p>
        </div>
        
        {/* Session and Mode Controls */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Session Controls */}
          <button
            onClick={startNewSession}
            style={{
              padding: '8px 14px',
              backgroundColor: '#00d9ff',
              color: '#000',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 'bold'
            }}
            title="Start new session"
          >
            ✨ New
          </button>
          
          <button
            onClick={loadSessionsList}
            style={{
              padding: '8px 14px',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 'bold'
            }}
            title="Load previous session"
          >
            📋 Sessions
          </button>
          
          {/* Mode Toggles */}
          <button
            onClick={() => setCommanderMode(!commanderMode)}
            style={{
              padding: '8px 14px',
              backgroundColor: commanderMode ? '#ff4444' : '#333',
              color: 'white',
              border: `2px solid ${commanderMode ? '#ff0000' : '#555'}`,
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 'bold'
            }}
            title={commanderMode ? 'Commander ON' : 'Commander OFF'}
          >
            {commanderMode ? '⚡ CMD' : '🔒 CMD'}
          </button>
          
          <button
            onClick={() => setWebSearchMode(!webSearchMode)}
            style={{
              padding: '8px 14px',
              backgroundColor: webSearchMode ? '#4CAF50' : '#333',
              color: 'white',
              border: `2px solid ${webSearchMode ? '#4CAF50' : '#555'}`,
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px',
              fontWeight: 'bold'
            }}
            title={webSearchMode ? 'Web Search ON' : 'Web Search OFF'}
          >
            {webSearchMode ? '🌐 WEB' : '🌐 WEB'}
          </button>
          
          <button 
            onClick={clearChat}
            style={{
              padding: '8px 16px',
              backgroundColor: '#ff4444',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            Clear
          </button>
        </div>
      </div>

      {/* Session List Modal */}
      {showSessionList && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: '#1a1a2e',
            borderRadius: '12px',
            padding: '24px',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'auto',
            border: '2px solid #333'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{ margin: 0, color: '#00d9ff' }}>📋 Sessions</h2>
              <button
                onClick={() => setShowSessionList(false)}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#ff4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                Close
              </button>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {sessions.length === 0 ? (
                <p style={{ textAlign: 'center', color: '#666' }}>No sessions found</p>
              ) : (
                sessions.map(session => (
                  <div 
                    key={session.session_id}
                    onClick={() => loadSessionFromList(session.session_id)}
                    style={{
                      padding: '12px',
                      backgroundColor: session.session_id === currentSessionId ? '#2a2a40' : '#0f0f1e',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      border: session.session_id === currentSessionId ? '2px solid #00d9ff' : '1px solid #333',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={e => e.currentTarget.style.backgroundColor = '#2a2a40'}
                    onMouseLeave={e => e.currentTarget.style.backgroundColor = session.session_id === currentSessionId ? '#2a2a40' : '#0f0f1e'}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#4a9eff', marginBottom: '4px' }}>
                          Session {session.session_id.substring(0, 8)}
                        </div>
                        <div style={{ fontSize: '12px', color: '#888', marginBottom: '6px' }}>
                          {new Date(session.started_at).toLocaleString()} • {session.message_count} messages
                        </div>
                        {session.preview && (
                          <div style={{ fontSize: '13px', color: '#ccc', fontStyle: 'italic' }}>
                            "{session.preview}..."
                          </div>
                        )}
                      </div>
                      <button
                        onClick={(e) => deleteSessionFromList(session.session_id, e)}
                        style={{
                          padding: '4px 8px',
                          backgroundColor: '#ff4444',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '11px',
                          marginLeft: '10px'
                        }}
                        title="Delete session"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        backgroundColor: '#0a0a0f',
        border: '1px solid #333',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px'
      }}>
        {messages.length === 0 && !currentResponse && (
          <div style={{ textAlign: 'center', color: '#666', marginTop: '50px' }}>
            <h3>Start a conversation</h3>
            <p>Type a message below to chat with your AI model</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} style={{
            marginBottom: '16px',
            padding: '12px 16px',
            backgroundColor: msg.role === 'user' ? '#1a1a2e' : '#0f3460',
            borderRadius: '8px',
            borderLeft: `4px solid ${msg.role === 'user' ? '#4a9eff' : '#00d9ff'}`
          }}>
            <div style={{ 
              fontSize: '12px', 
              color: '#888', 
              marginBottom: '4px',
              fontWeight: 'bold',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span>
                {msg.role === 'user' ? '👤 You' : 
                  <>
                    🤖 Assistant
                    {msg.hasTools && (
                      <span style={{
                        marginLeft: '8px',
                        padding: '2px 8px',
                        backgroundColor: 'rgba(255, 165, 0, 0.2)',
                        borderRadius: '4px',
                        color: '#ffa500',
                        fontSize: '0.8em',
                        fontWeight: 'bold'
                      }}>🛠️ TOOLS</span>
                    )}
                    {msg.modes?.commander && (
                      <span style={{
                        marginLeft: '8px', 
                        padding: '2px 8px',
                        backgroundColor: 'rgba(255, 68, 68, 0.2)',
                        borderRadius: '4px',
                        color: '#ff4444', 
                        fontSize: '0.8em',
                        fontWeight: 'bold'
                      }}>⚡ CMD</span>
                    )}
                    {msg.modes?.webSearch && (
                      <span style={{
                        marginLeft: '8px',
                        padding: '2px 8px', 
                        backgroundColor: 'rgba(68, 255, 68, 0.2)',
                        borderRadius: '4px',
                        color: '#44ff44', 
                        fontSize: '0.8em',
                        fontWeight: 'bold'
                      }}>🌐 WEB</span>
                    )}
                  </>
                }
              </span>
              <button
                onClick={(e) => {
                  navigator.clipboard.writeText(msg.content);
                  const btn = e.currentTarget;
                  const originalText = btn.textContent;
                  btn.textContent = '✓ Copied!';
                  btn.style.color = '#00ff88';
                  setTimeout(() => {
                    btn.textContent = originalText;
                    btn.style.color = '#888';
                  }, 1500);
                }}
                style={{
                  padding: '4px 8px',
                  backgroundColor: 'transparent',
                  color: '#888',
                  border: '1px solid #333',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '11px',
                  transition: 'all 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.target.style.borderColor = '#00d9ff';
                  e.target.style.color = '#00d9ff';
                }}
                onMouseLeave={(e) => {
                  e.target.style.borderColor = '#333';
                  e.target.style.color = '#888';
                }}
                title="Copy to clipboard"
              >
                📋 Copy
              </button>
            </div>
            <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
          </div>
        ))}

        {/* Streaming response */}
        {currentResponse && (
          <div style={{
            marginBottom: '16px',
            padding: '12px 16px',
            backgroundColor: '#0f3460',
            borderRadius: '8px',
            borderLeft: '4px solid #00d9ff'
          }}>
            <div style={{ 
              fontSize: '12px', 
              color: '#888', 
              marginBottom: '4px',
              fontWeight: 'bold',
              display: 'flex',
              gap: '8px',
              alignItems: 'center'
            }}>
              <span>🤖 Assistant</span>
              {currentResponse.includes('🛠️') && (
                <span style={{
                  padding: '2px 8px',
                  backgroundColor: 'rgba(255, 165, 0, 0.2)',
                  borderRadius: '4px',
                  color: '#ffa500',
                  fontSize: '0.8em',
                  fontWeight: 'bold'
                }}>🛠️ TOOLS</span>
              )}
              {commanderMode && (
                <span style={{
                  padding: '2px 8px',
                  backgroundColor: 'rgba(255, 68, 68, 0.2)',
                  borderRadius: '4px',
                  color: '#ff4444',
                  fontSize: '0.8em',
                  fontWeight: 'bold'
                }}>⚡ CMD</span>
              )}
              {webSearchMode && (
                <span style={{
                  padding: '2px 8px',
                  backgroundColor: 'rgba(68, 255, 68, 0.2)',
                  borderRadius: '4px',
                  color: '#44ff44',
                  fontSize: '0.8em',
                  fontWeight: 'bold'
                }}>🌐 WEB</span>
              )}
            </div>
            <div style={{ whiteSpace: 'pre-wrap' }}>
              {currentResponse}
              <span className="typing-cursor">▊</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={{ display: 'flex', gap: '12px' }}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
          disabled={isLoading}
          style={{
            flex: 1,
            padding: '12px',
            backgroundColor: '#1a1a2e',
            color: 'white',
            border: '1px solid #333',
            borderRadius: '8px',
            fontSize: '14px',
            resize: 'none',
            minHeight: '60px',
            fontFamily: 'inherit'
          }}
        />
        <button
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
          style={{
            padding: '12px 24px',
            backgroundColor: isLoading || !input.trim() ? '#333' : '#4a9eff',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: isLoading || !input.trim() ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: 'bold',
            minWidth: '100px'
          }}
        >
          {isLoading ? '⏳ Sending...' : '📤 Send'}
        </button>
      </div>

      <style>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
        .typing-cursor {
          animation: blink 1s infinite;
        }
      `}</style>
    </div>
  );
}

export default Chat;
