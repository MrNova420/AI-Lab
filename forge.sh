#!/bin/bash

# File: forge.sh
# Description: Main launcher script for NovaForge AI Lab.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: bash, python3.11+, git, wget
# Links: MASTER_PLAN.md

# --- Configuration ---
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"
SETUP_SCRIPT="$PROJECT_ROOT/setup.sh"
MAIN_MENU_SCRIPT="$PROJECT_ROOT/scripts/menu_main.sh"

# --- Functions ---

# Function to display error and exit
function error_exit {
    echo "❌ ERROR: $1" >&2
    exit 1
}

# Function to activate the virtual environment
function activate_venv {
    if [ ! -d "$VENV_DIR" ]; then
        echo "💡 Virtual environment not found. Running setup..."
        "$SETUP_SCRIPT" || error_exit "Setup failed. Please check the logs."
    fi

    source "$VENV_DIR/bin/activate" || error_exit "Failed to activate virtual environment."
    echo "✅ Virtual environment activated."
}

# --- Main Script ---

FORCE_TEXT_MENU=0

function is_wsl_environment {
    grep -qi "microsoft" /proc/version 2>/dev/null
}

function configure_wsl_audio_bridge {
    if ! is_wsl_environment; then
        return
    fi

    local pulse_sock="/mnt/wslg/PulseServer"
    local alsa_conf="/mnt/wslg/alsa-conf/alsa.conf"

    if [ -S "$pulse_sock" ]; then
        export PULSE_SERVER="unix:$pulse_sock"
        if [ -f "$alsa_conf" ]; then
            export ALSA_CONFIG_PATH="$alsa_conf"
        fi
        export NOVAFORGE_AUDIO_BRIDGE="wslg"
    else
        export NOVAFORGE_AUDIO_BRIDGE="missing"
        echo "⚠️  WSL audio bridge not detected. Voice features may require WSLg or PulseAudio. See docs/WSL_AUDIO.md." >&2
    fi
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --tm|--text-menu)
            FORCE_TEXT_MENU=1
            shift
            ;;
        *)
            echo "❌ Unknown option: $1"
            echo "Usage: ./forge.sh [--tm|--text-menu]"
            exit 1
            ;;
    esac
done

if [ "$FORCE_TEXT_MENU" -eq 1 ]; then
    export NOVAFORGE_FORCE_TEXT_MENU=1
fi

configure_wsl_audio_bridge

echo "🚀 Starting NovaForge AI Lab..."

# Check if setup script exists
if [ ! -f "$SETUP_SCRIPT" ]; then
    error_exit "Setup script ($SETUP_SCRIPT) not found. Please ensure the project is correctly cloned."
fi

# Activate virtual environment
activate_venv

# Run the main menu
if [ ! -f "$MAIN_MENU_SCRIPT" ]; then
    error_exit "Main menu script ($MAIN_MENU_SCRIPT) not found. This indicates an incomplete setup."
fi

# Pass the project root to the menu script
"$MAIN_MENU_SCRIPT" "$PROJECT_ROOT"

echo "👋 Exiting NovaForge AI Lab. Goodbye!"

# Deactivate the virtual environment on exit (best practice, though shell will exit)
deactivate
