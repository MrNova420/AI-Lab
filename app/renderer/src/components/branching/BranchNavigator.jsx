/**
 * Branch Navigator Component
 * Navigate between branches and manage branch operations
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { modalAnimations } from '../../animations/transitions';
import branchManager from '../../utils/branchManager';
import BranchTree from './BranchTree';

const BranchNavigator = ({ currentBranch, onSwitchBranch, onClose }) => {
  const [activeTab, setActiveTab] = useState('tree');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newBranchName, setNewBranchName] = useState('');
  const [newBranchDesc, setNewBranchDesc] = useState('');
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [stats, setStats] = useState(null);
  
  React.useEffect(() => {
    const statistics = branchManager.getStatistics();
    setStats(statistics);
  }, []);
  
  const handleCreateBranch = () => {
    if (!newBranchName.trim()) {
      alert('Please enter a branch name');
      return;
    }
    
    if (!selectedMessage) {
      alert('Please select a message as the branch point');
      return;
    }
    
    try {
      const newBranch = branchManager.createBranch({
        name: newBranchName,
        description: newBranchDesc,
        parentBranch: currentBranch,
        messageId: selectedMessage
      });
      
      setShowCreateForm(false);
      setNewBranchName('');
      setNewBranchDesc('');
      setSelectedMessage(null);
      onSwitchBranch(newBranch.id);
    } catch (error) {
      alert('Failed to create branch: ' + error.message);
    }
  };
  
  const handleMergeBranch = (branchId) => {
    if (confirm('Merge this branch into its parent?')) {
      try {
        branchManager.mergeBranch(branchId, 'append');
        alert('Branch merged successfully');
        const branch = branchManager.getBranch(branchId);
        onSwitchBranch(branch.parentBranch);
      } catch (error) {
        alert('Failed to merge branch: ' + error.message);
      }
    }
  };
  
  const handleDeleteBranch = (branchId) => {
    if (branchId === 'main') {
      alert('Cannot delete main branch');
      return;
    }
    
    if (confirm('Delete this branch and all its children?')) {
      try {
        branchManager.deleteBranch(branchId);
        alert('Branch deleted successfully');
        onSwitchBranch('main');
      } catch (error) {
        alert('Failed to delete branch: ' + error.message);
      }
    }
  };
  
  const renderCreateForm = () => {
    const branch = branchManager.getBranch(currentBranch);
    
    return (
      <motion.div
        className="create-branch-form"
        {...modalAnimations.dialog}
      >
        <h3>Create New Branch</h3>
        
        <div className="form-group">
          <label>Branch Name</label>
          <input
            type="text"
            value={newBranchName}
            onChange={(e) => setNewBranchName(e.target.value)}
            placeholder="Feature name or experiment"
            className="form-input"
          />
        </div>
        
        <div className="form-group">
          <label>Description (optional)</label>
          <textarea
            value={newBranchDesc}
            onChange={(e) => setNewBranchDesc(e.target.value)}
            placeholder="What are you exploring in this branch?"
            className="form-textarea"
          />
        </div>
        
        <div className="form-group">
          <label>Branch From Message</label>
          <select
            value={selectedMessage || ''}
            onChange={(e) => setSelectedMessage(e.target.value)}
            className="form-select"
          >
            <option value="">Select a message...</option>
            {branch?.messages.map((msg, index) => (
              <option key={msg.id} value={msg.id}>
                Message {index + 1}: {msg.content.substring(0, 50)}...
              </option>
            ))}
          </select>
        </div>
        
        <div className="form-actions">
          <button
            className="btn-primary"
            onClick={handleCreateBranch}
          >
            Create Branch
          </button>
          <button
            className="btn-secondary"
            onClick={() => setShowCreateForm(false)}
          >
            Cancel
          </button>
        </div>
      </motion.div>
    );
  };
  
  const renderBranchList = () => {
    const branches = branchManager.getAllBranches();
    
    return (
      <div className="branch-list">
        {branches.map(branch => (
          <motion.div
            key={branch.id}
            className={`branch-list-item ${branch.id === currentBranch ? 'current' : ''}`}
            whileHover={{ backgroundColor: 'var(--color-hover)' }}
          >
            <div className="branch-info">
              <div className="branch-header">
                <h4>{branch.name}</h4>
                {branch.id === currentBranch && (
                  <span className="current-badge">Current</span>
                )}
              </div>
              {branch.description && (
                <p className="branch-description">{branch.description}</p>
              )}
              <div className="branch-stats">
                <span>{branch.messages.length} messages</span>
                <span>•</span>
                <span>Updated {new Date(branch.updatedAt).toLocaleString()}</span>
              </div>
            </div>
            
            <div className="branch-actions">
              {branch.id !== currentBranch && (
                <button
                  className="btn-sm"
                  onClick={() => onSwitchBranch(branch.id)}
                >
                  Switch
                </button>
              )}
              {branch.parentBranch && (
                <button
                  className="btn-sm"
                  onClick={() => handleMergeBranch(branch.id)}
                >
                  Merge
                </button>
              )}
              {branch.id !== 'main' && (
                <button
                  className="btn-sm btn-danger"
                  onClick={() => handleDeleteBranch(branch.id)}
                >
                  Delete
                </button>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    );
  };
  
  return (
    <AnimatePresence>
      <motion.div
        className="branch-navigator-backdrop"
        {...modalAnimations.backdrop}
        onClick={onClose}
      >
        <motion.div
          className="branch-navigator"
          {...modalAnimations.dialog}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="navigator-header">
            <h2>Branch Navigator</h2>
            <button onClick={onClose} className="btn-icon">✕</button>
          </div>
          
          {stats && (
            <div className="navigator-stats">
              <div className="stat-item">
                <span className="stat-value">{stats.total}</span>
                <span className="stat-label">Total Branches</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{stats.totalMessages}</span>
                <span className="stat-label">Total Messages</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{stats.avgMessagesPerBranch}</span>
                <span className="stat-label">Avg per Branch</span>
              </div>
            </div>
          )}
          
          <div className="navigator-tabs">
            <button
              className={`tab ${activeTab === 'tree' ? 'active' : ''}`}
              onClick={() => setActiveTab('tree')}
            >
              Tree View
            </button>
            <button
              className={`tab ${activeTab === 'list' ? 'active' : ''}`}
              onClick={() => setActiveTab('list')}
            >
              List View
            </button>
            <button
              className="btn-primary"
              onClick={() => setShowCreateForm(true)}
            >
              + New Branch
            </button>
          </div>
          
          <div className="navigator-content">
            {showCreateForm ? (
              renderCreateForm()
            ) : activeTab === 'tree' ? (
              <BranchTree
                currentBranch={currentBranch}
                onSelectBranch={onSwitchBranch}
              />
            ) : (
              renderBranchList()
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default BranchNavigator;
