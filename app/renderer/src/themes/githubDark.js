/**
 * GitHub Dark Theme for AI-Lab
 * GitHub's popular dark theme
 */

export const githubDarkTheme = {
  name: 'GitHub Dark',
  id: 'github-dark',
  colors: {
    // Primary colors
    primary: '#58a6ff',
    primaryHover: '#4493e6',
    primaryActive: '#3080cc',
    
    // Background colors
    background: '#0d1117',
    backgroundAlt: '#161b22',
    surface: '#21262d',
    surfaceAlt: '#30363d',
    
    // Text colors
    text: '#c9d1d9',
    textSecondary: '#8b949e',
    textTertiary: '#6e7681',
    textDisabled: '#484f58',
    
    // Semantic colors
    success: '#3fb950',
    warning: '#d29922',
    error: '#f85149',
    info: '#58a6ff',
    
    // UI Elements
    border: '#30363d',
    divider: '#21262d',
    hover: '#161b22',
    active: '#21262d',
    focus: '#58a6ff',
    
    // Syntax highlighting
    syntax: {
      keyword: '#ff7b72',
      string: '#a5d6ff',
      number: '#79c0ff',
      comment: '#8b949e',
      function: '#d2a8ff',
      variable: '#ffa657',
      operator: '#ff7b72',
      tag: '#7ee787',
      attribute: '#79c0ff',
      constant: '#79c0ff',
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
    sm: '6px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    full: '9999px'
  },
  shadows: {
    sm: '0 0 transparent, 0 0 transparent, 0 1px 0 rgba(0,0,0,0.2)',
    md: '0 3px 6px rgba(0,0,0,0.15)',
    lg: '0 8px 24px rgba(0,0,0,0.2)',
    xl: '0 12px 28px rgba(0,0,0,0.25)',
    inner: 'inset 0 1px 0 rgba(255,255,255,0.05)'
  },
  transitions: {
    fast: '150ms ease-in-out',
    normal: '250ms ease-in-out',
    slow: '400ms ease-in-out'
  }
};

export default githubDarkTheme;
