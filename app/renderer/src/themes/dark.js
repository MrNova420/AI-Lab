/**
 * Dark Theme for AI-Lab
 * Professional dark mode with excellent contrast
 */

export const darkTheme = {
  name: 'Dark',
  id: 'dark',
  colors: {
    // Primary colors
    primary: '#0066cc',
    primaryHover: '#0052a3',
    primaryActive: '#004080',
    
    // Background colors
    background: '#1e1e1e',
    backgroundAlt: '#252525',
    surface: '#2d2d2d',
    surfaceAlt: '#383838',
    
    // Text colors
    text: '#ffffff',
    textSecondary: '#cccccc',
    textTertiary: '#999999',
    textDisabled: '#666666',
    
    // Semantic colors
    success: '#4caf50',
    warning: '#ff9800',
    error: '#f44336',
    info: '#2196f3',
    
    // UI Elements
    border: '#404040',
    divider: '#333333',
    hover: '#323232',
    active: '#404040',
    focus: '#0066cc',
    
    // Syntax highlighting
    syntax: {
      keyword: '#c586c0',
      string: '#ce9178',
      number: '#b5cea8',
      comment: '#6a9955',
      function: '#dcdcaa',
      variable: '#9cdcfe',
      operator: '#d4d4d4',
      tag: '#569cd6',
      attribute: '#9cdcfe',
      constant: '#4fc1ff',
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
    sm: '0 1px 2px rgba(0,0,0,0.2)',
    md: '0 4px 6px rgba(0,0,0,0.2)',
    lg: '0 10px 15px rgba(0,0,0,0.3)',
    xl: '0 20px 25px rgba(0,0,0,0.4)',
    inner: 'inset 0 2px 4px rgba(0,0,0,0.1)'
  },
  transitions: {
    fast: '150ms ease-in-out',
    normal: '250ms ease-in-out',
    slow: '400ms ease-in-out'
  }
};

export default darkTheme;
