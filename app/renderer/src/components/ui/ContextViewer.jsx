/**
 * Context Viewer Component
 * Displays token usage, context window, and message management
 */

import React, { useState, useEffect } from 'react';

const ContextViewer = ({ messages, onPinMessage, onUnpinMessage, pinnedMessages = [] }) => {
  const [contextStats, setContextStats] = useState({
    totalTokens: 0,
    usedTokens: 0,
    remainingTokens: 0,
    messageCount: 0,
    contextWindow: 8192 // Default, should be configurable
  });

  useEffect(() => {
    // Estimate tokens (rough approximation: 1 token ≈ 4 characters)
    const estimateTokens = (text) => Math.ceil(text.length / 4);
    
    let totalUsed = 0;
    messages.forEach(msg => {
      totalUsed += estimateTokens(msg.content);
    });

    const contextWindow = 8192; // Should come from model config
    const remaining = Math.max(0, contextWindow - totalUsed);
    const percentage = (totalUsed / contextWindow) * 100;

    setContextStats({
      totalTokens: contextWindow,
      usedTokens: totalUsed,
      remainingTokens: remaining,
      messageCount: messages.length,
      contextWindow,
      percentage: Math.min(100, percentage)
    });
  }, [messages]);

  const getStatusColor = () => {
    if (contextStats.percentage < 50) return '#4CAF50'; // Green
    if (contextStats.percentage < 75) return '#ff9800'; // Orange
    return '#f44336'; // Red
  };

  return (
    <div style={{
      backgroundColor: '#1a1a2e',
      border: '1px solid #333',
      borderRadius: '8px',
      padding: '16px',
      marginBottom: '16px'
    }}>
      {/* Context Usage Bar */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '8px'
        }}>
          <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#fff' }}>
            🧠 Context Window
          </span>
          <span style={{ fontSize: '12px', color: '#888' }}>
            {contextStats.usedTokens.toLocaleString()} / {contextStats.totalTokens.toLocaleString()} tokens
          </span>
        </div>
        
        {/* Progress Bar */}
        <div style={{
          width: '100%',
          height: '12px',
          backgroundColor: '#0a0a0f',
          borderRadius: '6px',
          overflow: 'hidden',
          border: '1px solid #333'
        }}>
          <div style={{
            width: `${contextStats.percentage}%`,
            height: '100%',
            backgroundColor: getStatusColor(),
            transition: 'width 0.3s ease, background-color 0.3s ease'
          }} />
        </div>

        {/* Stats */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: '8px',
          fontSize: '12px',
          color: '#888'
        }}>
          <span>📊 {contextStats.messageCount} messages</span>
          <span style={{ color: getStatusColor(), fontWeight: 'bold' }}>
            {contextStats.percentage.toFixed(1)}% used
          </span>
          <span>💾 {contextStats.remainingTokens.toLocaleString()} remaining</span>
        </div>
      </div>

      {/* Pinned Messages */}
      {pinnedMessages.length > 0 && (
        <div style={{
          borderTop: '1px solid #333',
          paddingTop: '12px'
        }}>
          <div style={{
            fontSize: '13px',
            fontWeight: 'bold',
            color: '#fff',
            marginBottom: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            📌 Pinned Messages ({pinnedMessages.length})
          </div>
          <div style={{ fontSize: '12px', color: '#888' }}>
            Pinned messages are always included in context
          </div>
        </div>
      )}

      {/* Context Tips */}
      {contextStats.percentage > 80 && (
        <div style={{
          marginTop: '12px',
          padding: '8px 12px',
          backgroundColor: 'rgba(255, 152, 0, 0.1)',
          border: '1px solid rgba(255, 152, 0, 0.3)',
          borderRadius: '6px',
          fontSize: '12px',
          color: '#ff9800'
        }}>
          ⚠️ Context window is {contextStats.percentage.toFixed(0)}% full. Consider starting a new session to maintain performance.
        </div>
      )}
    </div>
  );
};

export default ContextViewer;
