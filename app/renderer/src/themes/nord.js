/**
 * Nord Theme for AI-Lab
 * Cool minimal Arctic-inspired theme
 */

export const nordTheme = {
  name: 'Nord',
  id: 'nord',
  colors: {
    // Primary colors
    primary: '#88c0d0',
    primaryHover: '#81a1c1',
    primaryActive: '#5e81ac',
    
    // Background colors
    background: '#2e3440',
    backgroundAlt: '#3b4252',
    surface: '#434c5e',
    surfaceAlt: '#4c566a',
    
    // Text colors
    text: '#eceff4',
    textSecondary: '#e5e9f0',
    textTertiary: '#d8dee9',
    textDisabled: '#4c566a',
    
    // Semantic colors
    success: '#a3be8c',
    warning: '#ebcb8b',
    error: '#bf616a',
    info: '#88c0d0',
    
    // UI Elements
    border: '#4c566a',
    divider: '#434c5e',
    hover: '#3b4252',
    active: '#434c5e',
    focus: '#88c0d0',
    
    // Syntax highlighting
    syntax: {
      keyword: '#81a1c1',
      string: '#a3be8c',
      number: '#b48ead',
      comment: '#616e88',
      function: '#88c0d0',
      variable: '#d8dee9',
      operator: '#81a1c1',
      tag: '#81a1c1',
      attribute: '#8fbcbb',
      constant: '#5e81ac',
    }
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    monoFamily: "'Fira Code', 'Consolas', 'Monaco', monospace",
    sizes: {
      xs: '12px',
      sm: '14px',
      base: '16px',
      lg: '18px',
      xl: '20px',
      '2xl': '24px',
      '3xl': '30px',
      '4xl': '36px'
    },
    weights: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700
    },
    lineHeights: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.75
    }
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    '2xl': '48px',
    '3xl': '64px'
  },
  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px'
  },
  shadows: {
    sm: '0 1px 2px rgba(0,0,0,0.3)',
    md: '0 4px 6px rgba(0,0,0,0.3)',
    lg: '0 10px 15px rgba(0,0,0,0.4)',
    xl: '0 20px 25px rgba(0,0,0,0.5)',
    inner: 'inset 0 2px 4px rgba(0,0,0,0.2)'
  },
  transitions: {
    fast: '150ms ease-in-out',
    normal: '250ms ease-in-out',
    slow: '400ms ease-in-out'
  }
};

export default nordTheme;
