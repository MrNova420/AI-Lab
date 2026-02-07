import React, { useState, useEffect, useRef } from 'react';

function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [commanderMode, setCommanderMode] = useState(false);
  const [webSearchMode, setWebSearchMode] = useState(false);
  const [resources, setResources] = useState({cpu: {}, gpu: {}, memory: {}});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentResponse]);

  useEffect(() => {
    // Update resources every 2 seconds
    const interval = setInterval(loadResources, 2000);
    return () => clearInterval(interval);
  }, []);

  const loadResources = async () => {
    try {
      const response = await fetch('http://localhost:5174/api/resources/stats');
      const data = await response.json();
      setResources(data);
    } catch (err) {
      // Silent fail
    }
  };

  useEffect(() => {
    // Listen for streaming tokens
    if (window.electron?.chat?.onToken) {
      const unsubscribe = window.electron.chat.onToken((token) => {
        setCurrentResponse(prev => prev + token);
      });
      
      return () => unsubscribe?.();
    }
  }, []);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    const messageText = input;
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setCurrentResponse('');

    try {
      // Build history (last 10 messages for context)
      const history = messages.slice(-10);
      
      let fullResponse = '';
      
      // Check if running in Electron or browser
      const isElectron = window.electron?.chat?.send;
      
      if (isElectron) {
        console.log('Using Electron IPC bridge...');
        fullResponse = await window.electron.chat.send(messageText, history);
        
      } else {
        console.log('Using HTTP API (browser mode)...');
        
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
              } else if (data.type === 'error') {
                throw new Error(data.message);
              }
            } catch (e) {
              console.warn('Parse error:', e.message);
            }
          }
        }
      }
      
      // Add assistant message with mode indicators
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: fullResponse,
        modes: {
          commander: commanderMode,
          webSearch: webSearchMode
        }
      }]);
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
    setMessages([]);
    setCurrentResponse('');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 className="page-title">Chat</h1>
          <p className="page-description">Text conversation with AI</p>
        </div>
        
        {/* Mode Toggles & Live Stats */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {/* Live Resource Stats */}
          <div style={{
            display: 'flex',
            gap: '12px',
            marginRight: '10px',
            padding: '6px 12px',
            backgroundColor: '#1a1a2e',
            borderRadius: '6px',
            fontSize: '11px',
            color: '#888'
          }}>
            <span>🖥️ CPU: <strong style={{color: '#4a9eff'}}>{resources.cpu?.usage_percent?.toFixed(0) || '0'}%</strong></span>
            {resources.gpu?.available && (
              <span>🎮 GPU: <strong style={{color: '#00ff88'}}>{resources.gpu?.usage_percent?.toFixed(0)}%</strong></span>
            )}
            <span>💾 RAM: <strong style={{color: '#ffaa00'}}>{resources.memory?.percent?.toFixed(0) || '0'}%</strong></span>
          </div>

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
                    {msg.modes?.commander && <span style={{marginLeft: '8px', color: '#ff4444', fontSize: '0.85em'}}>⚡CMD</span>}
                    {msg.modes?.webSearch && <span style={{marginLeft: '8px', color: '#44ff44', fontSize: '0.85em'}}>🌐WEB</span>}
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
              fontWeight: 'bold' 
            }}>
              🤖 Assistant
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
