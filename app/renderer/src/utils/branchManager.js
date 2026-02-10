/**
 * Branch Manager
 * Manages conversation branches and their relationships
 */

class BranchManager {
  constructor() {
    this.branches = this.loadBranches();
  }
  
  // Load branches from localStorage
  loadBranches() {
    try {
      const stored = localStorage.getItem('ai-lab-branches');
      return stored ? JSON.parse(stored) : this.getDefaultBranches();
    } catch (error) {
      console.error('Failed to load branches:', error);
      return this.getDefaultBranches();
    }
  }
  
  // Get default branches structure
  getDefaultBranches() {
    return {
      main: {
        id: 'main',
        name: 'Main',
        description: 'Main conversation branch',
        messages: [],
        parentBranch: null,
        branchPoint: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    };
  }
  
  // Save branches to localStorage
  saveBranches() {
    try {
      localStorage.setItem('ai-lab-branches', JSON.stringify(this.branches));
    } catch (error) {
      console.error('Failed to save branches:', error);
    }
  }
  
  // Create new branch from a message
  createBranch({ name, description, parentBranch, messageId }) {
    const id = `branch-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const timestamp = new Date().toISOString();
    
    const parent = this.branches[parentBranch];
    if (!parent) {
      throw new Error('Parent branch not found');
    }
    
    // Find the branch point message index
    const branchPointIndex = parent.messages.findIndex(m => m.id === messageId);
    if (branchPointIndex === -1) {
      throw new Error('Branch point message not found');
    }
    
    // Copy messages up to branch point
    const branchMessages = parent.messages.slice(0, branchPointIndex + 1);
    
    const newBranch = {
      id,
      name,
      description,
      messages: branchMessages,
      parentBranch,
      branchPoint: messageId,
      createdAt: timestamp,
      updatedAt: timestamp,
      metadata: {
        totalMessages: branchMessages.length,
        divergedAt: branchPointIndex
      }
    };
    
    this.branches[id] = newBranch;
    this.saveBranches();
    
    return newBranch;
  }
  
  // Get branch by ID
  getBranch(branchId) {
    return this.branches[branchId] || null;
  }
  
  // Get all branches
  getAllBranches() {
    return Object.values(this.branches);
  }
  
  // Get branch tree structure
  getBranchTree() {
    const tree = {};
    
    Object.values(this.branches).forEach(branch => {
      if (!branch.parentBranch) {
        // Root branch
        tree[branch.id] = { ...branch, children: [] };
      }
    });
    
    // Add children to parents
    Object.values(this.branches).forEach(branch => {
      if (branch.parentBranch && tree[branch.parentBranch]) {
        if (!tree[branch.parentBranch].children) {
          tree[branch.parentBranch].children = [];
        }
        tree[branch.parentBranch].children.push({
          ...branch,
          children: []
        });
      } else if (branch.parentBranch) {
        // Find parent in existing tree
        const parent = this.findBranchInTree(tree, branch.parentBranch);
        if (parent) {
          if (!parent.children) {
            parent.children = [];
          }
          parent.children.push({ ...branch, children: [] });
        }
      }
    });
    
    return tree;
  }
  
  // Helper to find branch in tree
  findBranchInTree(tree, branchId) {
    // Handle both object with branches and array of branches
    const branches = Array.isArray(tree) ? tree : Object.values(tree);
    
    for (const branch of branches) {
      if (branch.id === branchId) {
        return branch;
      }
      if (branch.children && branch.children.length > 0) {
        const found = this.findBranchInTree(branch.children, branchId);
        if (found) return found;
      }
    }
    return null;
  }
  
  // Add message to branch
  addMessage(branchId, message) {
    const branch = this.branches[branchId];
    if (!branch) {
      throw new Error('Branch not found');
    }
    
    // Ensure message has an ID
    if (!message.id) {
      message.id = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    
    branch.messages.push(message);
    branch.updatedAt = new Date().toISOString();
    branch.metadata.totalMessages = branch.messages.length;
    
    this.saveBranches();
    return message;
  }
  
  // Update branch metadata
  updateBranch(branchId, updates) {
    const branch = this.branches[branchId];
    if (!branch) {
      throw new Error('Branch not found');
    }
    
    Object.assign(branch, updates);
    branch.updatedAt = new Date().toISOString();
    
    this.saveBranches();
    return branch;
  }
  
  // Delete branch
  deleteBranch(branchId) {
    if (branchId === 'main') {
      throw new Error('Cannot delete main branch');
    }
    
    if (!this.branches[branchId]) {
      throw new Error('Branch not found');
    }
    
    // Delete all child branches recursively
    const childBranches = Object.values(this.branches).filter(
      b => b.parentBranch === branchId
    );
    
    childBranches.forEach(child => {
      this.deleteBranch(child.id);
    });
    
    delete this.branches[branchId];
    this.saveBranches();
    
    return true;
  }
  
  // Merge branch into parent
  mergeBranch(branchId, strategy = 'append') {
    const branch = this.branches[branchId];
    if (!branch) {
      throw new Error('Branch not found');
    }
    
    if (!branch.parentBranch) {
      throw new Error('Cannot merge root branch');
    }
    
    const parent = this.branches[branch.parentBranch];
    if (!parent) {
      throw new Error('Parent branch not found');
    }
    
    // Get messages after branch point
    const branchPointIndex = parent.messages.findIndex(m => m.id === branch.branchPoint);
    const newMessages = branch.messages.slice(branchPointIndex + 1);
    
    switch (strategy) {
      case 'append':
        // Append new messages to parent
        parent.messages.push(...newMessages);
        break;
      case 'replace':
        // Replace messages after branch point with branch messages
        parent.messages = [
          ...parent.messages.slice(0, branchPointIndex + 1),
          ...newMessages
        ];
        break;
      default:
        throw new Error('Unknown merge strategy');
    }
    
    parent.updatedAt = new Date().toISOString();
    parent.metadata.totalMessages = parent.messages.length;
    
    this.saveBranches();
    return parent;
  }
  
  // Compare two branches
  compareBranches(branchId1, branchId2) {
    const branch1 = this.branches[branchId1];
    const branch2 = this.branches[branchId2];
    
    if (!branch1 || !branch2) {
      throw new Error('One or both branches not found');
    }
    
    // Find common ancestor
    const commonAncestor = this.findCommonAncestor(branch1, branch2);
    
    return {
      branch1: {
        id: branch1.id,
        name: branch1.name,
        messageCount: branch1.messages.length
      },
      branch2: {
        id: branch2.id,
        name: branch2.name,
        messageCount: branch2.messages.length
      },
      commonAncestor,
      divergence: {
        branch1: branch1.messages.length - (commonAncestor ? commonAncestor.messageCount : 0),
        branch2: branch2.messages.length - (commonAncestor ? commonAncestor.messageCount : 0)
      }
    };
  }
  
  // Find common ancestor of two branches
  findCommonAncestor(branch1, branch2) {
    const ancestors1 = this.getAncestors(branch1.id);
    const ancestors2 = this.getAncestors(branch2.id);
    
    // Find first common ancestor
    for (const ancestor1 of ancestors1) {
      if (ancestors2.includes(ancestor1)) {
        return this.branches[ancestor1];
      }
    }
    
    return null;
  }
  
  // Get all ancestors of a branch
  getAncestors(branchId) {
    const ancestors = [];
    let current = this.branches[branchId];
    
    while (current && current.parentBranch) {
      ancestors.push(current.parentBranch);
      current = this.branches[current.parentBranch];
    }
    
    return ancestors;
  }
  
  // Get statistics
  getStatistics() {
    const branches = Object.values(this.branches);
    
    return {
      total: branches.length,
      active: branches.length,
      totalMessages: branches.reduce((sum, b) => sum + b.messages.length, 0),
      avgMessagesPerBranch: Math.round(
        branches.reduce((sum, b) => sum + b.messages.length, 0) / branches.length
      )
    };
  }
}

// Singleton instance
const branchManager = new BranchManager();

export default branchManager;
export { BranchManager };
