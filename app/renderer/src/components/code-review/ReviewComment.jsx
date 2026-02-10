/**
 * Review Comment Component
 * Individual comment with replies and actions
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import codeReviewManager from '../../utils/codeReviewManager';

const ReviewComment = ({ comment, reviewId, onUpdate, showLine = false }) => {
  const [replyText, setReplyText] = useState('');
  const [showReplyForm, setShowReplyForm] = useState(false);
  
  const typeEmojis = {
    suggestion: '💡',
    question: '❓',
    praise: '👍',
    issue: '⚠️'
  };
  
  const handleResolve = () => {
    if (comment.resolved) {
      codeReviewManager.unresolveComment(reviewId, comment.id);
    } else {
      codeReviewManager.resolveComment(reviewId, comment.id);
    }
    onUpdate();
  };
  
  const handleAddReply = () => {
    if (!replyText.trim()) return;
    
    codeReviewManager.addReply(reviewId, comment.id, {
      text: replyText
    });
    
    setReplyText('');
    setShowReplyForm(false);
    onUpdate();
  };
  
  const handleDelete = () => {
    if (confirm('Delete this comment?')) {
      codeReviewManager.deleteComment(reviewId, comment.id);
      onUpdate();
    }
  };
  
  return (
    <motion.div
      className={`review-comment ${comment.resolved ? 'resolved' : ''}`}
      layout
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
    >
      <div className="comment-header">
        <span className="comment-type">
          {typeEmojis[comment.type]} {comment.type}
        </span>
        {showLine && (
          <span className="comment-line">Line {comment.line}</span>
        )}
        <span className="comment-author">{comment.author}</span>
        <span className="comment-time">
          {new Date(comment.createdAt).toLocaleString()}
        </span>
      </div>
      
      <div className="comment-body">
        {comment.text}
      </div>
      
      {comment.replies.length > 0 && (
        <div className="comment-replies">
          {comment.replies.map(reply => (
            <div key={reply.id} className="comment-reply">
              <div className="reply-header">
                <span className="reply-author">{reply.author}</span>
                <span className="reply-time">
                  {new Date(reply.createdAt).toLocaleString()}
                </span>
              </div>
              <div className="reply-body">{reply.text}</div>
            </div>
          ))}
        </div>
      )}
      
      {showReplyForm && (
        <div className="reply-form">
          <textarea
            className="reply-textarea"
            placeholder="Write a reply..."
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            autoFocus
          />
          <div className="reply-actions">
            <button
              className="btn-primary btn-sm"
              onClick={handleAddReply}
            >
              Reply
            </button>
            <button
              className="btn-secondary btn-sm"
              onClick={() => {
                setShowReplyForm(false);
                setReplyText('');
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
      
      <div className="comment-actions">
        <button
          className="btn-link"
          onClick={() => setShowReplyForm(!showReplyForm)}
        >
          Reply
        </button>
        <button
          className={`btn-link ${comment.resolved ? 'resolved' : ''}`}
          onClick={handleResolve}
        >
          {comment.resolved ? 'Unresolve' : 'Resolve'}
        </button>
        <button
          className="btn-link btn-danger"
          onClick={handleDelete}
        >
          Delete
        </button>
      </div>
    </motion.div>
  );
};

export default ReviewComment;
