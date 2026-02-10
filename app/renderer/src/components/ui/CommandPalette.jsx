/**
 * Command Palette Component
 * Quick command execution interface (Cmd/Ctrl + K)
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { modalAnimations } from '../../animations/transitions';
import { searchCommands } from '../../utils/keyboardManager';

const CommandPalette = ({ isOpen, onClose, onExecuteCommand }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);
  
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);
  
  useEffect(() => {
    if (query.trim()) {
      const searchResults = searchCommands(query);
      setResults(searchResults);
      setSelectedIndex(0);
    } else {
      // Show all commands when no query
      setResults(searchCommands(''));
    }
  }, [query]);
  
  const handleKeyDown = (e) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (results[selectedIndex]) {
          executeCommand(results[selectedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        onClose();
        break;
    }
  };
  
  const executeCommand = (command) => {
    onExecuteCommand(command.id);
    onClose();
  };
  
  if (!isOpen) return null;
  
  return (
    <AnimatePresence>
      <motion.div
        className="command-palette-backdrop"
        {...modalAnimations.backdrop}
        onClick={onClose}
      >
        <motion.div
          className="command-palette"
          {...modalAnimations.dialog}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="command-palette-header">
            <input
              ref={inputRef}
              type="text"
              className="command-palette-input"
              placeholder="Type a command or search..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
            />
          </div>
          
          <div className="command-palette-results">
            {results.length === 0 ? (
              <div className="command-palette-empty">
                No commands found
              </div>
            ) : (
              results.map((command, index) => (
                <motion.div
                  key={command.id}
                  className={`command-palette-item ${index === selectedIndex ? 'selected' : ''}`}
                  onClick={() => executeCommand(command)}
                  whileHover={{ backgroundColor: 'var(--color-hover)' }}
                >
                  <div className="command-info">
                    <div className="command-label">{command.label}</div>
                    <div className="command-category">{command.category}</div>
                  </div>
                </motion.div>
              ))
            )}
          </div>
          
          <div className="command-palette-footer">
            <div className="command-palette-hint">
              <kbd>↑↓</kbd> Navigate
              <kbd>Enter</kbd> Execute
              <kbd>Esc</kbd> Close
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default CommandPalette;
