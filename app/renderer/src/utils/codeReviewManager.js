/**
 * Code Review Manager
 * Manages code reviews, comments, and review state
 */

class CodeReviewManager {
  constructor() {
    this.reviews = this.loadReviews();
  }
  
  // Load reviews from localStorage
  loadReviews() {
    try {
      const stored = localStorage.getItem('ai-lab-reviews');
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Failed to load reviews:', error);
      return {};
    }
  }
  
  // Save reviews to localStorage
  saveReviews() {
    try {
      localStorage.setItem('ai-lab-reviews', JSON.stringify(this.reviews));
    } catch (error) {
      console.error('Failed to save reviews:', error);
    }
  }
  
  // Create new review
  createReview({ codeBlockId, code, language, messageId }) {
    const id = `review-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const timestamp = new Date().toISOString();
    
    const review = {
      id,
      codeBlockId,
      code,
      language,
      messageId,
      status: 'pending', // pending, approved, changes-requested
      comments: [],
      createdAt: timestamp,
      updatedAt: timestamp,
      reviewer: 'user', // Could be expanded for multi-user
      metadata: {
        totalComments: 0,
        resolvedComments: 0,
        unresolvedComments: 0
      }
    };
    
    this.reviews[id] = review;
    this.saveReviews();
    
    return review;
  }
  
  // Get review by ID
  getReview(reviewId) {
    return this.reviews[reviewId] || null;
  }
  
  // Get all reviews
  getAllReviews() {
    return Object.values(this.reviews);
  }
  
  // Get reviews by status
  getReviewsByStatus(status) {
    return Object.values(this.reviews).filter(r => r.status === status);
  }
  
  // Add comment to review
  addComment(reviewId, { line, text, type = 'suggestion' }) {
    const review = this.reviews[reviewId];
    if (!review) {
      throw new Error('Review not found');
    }
    
    const commentId = `comment-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const timestamp = new Date().toISOString();
    
    const comment = {
      id: commentId,
      line,
      text,
      type, // suggestion, question, praise, issue
      resolved: false,
      replies: [],
      createdAt: timestamp,
      updatedAt: timestamp,
      author: 'user'
    };
    
    review.comments.push(comment);
    review.updatedAt = timestamp;
    review.metadata.totalComments++;
    review.metadata.unresolvedComments++;
    
    this.saveReviews();
    return comment;
  }
  
  // Add reply to comment
  addReply(reviewId, commentId, { text }) {
    const review = this.reviews[reviewId];
    if (!review) {
      throw new Error('Review not found');
    }
    
    const comment = review.comments.find(c => c.id === commentId);
    if (!comment) {
      throw new Error('Comment not found');
    }
    
    const replyId = `reply-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const timestamp = new Date().toISOString();
    
    const reply = {
      id: replyId,
      text,
      createdAt: timestamp,
      author: 'user'
    };
    
    comment.replies.push(reply);
    comment.updatedAt = timestamp;
    review.updatedAt = timestamp;
    
    this.saveReviews();
    return reply;
  }
  
  // Resolve comment
  resolveComment(reviewId, commentId) {
    const review = this.reviews[reviewId];
    if (!review) {
      throw new Error('Review not found');
    }
    
    const comment = review.comments.find(c => c.id === commentId);
    if (!comment) {
      throw new Error('Comment not found');
    }
    
    comment.resolved = true;
    comment.updatedAt = new Date().toISOString();
    review.updatedAt = new Date().toISOString();
    review.metadata.resolvedComments++;
    review.metadata.unresolvedComments--;
    
    this.saveReviews();
    return comment;
  }
  
  // Unresolve comment
  unresolveComment(reviewId, commentId) {
    const review = this.reviews[reviewId];
    if (!review) {
      throw new Error('Review not found');
    }
    
    const comment = review.comments.find(c => c.id === commentId);
    if (!comment) {
      throw new Error('Comment not found');
    }
    
    comment.resolved = false;
    comment.updatedAt = new Date().toISOString();
    review.updatedAt = new Date().toISOString();
    review.metadata.resolvedComments--;
    review.metadata.unresolvedComments++;
    
    this.saveReviews();
    return comment;
  }
  
  // Update review status
  updateStatus(reviewId, status) {
    const review = this.reviews[reviewId];
    if (!review) {
      throw new Error('Review not found');
    }
    
    review.status = status;
    review.updatedAt = new Date().toISOString();
    
    this.saveReviews();
    return review;
  }
  
  // Approve review
  approveReview(reviewId) {
    return this.updateStatus(reviewId, 'approved');
  }
  
  // Request changes
  requestChanges(reviewId) {
    return this.updateStatus(reviewId, 'changes-requested');
  }
  
  // Delete review
  deleteReview(reviewId) {
    if (!this.reviews[reviewId]) {
      throw new Error('Review not found');
    }
    
    delete this.reviews[reviewId];
    this.saveReviews();
    return true;
  }
  
  // Delete comment
  deleteComment(reviewId, commentId) {
    const review = this.reviews[reviewId];
    if (!review) {
      throw new Error('Review not found');
    }
    
    const commentIndex = review.comments.findIndex(c => c.id === commentId);
    if (commentIndex === -1) {
      throw new Error('Comment not found');
    }
    
    const comment = review.comments[commentIndex];
    review.comments.splice(commentIndex, 1);
    review.metadata.totalComments--;
    
    if (comment.resolved) {
      review.metadata.resolvedComments--;
    } else {
      review.metadata.unresolvedComments--;
    }
    
    review.updatedAt = new Date().toISOString();
    this.saveReviews();
    return true;
  }
  
  // Get statistics
  getStatistics() {
    const reviews = Object.values(this.reviews);
    
    return {
      total: reviews.length,
      pending: reviews.filter(r => r.status === 'pending').length,
      approved: reviews.filter(r => r.status === 'approved').length,
      changesRequested: reviews.filter(r => r.status === 'changes-requested').length,
      totalComments: reviews.reduce((sum, r) => sum + r.metadata.totalComments, 0),
      resolvedComments: reviews.reduce((sum, r) => sum + r.metadata.resolvedComments, 0),
      unresolvedComments: reviews.reduce((sum, r) => sum + r.metadata.unresolvedComments, 0)
    };
  }
}

// Singleton instance
const codeReviewManager = new CodeReviewManager();

export default codeReviewManager;
export { CodeReviewManager };
