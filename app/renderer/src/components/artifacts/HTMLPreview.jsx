/**
 * HTML Preview Component
 * Safe HTML/CSS rendering in iframe
 */

import React, { useRef, useEffect, useState } from 'react';

const HTMLPreview = ({ artifact, isEditing, onUpdate }) => {
  const iframeRef = useRef(null);
  const [html, setHtml] = useState(artifact.content);
  const [activeTab, setActiveTab] = useState('preview');
  
  useEffect(() => {
    if (iframeRef.current && !isEditing) {
      const iframe = iframeRef.current;
      const doc = iframe.contentDocument || iframe.contentWindow.document;
      
      doc.open();
      doc.write(html);
      doc.close();
    }
  }, [html, isEditing]);
  
  const handleSave = () => {
    onUpdate(artifact.id, {
      content: html,
      annotation: 'HTML updated'
    });
  };
  
  if (isEditing) {
    return (
      <div className="html-editor">
        <div className="editor-tabs">
          <button
            className={`tab ${activeTab === 'code' ? 'active' : ''}`}
            onClick={() => setActiveTab('code')}
          >
            Code
          </button>
          <button
            className={`tab ${activeTab === 'preview' ? 'active' : ''}`}
            onClick={() => setActiveTab('preview')}
          >
            Preview
          </button>
        </div>
        
        <div className="editor-content">
          {activeTab === 'code' ? (
            <textarea
              className="html-textarea"
              value={html}
              onChange={(e) => setHtml(e.target.value)}
              spellCheck={false}
            />
          ) : (
            <iframe
              ref={iframeRef}
              className="html-preview-frame"
              sandbox="allow-scripts"
              title="HTML Preview"
            />
          )}
        </div>
        
        <div className="editor-actions">
          <button className="btn-primary" onClick={handleSave}>
            Save Changes
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="html-preview">
      <iframe
        ref={iframeRef}
        className="html-preview-frame"
        sandbox="allow-scripts"
        title="HTML Preview"
      />
    </div>
  );
};

export default HTMLPreview;
