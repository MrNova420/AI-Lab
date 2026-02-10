/**
 * Theme Context Provider
 * Provides theme context to entire application
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { applyTheme, loadSavedTheme, getAllThemes } from '../themes';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [currentThemeId, setCurrentThemeId] = useState('dark');
  const [theme, setTheme] = useState(null);
  
  // Load saved theme on mount
  useEffect(() => {
    const savedTheme = loadSavedTheme();
    setTheme(savedTheme);
    setCurrentThemeId(savedTheme.id);
  }, []);
  
  // Change theme
  const changeTheme = (themeId) => {
    const newTheme = applyTheme(themeId);
    setTheme(newTheme);
    setCurrentThemeId(themeId);
  };
  
  // Get all available themes
  const availableThemes = getAllThemes();
  
  const value = {
    theme,
    currentThemeId,
    changeTheme,
    availableThemes
  };
  
  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeProvider;
