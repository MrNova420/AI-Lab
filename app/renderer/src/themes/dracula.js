/**
 * Dracula Theme for AI-Lab
 * Popular dark theme with purple accents
 */

export const draculaTheme = {
  name: 'Dracula',
  id: 'dracula',
  colors: {
    // Primary colors
    primary: '#bd93f9',
    primaryHover: '#a67de8',
    primaryActive: '#9067d7',
    
    // Background colors
    background: '#282a36',
    backgroundAlt: '#21222c',
    surface: '#343746',
    surfaceAlt: '#44475a',
    
    // Text colors
    text: '#f8f8f2',
    textSecondary: '#e1e1dc',
    textTertiary: '#6272a4',
    textDisabled: '#44475a',
    
    // Semantic colors
    success: '#50fa7b',
    warning: '#ffb86c',
    error: '#ff5555',
    info: '#8be9fd',
    
    // UI Elements
    border: '#44475a',
    divider: '#383a59',
    hover: '#343746',
    active: '#44475a',
    focus: '#bd93f9',
    
    // Syntax highlighting
    syntax: {
      keyword: '#ff79c6',
      string: '#f1fa8c',
      number: '#bd93f9',
      comment: '#6272a4',
      function: '#50fa7b',
      variable: '#f8f8f2',
      operator: '#ff79c6',
      tag: '#ff79c6',
      attribute: '#50fa7b',
      constant: '#bd93f9',
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

export default draculaTheme;
