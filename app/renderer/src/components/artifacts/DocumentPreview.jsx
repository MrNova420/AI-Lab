/**
 * Document Preview Component
 * Markdown document with rich formatting
 */

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';

const DocumentPreview = ({ artifact, isEditing, onUpdate }) => {
  const [content, setContent] = useState(artifact.content);
  
  const handleSave = () => {
    onUpdate(artifact.id, {
      content,
      annotation: 'Document updated'
    });
  };
  
  if (isEditing) {
    return (
      <div className="document-editor">
        <div className="editor-split">
          <div className="editor-pane">
            <h4>Edit</h4>
            <textarea
              className="document-textarea"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Write your markdown here..."
            />
          </div>
          <div className="preview-pane">
            <h4>Preview</h4>
            <div className="markdown-preview">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          </div>
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
    <div className="document-preview">
      <div className="markdown-content">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );
};

export default DocumentPreview;
