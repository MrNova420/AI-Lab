/**
 * Code Preview Component
 * Syntax highlighted code display with editing capability
 */

import React, { useState, useEffect } from 'react';
import { Highlight, themes } from 'prism-react-renderer';

const CodePreview = ({ artifact, isEditing, onUpdate }) => {
  const [code, setCode] = useState(artifact.content);
  const [copied, setCopied] = useState(false);
  
  useEffect(() => {
    setCode(artifact.content);
  }, [artifact.content]);
  
  const handleSave = () => {
    onUpdate(artifact.id, {
      content: code,
      annotation: 'Manual edit'
    });
  };
  
  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  if (isEditing) {
    return (
      <div className="code-editor">
        <textarea
          className="code-textarea"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          spellCheck={false}
        />
        <div className="editor-actions">
          <button className="btn-primary" onClick={handleSave}>
            Save Changes
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="code-preview">
      <div className="code-header">
        <span className="code-language">{artifact.language || 'plaintext'}</span>
        <button
          className="btn-icon copy-button"
          onClick={handleCopy}
          title="Copy code"
        >
          {copied ? '✓ Copied' : '📋 Copy'}
        </button>
      </div>
      
      <Highlight
        theme={themes.vsDark}
        code={code}
        language={artifact.language || 'javascript'}
      >
        {({ className, style, tokens, getLineProps, getTokenProps }) => (
          <pre className={className} style={style}>
            {tokens.map((line, i) => (
              <div key={i} {...getLineProps({ line })}>
                <span className="line-number">{i + 1}</span>
                <span className="line-content">
                  {line.map((token, key) => (
                    <span key={key} {...getTokenProps({ token })} />
                  ))}
                </span>
              </div>
            ))}
          </pre>
        )}
      </Highlight>
    </div>
  );
};

export default CodePreview;
