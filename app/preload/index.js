const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  models: {
    list: () => ipcRenderer.invoke('models:list'),
    download: (modelTag) => ipcRenderer.invoke('models:download', modelTag),
    onDownloadProgress: (callback) => {
      const handler = (_, message) => callback(message);
      ipcRenderer.on('models:download-progress', handler);
      return () => ipcRenderer.removeListener('models:download-progress', handler);
    },
    select: (modelTag) => ipcRenderer.invoke('models:select', modelTag),
    remove: (modelTag) => ipcRenderer.invoke('models:remove', modelTag),
    sync: () => ipcRenderer.invoke('models:sync')
  },
  project: {
    getConfig: () => ipcRenderer.invoke('project:get-config')
  },
  chat: {
    send: (message, history) => ipcRenderer.invoke('chat:send', message, history),
    onToken: (callback) => {
      const handler = (_, token) => callback(token);
      ipcRenderer.on('chat:token', handler);
      return () => ipcRenderer.removeListener('chat:token', handler);
    }
  },
  voice: {
    transcribe: (audioPath) => ipcRenderer.invoke('voice:transcribe', audioPath)
  }
});
