// Session Manager - Backend-integrated session management
// Replaces localStorage-based approach with proper backend persistence

const API_BASE = 'http://localhost:5174/api';

// Session timeout: 30 minutes of inactivity
const SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

/**
 * Session Manager Class
 * Handles all session operations with backend integration
 * Includes smart session resumption and activity tracking
 */
class SessionManager {
  constructor() {
    this.currentSession = null;
    this.autoSaveInterval = null;
    this.autoSaveDelay = 5000; // Auto-save every 5 seconds
    this.lastActivity = null;
    this.loadLastActivity();
  }

  /**
   * Load last activity timestamp from localStorage
   */
  loadLastActivity() {
    try {
      const stored = localStorage.getItem('session_last_activity');
      if (stored) {
        this.lastActivity = new Date(stored);
      }
    } catch (error) {
      console.error('Error loading last activity:', error);
    }
  }

  /**
   * Save last activity timestamp to localStorage
   */
  saveLastActivity() {
    try {
      this.lastActivity = new Date();
      localStorage.setItem('session_last_activity', this.lastActivity.toISOString());
    } catch (error) {
      console.error('Error saving last activity:', error);
    }
  }

  /**
   * Check if last session is still fresh (< 30 min old)
   * @returns {boolean} True if session is fresh
   */
  isSessionFresh() {
    if (!this.lastActivity) {
      return false;
    }
    
    const now = new Date();
    const timeSinceActivity = now - this.lastActivity;
    return timeSinceActivity < SESSION_TIMEOUT_MS;
  }

