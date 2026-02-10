/**
 * Artifact Library Component
 * Browse and manage all artifacts
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { listAnimations } from '../../animations/transitions';
import artifactManager, { ArtifactTypes } from '../../utils/artifactManager';
import Artifact from './Artifact';

const ArtifactLibrary = ({ onClose }) => {
  const [artifacts, setArtifacts] = useState([]);
  const [filteredArtifacts, setFilteredArtifacts] = useState([]);
  const [filterType, setFilterType] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('updated');
  const [selectedArtifact, setSelectedArtifact] = useState(null);
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    loadArtifacts();
  }, []);
  
  useEffect(() => {
    filterAndSortArtifacts();
  }, [artifacts, filterType, searchQuery, sortBy]);
  
  const loadArtifacts = () => {
    const allArtifacts = artifactManager.getAllArtifacts();
    const statistics = artifactManager.getStatistics();
    setArtifacts(allArtifacts);
    setStats(statistics);
  };
  
  const filterAndSortArtifacts = () => {
    let filtered = [...artifacts];
    
    // Filter by type
    if (filterType !== 'all') {
      filtered = filtered.filter(a => a.type === filterType);
    }
    
    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(a =>
        a.title.toLowerCase().includes(query) ||
        a.content.toLowerCase().includes(query) ||
        a.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }
    
    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'updated':
          return new Date(b.updatedAt) - new Date(a.updatedAt);
        case 'created':
          return new Date(b.createdAt) - new Date(a.createdAt);
        case 'title':
          return a.title.localeCompare(b.title);
        case 'type':
          return a.type.localeCompare(b.type);
        default:
          return 0;
      }
    });
    
    setFilteredArtifacts(filtered);
  };
  
  const handleUpdate = (id, update) => {
    artifactManager.updateArtifact(id, update);
    loadArtifacts();
  };
  
  const handleDelete = (id) => {
    if (confirm('Are you sure you want to delete this artifact?')) {
      artifactManager.deleteArtifact(id);
      loadArtifacts();
      setSelectedArtifact(null);
    }
  };
  
  const handleExport = (artifact) => {
    const formats = ['json', 'markdown', 'plain'];
    const format = prompt(`Export format (${formats.join(', ')}):`, 'json');
    
    if (format && formats.includes(format)) {
      const exported = artifactManager.exportArtifact(artifact.id, format);
      
      if (exported) {
        const blob = new Blob([exported], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${artifact.title}.${format === 'plain' ? 'txt' : format}`;
        a.click();
      }
    }
  };
  
  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const imported = artifactManager.importArtifact(event.target.result);
          if (imported) {
            loadArtifacts();
            alert('Artifact imported successfully!');
          } else {
            alert('Failed to import artifact');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };
  
  return (
    <div className="artifact-library">
      <div className="library-sidebar">
        <div className="library-header">
          <h2>Artifact Library</h2>
          <button onClick={onClose} className="btn-icon">✕</button>
        </div>
        
        {stats && (
          <div className="library-stats">
            <div className="stat-item">
              <span className="stat-value">{stats.total}</span>
              <span className="stat-label">Total Artifacts</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{stats.pinned}</span>
              <span className="stat-label">Pinned</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{stats.totalVersions}</span>
              <span className="stat-label">Versions</span>
            </div>
          </div>
        )}
        
        <div className="library-filters">
          <h3>Filter by Type</h3>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Types</option>
            <option value={ArtifactTypes.CODE}>Code</option>
            <option value={ArtifactTypes.DOCUMENT}>Document</option>
            <option value={ArtifactTypes.DATA}>Data</option>
            <option value={ArtifactTypes.CHART}>Chart</option>
            <option value={ArtifactTypes.HTML}>HTML</option>
          </select>
          
          <h3>Sort By</h3>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="filter-select"
          >
            <option value="updated">Recently Updated</option>
            <option value="created">Recently Created</option>
            <option value="title">Title (A-Z)</option>
            <option value="type">Type</option>
          </select>
        </div>
        
        <div className="library-actions">
          <button className="btn-secondary" onClick={handleImport}>
            Import Artifact
          </button>
        </div>
      </div>
      
      <div className="library-main">
        <div className="library-search">
          <input
            type="text"
            className="search-input"
            placeholder="Search artifacts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <span className="search-count">
            {filteredArtifacts.length} artifact{filteredArtifacts.length !== 1 ? 's' : ''}
          </span>
        </div>
        
        <motion.div
          className="artifacts-grid"
          variants={listAnimations.container}
          initial="initial"
          animate="animate"
        >
          <AnimatePresence>
            {filteredArtifacts.length === 0 ? (
              <div className="empty-state">
                <p>No artifacts found</p>
                <p className="hint">Create artifacts from your conversations</p>
              </div>
            ) : (
              filteredArtifacts.map((artifact) => (
                <motion.div
                  key={artifact.id}
                  variants={listAnimations.item}
                  layout
                  onClick={() => setSelectedArtifact(artifact)}
                  className="artifact-card"
                >
                  <Artifact
                    artifact={artifact}
                    onUpdate={handleUpdate}
                    onDelete={handleDelete}
                    onExport={handleExport}
                  />
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
};

export default ArtifactLibrary;
