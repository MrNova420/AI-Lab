import { app, BrowserWindow, ipcMain } from 'electron';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { spawn } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

let mainWindow = null;
const PYTHON_BIN = join(__dirname, '..', '..', 'venv', 'bin', 'python');
const PROJECT_ROOT = join(__dirname, '..', '..');

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    backgroundColor: '#0a0a0f',
    webPreferences: {
      preload: join(__dirname, '..', 'preload', 'index.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // Grant media permissions
  mainWindow.webContents.session.setPermissionRequestHandler((webContents, permission, callback) => {
    console.log('[Permissions] Request for:', permission);
    if (permission === 'media' || permission === 'microphone') {
      callback(true);
    } else {
      callback(false);
    }
  });

  if (!app.isPackaged) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(join(__dirname, '..', 'dist', 'index.html'));
  }
}

// IPC Handlers
ipcMain.handle('models:list', async () => {
  return new Promise((resolve) => {
    const py = spawn(PYTHON_BIN, ['-c', `
import sys
sys.path.insert(0, '${PROJECT_ROOT}')
from core.model_manager import ModelManager
mm = ModelManager('${PROJECT_ROOT}')
models = mm.list_downloaded_models()
import json
print(json.dumps(models))
`]);

    let stdout = '';
    py.stdout.on('data', (data) => stdout += data.toString());
    py.on('close', () => {
      try {
        resolve(JSON.parse(stdout));
      } catch {
        resolve([]);
      }
    });
  });
});

ipcMain.handle('project:get-config', async () => {
  return new Promise((resolve) => {
    const py = spawn(PYTHON_BIN, ['-c', `
import sys
sys.path.insert(0, '${PROJECT_ROOT}')
from core.project_manager import ProjectManager
pm = ProjectManager('${PROJECT_ROOT}')
config = pm.get_active_project_config()
import json
print(json.dumps(config))
`]);

    let stdout = '';
    py.stdout.on('data', (data) => stdout += data.toString());
    py.on('close', () => {
      try {
        resolve(JSON.parse(stdout));
      } catch {
        resolve({project_name: 'default'});
      }
    });
  });
});

// Chat streaming handler
ipcMain.handle('chat:send', async (event, message, history = []) => {
  return new Promise((resolve, reject) => {
    console.log('[Chat] Starting chat with message:', message);
    
    const py = spawn(PYTHON_BIN, [
      join(PROJECT_ROOT, 'scripts', 'chat_stream.py'),
      message,
      JSON.stringify(history)
    ], {
      env: { ...process.env, PYTHONPATH: PROJECT_ROOT }
    });

    let fullResponse = '';
    
    py.stdout.on('data', (data) => {
      const chunks = data.toString().split('\n').filter(Boolean);
      chunks.forEach(chunk => {
        try {
          const parsed = JSON.parse(chunk);
          console.log('[Chat] Received:', parsed.type);
          
          if (parsed.type === 'token') {
            fullResponse += parsed.token;
            event.sender.send('chat:token', parsed.token);
          } else if (parsed.type === 'done') {
            console.log('[Chat] Done, full response length:', parsed.full_response.length);
            resolve(parsed.full_response);
          } else if (parsed.type === 'error') {
            reject(new Error(parsed.message));
          }
        } catch (e) {
          console.log('[Chat] Parse error:', e.message);
        }
      });
    });

    py.stderr.on('data', (data) => {
      console.error('[Chat] stderr:', data.toString());
    });

    py.on('close', (code) => {
      console.log('[Chat] Process closed with code:', code, 'Response length:', fullResponse.length);
      // If we got tokens but no 'done' message, resolve with what we have
      if (fullResponse && !resolved) {
        console.log('[Chat] Resolving with partial response');
        resolve(fullResponse);
      }
    });

    let resolved = false;
    const originalResolve = resolve;
    resolve = (value) => {
      if (!resolved) {
        resolved = true;
        originalResolve(value);
      }
    };

    py.on('error', (err) => {
      console.error('[Chat] Process error:', err);
      if (!resolved) {
        reject(err);
      }
    });

    // Timeout after 60 seconds
    setTimeout(() => {
      if (!resolved) {
        console.log('[Chat] Timeout, resolving with what we have:', fullResponse);
        resolve(fullResponse || 'Request timed out');
      }
    }, 60000);
  });
});

