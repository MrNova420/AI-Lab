/**
 * Code Review Component
 * Main interface for code reviews with inline comments
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Highlight, themes } from 'prism-react-renderer';
import codeReviewManager from '../../utils/codeReviewManager';
import ReviewComment from './ReviewComment';

const CodeReview = ({ review, onUpdate, onClose }) => {
  const [selectedLine, setSelectedLine] = useState(null);
  const [commentText, setCommentText] = useState('');
  const [commentType, setCommentType] = useState('suggestion');
  const [showResolved, setShowResolved] = useState(false);
  
  const handleAddComment = () => {
    if (!commentText.trim() || selectedLine === null) return;
    
    codeReviewManager.addComment(review.id, {
      line: selectedLine,
      text: commentText,
      type: commentType
    });
    
    setCommentText('');
    setSelectedLine(null);
    onUpdate();
  };
  
  const handleApprove = () => {
    codeReviewManager.approveReview(review.id);
    onUpdate();
  };
  
  const handleRequestChanges = () => {
    codeReviewManager.requestChanges(review.id);
    onUpdate();
  };
  
  const getCommentsForLine = (lineNumber) => {
    return review.comments.filter(c => c.line === lineNumber);
  };
  
  const filteredComments = showResolved
    ? review.comments
    : review.comments.filter(c => !c.resolved);
  
  return (
    <div className="code-review">
      <div className="review-header">
        <div className="review-info">
          <h3>Code Review</h3>
          <span className={`status-badge status-${review.status}`}>
            {review.status}
          </span>
        </div>
        
        <div className="review-actions">
          <button
            className="btn-success"
            onClick={handleApprove}
            disabled={review.status === 'approved'}
          >
            ✓ Approve
          </button>
          <button
            className="btn-warning"
            onClick={handleRequestChanges}
            disabled={review.status === 'changes-requested'}
          >
            ⚠ Request Changes
          </button>
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
      
      <div className="review-stats">
        <span>{review.metadata.totalComments} comments</span>
        <span>•</span>
        <span>{review.metadata.resolvedComments} resolved</span>
        <span>•</span>
        <span>{review.metadata.unresolvedComments} unresolved</span>
        <label className="show-resolved-toggle">
          <input
            type="checkbox"
            checked={showResolved}
            onChange={(e) => setShowResolved(e.target.checked)}
          />
          Show resolved
        </label>
      </div>
      
      <div className="review-content">
        <div className="code-panel">
          <div className="code-header">
            <span className="code-language">{review.language || 'plaintext'}</span>
            <span className="code-hint">Click on line numbers to add comments</span>
          </div>
          
          <Highlight
            theme={themes.vsDark}
            code={review.code}
            language={review.language || 'javascript'}
          >
            {({ className, style, tokens, getLineProps, getTokenProps }) => (
              <pre className={className} style={style}>
                {tokens.map((line, i) => {
                  const lineNumber = i + 1;
                  const lineComments = getCommentsForLine(lineNumber);
                  const hasComments = lineComments.length > 0;
                  
                  return (
                    <div key={i} className="code-line-wrapper">
                      <div
                        {...getLineProps({ line })}
                        className={`code-line ${selectedLine === lineNumber ? 'selected' : ''} ${hasComments ? 'has-comments' : ''}`}
                      >
                        <span
                          className="line-number"
                          onClick={() => setSelectedLine(lineNumber)}
                        >
                          {lineNumber}
                          {hasComments && <span className="comment-indicator">💬</span>}
                        </span>
                        <span className="line-content">
                          {line.map((token, key) => (
                            <span key={key} {...getTokenProps({ token })} />
                          ))}
                        </span>
                      </div>
                      
                      {selectedLine === lineNumber && (
                        <motion.div
                          className="inline-comment-form"
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                        >
                          <select
                            value={commentType}
                            onChange={(e) => setCommentType(e.target.value)}
                            className="comment-type-select"
                          >
                            <option value="suggestion">💡 Suggestion</option>
                            <option value="question">❓ Question</option>
                            <option value="praise">👍 Praise</option>
                            <option value="issue">⚠️ Issue</option>
                          </select>
                          <textarea
                            className="comment-textarea"
                            placeholder="Add your comment..."
                            value={commentText}
                            onChange={(e) => setCommentText(e.target.value)}
                            autoFocus
                          />
                          <div className="comment-actions">
                            <button
                              className="btn-primary btn-sm"
                              onClick={handleAddComment}
                            >
                              Add Comment
                            </button>
                            <button
                              className="btn-secondary btn-sm"
                              onClick={() => {
                                setSelectedLine(null);
                                setCommentText('');
                              }}
                            >
                              Cancel
                            </button>
                          </div>
                        </motion.div>
                      )}
                      
                      {hasComments && (
                        <div className="line-comments">
                          {lineComments.map(comment => (
                            <ReviewComment
                              key={comment.id}
                              comment={comment}
                              reviewId={review.id}
                              onUpdate={onUpdate}
                            />
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </pre>
            )}
          </Highlight>
        </div>
        
        <div className="comments-panel">
          <h4>All Comments</h4>
          {filteredComments.length === 0 ? (
            <div className="empty-state">
              <p>No {showResolved ? '' : 'unresolved '}comments</p>
            </div>
          ) : (
            <div className="comments-list">
              {filteredComments.map(comment => (
                <ReviewComment
                  key={comment.id}
                  comment={comment}
                  reviewId={review.id}
                  onUpdate={onUpdate}
                  showLine
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CodeReview;