  /**
   * Get time since last activity in human-readable format
   * @returns {string} Time description
   */
  getTimeSinceActivity() {
    if (!this.lastActivity) {
      return 'Never';
    }
    
    const now = new Date();
    const minutes = Math.floor((now - this.lastActivity) / (60 * 1000));
    
    if (minutes < 1) return 'Just now';
    if (minutes === 1) return '1 minute ago';
    if (minutes < 60) return `${minutes} minutes ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours === 1) return '1 hour ago';
    if (hours < 24) return `${hours} hours ago`;
    
    const days = Math.floor(hours / 24);
    if (days === 1) return '1 day ago';
    return `${days} days ago`;
  }

  /**
   * Update activity timestamp (call on every user action)
   */
  updateActivity() {
    this.saveLastActivity();
  }

  /**
   * Start a new session
   * @param {string} userName - User name for the session (deprecated, uses current user)
   * @param {object} metadata - Additional metadata
   * @returns {Promise<string>} Session ID
   */
  async startNewSession(userName = 'User', metadata = {}) {
    try {
      const response = await fetch(`${API_BASE}/sessions/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ metadata })
      });
      
      const data = await response.json();
      
      if (data.session_id) {
        this.currentSession = {
          session_id: data.session_id,
          started_at: data.started_at,
          user_name: data.user_name || userName,
          user_id: data.user_id,
          messages: [],
          metadata
        };
        
        // Update activity timestamp
        this.updateActivity();
        
        // Start auto-save
        this.startAutoSave();
        
        console.log(`✅ New session started: ${data.session_id}`);
        return data.session_id;
      } else {
        throw new Error('Failed to start session');
      }
    } catch (error) {
      console.error('Error starting session:', error);
      throw error;
    }
  }

  /**
   * Load an existing session
   * @param {string} sessionId - Session ID to load
   * @returns {Promise<object>} Session data with full message history
   */
  async loadSession(sessionId) {
    try {
      const response = await fetch(`${API_BASE}/sessions/load`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
      
      const sessionData = await response.json();
      
      if (sessionData.session_id) {
        this.currentSession = sessionData;
        
        // Start auto-save
        this.startAutoSave();
        
        console.log(`📥 Loaded session: ${sessionId} (${sessionData.messages.length} messages)`);
        return sessionData;
      } else {
        throw new Error('Session not found');
      }
    } catch (error) {
      console.error('Error loading session:', error);
      throw error;
    }
  }

  /**
   * List all sessions
   * @param {number} limit - Max number of sessions to return
   * @param {number} offset - Offset for pagination
   * @returns {Promise<object>} Sessions list with metadata
   */
  async listSessions(limit = 100, offset = 0) {
    try {
      const response = await fetch(`${API_BASE}/sessions/list`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit, offset })
      });
      
      const data = await response.json();
      console.log(`📋 Listed ${data.sessions.length} sessions`);
      return data;
    } catch (error) {
      console.error('Error listing sessions:', error);
      throw error;
    }
  }

  /**
   * Delete a session
   * @param {string} sessionId - Session ID to delete
   * @returns {Promise<boolean>} Success status
   */
  async deleteSession(sessionId) {
    try {
      const response = await fetch(`${API_BASE}/sessions/delete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // If we deleted the current session, clear it
        if (this.currentSession && this.currentSession.session_id === sessionId) {
          this.currentSession = null;
          this.stopAutoSave();
        }
        
        console.log(`🗑️ Deleted session: ${sessionId}`);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error deleting session:', error);
      throw error;
    }
  }

  /**
   * Save current session to backend
   * @returns {Promise<boolean>} Success status
   */
  async saveSession() {
    if (!this.currentSession) {
      return false;
    }

    try {
      const response = await fetch(`${API_BASE}/sessions/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.currentSession)
      });
      
      const data = await response.json();
      
      if (data.success) {
        console.log(`💾 Session saved: ${this.currentSession.session_id}`);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error saving session:', error);
      return false;
    }
  }

  /**
   * Add a message to the current session
   * @param {string} role - Message role (user/assistant)
   * @param {string} content - Message content
   * @param {object} metadata - Additional metadata
   */
  addMessage(role, content, metadata = {}) {
    if (!this.currentSession) {
      throw new Error('No active session');
    }

    const message = {
      role,
      content,
      timestamp: new Date().toISOString(),
      metadata
    };

    this.currentSession.messages.push(message);
    this.currentSession.last_updated = new Date().toISOString();
    
    // Update activity timestamp on every message
    this.updateActivity();
    
    // Update stats
    if (!this.currentSession.stats) {
      this.currentSession.stats = {
        total_messages: 0,
        user_messages: 0,
        assistant_messages: 0,
        errors: 0
      };
    }
    
    this.currentSession.stats.total_messages++;
    if (role === 'user') {
      this.currentSession.stats.user_messages++;
    } else if (role === 'assistant') {
      this.currentSession.stats.assistant_messages++;
    }
    
    return message;
  }

  /**
   * Get current session
   * @returns {object|null} Current session data
   */
  getCurrentSession() {
    return this.currentSession;
  }

  /**
   * Get current session ID
   * @returns {string|null} Session ID
   */
  getCurrentSessionId() {
    return this.currentSession ? this.currentSession.session_id : null;
  }

  /**
   * Get messages from current session
   * @returns {array} Messages array
   */
  getMessages() {
    return this.currentSession ? this.currentSession.messages : [];
  }

  /**
   * Clear current session (doesn't delete from backend)
   */
  clearCurrentSession() {
    this.stopAutoSave();
    this.currentSession = null;
    console.log('🧹 Current session cleared');
  }

  /**
   * Start auto-save timer
   */
  startAutoSave() {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
    }
    
    this.autoSaveInterval = setInterval(() => {
      if (this.currentSession && this.currentSession.messages.length > 0) {
        this.saveSession();
      }
    }, this.autoSaveDelay);
  }

  /**
   * Stop auto-save timer
   */
  stopAutoSave() {
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
      this.autoSaveInterval = null;
    }
  }

  /**
   * Export session
   * @param {string} sessionId - Session ID to export (optional, uses current if not provided)
   * @param {string} format - Export format (jsonl, json)
   * @returns {Promise<string>} Export file path
   */
  async exportSession(sessionId = null, format = 'jsonl') {
    try {
      const response = await fetch(`${API_BASE}/sessions/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          session_id: sessionId || this.getCurrentSessionId(),
          format 
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        console.log(`📤 Session exported: ${data.export_path}`);
        return data.export_path;
      }
      throw new Error('Export failed');
    } catch (error) {
      console.error('Error exporting session:', error);
      throw error;
    }
  }
}

// Create singleton instance
const sessionManager = new SessionManager();

export default sessionManager;

// Named exports for convenience
export {
  sessionManager,
  SessionManager
};
