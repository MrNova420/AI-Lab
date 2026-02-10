/**
 * Artifact Component
 * Main container for displaying artifacts
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { messageAnimations } from '../../animations/transitions';
import CodePreview from './CodePreview';
import DocumentPreview from './DocumentPreview';
import DataPreview from './DataPreview';
import ChartPreview from './ChartPreview';
import HTMLPreview from './HTMLPreview';
import { ArtifactTypes } from '../../utils/artifactManager';

const Artifact = ({ artifact, onUpdate, onDelete, onExport }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [showVersions, setShowVersions] = useState(false);
  
  const getPreviewComponent = () => {
    switch (artifact.type) {
      case ArtifactTypes.CODE:
        return <CodePreview artifact={artifact} isEditing={isEditing} onUpdate={onUpdate} />;
      case ArtifactTypes.DOCUMENT:
        return <DocumentPreview artifact={artifact} isEditing={isEditing} onUpdate={onUpdate} />;
      case ArtifactTypes.DATA:
        return <DataPreview artifact={artifact} isEditing={isEditing} onUpdate={onUpdate} />;
      case ArtifactTypes.CHART:
        return <ChartPreview artifact={artifact} isEditing={isEditing} onUpdate={onUpdate} />;
      case ArtifactTypes.HTML:
        return <HTMLPreview artifact={artifact} isEditing={isEditing} onUpdate={onUpdate} />;
      default:
        return <div>Unknown artifact type</div>;
    }
  };
  
  return (
    <motion.div
      className="artifact"
      {...messageAnimations.slideInUp}
      layout
    >
      <div className="artifact-header">
        <div className="artifact-title">
          <span className="artifact-type-badge">{artifact.type}</span>
          <h3>{artifact.title}</h3>
        </div>
        
        <div className="artifact-actions">
          <button
            className="btn-icon"
            onClick={() => setIsEditing(!isEditing)}
            title={isEditing ? 'Cancel' : 'Edit'}
          >
            {isEditing ? '✕' : '✏️'}
          </button>
          <button
            className="btn-icon"
            onClick={() => setShowVersions(!showVersions)}
            title="Version history"
          >
            🕐 {artifact.versions.length}
          </button>
          <button
            className="btn-icon"
            onClick={() => onExport(artifact)}
            title="Export"
          >
            ⬇️
          </button>
          <button
            className="btn-icon"
            onClick={() => onDelete(artifact.id)}
            title="Delete"
          >
            🗑️
          </button>
        </div>
      </div>
      
      <div className="artifact-content">
        {getPreviewComponent()}
      </div>
      
      {showVersions && (
        <motion.div
          className="artifact-versions"
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
        >
          <h4>Version History</h4>
          <div className="versions-list">
            {artifact.versions.map((version) => (
              <div
                key={version.id}
                className={`version-item ${version.id === artifact.currentVersion ? 'current' : ''}`}
              >
                <span className="version-id">v{version.id}</span>
                <span className="version-timestamp">
                  {new Date(version.timestamp).toLocaleString()}
                </span>
                <span className="version-annotation">{version.annotation}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}
      
      <div className="artifact-footer">
        <div className="artifact-metadata">
          {artifact.tags.length > 0 && (
            <div className="artifact-tags">
              {artifact.tags.map((tag) => (
                <span key={tag} className="tag">{tag}</span>
              ))}
            </div>
          )}
          <span className="artifact-date">
            Updated {new Date(artifact.updatedAt).toLocaleString()}
          </span>
        </div>
      </div>
    </motion.div>
  );
};

export default Artifact;
