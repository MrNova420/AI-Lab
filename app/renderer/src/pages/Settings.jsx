import React from 'react';
import { useTheme } from '../contexts/ThemeContext';

function Settings() {
  const { currentThemeId, changeTheme, availableThemes } = useTheme();
  
  return (
    <div>
      <h1 className="page-title">Settings</h1>
      <p className="page-description">Configure AI-Lab</p>
      
      <div className="card">
        <h2 className="card-title">Appearance</h2>
        
        <div className="setting-group">
          <label className="setting-label">Theme</label>
          <p className="setting-description">Choose your preferred color scheme</p>
          
          <div className="theme-grid">
            {availableThemes.map((theme) => (
              <button
                key={theme.id}
                className={`theme-option ${currentThemeId === theme.id ? 'active' : ''}`}
                onClick={() => changeTheme(theme.id)}
              >
                <div className="theme-preview" style={{
                  background: theme.colors.background,
                  border: `2px solid ${currentThemeId === theme.id ? theme.colors.primary : theme.colors.border}`
                }}>
                  <div className="theme-preview-colors">
                    <span style={{ background: theme.colors.primary }}></span>
                    <span style={{ background: theme.colors.success }}></span>
                    <span style={{ background: theme.colors.warning }}></span>
                    <span style={{ background: theme.colors.error }}></span>
                  </div>
                </div>
                <div className="theme-name">{theme.name}</div>
                {currentThemeId === theme.id && (
                  <div className="theme-active-badge">✓ Active</div>
                )}
              </button>
            ))}
          </div>
        </div>
      </div>
      
      <div className="card">
        <h2 className="card-title">Keyboard Shortcuts</h2>
        <p className="setting-description">Press <kbd>Cmd/Ctrl + /</kbd> to view all keyboard shortcuts</p>
      </div>
      
      <div className="card">
        <h2 className="card-title">About</h2>
        <div className="about-info">
          <p><strong>AI-Lab v1 Beta</strong></p>
          <p>Advanced AI Development Environment</p>
          <p className="text-muted">Local, private, and powerful</p>
        </div>
      </div>
    </div>
  );
}

export default Settings;
