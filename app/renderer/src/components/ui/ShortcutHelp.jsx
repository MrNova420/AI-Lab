/**
 * Keyboard Shortcuts Help Component
 * Display all available keyboard shortcuts
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { modalAnimations } from '../../animations/transitions';
import { getAllShortcuts } from '../../utils/keyboardManager';

const ShortcutHelp = ({ isOpen, onClose }) => {
  const shortcuts = getAllShortcuts();
  
  // Group shortcuts by category
  const groupedShortcuts = shortcuts.reduce((acc, shortcut) => {
    if (!acc[shortcut.category]) {
      acc[shortcut.category] = [];
    }
    acc[shortcut.category].push(shortcut);
    return acc;
  }, {});
  
  const formatKeys = (keys) => {
    return keys
      .replace('mod', navigator.platform.includes('Mac') ? '⌘' : 'Ctrl')
      .replace('shift', '⇧')
      .replace('alt', '⌥')
      .replace('enter', '↵')
      .replace('up', '↑')
      .replace('down', '↓')
      .replace('left', '←')
      .replace('right', '→')
      .split('+')
      .map(key => key.trim());
  };
  
  if (!isOpen) return null;
  
  return (
    <AnimatePresence>
      <motion.div
        className="shortcut-help-backdrop"
        {...modalAnimations.backdrop}
        onClick={onClose}
      >
        <motion.div
          className="shortcut-help"
          {...modalAnimations.dialog}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="shortcut-help-header">
            <h2>Keyboard Shortcuts</h2>
            <button onClick={onClose} className="close-button">✕</button>
          </div>
          
          <div className="shortcut-help-content">
            {Object.entries(groupedShortcuts).map(([category, shortcuts]) => (
              <div key={category} className="shortcut-category">
                <h3 className="category-title">{category}</h3>
                <div className="shortcuts-list">
                  {shortcuts.map((shortcut) => (
                    <div key={shortcut.id} className="shortcut-item">
                      <div className="shortcut-description">
                        {shortcut.description}
                      </div>
                      <div className="shortcut-keys">
                        {formatKeys(shortcut.keys).map((key, index) => (
                          <React.Fragment key={index}>
                            {index > 0 && <span className="key-separator">+</span>}
                            <kbd className="key">{key}</kbd>
                          </React.Fragment>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          
          <div className="shortcut-help-footer">
            <button onClick={onClose} className="btn-primary">
              Close
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ShortcutHelp;
