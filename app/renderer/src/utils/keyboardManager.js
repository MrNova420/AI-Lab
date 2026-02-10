/**
 * Keyboard Shortcuts Manager for AI-Lab
 * Comprehensive keyboard navigation and command system
 */

import { useHotkeys } from 'react-hotkeys-hook';

// Shortcut categories and definitions
export const shortcuts = {
  // Navigation shortcuts
  navigation: {
    commandPalette: { keys: 'mod+k', description: 'Open command palette', action: 'openCommandPalette' },
    showShortcuts: { keys: 'mod+/', description: 'Show keyboard shortcuts', action: 'showShortcuts' },
    newChat: { keys: 'mod+n', description: 'New chat', action: 'newChat' },
    openSession: { keys: 'mod+o', description: 'Open session', action: 'openSession' },
    saveSession: { keys: 'mod+s', description: 'Save session', action: 'saveSession' },
    closeSession: { keys: 'mod+w', description: 'Close session', action: 'closeSession' },
    settings: { keys: 'mod+,', description: 'Open settings', action: 'openSettings' },
    toggleSidebar: { keys: 'mod+b', description: 'Toggle sidebar', action: 'toggleSidebar' },
    showHistory: { keys: 'mod+h', description: 'Show history', action: 'showHistory' },
    findInConversation: { keys: 'mod+f', description: 'Find in conversation', action: 'findInConversation' },
    goToMessage: { keys: 'mod+g', description: 'Go to message', action: 'goToMessage' },
    previousSession: { keys: 'mod+[', description: 'Previous session', action: 'previousSession' },
    nextSession: { keys: 'mod+]', description: 'Next session', action: 'nextSession' },
  },
  
  // Editing shortcuts
  editing: {
    sendMessage: { keys: 'mod+enter', description: 'Send message', action: 'sendMessage' },
    undo: { keys: 'mod+z', description: 'Undo', action: 'undo' },
    redo: { keys: 'mod+y', description: 'Redo', action: 'redo' },
    copy: { keys: 'mod+c', description: 'Copy', action: 'copy' },
    paste: { keys: 'mod+v', description: 'Paste', action: 'paste' },
    cut: { keys: 'mod+x', description: 'Cut', action: 'cut' },
    selectAll: { keys: 'mod+a', description: 'Select all', action: 'selectAll' },
    duplicateLine: { keys: 'mod+d', description: 'Duplicate line', action: 'duplicateLine' },
    selectLine: { keys: 'mod+l', description: 'Select line', action: 'selectLine' },
    deleteLine: { keys: 'mod+shift+k', description: 'Delete line', action: 'deleteLine' },
    moveLineUp: { keys: 'mod+shift+up', description: 'Move line up', action: 'moveLineUp' },
    moveLineDown: { keys: 'mod+shift+down', description: 'Move line down', action: 'moveLineDown' },
  },
  
  // Feature shortcuts
  features: {
    toggleCommander: { keys: 'mod+shift+c', description: 'Toggle Commander Mode', action: 'toggleCommander' },
    toggleWebSearch: { keys: 'mod+shift+w', description: 'Toggle Web Search', action: 'toggleWebSearch' },
    toggleVoice: { keys: 'mod+shift+v', description: 'Toggle Voice Mode', action: 'toggleVoice' },
    regenerate: { keys: 'mod+r', description: 'Regenerate response', action: 'regenerate' },
    editMessage: { keys: 'mod+e', description: 'Edit message', action: 'editMessage' },
    deleteMessage: { keys: 'mod+delete', description: 'Delete message', action: 'deleteMessage' },
    pinMessage: { keys: 'mod+p', description: 'Pin message', action: 'pinMessage' },
    newWorkflow: { keys: 'mod+t', description: 'New workflow', action: 'newWorkflow' },
    openWorkflow: { keys: 'mod+shift+t', description: 'Open workflow', action: 'openWorkflow' },
    saveWorkflow: { keys: 'mod+shift+s', description: 'Save workflow', action: 'saveWorkflow' },
    createBranch: { keys: 'mod+shift+b', description: 'Create branch', action: 'createBranch' },
    mergeBranch: { keys: 'mod+shift+m', description: 'Merge branch', action: 'mergeBranch' },
    createArtifact: { keys: 'mod+shift+a', description: 'Create artifact', action: 'createArtifact' },
    editArtifact: { keys: 'mod+shift+e', description: 'Edit artifact', action: 'editArtifact' },
    exportArtifact: { keys: 'mod+shift+x', description: 'Export artifact', action: 'exportArtifact' },
    startReview: { keys: 'mod+shift+r', description: 'Start code review', action: 'startReview' },
    addComment: { keys: 'mod+shift+l', description: 'Add review comment', action: 'addComment' },
    approveReview: { keys: 'mod+shift+p', description: 'Approve review', action: 'approveReview' },
    requestChanges: { keys: 'mod+shift+h', description: 'Request changes', action: 'requestChanges' },
    toggleFullscreen: { keys: 'mod+shift+f', description: 'Toggle fullscreen', action: 'toggleFullscreen' },
  },
  
  // Quick number shortcuts (switch tabs)
  quick: {
    switchTab1: { keys: 'mod+1', description: 'Switch to tab 1', action: 'switchTab', params: { tab: 0 } },
    switchTab2: { keys: 'mod+2', description: 'Switch to tab 2', action: 'switchTab', params: { tab: 1 } },
    switchTab3: { keys: 'mod+3', description: 'Switch to tab 3', action: 'switchTab', params: { tab: 2 } },
    switchTab4: { keys: 'mod+4', description: 'Switch to tab 4', action: 'switchTab', params: { tab: 3 } },
    switchTab5: { keys: 'mod+5', description: 'Switch to tab 5', action: 'switchTab', params: { tab: 4 } },
  }
};

