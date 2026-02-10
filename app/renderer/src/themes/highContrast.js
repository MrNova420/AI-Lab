/**
 * High Contrast Theme for AI-Lab
 * Maximum accessibility and readability
 */

export const highContrastTheme = {
  name: 'High Contrast',
  id: 'high-contrast',
  colors: {
    // Primary colors
    primary: '#0000ff',
    primaryHover: '#0000cc',
    primaryActive: '#000099',
    
    // Background colors
    background: '#000000',
    backgroundAlt: '#1a1a1a',
    surface: '#0a0a0a',
    surfaceAlt: '#1f1f1f',
    
    // Text colors
    text: '#ffffff',
    textSecondary: '#ffffff',
    textTertiary: '#e0e0e0',
    textDisabled: '#808080',
    
    // Semantic colors
    success: '#00ff00',
    warning: '#ffff00',
    error: '#ff0000',
    info: '#00ffff',
    
    // UI Elements
    border: '#ffffff',
    divider: '#808080',
    hover: '#1a1a1a',
    active: '#333333',
    focus: '#ffff00',
    
    // Syntax highlighting
    syntax: {
      keyword: '#ff00ff',
      string: '#00ff00',
      number: '#00ffff',
      comment: '#808080',
      function: '#ffff00',
      variable: '#ffffff',
      operator: '#ffffff',
      tag: '#ff00ff',
      attribute: '#00ffff',
      constant: '#ffff00',
    }
  },
  typography: {
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    monoFamily: "'Fira Code', 'Consolas', 'Monaco', monospace",
    sizes: {
      xs: '14px',
      sm: '16px',
      base: '18px',
      lg: '20px',
      xl: '22px',
      '2xl': '26px',
      '3xl': '32px',
      '4xl': '38px'
    },
    weights: {
      normal: 600,
      medium: 700,
      semibold: 700,
      bold: 900
    },
    lineHeights: {
      tight: 1.3,
      normal: 1.6,
      relaxed: 1.9
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
    sm: '0px',
    md: '0px',
    lg: '0px',
    xl: '0px',
    full: '0px'
  },
  shadows: {
    sm: 'none',
    md: '0 0 0 2px #ffffff',
    lg: '0 0 0 3px #ffffff',
    xl: '0 0 0 4px #ffffff',
    inner: 'none'
  },
  transitions: {
    fast: '0ms',
    normal: '0ms',
    slow: '0ms'
  }
};

export default highContrastTheme;
