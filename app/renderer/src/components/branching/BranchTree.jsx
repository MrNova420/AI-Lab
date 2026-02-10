/**
 * Branch Tree Component
 * Visual tree representation of conversation branches
 */

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import branchManager from '../../utils/branchManager';

const BranchTree = ({ currentBranch, onSelectBranch }) => {
  const [tree, setTree] = useState({});
  const [expandedBranches, setExpandedBranches] = useState(new Set(['main']));
  
  useEffect(() => {
    loadTree();
  }, []);
  
  const loadTree = () => {
    const branchTree = branchManager.getBranchTree();
    setTree(branchTree);
  };
  
  const toggleExpand = (branchId) => {
    setExpandedBranches(prev => {
      const newSet = new Set(prev);
      if (newSet.has(branchId)) {
        newSet.delete(branchId);
      } else {
        newSet.add(branchId);
      }
      return newSet;
    });
  };
  
  const renderBranch = (branch, level = 0) => {
    const isExpanded = expandedBranches.has(branch.id);
    const isCurrent = branch.id === currentBranch;
    const hasChildren = branch.children && branch.children.length > 0;
    
    return (
      <div key={branch.id} className="branch-item" style={{ marginLeft: `${level * 20}px` }}>
        <motion.div
          className={`branch-node ${isCurrent ? 'current' : ''}`}
          whileHover={{ scale: 1.02 }}
          onClick={() => onSelectBranch(branch.id)}
        >
          {hasChildren && (
            <button
              className="branch-toggle"
              onClick={(e) => {
                e.stopPropagation();
                toggleExpand(branch.id);
              }}
            >
              {isExpanded ? '▼' : '▶'}
            </button>
          )}
          
          <div className="branch-info">
            <div className="branch-name">
              {branch.name}
              {isCurrent && <span className="current-badge">Current</span>}
            </div>
            <div className="branch-meta">
              {branch.messages.length} messages
              {branch.parentBranch && (
                <span className="branch-parent"> • from {branchManager.getBranch(branch.parentBranch)?.name}</span>
              )}
            </div>
          </div>
          
          {branch.description && (
            <div className="branch-description">{branch.description}</div>
          )}
        </motion.div>
        
        {hasChildren && isExpanded && (
          <div className="branch-children">
            {branch.children.map(child => renderBranch(child, level + 1))}
          </div>
        )}
      </div>
    );
  };
  
  return (
    <div className="branch-tree">
      <div className="branch-tree-header">
        <h3>Conversation Branches</h3>
      </div>
      
      <div className="branch-tree-content">
        {Object.values(tree).map(branch => renderBranch(branch))}
      </div>
    </div>
  );
};

export default BranchTree;