// Command palette commands
export const commands = [
  { id: 'newChat', label: 'New Chat', category: 'Navigation', keywords: ['new', 'chat', 'conversation'] },
  { id: 'openSession', label: 'Open Session', category: 'Navigation', keywords: ['open', 'session', 'load'] },
  { id: 'saveSession', label: 'Save Session', category: 'Navigation', keywords: ['save', 'session', 'store'] },
  { id: 'exportSession', label: 'Export Session', category: 'File', keywords: ['export', 'download', 'save'] },
  { id: 'openSettings', label: 'Settings', category: 'Navigation', keywords: ['settings', 'preferences', 'config'] },
  { id: 'toggleTheme', label: 'Toggle Theme', category: 'Appearance', keywords: ['theme', 'dark', 'light'] },
  { id: 'toggleCommander', label: 'Toggle Commander Mode', category: 'Features', keywords: ['commander', 'mode', 'tools'] },
  { id: 'toggleWebSearch', label: 'Toggle Web Search', category: 'Features', keywords: ['web', 'search', 'internet'] },
  { id: 'createWorkflow', label: 'Create Workflow', category: 'Workflow', keywords: ['workflow', 'create', 'new'] },
  { id: 'openWorkflow', label: 'Open Workflow', category: 'Workflow', keywords: ['workflow', 'open', 'load'] },
  { id: 'marketplace', label: 'Marketplace', category: 'Workflow', keywords: ['marketplace', 'templates', 'browse'] },
  { id: 'createArtifact', label: 'New Artifact', category: 'Artifacts', keywords: ['artifact', 'create', 'new'] },
  { id: 'viewArtifacts', label: 'View Artifacts', category: 'Artifacts', keywords: ['artifacts', 'view', 'library'] },
  { id: 'createBranch', label: 'Create Branch', category: 'Branching', keywords: ['branch', 'create', 'fork'] },
  { id: 'viewBranches', label: 'View Branches', category: 'Branching', keywords: ['branches', 'view', 'tree'] },
  { id: 'startReview', label: 'Start Review', category: 'Code Review', keywords: ['review', 'code', 'start'] },
  { id: 'viewReviews', label: 'View Reviews', category: 'Code Review', keywords: ['reviews', 'view', 'list'] },
  { id: 'showContext', label: 'Show Context', category: 'Context', keywords: ['context', 'show', 'view'] },
  { id: 'compressContext', label: 'Compress Context', category: 'Context', keywords: ['compress', 'context', 'optimize'] },
  { id: 'showShortcuts', label: 'Keyboard Shortcuts', category: 'Help', keywords: ['shortcuts', 'keyboard', 'help'] },
  { id: 'documentation', label: 'Documentation', category: 'Help', keywords: ['docs', 'documentation', 'help'] },
];

// Keyboard shortcuts hook
export const useKeyboardShortcuts = (handlers) => {
  // Flatten all shortcuts
  const allShortcuts = Object.values(shortcuts).reduce((acc, category) => {
    return { ...acc, ...category };
  }, {});
  
  // Register each shortcut
  Object.entries(allShortcuts).forEach(([key, shortcut]) => {
    const handler = handlers[shortcut.action];
    if (handler) {
      useHotkeys(shortcut.keys, (e) => {
        e.preventDefault();
        handler(shortcut.params);
      }, [handler]);
    }
  });
};

// Get all shortcuts as flat array
export const getAllShortcuts = () => {
  return Object.entries(shortcuts).reduce((acc, [category, shortcuts]) => {
    return [
      ...acc,
      ...Object.entries(shortcuts).map(([key, shortcut]) => ({
        ...shortcut,
        category,
        id: key
      }))
    ];
  }, []);
};

// Search shortcuts
export const searchShortcuts = (query) => {
  const allShortcuts = getAllShortcuts();
  const lowerQuery = query.toLowerCase();
  
  return allShortcuts.filter(shortcut => 
    shortcut.description.toLowerCase().includes(lowerQuery) ||
    shortcut.keys.toLowerCase().includes(lowerQuery)
  );
};

// Search commands
export const searchCommands = (query) => {
  const lowerQuery = query.toLowerCase();
  
  return commands.filter(command =>
    command.label.toLowerCase().includes(lowerQuery) ||
    command.keywords.some(keyword => keyword.includes(lowerQuery))
  );
};

export default {
  shortcuts,
  commands,
  useKeyboardShortcuts,
  getAllShortcuts,
  searchShortcuts,
  searchCommands
};
