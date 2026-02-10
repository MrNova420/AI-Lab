/**
 * Code Block Component with Review Capabilities
 * Displays code with syntax highlighting and review options
 */

import React, { useState } from 'react';
import codeReviewManager from '../../utils/codeReviewManager';
import CodeReview from '../code-review/CodeReview';

const CodeBlock = ({ code, language, messageId }) => {
  const [showReview, setShowReview] = useState(false);
  const [reviewId, setReviewId] = useState(null);
  const [copied, setCopied] = useState(false);
  
  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  const handleStartReview = () => {
    // Create a review for this code block
    const codeBlockId = `code-${messageId}-${Date.now()}`;
    const review = codeReviewManager.createReview({
      codeBlockId,
      code,
      language: language || 'plaintext',
      messageId
    });
    setReviewId(review.id);
    setShowReview(true);
  };
  
  const handleCloseReview = () => {
    setShowReview(false);
  };
  
  const handleUpdateReview = () => {
    // Refresh review data if needed
  };
  
  if (showReview && reviewId) {
    const review = codeReviewManager.getReview(reviewId);
    return (
      <CodeReview
        review={review}
        onUpdate={handleUpdateReview}
        onClose={handleCloseReview}
      />
    );
  }
  
  return (
    <div style={{
      backgroundColor: '#1a1a2e',
      border: '1px solid #333',
      borderRadius: '8px',
      margin: '8px 0',
      overflow: 'hidden'
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '8px 12px',
        backgroundColor: '#0f0f1e',
        borderBottom: '1px solid #333'
      }}>
        <span style={{
          fontSize: '12px',
          color: '#888',
          fontFamily: 'monospace',
          textTransform: 'uppercase'
        }}>
          {language || 'code'}
        </span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={handleStartReview}
            style={{
              padding: '4px 8px',
              backgroundColor: '#9c27b0',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '11px',
              fontWeight: 'bold'
            }}
            title="Start code review"
          >
            🔍 Review
          </button>
          <button
            onClick={handleCopy}
            style={{
              padding: '4px 8px',
              backgroundColor: copied ? '#4CAF50' : 'transparent',
              color: copied ? 'white' : '#888',
              border: '1px solid #333',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '11px'
            }}
            title="Copy code"
          >
            {copied ? '✓ Copied' : '📋 Copy'}
          </button>
        </div>
      </div>
      <pre style={{
        margin: 0,
        padding: '12px',
        overflowX: 'auto',
        fontSize: '13px',
        lineHeight: '1.5',
        fontFamily: 'monospace',
        color: '#e0e0e0'
      }}>
        <code>{code}</code>
      </pre>
    </div>
  );
};

export default CodeBlock;
