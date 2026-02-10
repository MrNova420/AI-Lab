/**
 * Light Theme for AI-Lab
 * Clean, bright, professional light mode
 */

export const lightTheme = {
  name: 'Light',
  id: 'light',
  colors: {
    // Primary colors
    primary: '#0066cc',
    primaryHover: '#0052a3',
    primaryActive: '#004080',
    
    // Background colors
    background: '#ffffff',
    backgroundAlt: '#f5f5f5',
    surface: '#fafafa',
    surfaceAlt: '#f0f0f0',
    
    // Text colors
    text: '#1a1a1a',
    textSecondary: '#4a4a4a',
    textTertiary: '#737373',
    textDisabled: '#a3a3a3',
    
    // Semantic colors
    success: '#2e7d32',
    warning: '#ed6c02',
    error: '#d32f2f',
    info: '#0288d1',
    
    // UI Elements
    border: '#e0e0e0',
    divider: '#eeeeee',
    hover: '#f5f5f5',
    active: '#e8e8e8',
    focus: '#0066cc',
    
    // Syntax highlighting
    syntax: {
      keyword: '#af00db',
      string: '#a31515',
      number: '#098658',
      comment: '#008000',
      function: '#795e26',
      variable: '#001080',
      operator: '#000000',
      tag: '#800000',
      attribute: '#e50000',
      constant: '#0070c1',
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
    sm: '0 1px 2px rgba(0,0,0,0.05)',
    md: '0 4px 6px rgba(0,0,0,0.07)',
    lg: '0 10px 15px rgba(0,0,0,0.1)',
    xl: '0 20px 25px rgba(0,0,0,0.15)',
    inner: 'inset 0 2px 4px rgba(0,0,0,0.05)'
  },
  transitions: {
    fast: '150ms ease-in-out',
    normal: '250ms ease-in-out',
    slow: '400ms ease-in-out'
  }
};

export default lightTheme;
