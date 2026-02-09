// State persistence utility
// Manages localStorage for user preferences, mode settings, and chat history

const STORAGE_KEYS = {
  COMMANDER_MODE: 'ailab_commander_mode',
  WEB_SEARCH_MODE: 'ailab_web_search_mode',
  CHAT_HISTORY: 'ailab_chat_history',
  VOICE_HISTORY: 'ailab_voice_history',
  USER_PREFERENCES: 'ailab_user_preferences',
  SESSION_STATE: 'ailab_session_state'
};

// Default preferences
const DEFAULT_PREFERENCES = {
  theme: 'dark',
  fontSize: 'medium',
  autoScroll: true,
  soundEnabled: true,
  notificationsEnabled: false,
  maxHistorySize: 100
};

/**
 * Save mode preferences
 */
export function saveModePreferences(commanderMode, webSearchMode) {
  try {
    localStorage.setItem(STORAGE_KEYS.COMMANDER_MODE, JSON.stringify(commanderMode));
    localStorage.setItem(STORAGE_KEYS.WEB_SEARCH_MODE, JSON.stringify(webSearchMode));
    console.log('💾 Mode preferences saved');
  } catch (error) {
    console.error('Failed to save mode preferences:', error);
  }
}

/**
 * Load mode preferences
 */
export function loadModePreferences() {
  try {
    const commander = localStorage.getItem(STORAGE_KEYS.COMMANDER_MODE);
    const webSearch = localStorage.getItem(STORAGE_KEYS.WEB_SEARCH_MODE);
    
    return {
      commanderMode: commander ? JSON.parse(commander) : false,
      webSearchMode: webSearch ? JSON.parse(webSearch) : false
    };
  } catch (error) {
    console.error('Failed to load mode preferences:', error);
    return { commanderMode: false, webSearchMode: false };
  }
}

/**
 * Save chat history
 */
export function saveChatHistory(messages, maxSize = 100) {
  try {
    // Limit history size to prevent storage bloat
    const limitedMessages = messages.slice(-maxSize);
    localStorage.setItem(STORAGE_KEYS.CHAT_HISTORY, JSON.stringify(limitedMessages));
    console.log(`💾 Chat history saved (${limitedMessages.length} messages)`);
  } catch (error) {
    console.error('Failed to save chat history:', error);
  }
}

/**
 * Load chat history
 */
export function loadChatHistory() {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.CHAT_HISTORY);
    if (stored) {
      const messages = JSON.parse(stored);
      console.log(`📥 Loaded ${messages.length} messages from history`);
      return messages;
    }
  } catch (error) {
    console.error('Failed to load chat history:', error);
  }
  return [];
}

/**
 * Clear chat history
 */
export function clearChatHistory() {
  try {
    localStorage.removeItem(STORAGE_KEYS.CHAT_HISTORY);
    console.log('🗑️ Chat history cleared');
  } catch (error) {
    console.error('Failed to clear chat history:', error);
  }
}

/**
 * Save voice history
 */
export function saveVoiceHistory(messages, maxSize = 50) {
  try {
    const limitedMessages = messages.slice(-maxSize);
    localStorage.setItem(STORAGE_KEYS.VOICE_HISTORY, JSON.stringify(limitedMessages));
    console.log(`💾 Voice history saved (${limitedMessages.length} messages)`);
  } catch (error) {
    console.error('Failed to save voice history:', error);
  }
}

/**
 * Load voice history
 */
export function loadVoiceHistory() {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.VOICE_HISTORY);
    if (stored) {
      const messages = JSON.parse(stored);
      console.log(`📥 Loaded ${messages.length} messages from voice history`);
      return messages;
    }
  } catch (error) {
    console.error('Failed to load voice history:', error);
  }
  return [];
}

/**
 * Clear voice history
 */
export function clearVoiceHistory() {
  try {
    localStorage.removeItem(STORAGE_KEYS.VOICE_HISTORY);
    console.log('🗑️ Voice history cleared');
  } catch (error) {
    console.error('Failed to clear voice history:', error);
  }
}

/**
 * Save user preferences
 */
export function saveUserPreferences(preferences) {
  try {
    const mergedPrefs = { ...DEFAULT_PREFERENCES, ...preferences };
    localStorage.setItem(STORAGE_KEYS.USER_PREFERENCES, JSON.stringify(mergedPrefs));
    console.log('💾 User preferences saved');
  } catch (error) {
    console.error('Failed to save user preferences:', error);
  }
}

/**
 * Load user preferences
 */
export function loadUserPreferences() {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.USER_PREFERENCES);
    if (stored) {
      return { ...DEFAULT_PREFERENCES, ...JSON.parse(stored) };
    }
  } catch (error) {
    console.error('Failed to load user preferences:', error);
  }
  return DEFAULT_PREFERENCES;
}

/**
 * Save session state (for recovery)
 */
export function saveSessionState(state) {
  try {
    const sessionData = {
      ...state,
      timestamp: new Date().toISOString()
    };
    localStorage.setItem(STORAGE_KEYS.SESSION_STATE, JSON.stringify(sessionData));
    console.log('💾 Session state saved');
  } catch (error) {
    console.error('Failed to save session state:', error);
  }
}

/**
 * Load session state
 */
export function loadSessionState() {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.SESSION_STATE);
    if (stored) {
      const state = JSON.parse(stored);
      // Check if session is recent (within last 24 hours)
      const timestamp = new Date(state.timestamp);
      const now = new Date();
      const hoursDiff = (now - timestamp) / (1000 * 60 * 60);
      
      if (hoursDiff < 24) {
        console.log('📥 Session state recovered');
        return state;
      } else {
        console.log('⏰ Session state expired, clearing...');
        clearSessionState();
      }
    }
  } catch (error) {
    console.error('Failed to load session state:', error);
  }
  return null;
}

/**
 * Clear session state
 */
export function clearSessionState() {
  try {
    localStorage.removeItem(STORAGE_KEYS.SESSION_STATE);
    console.log('🗑️ Session state cleared');
  } catch (error) {
    console.error('Failed to clear session state:', error);
  }
}

/**
 * Clear all AI Lab data
 */
export function clearAllData() {
  try {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
    // Also clear tool stats
    localStorage.removeItem('toolExecutionStats');
    console.log('🗑️ All AI Lab data cleared');
  } catch (error) {
    console.error('Failed to clear all data:', error);
  }
}

/**
 * Export all data for backup
 */
export function exportAllData() {
  try {
    const data = {};
    Object.entries(STORAGE_KEYS).forEach(([name, key]) => {
      const value = localStorage.getItem(key);
      if (value) {
        data[name] = JSON.parse(value);
      }
    });
    
    // Include tool stats
    const toolStats = localStorage.getItem('toolExecutionStats');
    if (toolStats) {
      data.TOOL_STATS = JSON.parse(toolStats);
    }
    
    return data;
  } catch (error) {
    console.error('Failed to export data:', error);
    return null;
  }
}

/**
 * Import data from backup
 */
export function importAllData(data) {
  try {
    Object.entries(data).forEach(([name, value]) => {
      if (name === 'TOOL_STATS') {
        localStorage.setItem('toolExecutionStats', JSON.stringify(value));
      } else if (STORAGE_KEYS[name]) {
        localStorage.setItem(STORAGE_KEYS[name], JSON.stringify(value));
      }
    });
    console.log('📥 Data imported successfully');
    return true;
  } catch (error) {
    console.error('Failed to import data:', error);
    return false;
  }
}
