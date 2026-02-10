/**
 * Monokai Theme for AI-Lab
 * Classic code editor theme
 */

export const monokaiTheme = {
  name: 'Monokai',
  id: 'monokai',
  colors: {
    // Primary colors
    primary: '#66d9ef',
    primaryHover: '#52c5db',
    primaryActive: '#3eb1c7',
    
    // Background colors
    background: '#272822',
    backgroundAlt: '#1e1f1c',
    surface: '#3e3d32',
    surfaceAlt: '#49483e',
    
    // Text colors
    text: '#f8f8f2',
    textSecondary: '#cfcfc2',
    textTertiary: '#75715e',
    textDisabled: '#49483e',
    
    // Semantic colors
    success: '#a6e22e',
    warning: '#e6db74',
    error: '#f92672',
    info: '#66d9ef',
    
    // UI Elements
    border: '#49483e',
    divider: '#3e3d32',
    hover: '#3e3d32',
    active: '#49483e',
    focus: '#66d9ef',
    
    // Syntax highlighting
    syntax: {
      keyword: '#f92672',
      string: '#e6db74',
      number: '#ae81ff',
      comment: '#75715e',
      function: '#a6e22e',
      variable: '#f8f8f2',
      operator: '#f92672',
      tag: '#f92672',
      attribute: '#a6e22e',
      constant: '#ae81ff',
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
    sm: '0 1px 2px rgba(0,0,0,0.4)',
    md: '0 4px 6px rgba(0,0,0,0.4)',
    lg: '0 10px 15px rgba(0,0,0,0.5)',
    xl: '0 20px 25px rgba(0,0,0,0.6)',
    inner: 'inset 0 2px 4px rgba(0,0,0,0.3)'
  },
  transitions: {
    fast: '150ms ease-in-out',
    normal: '250ms ease-in-out',
    slow: '400ms ease-in-out'
  }
};

export default monokaiTheme;
