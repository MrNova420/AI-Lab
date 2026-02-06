#!/bin/bash

# File: setup.sh
# Description: Sets up the NovaForge AI Lab environment, including Python venv and dependencies.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: python3.11+, git, wget
# Links: MASTER_PLAN.md

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"
REQUIREMENTS_FILE="$PROJECT_ROOT/core/requirements.txt"
LOG_FILE="$PROJECT_ROOT/logs/setup.log"

if [ -z "$OLLAMA_CMD" ]; then
    OLLAMA_CMD="ollama"
fi

# --- Functions ---

# Function to display error and exit
function error_exit {
    echo "❌ ERROR: $1" >&2
    echo "Setup failed. Check $LOG_FILE for details." >&2
    exit 1
}

# Function to log messages
function log_message {
    echo "$1" | tee -a "$LOG_FILE"
}

# Check for required commands
function check_command {
    command -v "$1" >/dev/null 2>&1 || error_exit "Command not found: $1. Please install $1."
}

# --- Main Script ---
clear
log_message "🚀 Starting NovaForge AI Lab Setup..."
log_message "------------------------------------"
log_message "Log file: $LOG_FILE"
log_message "Project Root: $PROJECT_ROOT"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/logs" || error_exit "Failed to create logs directory."

# Clear previous log
> "$LOG_FILE"

# 1. Check System Requirements
log_message "Checking system requirements..."
check_command "python3"
check_command "git"
check_command "wget"
# Removed check_command "pip" - will use python3 -m pip directly

# Optional: Ollama availability (warn only)
if ! command -v "$OLLAMA_CMD" >/dev/null 2>&1; then
    log_message "⚠️ Ollama CLI not found. Install it from https://ollama.com/download or run 'sudo snap install ollama' (Linux) so you can download models."
else
    log_message "✅ Ollama CLI detected ($(command -v "$OLLAMA_CMD"))."
fi

# Verify Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if (( $(echo "$PYTHON_VERSION >= 3.11" | bc -l) )); then
    log_message "✅ Python $PYTHON_VERSION (>= 3.11) found."
else
    error_exit "Python 3.11 or newer is required. Found Python $PYTHON_VERSION."
fi

# 2. Create Python Virtual Environment
log_message "Creating Python virtual environment..."
if [ -d "$VENV_DIR" ]; then
    log_message "💡 Existing virtual environment found. Removing old environment..."
    rm -rf "$VENV_DIR" || error_exit "Failed to remove old virtual environment."
fi
python3 -m venv "$VENV_DIR" || error_exit "Failed to create virtual environment."
log_message "✅ Virtual environment created at $VENV_DIR."

# 3. Activate Virtual Environment
log_message "Activating virtual environment..."
source "$VENV_DIR/bin/activate" || error_exit "Failed to activate virtual environment."
log_message "✅ Virtual environment activated."

# 4. Install Python Dependencies
log_message "Installing Python dependencies..."
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    log_message "💡 core/requirements.txt not found. Creating a minimal one."
    # The requirement.txt is now pre-created by me, so this block should not be hit.
    # Keeping it as a fallback, but the content should be from the created file.
    echo "requests" > "$REQUIREMENTS_FILE"
    echo "prompt_toolkit" >> "$REQUIREMENTS_FILE"
    echo "pyaudio" >> "$REQUIREMENTS_FILE" # For sounddevice/pyaudio
    echo "sounddevice" >> "$REQUIREMENTS_FILE"
    echo "numpy" >> "$REQUIREMENTS_FILE" # often a dependency for audio libs
    echo "scipy" >> "$REQUIREMENTS_FILE" # often a dependency for audio libs
    echo "filelock" >> "$REQUIREMENTS_FILE" # for safe JSON file ops
    echo "pytest" >> "$REQUIREMENTS_FILE" # For testing
    echo "requests-mock" >> "$REQUIREMENTS_FILE" # For testing
fi
python3 -m pip install -r "$REQUIREMENTS_FILE" || error_exit "Failed to install Python dependencies."
log_message "✅ Python dependencies installed."

# 5. Download/Compile C++ Binaries (Whisper.cpp, Piper) - Placeholder for Phase 2 implementation
log_message "Downloading/Compiling C++ Binaries (Whisper.cpp, Piper)... (Skipped for Phase 1 - will be implemented in Phase 2)"
# Example placeholder for later:
# cd "$PROJECT_ROOT/voice/stt" && git clone https://github.com/ggerganov/whisper.cpp . && make || error_exit "Failed to compile whisper.cpp"
# cd "$PROJECT_ROOT/voice/tts" && wget ... piper_binary ... || error_exit "Failed to download Piper"
# Need to download default STT and TTS models here.

# 6. Initialize Configuration Files
log_message "Initializing configuration files..."
# config/settings.json
if [ ! -f "$PROJECT_ROOT/config/settings.json" ]; then
    echo '{"active_project": "default", "theme": "dark"}' > "$PROJECT_ROOT/config/settings.json" || error_exit "Failed to create settings.json"
    log_message "Created default config/settings.json."
else
    log_message "config/settings.json already exists. Skipping creation."
fi

# projects/default/project.json
mkdir -p "$PROJECT_ROOT/projects/default" || error_exit "Failed to create default project directory."
if [ ! -f "$PROJECT_ROOT/projects/default/project.json" ]; then
    echo '{
      "project_name": "default",
      "version": "1.0",
      "created_date": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
      "active_model_tag": "",
      "system_prompt": "You are NovaForge, a helpful AI assistant. Always strive to provide concise and accurate information.",
      "active_tools": [],
      "memory": {
        "enabled": false,
        "vector_db_path": ""
      },
      "voice": {
        "stt_model": "",
        "tts_voice": ""
      }
    }' > "$PROJECT_ROOT/projects/default/project.json" || error_exit "Failed to create default project.json"
    log_message "Created default projects/default/project.json."
else
    log_message "projects/default/project.json already exists. Skipping creation."
fi

# models/models.json
if [ ! -f "$PROJECT_ROOT/models/models.json" ]; then
    echo '{}' > "$PROJECT_ROOT/models/models.json" || error_exit "Failed to create models.json"
    log_message "Created empty models/models.json."
else
    log_message "models/models.json already exists. Skipping creation."
fi
log_message "✅ Configuration files initialized."


# 7. Final Verification (Placeholder for core/doctor.py in a later step)
log_message "Running final verification... (Placeholder: will integrate core/doctor.py later)"
log_message "NovaForge AI Lab is set up! Please ensure Ollama is running if you plan to use models immediately."
log_message "You can start Ollama with: ollama serve"
log_message "Then, you can run: ./forge.sh"
log_message "------------------------------------"
log_message "🚀 NovaForge AI Lab Setup COMPLETE!"
log_message "------------------------------------"

# Deactivate venv (script will exit, so it's mainly for clarity)
deactivate
exit 0