// Model management
ipcMain.handle('models:download', async (event, modelTag) => {
  return new Promise((resolve, reject) => {
    console.log('[Models] Downloading:', modelTag);
    
    const py = spawn(PYTHON_BIN, ['-c', `
import sys
sys.path.insert(0, '${PROJECT_ROOT}')
from core.model_manager import ModelManager
try:
    mm = ModelManager('${PROJECT_ROOT}')
    mm.download_model('${modelTag.replace(/'/g, "\\'")}')
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
`]);

    let output = '';
    py.stdout.on('data', (data) => {
      const text = data.toString();
      output += text;
      console.log('[Models] Download output:', text);
      // Send progress updates to renderer
      event.sender.send('models:download-progress', text);
    });
    
    py.stderr.on('data', (data) => {
      const text = data.toString();
      console.log('[Models] Download stderr:', text);
      event.sender.send('models:download-progress', text);
    });

    py.on('close', (code) => {
      console.log('[Models] Download finished with code:', code);
      if (code === 0 || output.includes('SUCCESS')) {
        resolve({ success: true });
      } else {
        reject(new Error(output || 'Download failed'));
      }
    });
    
    py.on('error', (err) => {
      console.error('[Models] Download error:', err);
      reject(err);
    });
  });
});

ipcMain.handle('models:select', async (event, modelTag) => {
  return new Promise((resolve) => {
    const py = spawn(PYTHON_BIN, ['-c', `
import sys
sys.path.insert(0, '${PROJECT_ROOT}')
from core.project_manager import ProjectManager
pm = ProjectManager('${PROJECT_ROOT}')
pm.set_active_model('${modelTag}')
print('success')
`]);

    py.on('close', () => resolve({ success: true }));
  });
});

ipcMain.handle('models:remove', async (event, modelTag) => {
  return new Promise((resolve) => {
    const py = spawn(PYTHON_BIN, ['-c', `
import sys
sys.path.insert(0, '${PROJECT_ROOT}')
from core.model_manager import ModelManager
mm = ModelManager('${PROJECT_ROOT}')
mm.remove_model('${modelTag}')
print('success')
`]);

    py.on('close', () => resolve({ success: true }));
  });
});

// Sync models with Ollama
ipcMain.handle('models:sync', async () => {
  return new Promise((resolve) => {
    const py = spawn(PYTHON_BIN, ['-c', `
import sys
sys.path.insert(0, '${PROJECT_ROOT}')
from core.model_manager import ModelManager
mm = ModelManager('${PROJECT_ROOT}')
result = mm.sync_models()
import json
print(json.dumps(result))
`]);

    let stdout = '';
    py.stdout.on('data', (data) => stdout += data.toString());
    py.on('close', () => {
      try {
        resolve(JSON.parse(stdout));
      } catch {
        resolve({ added: 0, removed: 0, total: 0 });
      }
    });
  });
});

// Voice transcription handler
ipcMain.handle('voice:transcribe', async (event, audioPath) => {
  return new Promise((resolve, reject) => {
    const py = spawn(PYTHON_BIN, ['-c', `
import sys
sys.path.insert(0, '${PROJECT_ROOT}')
from voice.transcribe import transcribe_audio
text = transcribe_audio('${audioPath}')
print(text)
`]);

    let stdout = '';
    py.stdout.on('data', (data) => stdout += data.toString());
    py.on('close', (code) => {
      if (code === 0) {
        resolve(stdout.trim());
      } else {
        reject(new Error('Transcription failed'));
      }
    });
  });
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
