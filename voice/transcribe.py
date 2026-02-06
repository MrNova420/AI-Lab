#!/usr/bin/env python3
"""
Voice transcription module using Ollama whisper.
"""
import os
import sys
from pathlib import Path
import requests

def transcribe_audio(audio_path: str, model: str = "whisper") -> str:
    """
    Transcribe audio file using Ollama whisper model.
    
    Args:
        audio_path: Path to audio file (WAV format)
        model: Ollama model to use (default: whisper)
    
    Returns:
        Transcribed text
    """
    ollama_base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    with open(audio_path, 'rb') as f:
        audio_data = f.read()
    
    # Call Ollama API for transcription
    # Note: This is a simplified version - actual Ollama whisper API may differ
    try:
        response = requests.post(
            f"{ollama_base_url}/api/transcribe",
            files={'file': audio_data},
            data={'model': model},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get('text', '')
        else:
            return f"[Transcription failed: {response.status_code}]"
            
    except Exception as e:
        return f"[Transcription error: {str(e)}]"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: transcribe.py <audio_file>")
        sys.exit(1)
    
    result = transcribe_audio(sys.argv[1])
    print(result)
