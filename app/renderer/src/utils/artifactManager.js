/**
 * Artifact Manager
 * Manages artifact creation, storage, and version control
 */

// Artifact types
export const ArtifactTypes = {
  CODE: 'code',
  DOCUMENT: 'document',
  DATA: 'data',
  CHART: 'chart',
  HTML: 'html'
};

// Artifact storage structure
class ArtifactManager {
  constructor() {
    this.artifacts = this.loadArtifacts();
  }
  
  // Load artifacts from localStorage
  loadArtifacts() {
    try {
      const stored = localStorage.getItem('ai-lab-artifacts');
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Failed to load artifacts:', error);
      return {};
    }
  }
  
  // Save artifacts to localStorage
  saveArtifacts() {
    try {
      localStorage.setItem('ai-lab-artifacts', JSON.stringify(this.artifacts));
    } catch (error) {
      console.error('Failed to save artifacts:', error);
    }
  }
  
  // Create new artifact
  createArtifact({ type, language, title, content, metadata = {} }) {
    const id = `artifact-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const timestamp = new Date().toISOString();
    
    const artifact = {
      id,
      type,
      language: language || null,
      title: title || `Untitled ${type}`,
      content,
      metadata,
      versions: [
        {
          id: 1,
          content,
          timestamp,
          annotation: 'Initial version'
        }
      ],
      currentVersion: 1,
      createdAt: timestamp,
      updatedAt: timestamp,
      tags: [],
      pinned: false
    };
    
    this.artifacts[id] = artifact;
    this.saveArtifacts();
    
    return artifact;
  }
  
  // Get artifact by ID
  getArtifact(id) {
    return this.artifacts[id] || null;
  }
  
  // Get all artifacts
  getAllArtifacts() {
    return Object.values(this.artifacts);
  }
  
  // Get artifacts by type
  getArtifactsByType(type) {
    return Object.values(this.artifacts).filter(a => a.type === type);
  }
  
  // Update artifact content
  updateArtifact(id, { content, annotation = '' }) {
    const artifact = this.artifacts[id];
    if (!artifact) return null;
    
    const timestamp = new Date().toISOString();
    const newVersion = {
      id: artifact.versions.length + 1,
      content,
      timestamp,
      annotation
    };
    
    artifact.versions.push(newVersion);
    artifact.content = content;
    artifact.currentVersion = newVersion.id;
    artifact.updatedAt = timestamp;
    
    this.saveArtifacts();
    return artifact;
  }
  
  // Update artifact metadata
  updateMetadata(id, metadata) {
    const artifact = this.artifacts[id];
    if (!artifact) return null;
    
    artifact.metadata = { ...artifact.metadata, ...metadata };
    artifact.updatedAt = new Date().toISOString();
    
    this.saveArtifacts();
    return artifact;
  }
  
  // Restore specific version
  restoreVersion(id, versionId) {
    const artifact = this.artifacts[id];
    if (!artifact) return null;
    
    const version = artifact.versions.find(v => v.id === versionId);
    if (!version) return null;
    
    artifact.content = version.content;
    artifact.currentVersion = versionId;
    artifact.updatedAt = new Date().toISOString();
    
    this.saveArtifacts();
    return artifact;
  }
  
  // Get version diff
  getVersionDiff(id, fromVersion, toVersion) {
    const artifact = this.artifacts[id];
    if (!artifact) return null;
    
    const from = artifact.versions.find(v => v.id === fromVersion);
    const to = artifact.versions.find(v => v.id === toVersion);
    
    if (!from || !to) return null;
    
    return {
      from: {
        id: from.id,
        content: from.content,
        timestamp: from.timestamp
      },
      to: {
        id: to.id,
        content: to.content,
        timestamp: to.timestamp
      }
    };
  }
  
  // Delete artifact
  deleteArtifact(id) {
    if (!this.artifacts[id]) return false;
    
    delete this.artifacts[id];
    this.saveArtifacts();
    return true;
  }
  
  // Pin/unpin artifact
  togglePin(id) {
    const artifact = this.artifacts[id];
    if (!artifact) return null;
    
    artifact.pinned = !artifact.pinned;
    artifact.updatedAt = new Date().toISOString();
    
    this.saveArtifacts();
    return artifact;
  }
  
  // Add tag to artifact
  addTag(id, tag) {
    const artifact = this.artifacts[id];
    if (!artifact) return null;
    
    if (!artifact.tags.includes(tag)) {
      artifact.tags.push(tag);
      artifact.updatedAt = new Date().toISOString();
      this.saveArtifacts();
    }
    
    return artifact;
  }
  
  // Remove tag from artifact
  removeTag(id, tag) {
    const artifact = this.artifacts[id];
    if (!artifact) return null;
    
    artifact.tags = artifact.tags.filter(t => t !== tag);
    artifact.updatedAt = new Date().toISOString();
    this.saveArtifacts();
    
    return artifact;
  }
  
  // Search artifacts
  searchArtifacts(query) {
    const lowerQuery = query.toLowerCase();
    return Object.values(this.artifacts).filter(artifact =>
      artifact.title.toLowerCase().includes(lowerQuery) ||
      artifact.content.toLowerCase().includes(lowerQuery) ||
      artifact.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
    );
  }
  
  // Export artifact
  exportArtifact(id, format = 'json') {
    const artifact = this.artifacts[id];
    if (!artifact) return null;
    
    switch (format) {
      case 'json':
        return JSON.stringify(artifact, null, 2);
      case 'markdown':
        return `# ${artifact.title}\n\n${artifact.content}`;
      case 'plain':
        return artifact.content;
      default:
        return null;
    }
  }
  
  // Import artifact
  importArtifact(data) {
    try {
      const artifact = typeof data === 'string' ? JSON.parse(data) : data;
      
      // Generate new ID to avoid conflicts
      const newId = `artifact-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      artifact.id = newId;
      
      this.artifacts[newId] = artifact;
      this.saveArtifacts();
      
      return artifact;
    } catch (error) {
      console.error('Failed to import artifact:', error);
      return null;
    }
  }
  
  // Get statistics
  getStatistics() {
    const artifacts = Object.values(this.artifacts);
    
    return {
      total: artifacts.length,
      byType: {
        code: artifacts.filter(a => a.type === ArtifactTypes.CODE).length,
        document: artifacts.filter(a => a.type === ArtifactTypes.DOCUMENT).length,
        data: artifacts.filter(a => a.type === ArtifactTypes.DATA).length,
        chart: artifacts.filter(a => a.type === ArtifactTypes.CHART).length,
        html: artifacts.filter(a => a.type === ArtifactTypes.HTML).length,
      },
      pinned: artifacts.filter(a => a.pinned).length,
      totalVersions: artifacts.reduce((sum, a) => sum + a.versions.length, 0)
    };
  }
}

// Singleton instance
const artifactManager = new ArtifactManager();

export default artifactManager;
export { ArtifactManager };
