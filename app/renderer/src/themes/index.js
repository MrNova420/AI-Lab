/**
 * Theme Registry and Manager for AI-Lab
 * Central management for all themes
 */

import darkTheme from './dark.js';
import lightTheme from './light.js';
import highContrastTheme from './highContrast.js';
import draculaTheme from './dracula.js';
import nordTheme from './nord.js';
import githubDarkTheme from './githubDark.js';
import monokaiTheme from './monokai.js';

// Theme registry
export const themes = {
  dark: darkTheme,
  light: lightTheme,
  'high-contrast': highContrastTheme,
  dracula: draculaTheme,
  nord: nordTheme,
  'github-dark': githubDarkTheme,
  monokai: monokaiTheme,
};

// Default theme
export const defaultTheme = 'dark';

// Get theme by ID
export const getTheme = (themeId) => {
  return themes[themeId] || themes[defaultTheme];
};

// Get all theme IDs
export const getThemeIds = () => {
  return Object.keys(themes);
};

// Get all themes
export const getAllThemes = () => {
  return Object.values(themes);
};

// Apply theme to document
export const applyTheme = (themeId) => {
  const theme = getTheme(themeId);
  const root = document.documentElement;
  
  // Apply colors
  Object.entries(theme.colors).forEach(([key, value]) => {
    if (typeof value === 'object') {
      // Handle nested objects like syntax
      Object.entries(value).forEach(([subKey, subValue]) => {
        root.style.setProperty(`--color-${key}-${subKey}`, subValue);
      });
    } else {
      root.style.setProperty(`--color-${key}`, value);
    }
  });
  
  // Apply typography
  Object.entries(theme.typography).forEach(([key, value]) => {
    if (typeof value === 'object') {
      Object.entries(value).forEach(([subKey, subValue]) => {
        root.style.setProperty(`--typography-${key}-${subKey}`, subValue);
      });
    } else {
      root.style.setProperty(`--typography-${key}`, value);
    }
  });
  
  // Apply spacing
  Object.entries(theme.spacing).forEach(([key, value]) => {
    root.style.setProperty(`--spacing-${key}`, value);
  });
  
  // Apply border radius
  Object.entries(theme.borderRadius).forEach(([key, value]) => {
    root.style.setProperty(`--radius-${key}`, value);
  });
  
  // Apply shadows
  Object.entries(theme.shadows).forEach(([key, value]) => {
    root.style.setProperty(`--shadow-${key}`, value);
  });
  
  // Apply transitions
  Object.entries(theme.transitions).forEach(([key, value]) => {
    root.style.setProperty(`--transition-${key}`, value);
  });
  
  // Store current theme
  localStorage.setItem('ai-lab-theme', themeId);
  
  return theme;
};

// Load saved theme or default
export const loadSavedTheme = () => {
  const savedTheme = localStorage.getItem('ai-lab-theme');
  return applyTheme(savedTheme || defaultTheme);
};

// Note: useTheme hook is provided by contexts/ThemeContext.jsx
// Import it here to re-export for convenience
export { useTheme } from '../contexts/ThemeContext';

export default {
  themes,
  getTheme,
  getAllThemes,
  getThemeIds,
  applyTheme,
  loadSavedTheme,
  defaultTheme,
};
