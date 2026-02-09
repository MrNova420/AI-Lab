import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2 } from 'lucide-react';
import BrowserCommander from './commander-browser.js';
import { trackToolsFromResponse } from '../utils/toolTracking';
import { saveModePreferences, loadModePreferences } from '../utils/statePersistence';
import sessionManager from '../utils/sessionManager';

function Voice() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState('');
  const [audioDevices, setAudioDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');
  const [messages, setMessages] = useState([]);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [textOnlyMode, setTextOnlyMode] = useState(false);
  const [commanderMode, setCommanderMode] = useState(false);
  const [webSearchMode, setWebSearchMode] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [showSessionList, setShowSessionList] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const recognitionRef = useRef(null);
  const lastUserMessageRef = useRef('');
  const lastAIMessageRef = useRef('');
  const commanderRef = useRef(new BrowserCommander());

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Stop any ongoing speech
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
      // Stop recognition
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        recognitionRef.current = null;
      }
      // Stop media streams
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      // Stop media recorder
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
    };
  }, []);

  // Initialize session on mount
  const sessionInitialized = useRef(false);
  useEffect(() => {
    const initializeSession = async () => {
      if (sessionInitialized.current) return;
      sessionInitialized.current = true;
      
      const prefs = loadModePreferences();
      setCommanderMode(prefs.commanderMode);
      setWebSearchMode(prefs.webSearchMode);
      
      // Start a new voice session
      try {
        const sessionId = await sessionManager.startNewSession('User', { type: 'voice' });
        setCurrentSessionId(sessionId);
        console.log(`🎤 Started voice session: ${sessionId}`);
      } catch (error) {
        console.error('Voice session initialization error:', error);
      }
    };
    
    initializeSession();
  }, []);

  // Save mode preferences whenever they change
  useEffect(() => {
    saveModePreferences(commanderMode, webSearchMode);
  }, [commanderMode, webSearchMode]);

  // Sync messages with session manager
  useEffect(() => {
    if (messages.length > 0 && currentSessionId) {
      const session = sessionManager.getCurrentSession();
      if (session && session.session_id === currentSessionId) {
        session.messages = messages;
      }
    }
  }, [messages, currentSessionId]);

  // Load text-only preference from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('voiceTextOnlyMode');
    if (saved !== null) {
      setTextOnlyMode(JSON.parse(saved));
    }
    
    const savedCommander = localStorage.getItem('voiceCommanderMode');
    if (savedCommander !== null) {
      setCommanderMode(JSON.parse(savedCommander));
    }
    
    // Load voices for TTS - wait for them to load
    if ('speechSynthesis' in window) {
      const loadVoices = () => {
        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
          console.log('🎤 Available voices:', voices.length);
          // Log female voices
          const femaleVoices = voices.filter(v => 
            v.name.toLowerCase().includes('female') ||
            v.name.toLowerCase().includes('zira') ||
            v.name.toLowerCase().includes('samantha') ||
            v.name.toLowerCase().includes('woman')
          );
          console.log('👩 Female voices found:', femaleVoices.map(v => v.name).join(', '));
        }
      };
      
      // Load immediately and on voices changed
      loadVoices();
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
      }
    }
  }, []);

  useEffect(() => {
    // Get available audio devices
    const loadDevices = async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = devices.filter(d => d.kind === 'audioinput');
        console.log('Initial audio devices:', audioInputs);
        setAudioDevices(audioInputs);
        
        if (audioInputs.length > 0 && !selectedDevice) {
          setSelectedDevice(audioInputs[0].deviceId);
        }
      } catch (err) {
        console.error('Device enumeration error:', err);
        setError('Browser microphone API not available: ' + err.message);
      }
    };
    
    loadDevices();
    
    // Listen for device changes (e.g., Bluetooth connects)
    navigator.mediaDevices.addEventListener('devicechange', loadDevices);
    return () => {
      navigator.mediaDevices.removeEventListener('devicechange', loadDevices);
    };
  }, []);

  const startRecording = async () => {
    try {
      setError('');
      setTranscript('');
      setResponse('');
      
      // Check if running in Electron
      const isElectron = window.navigator.userAgent.includes('Electron');
      
      // First time or no devices: request any audio device
      const constraints = {
        audio: (audioDevices.length === 0 || !selectedDevice) 
          ? true 
          : { deviceId: { exact: selectedDevice } }
      };
      
      console.log('Requesting audio with constraints:', constraints);
      console.log('Is Electron?', isElectron);
      console.log('User agent:', window.navigator.userAgent);
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      
      // After getting permission, refresh device list
      const devices = await navigator.mediaDevices.enumerateDevices();
      const audioInputs = devices.filter(d => d.kind === 'audioinput');
      console.log('Refreshed audio devices after permission:', audioInputs);
      setAudioDevices(audioInputs);
      
      if (audioInputs.length > 0 && !selectedDevice) {
        setSelectedDevice(audioInputs[0].deviceId);
      }
      
      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await processAudio(audioBlob);
        
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      console.log('Recording started');
      
      // Initialize Web Speech API for live transcription
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        recognition.maxAlternatives = 1;
        
        recognition.onstart = () => {
          console.log('🎤 Speech recognition started');
          setTranscript('[Listening...]');
        };
        
        recognition.onresult = (event) => {
          let interimTranscript = '';
          let finalTranscript = '';
          
          for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcriptPiece = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
              finalTranscript += transcriptPiece + ' ';
            } else {
              interimTranscript += transcriptPiece;
            }
          }
          
          // Build complete transcript
          const fullTranscript = finalTranscript || interimTranscript;
          console.log('🎤 Transcript update:', fullTranscript);
          
          if (fullTranscript.trim()) {
            setTranscript(fullTranscript.trim());
          }
        };
        
        recognition.onerror = (event) => {
          console.error('Speech recognition error:', event.error);
          if (event.error === 'no-speech') {
            console.log('No speech detected yet, still listening...');
            // Don't show error for no-speech, it's expected while silent
          } else if (event.error === 'not-allowed') {
            setError('❌ Microphone permission denied');
          } else {
            setError(`⚠️ Speech recognition error: ${event.error}`);
          }
        };
        
        recognition.onend = () => {
          console.log('🛑 Speech recognition ended');
          // If still recording, restart recognition (for continuous listening)
          if (isRecording && mediaRecorderRef.current?.state === 'recording') {
            console.log('Restarting speech recognition...');
            try {
              recognition.start();
            } catch (e) {
              console.log('Could not restart recognition:', e.message);
            }
          }
        };
        
        recognitionRef.current = recognition;
        
        try {
          recognition.start();
          console.log('✅ Web Speech API started');
        } catch (e) {
          console.error('Failed to start speech recognition:', e);
          setError('⚠️ Could not start speech recognition: ' + e.message);
        }
      } else {
        console.warn('⚠️ Web Speech API not supported in this browser');
        setTranscript('[Web Speech API not available - using audio recording only]');
      }
      
      // Auto-stop after 60 seconds to prevent infinite recording
      setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          console.log('Auto-stopping recording after timeout');
          stopRecording();
        }
      }, 60000);
      
    } catch (err) {
      console.error('Recording error:', err);
      
      // Check if this is the WSL/Electron issue
      const isElectron = window.navigator.userAgent.includes('Electron');
      
      if (err.name === 'NotFoundError' && isElectron) {
        setError(
          '🚨 WSL + Electron Limitation Detected!\n\n' +
          'Electron in WSL cannot access Windows microphones.\n\n' +
          '✅ EASY FIX: Open Chrome/Edge on Windows and go to:\n' +
          'http://localhost:5174\n\n' +
          'Voice will work perfectly in a regular browser! 🎤'
        );
      } else if (err.name === 'NotAllowedError') {
        setError('❌ Microphone permission denied. Please allow access and try again.');
      } else if (err.name === 'NotFoundError') {
        setError('⚠️ No microphone found. Please connect a microphone and try again.');
      } else {
        setError('⚠️ Microphone access failed: ' + err.message);
      }
      
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = devices.filter(d => d.kind === 'audioinput');
        setAudioDevices(audioInputs);
        if (audioInputs.length > 0 && !selectedDevice) {
          setSelectedDevice(audioInputs[0].deviceId);
        }
      } catch {}
    }
  };

  const stopRecording = async () => {
    if (mediaRecorderRef.current && isRecording) {
      console.log('🛑 Stopping recording...');
      console.log('Current transcript:', transcript);
      
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Stop live transcription
      if (recognitionRef.current) {
        console.log('Stopping speech recognition...');
        recognitionRef.current.stop();
        recognitionRef.current = null;
      }
      
      // Stop audio stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      
      // Clean up transcript (remove interim markers and [Listening...])
      const cleanTranscript = transcript
        .replace(/\[Listening\.\.\.\]/g, '')
        .replace(/\[interim\].*$/g, '')
        .trim();
      
      console.log('Cleaned transcript:', cleanTranscript);
      setTranscript(cleanTranscript || '[No speech detected]');
      
      if (cleanTranscript && cleanTranscript.length > 0) {
        // Ultra strict duplicate check using ref
        if (lastUserMessageRef.current === cleanTranscript) {
          console.warn('⚠️ Duplicate message detected (ref check), skipping');
          return;
        }
        
        // Update ref FIRST
        lastUserMessageRef.current = cleanTranscript;
        
        // DON'T add user message here - let getAIResponse handle it
        // This prevents duplicates when Commander mode or normal chat adds the message
        
        // Add user message to session manager
        if (currentSessionId && cleanTranscript) {
          sessionManager.addMessage('user', cleanTranscript);
        }
        
        // Send to AI
        console.log('📤 Sending to AI/Commander:', cleanTranscript);
        setIsTranscribing(true);
        await getAIResponse(cleanTranscript);
        setIsTranscribing(false);
      } else {
        console.warn('⚠️ No speech detected in transcript');
        setError('No speech detected. Please speak clearly and try again.');
        // Reset transcript display
        setTimeout(() => setTranscript(''), 3000);
      }
    }
  };

  const processAudio = async (audioBlob) => {
    // No longer needed - we use live transcription
    // This function is kept for compatibility but does nothing
    console.log('Audio blob captured:', audioBlob.size, 'bytes');
  };

  const getAIResponse = async (userMessage) => {
    try {
      console.log('📤 Getting AI response for:', userMessage);
      setResponse('🤖 Thinking...');
      
      // Always add user message first (only once, centralized here)
      setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
      console.log('✅ User message added to messages');
      
      const history = messages.slice(-10);
      console.log('📜 History length:', history.length);
      console.log(`⚡ Commander mode: ${commanderMode ? 'ENABLED - AI will use tools' : 'disabled'}`);
      
      let fullResponse = '';
      let sentenceBuffer = '';  // Buffer for streaming TTS
      let hasSpoken = false;    // Track if we've started speaking
      
      // Check if running in Electron or browser
      const isElectron = window.electron?.chat?.send;
      
      // Get API URL (WSL IP for browser, localhost for Electron)
      const apiUrl = isElectron ? 'http://localhost:5174' : 'http://localhost:5174';
      
      if (isElectron) {
        console.log('✅ Using Electron IPC bridge...');
        
        // Listen for streaming tokens
        const unsubscribe = window.electron.chat.onToken((token) => {
          console.log('🔵 Token received:', token);
          fullResponse += token;
          setResponse(fullResponse);
          
          // Streaming TTS - speak sentences as they complete
          if (!textOnlyMode) {
            sentenceBuffer += token;
            const sentences = sentenceBuffer.match(/[^.!?]+[.!?]+/g);
            
            if (sentences && sentences.length > 0) {
              // Speak complete sentences
              for (let i = 0; i < sentences.length - 1; i++) {
                speakSentence(sentences[i].trim());
                hasSpoken = true;
              }
              // Keep last incomplete sentence in buffer
              sentenceBuffer = sentenceBuffer.substring(sentences.slice(0, -1).join('').length);
            }
          }
        });
        
        fullResponse = await window.electron.chat.send(userMessage, history);
        unsubscribe();
        
      } else {
        console.log('🌐 Using HTTP API (browser mode)...');
        console.log('🔗 API URL:', apiUrl);
        
        // Use HTTP API for browser with commander_mode flag
        const response = await fetch(`${apiUrl}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            message: userMessage, 
            history,
            commander_mode: commanderMode,
            web_search_mode: webSearchMode,
            session_id: 'browser_session'  // Session tracking for reasoning layer
          })
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        // Read streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value);
          const lines = chunk.split('\n').filter(Boolean);
          
          for (const line of lines) {
            try {
              const data = JSON.parse(line);
              console.log('🔵 API data:', data.type);
              
              if (data.type === 'reasoning') {
                // Show reasoning info 🧠
                console.log('🧠 Reasoning:', {
                  intent: data.intent,
                  complexity: data.complexity,
                  confidence: data.confidence,
                  cached_count: data.cached_count,
                  trace: data.trace
                });
                
                // Add visual feedback for reasoning
                if (data.can_optimize && data.cached_count > 0) {
                  const cacheInfo = `\n⚡ Using ${data.cached_count} cached result(s) for faster response!\n`;
                  fullResponse += cacheInfo;
                  setResponse(fullResponse);
                }
                
                if (data.trace && data.trace.length > 0) {
                  console.log('🧠 Reasoning trace:');
                  data.trace.forEach(t => console.log(`   ${t}`));
                }
                
              } else if (data.type === 'token') {
                fullResponse += data.token;
                setResponse(fullResponse);
                
                // Streaming TTS - speak sentences as they complete
                if (!textOnlyMode) {
                  sentenceBuffer += data.token;
                  const sentences = sentenceBuffer.match(/[^.!?]+[.!?]+/g);
                  
                  if (sentences && sentences.length > 0) {
                    // Speak complete sentences
                    for (let i = 0; i < sentences.length - 1; i++) {
                      speakSentence(sentences[i].trim());
                      hasSpoken = true;
                    }
                    // Keep last incomplete sentence in buffer
                    sentenceBuffer = sentenceBuffer.substring(sentences.slice(0, -1).join('').length);
                  }
                }
                
              } else if (data.type === 'tool_results') {
                // Commander mode: Show formatted tool results (like Copilot/Gemini)
                console.log('🛠️ Tools executed:', data.results);
                
                // If we have formatted output from backend, use it
                if (data.formatted) {
                  fullResponse += data.formatted;
                  setResponse(fullResponse);
                } else {
                  // Fallback: Show feedback for each tool
                  const toolFeedback = data.results.map(r => {
                    if (r.result.success) {
                      return `✅ ${r.tool}: ${r.result.message || 'Done'}`;
                    } else {
                      return `❌ ${r.tool}: ${r.result.error}`;
                    }
                  }).join('\n');
                  
                  fullResponse += '\n\n' + toolFeedback;
                  setResponse(fullResponse);
                }
                
                hasSpoken = true;
              } else if (data.type === 'done') {
                fullResponse = data.full_response;
              } else if (data.type === 'error') {
                throw new Error(data.message);
              }
            } catch (e) {
              console.warn('Parse error:', e.message);
            }
          }
        }
      }
      
      // Speak any remaining text in buffer
      if (!textOnlyMode && sentenceBuffer.trim().length > 0) {
        speakSentence(sentenceBuffer.trim());
        hasSpoken = true;
      }
      
      console.log('✅ Full response received, length:', fullResponse.length);
      setResponse(fullResponse);
      
      // Ultra strict duplicate check using ref
      if (lastAIMessageRef.current === fullResponse) {
        console.warn('⚠️ Duplicate AI response detected (ref check), skipping');
        return;
      }
      
      // Update ref
      lastAIMessageRef.current = fullResponse;
      
      // Add to messages with mode indicators and tool detection
      if (fullResponse.trim().length > 0) {
        const assistantMessage = {
          role: 'assistant',
          content: fullResponse,
          modes: {
            commander: commanderMode,
            webSearch: webSearchMode
          },
          timestamp: new Date().toISOString()
        };
        
        // Check if response contains tool executions
        if (fullResponse.includes('🛠️')) {
          assistantMessage.hasTools = true;
          // Track tool usage for statistics
          trackToolsFromResponse(fullResponse);
        }
        
        setMessages(prev => [...prev, assistantMessage]);
        
        // Add to session manager
        if (currentSessionId) {
          sessionManager.addMessage('assistant', fullResponse, {
            modes: assistantMessage.modes,
            hasTools: assistantMessage.hasTools,
            timestamp: assistantMessage.timestamp
          });
        }
        
        console.log('✅ AI response added to messages with metadata');
      }
      
      // If we didn't speak anything yet and not in text-only mode, speak the full response
      if (!textOnlyMode && !hasSpoken && fullResponse.trim().length > 0) {
        console.log('🔊 Speaking full response...');
        speakResponse(fullResponse);
      }
      
    } catch (err) {
      console.error('❌ AI response error:', err);
      setError('Failed to get AI response: ' + err.message);
      setResponse('');
    }
  };

  // Streaming TTS - speak individual sentences as they complete
  const speakSentence = (text) => {
    if ('speechSynthesis' in window && text.trim().length > 0) {
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Get available voices
      const voices = window.speechSynthesis.getVoices();
      
      // Prefer Microsoft David Desktop (confirmed working!)
      const preferredVoices = [
        'Microsoft David Desktop',  // Windows 10/11 - WORKING!
        'Microsoft David',          // Windows fallback
        'Google UK English Male',   // Google neural
        'Alex',                     // macOS
      ];
      
      // Find voice
      let selectedVoice = null;
      for (const preferred of preferredVoices) {
        selectedVoice = voices.find(v => v.name === preferred);
        if (selectedVoice) break;
      }
      
      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }
      
      // ULTRA SMOOTH JARVIS-LIKE SETTINGS
      utterance.rate = 0.85;      // Even slower = even smoother
      utterance.pitch = 0.75;     // Lower = deeper masculine
      utterance.volume = 0.88;    // Softer = smoother
      
      utterance.onerror = (e) => {
        console.error('❌ TTS error:', e);
      };
      
      // Queue the sentence
      window.speechSynthesis.speak(utterance);
      console.log('🔊 Streaming TTS:', text.substring(0, 50) + '...');
    }
  };

  const speakResponse = (text) => {
    // Use Web Speech API for TTS with smooth natural male voice
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Get available voices
      const voices = window.speechSynthesis.getVoices();
      
      // Prefer Microsoft David Desktop (you confirmed it's working!)
      const preferredVoices = [
        'Microsoft David Desktop',  // Windows 10/11 - WORKING!
        'Microsoft David',          // Windows fallback
        'Google UK English Male',   // Google neural
        'Alex',                     // macOS
      ];
      
      // Find voice
      let selectedVoice = null;
      for (const preferred of preferredVoices) {
        selectedVoice = voices.find(v => v.name === preferred);
        if (selectedVoice) break;
      }
      
      if (selectedVoice) {
        utterance.voice = selectedVoice;
        console.log('🎤 Using voice:', selectedVoice.name);
      }
      
      // ULTRA SMOOTH JARVIS-LIKE SETTINGS
      utterance.rate = 0.85;      // Even slower = even smoother
      utterance.pitch = 0.75;     // Lower = deeper masculine
      utterance.volume = 0.88;    // Softer = smoother
      
      // Better event handling
      utterance.onstart = () => {
        console.log('🔊 Speaking with smooth voice...');
      };
      utterance.onend = () => {
        console.log('✅ Speech finished');
      };
      utterance.onerror = (e) => {
        console.error('❌ Speech error:', e);
      };
      
      window.speechSynthesis.speak(utterance);
    }
  };

  const clearConversation = async () => {
    // Start new voice session
    try {
      const sessionId = await sessionManager.startNewSession('User', { type: 'voice' });
      setCurrentSessionId(sessionId);
      setMessages([]);
      setTranscript('');
      setResponse('');
      setError('');
      lastUserMessageRef.current = '';
      lastAIMessageRef.current = '';
      console.log('✨ New voice session started');
    } catch (error) {
      console.error('Failed to start new voice session:', error);
      // Fallback
      setMessages([]);
      setTranscript('');
      setResponse('');
      setError('');
      lastUserMessageRef.current = '';
      lastAIMessageRef.current = '';
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ marginBottom: '20px' }}>
        <h1 className="page-title">Voice Assistant</h1>
        <p className="page-description">
          🎉 Native Web Audio API - NO WSL audio bridge issues!
        </p>
        
        {/* Commander Mode Indicator */}
        {commanderMode && (
          <div style={{
            marginTop: '12px',
            padding: '12px 16px',
            backgroundColor: '#ff4444',
            border: '2px solid #ff6666',
            borderRadius: '8px',
            color: 'white',
            fontWeight: 'bold',
            fontSize: '14px',
            textAlign: 'center',
            animation: 'pulse 2s ease-in-out infinite'
          }}>
            ⚡ COMMANDER MODE ACTIVE ⚡
            <div style={{ fontSize: '11px', opacity: 0.9, marginTop: '4px' }}>
              AI can control mouse, keyboard, applications, and system operations
            </div>
          </div>
        )}
        
        {audioDevices.length === 0 && (
          <div style={{
            marginTop: '12px',
            padding: '12px',
            backgroundColor: '#1a1a2e',
            borderLeft: '4px solid #4a9eff',
            borderRadius: '4px',
            fontSize: '14px'
          }}>
            <strong>🎯 First time setup:</strong><br/>
            Click the blue microphone button below → Browser will ask for permission → Click "Allow" → Your Bluetooth devices will appear!
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div style={{
          padding: '16px',
          backgroundColor: '#1a1a2e',
          color: 'white',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '2px solid #ff6b6b',
          whiteSpace: 'pre-wrap',
          fontSize: '14px',
          lineHeight: '1.6'
        }}>
          {error}
        </div>
      )}

      {/* Microphone Selection */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3 style={{ marginBottom: '12px' }}>🎤 Microphone Selection</h3>
        <select
          value={selectedDevice}
          onChange={(e) => setSelectedDevice(e.target.value)}
          disabled={isRecording}
          style={{
            width: '100%',
            padding: '10px',
            backgroundColor: '#1a1a2e',
            color: 'white',
            border: '1px solid #333',
            borderRadius: '6px',
            fontSize: '14px'
          }}
        >
          {audioDevices.map((device, idx) => (
            <option key={device.deviceId || idx} value={device.deviceId}>
              {device.label || `Microphone ${idx + 1}`}
            </option>
          ))}
        </select>
        {audioDevices.length === 0 ? (
          <p style={{ marginTop: '8px', color: '#ff6b6b', fontSize: '12px' }}>
            ⚠️ No microphones detected. Click the record button below to grant permission.
          </p>
        ) : audioDevices[0]?.label ? (
          <p style={{ marginTop: '8px', color: '#00d9ff', fontSize: '12px' }}>
            ✅ {audioDevices.length} device(s) found including Bluetooth! Select one above.
          </p>
        ) : (
          <p style={{ marginTop: '8px', color: '#ffaa00', fontSize: '12px' }}>
            📋 {audioDevices.length} device(s) detected. Click record button to see names.
          </p>
        )}
      </div>

      {/* Recording Control */}
      <div className="card" style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', minHeight: '300px' }}>
        <button
          onClick={isRecording ? stopRecording : startRecording}
          style={{
            width: '200px',
            height: '200px',
            borderRadius: '50%',
            border: 'none',
            backgroundColor: isRecording ? '#ff4444' : '#4a9eff',
            color: 'white',
            fontSize: '18px',
            fontWeight: 'bold',
            cursor: 'pointer',
            boxShadow: isRecording ? '0 0 30px rgba(255, 68, 68, 0.5)' : '0 0 30px rgba(74, 158, 255, 0.3)',
            transition: 'all 0.3s ease',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px'
          }}
          onMouseEnter={(e) => {
            if (!isRecording) {
              e.currentTarget.style.transform = 'scale(1.05)';
              e.currentTarget.style.boxShadow = '0 0 40px rgba(74, 158, 255, 0.5)';
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
            e.currentTarget.style.boxShadow = isRecording ? '0 0 30px rgba(255, 68, 68, 0.5)' : '0 0 30px rgba(74, 158, 255, 0.3)';
          }}
        >
          {isRecording ? <MicOff size={48} /> : <Mic size={48} />}
          <div>{isRecording ? 'Stop Recording' : 'Start Recording'}</div>
          {audioDevices.length === 0 && !isRecording && (
            <div style={{ fontSize: '11px', opacity: 0.8 }}>
              (Grant Permission)
            </div>
          )}
        </button>
        
        {/* Toggle buttons on the right */}
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '12px',
          marginLeft: '30px'
        }}>
          <button
            onClick={() => {
              const newValue = !textOnlyMode;
              setTextOnlyMode(newValue);
              localStorage.setItem('voiceTextOnlyMode', JSON.stringify(newValue));
            }}
            style={{
              padding: '16px 20px',
              backgroundColor: textOnlyMode ? '#1a1a2e' : '#00d9ff',
              color: 'white',
              border: `2px solid ${textOnlyMode ? '#333' : '#00d9ff'}`,
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
              transition: 'all 0.2s ease',
              minWidth: '180px',
              textAlign: 'left'
            }}
            title={textOnlyMode ? 'Click to enable voice responses - AI will speak back' : 'Voice enabled - AI will speak responses'}
          >
            <div style={{ fontSize: '18px', marginBottom: '4px' }}>
              {textOnlyMode ? '📝 Text Only' : '🔊 Voice Enabled'}
            </div>
            <div style={{ fontSize: '11px', opacity: 0.8 }}>
              {textOnlyMode ? 'AI responds in text' : 'AI speaks responses'}
            </div>
          </button>
          
          <button
            onClick={() => {
              const newValue = !webSearchMode;
              setWebSearchMode(newValue);
            }}
            style={{
              padding: '16px 20px',
              backgroundColor: webSearchMode ? '#4CAF50' : '#1a1a2e',
              color: 'white',
              border: `2px solid ${webSearchMode ? '#4CAF50' : '#333'}`,
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
              transition: 'all 0.2s ease',
              minWidth: '180px',
              textAlign: 'left'
            }}
            title={webSearchMode ? 'Web search enabled' : 'Enable web search for current info'}
          >
            <div style={{ fontSize: '18px', marginBottom: '4px' }}>
              {webSearchMode ? '🌐 Web Search ON' : '🌐 Web Search Off'}
            </div>
            <div style={{ fontSize: '11px', opacity: 0.8 }}>
              {webSearchMode ? 'Multi-source enabled' : 'Local AI only'}
            </div>
          </button>
          
          <button
            onClick={() => {
              const newValue = !commanderMode;
              setCommanderMode(newValue);
              localStorage.setItem('voiceCommanderMode', JSON.stringify(newValue));
            }}
            style={{
              padding: '16px 20px',
              backgroundColor: commanderMode ? '#ff4444' : '#1a1a2e',
              color: 'white',
              border: `2px solid ${commanderMode ? '#ff4444' : '#333'}`,
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
              transition: 'all 0.2s ease',
              minWidth: '180px',
              textAlign: 'left'
            }}
            title={commanderMode ? 'Click to disable PC control - AI cannot control system' : 'Click to enable PC control - AI can move mouse, type, open apps, etc.'}
          >
            <div style={{ fontSize: '18px', marginBottom: '4px' }}>
              {commanderMode ? '⚡ Commander Active' : '🔒 Commander Off'}
            </div>
            <div style={{ fontSize: '11px', opacity: 0.8 }}>
              {commanderMode ? 'Full PC control enabled' : 'System control disabled'}
            </div>
          </button>
        </div>
        
        {isRecording && (
          <div style={{ marginTop: '20px' }}>
            <div style={{ color: '#ff4444', fontWeight: 'bold', marginBottom: '12px' }}>
              🔴 Recording... Click to stop and send to AI
            </div>
            {transcript && (
              <div style={{
                padding: '12px',
                backgroundColor: '#1a1a2e',
                borderRadius: '8px',
                fontSize: '14px',
                fontStyle: 'italic',
                color: '#00d9ff'
              }}>
                <strong>Live Transcription:</strong><br/>
                {transcript}
              </div>
            )}
          </div>
        )}
        
        {isTranscribing && (
          <div style={{ marginTop: '20px', color: '#4a9eff', fontWeight: 'bold' }}>
            ⏳ Sending to AI...
          </div>
        )}
        
        {!isRecording && audioDevices.length === 0 && (
          <div style={{ marginTop: '20px', color: '#ffaa00', fontSize: '14px' }}>
            👆 Click the button above to grant microphone permission
          </div>
        )}
      </div>

      {/* Conversation History */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '16px'
        }}>
          <h3>💬 Conversation</h3>
          <button
            onClick={clearConversation}
            style={{
              padding: '6px 12px',
              backgroundColor: '#333',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            Clear
          </button>
        </div>

        <div style={{ 
          flex: 1, 
          overflowY: 'auto',
          backgroundColor: '#0a0a0f',
          borderRadius: '8px',
          padding: '16px'
        }}>
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', color: '#666', padding: '40px' }}>
              <p>No conversation yet</p>
              <p style={{ fontSize: '14px', marginTop: '8px' }}>
                Click the microphone button to start talking
              </p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div key={idx} style={{
              marginBottom: '12px',
              padding: '12px',
              backgroundColor: msg.role === 'user' ? '#1a1a2e' : '#0f3460',
              borderRadius: '8px',
              borderLeft: `4px solid ${msg.role === 'user' ? '#4a9eff' : '#00d9ff'}`,
              position: 'relative'
            }}>
              <div style={{ 
                fontSize: '12px', 
                color: '#888', 
                marginBottom: '4px',
                fontWeight: 'bold',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <span>
                  {msg.role === 'user' ? '👤 You' : 
                    <>
                      🤖 Assistant
                      {msg.hasTools && (
                        <span style={{
                          marginLeft: '8px',
                          padding: '2px 8px',
                          backgroundColor: 'rgba(255, 165, 0, 0.2)',
                          borderRadius: '4px',
                          color: '#ffa500',
                          fontSize: '0.8em',
                          fontWeight: 'bold'
                        }}>🛠️ TOOLS</span>
                      )}
                      {msg.modes?.commander && (
                        <span style={{
                          marginLeft: '8px',
                          padding: '2px 8px',
                          backgroundColor: 'rgba(255, 68, 68, 0.2)',
                          borderRadius: '4px',
                          color: '#ff4444',
                          fontSize: '0.8em',
                          fontWeight: 'bold'
                        }}>⚡ CMD</span>
                      )}
                      {msg.modes?.webSearch && (
                        <span style={{
                          marginLeft: '8px',
                          padding: '2px 8px',
                          backgroundColor: 'rgba(68, 255, 68, 0.2)',
                          borderRadius: '4px',
                          color: '#44ff44',
                          fontSize: '0.8em',
                          fontWeight: 'bold'
                        }}>🌐 WEB</span>
                      )}
                    </>
                  }
                </span>
                <button
                  onClick={(e) => {
                    navigator.clipboard.writeText(msg.content);
                    const btn = e.currentTarget;
                    const originalText = btn.textContent;
                    btn.textContent = '✓ Copied!';
                    btn.style.color = '#00ff88';
                    setTimeout(() => {
                      btn.textContent = originalText;
                      btn.style.color = '#888';
                    }, 1500);
                  }}
                  style={{
                    padding: '4px 8px',
                    backgroundColor: 'transparent',
                    color: '#888',
                    border: '1px solid #333',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '11px',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.borderColor = '#00d9ff';
                    e.target.style.color = '#00d9ff';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.borderColor = '#333';
                    e.target.style.color = '#888';
                  }}
                  title="Copy to clipboard"
                >
                  📋 Copy
                </button>
              </div>
              <div style={{ whiteSpace: 'pre-wrap', fontSize: '14px' }}>
                {msg.content}
              </div>
            </div>
          ))}

          {/* Current transcript (only show if not in messages yet) */}
          {transcript && !isRecording && !messages.find(m => m.content === transcript) && (
            <div style={{
              padding: '12px',
              backgroundColor: '#1a1a2e',
              borderRadius: '8px',
              borderLeft: '4px solid #4a9eff',
              marginBottom: '12px'
            }}>
              <div style={{ 
                fontSize: '12px', 
                color: '#888', 
                marginBottom: '4px',
                fontWeight: 'bold'
              }}>
                👤 You (processing...)
              </div>
              <div style={{ whiteSpace: 'pre-wrap', fontSize: '14px' }}>
                {transcript}
              </div>
            </div>
          )}

          {/* Current response */}
          {response && (
            <div style={{
              marginTop: '12px',
              padding: '12px',
              backgroundColor: '#0f3460',
              borderRadius: '8px',
              borderLeft: '4px solid #00d9ff'
            }}>
              <div style={{ 
                fontSize: '12px', 
                color: '#888', 
                marginBottom: '4px',
                fontWeight: 'bold'
              }}>
                🤖 Assistant
              </div>
              <div style={{ whiteSpace: 'pre-wrap', fontSize: '14px' }}>
                {response}
              </div>
            </div>
          )}
        </div>
      </div>

      <div style={{ 
        marginTop: '16px', 
        padding: '12px', 
        backgroundColor: '#1a1a2e',
        borderRadius: '8px',
        fontSize: '12px',
        color: '#888'
      }}>
        💡 <strong>Tip:</strong> This uses native browser APIs (MediaRecorder + Web Speech) - 
        no WSL audio configuration needed! Grant microphone permissions when prompted.
      </div>
    </div>
  );
}

export default Voice;
