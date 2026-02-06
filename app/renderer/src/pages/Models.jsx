import React, { useState, useEffect } from 'react';
import { Download, Trash2, CheckCircle, Star } from 'lucide-react';

function Models() {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeModel, setActiveModel] = useState('');
  const [showDownload, setShowDownload] = useState(false);
  const [downloadTag, setDownloadTag] = useState('');
  const [downloading, setDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState('');
  const [error, setError] = useState('');

  // Popular models to suggest
  const popularModels = [
    { tag: 'llama3.2:3b', name: 'Llama 3.2 (3B)', size: '2GB', desc: 'Fast & efficient' },
    { tag: 'llama3.2:1b', name: 'Llama 3.2 (1B)', size: '1GB', desc: 'Ultra lightweight' },
    { tag: 'phi3:mini', name: 'Phi-3 Mini', size: '2.3GB', desc: 'Microsoft model' },
    { tag: 'mistral:7b', name: 'Mistral 7B', size: '4.1GB', desc: 'Balanced performance' },
    { tag: 'codellama:7b', name: 'Code Llama 7B', size: '3.8GB', desc: 'Coding specialist' },
  ];

  useEffect(() => {
    loadModels();
    loadActiveModel();
    
    // Listen for download progress
    if (window.electron?.models?.onDownloadProgress) {
      const unsubscribe = window.electron.models.onDownloadProgress((message) => {
        setDownloadProgress(prev => prev + message);
      });
      return () => unsubscribe?.();
    }
  }, []);

  const loadModels = async () => {
    setLoading(true);
    try {
      const isElectron = !!window.electron?.models;
      
      if (isElectron) {
        // Electron mode
        const syncResult = await window.electron.models.sync();
        if (syncResult.added > 0) {
          console.log(`Synced ${syncResult.added} new models from Ollama`);
        }
        const data = await window.electron.models.list();
        setModels(data);
      } else {
        // Browser mode - use HTTP API
        const syncResponse = await fetch('http://localhost:5174/api/models/sync', {
          method: 'POST'
        });
        const syncResult = await syncResponse.json();
        
        if (syncResult.added > 0) {
          console.log(`Synced ${syncResult.added} new models from Ollama`);
        }
        
        const listResponse = await fetch('http://localhost:5174/api/models');
        const data = await listResponse.json();
        setModels(data);
      }
    } catch (err) {
      setError('Failed to load models: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadActiveModel = () => {
    if (window.electron) {
      window.electron.project.getConfig().then(config => {
        setActiveModel(config.model || '');
      });
    }
  };

  const selectModel = async (modelTag) => {
    try {
      setError('');
      
      const isElectron = !!window.electron?.models;
      
      if (isElectron) {
        await window.electron.models.select(modelTag);
      } else {
        const response = await fetch('http://localhost:5174/api/models/select', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model_tag: modelTag })
        });
        const result = await response.json();
        if (result.error) throw new Error(result.error);
      }
      
      setActiveModel(modelTag);
    } catch (err) {
      setError('Failed to select model: ' + err.message);
    }
  };

  const removeModel = async (modelTag) => {
    if (!confirm(`Remove model "${modelTag}"?`)) return;
    
    try {
      setError('');
      
      const isElectron = !!window.electron?.models;
      
      if (isElectron) {
        await window.electron.models.remove(modelTag);
      } else {
        const response = await fetch('http://localhost:5174/api/models/remove', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model_tag: modelTag })
        });
        const result = await response.json();
        if (result.error) throw new Error(result.error);
      }
      
      await loadModels();
      if (activeModel === modelTag) {
        setActiveModel('');
      }
    } catch (err) {
      setError('Failed to remove model: ' + err.message);
    }
  };

  const downloadModel = async () => {
    if (!downloadTag.trim()) return;
    
    try {
      setError('');
      setDownloading(true);
      setDownloadProgress('Starting download...\n');
      
      const isElectron = !!window.electron?.models;
      
      if (isElectron) {
        await window.electron.models.download(downloadTag);
      } else {
        const response = await fetch('http://localhost:5174/api/models/download', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ model_name: downloadTag })
        });
        const result = await response.json();
        if (result.error) throw new Error(result.error);
      }
      
      setDownloadProgress(prev => prev + '\n✅ Download complete!\n');
      await loadModels();
      setDownloadTag('');
      
      setTimeout(() => {
        setShowDownload(false);
        setDownloadProgress('');
      }, 2000);
    } catch (err) {
      setError('Failed to download model: ' + err.message);
      setDownloadProgress(prev => prev + '\n❌ Download failed: ' + err.message);
    } finally {
      setDownloading(false);
    }
  };

  const syncModels = async () => {
    try {
      setError('');
      setLoading(true);
      
      const isElectron = !!window.electron?.models;
      let result;
      
      if (isElectron) {
        result = await window.electron.models.sync();
      } else {
        const response = await fetch('http://localhost:5174/api/models/sync', {
          method: 'POST'
        });
        result = await response.json();
        if (result.error) throw new Error(result.error);
      }
      
      await loadModels();
      
      if (result.added > 0 || result.removed > 0) {
        alert(`Sync complete!\n✅ Added: ${result.added}\n🗑️ Removed: ${result.removed}\n📊 Total: ${result.total}`);
      } else {
        alert(`All models are already synced! (${result.total} total)`);
      }
    } catch (err) {
      setError('Failed to sync models: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 className="page-title">Models</h1>
          <p className="page-description">Manage your Ollama models</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            onClick={syncModels}
            disabled={loading}
            style={{
              padding: '10px 20px',
              backgroundColor: loading ? '#333' : '#00d9ff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: 'bold'
            }}
          >
            🔄 Sync
          </button>
          <button 
            onClick={() => setShowDownload(!showDownload)}
            style={{
              padding: '10px 20px',
              backgroundColor: '#4a9eff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: 'bold'
            }}
          >
            <Download size={18} />
            Download Model
          </button>
        </div>
      </div>

      {error && (
        <div style={{
          padding: '12px',
          backgroundColor: '#ff4444',
          color: 'white',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* Download Panel */}
      {showDownload && (
        <div className="card" style={{ marginBottom: '20px', backgroundColor: '#1a1a2e' }}>
          <h3 style={{ marginBottom: '16px' }}>Download Model</h3>
          
          {/* Quick Select */}
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ fontSize: '14px', marginBottom: '12px', color: '#888' }}>
              Popular Models
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '12px' }}>
              {popularModels.map(model => (
                <div
                  key={model.tag}
                  onClick={() => setDownloadTag(model.tag)}
                  style={{
                    padding: '12px',
                    backgroundColor: downloadTag === model.tag ? '#0f3460' : '#0a0a0f',
                    border: `2px solid ${downloadTag === model.tag ? '#4a9eff' : '#333'}`,
                    borderRadius: '6px',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{model.name}</div>
                  <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>
                    {model.size} · {model.desc}
                  </div>
                  <div style={{ fontSize: '11px', color: '#666' }}>
                    {model.tag}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Custom Tag Input */}
          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: '#888' }}>
                Or enter custom model tag:
              </label>
              <input
                type="text"
                value={downloadTag}
                onChange={(e) => setDownloadTag(e.target.value)}
                placeholder="e.g., llama3:8b, mistral:latest"
                disabled={downloading}
                style={{
                  width: '100%',
                  padding: '10px',
                  backgroundColor: '#0a0a0f',
                  color: 'white',
                  border: '1px solid #333',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              />
            </div>
            <button
              onClick={downloadModel}
              disabled={!downloadTag.trim() || downloading}
              style={{
                padding: '10px 20px',
                backgroundColor: !downloadTag.trim() || downloading ? '#333' : '#4a9eff',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: !downloadTag.trim() || downloading ? 'not-allowed' : 'pointer',
                fontWeight: 'bold',
                minWidth: '120px'
              }}
            >
              {downloading ? 'Downloading...' : 'Download'}
            </button>
          </div>

          <p style={{ marginTop: '12px', fontSize: '12px', color: '#666' }}>
            💡 Find more models at <a href="https://ollama.com/library" target="_blank" style={{ color: '#4a9eff' }}>ollama.com/library</a>
          </p>
          
          {downloadProgress && (
            <div style={{
              marginTop: '16px',
              padding: '12px',
              backgroundColor: '#0a0a0f',
              borderRadius: '6px',
              fontSize: '12px',
              fontFamily: 'monospace',
              whiteSpace: 'pre-wrap',
              maxHeight: '200px',
              overflowY: 'auto',
              border: '1px solid #333'
            }}>
              {downloadProgress}
            </div>
          )}
        </div>
      )}

      {/* Models List */}
      {loading ? (
        <div className="card">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="spinner" style={{ 
              margin: '0 auto 16px',
              width: '40px',
              height: '40px',
              border: '4px solid #333',
              borderTop: '4px solid #4a9eff',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }} />
            <p>Loading models...</p>
          </div>
        </div>
      ) : models.length === 0 ? (
        <div className="card">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <p style={{ marginBottom: '16px' }}>No models downloaded yet.</p>
            <p style={{ color: '#888', fontSize: '14px' }}>
              Click "Download Model" above to get started, or use the terminal:
            </p>
            <code style={{ 
              display: 'block',
              marginTop: '12px',
              padding: '8px',
              backgroundColor: '#0a0a0f',
              borderRadius: '4px'
            }}>
              ollama pull llama3.2:3b
            </code>
          </div>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '12px' }}>
          {models.map((model, idx) => {
            const isActive = model.name === activeModel;
            
            return (
              <div 
                key={idx} 
                className="card" 
                style={{
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center',
                  backgroundColor: isActive ? '#0f3460' : undefined,
                  border: isActive ? '2px solid #4a9eff' : '1px solid #333'
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <h3 style={{ margin: 0 }}>{model.name || 'Unknown'}</h3>
                    {isActive && (
                      <span style={{
                        padding: '2px 8px',
                        backgroundColor: '#4a9eff',
                        color: 'white',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 'bold'
                      }}>
                        ACTIVE
                      </span>
                    )}
                  </div>
                  <p style={{ color: '#888', fontSize: '14px', margin: 0 }}>
                    {model.size ? `${(model.size / 1e9).toFixed(2)} GB` : 'Size unknown'}
                    {model.modified_at && ` · Modified ${new Date(model.modified_at).toLocaleDateString()}`}
                  </p>
                </div>
                
                <div style={{ display: 'flex', gap: '8px' }}>
                  {!isActive && (
                    <button 
                      onClick={() => selectModel(model.name)}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: '#4a9eff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontWeight: 'bold'
                      }}
                    >
                      <CheckCircle size={16} />
                      Select
                    </button>
                  )}
                  <button 
                    onClick={() => removeModel(model.name)}
                    style={{
                      padding: '8px 16px',
                      backgroundColor: '#ff4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <Trash2 size={16} />
                    Remove
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default Models;
