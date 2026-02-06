#!/bin/bash

if [ -z "$BASH_VERSION" ]; then
    exec /bin/bash "$0" "$@"
fi

# File: scripts/menu_main.sh
# Description: Displays the main menu for NovaForge AI Lab and dispatches actions.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: bash, python3 (active venv), dialog (optional for better UI)
# Links: MASTER_PLAN.md

# --- Configuration ---
PROJECT_ROOT="$1" # Passed from forge.sh
CONFIG_DIR="$PROJECT_ROOT/config"
PROJECTS_DIR="$PROJECT_ROOT/projects"
SETTINGS_FILE="$CONFIG_DIR/settings.json"
LOGS_DIR="$PROJECT_ROOT/logs"
MENU_DEBUG_LOG="$LOGS_DIR/menu_debug.log"

mkdir -p "$LOGS_DIR"

if [ -z "$OLLAMA_CMD" ]; then
    OLLAMA_CMD="ollama"
fi
if [ -z "$OLLAMA_PORT" ]; then
    OLLAMA_PORT="11434"
fi

DIALOG_THEME_FILE="$CONFIG_DIR/dialogrc"
if [ -f "$DIALOG_THEME_FILE" ]; then
    export DIALOGRC="$DIALOG_THEME_FILE"
fi

# --- Functions ---

# Logging helper
function menu_debug_log {
    if [ -z "$MENU_DEBUG_LOG" ]; then
        return
    fi
    printf '%s %s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" "$1" >> "$MENU_DEBUG_LOG"
}

function sanitize_choice_value {
    local raw="$1"
    local sanitized
    sanitized="$(printf '%s' "$raw" | tr -d '\r' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
    echo "$sanitized"
}

# Function to get active project name
function get_active_project_name {
    # Check if settings.json exists and contains active_project
    if [ ! -f "$SETTINGS_FILE" ]; then
        echo "default" # Fallback if settings file is missing
        return
    fi
    SETTINGS_FILE="$SETTINGS_FILE" PYTHONPATH="$PROJECT_ROOT" python3 <<'PY'
import os
from pathlib import Path
from core.config import ConfigManager, ConfigError

settings_path = Path(os.environ["SETTINGS_FILE"])

try:
    config = ConfigManager(settings_path)
    print(config.get("active_project", "default"))
except (ConfigError, Exception):
    print("default")
PY
}

# Generic function to display menu and get choice
function ollama_service_status {
    local cmd="$OLLAMA_CMD"
    local port="$OLLAMA_PORT"

    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "missing"
        return
    fi

    if command -v curl >/dev/null 2>&1; then
        if curl -sSf --max-time 1 "http://127.0.0.1:${port}/api/version" >/dev/null 2>&1; then
            echo "running"
            return
        fi
    fi

    if pgrep -f "$cmd serve" >/dev/null 2>&1; then
        echo "starting"
    else
        echo "stopped"
    fi
}

function start_ollama_service {
    local cmd="$OLLAMA_CMD"
    local port="$OLLAMA_PORT"

    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "❌ Ollama CLI not found. Install it from https://ollama.com/download or set OLLAMA_CMD."
        return 1
    fi
    if [ "$(ollama_service_status)" = "running" ]; then
        echo "ℹ️ Ollama already running."
        return 0
    fi
    echo "Starting Ollama (port $port)..."
    (nohup "$cmd" serve >/dev/null 2>&1 & echo $! > "$PROJECT_ROOT/logs/ollama.pid") || {
        echo "❌ Failed to launch Ollama process."
        return 1
    }
    sleep 2
    if [ "$(ollama_service_status)" = "running" ]; then
        echo "✅ Ollama started."
    else
        echo "❌ Failed to start Ollama. Check logs or run '${OLLAMA_CMD:-ollama} serve' manually."
    fi
}

function stop_ollama_service {
    local cmd="$OLLAMA_CMD"
    local pids
    pids=$(pgrep -f "$cmd serve")
    if [ -z "$pids" ]; then
        echo "ℹ️ Ollama is not running."
        return 0
    fi
    echo "Stopping Ollama..."
    for pid in $pids; do
        kill "$pid" >/dev/null 2>&1 || true
    done
    sleep 1
    if [ "$(ollama_service_status)" = "running" ]; then
        echo "❌ Could not stop Ollama. You may need to terminate it manually."
    else
        echo "✅ Ollama stopped."
    fi
}

function show_menu {
    local title="$1"
    shift
    local menu_options=("$@")
    local selected_choice=""
    local interactive=1
    local prefer_dialog=1

    if [ ! -t 0 ] || [ ! -t 1 ]; then
        interactive=0
    fi
    if [ -n "$NOVAFORGE_FORCE_TEXT_MENU" ] || [ $interactive -eq 0 ]; then
        prefer_dialog=0
    fi

    if [ $prefer_dialog -eq 1 ] && command -v dialog >/dev/null 2>&1; then
        local dialog_exit=0
        local dialog_choice=$(
            dialog --clear --colors --stdout --backtitle "NovaForge AI Lab" \
                   --title "$title" \
                   --menu "Choose an option:" 18 60 15 \
                   "${menu_options[@]}"
        ) || dialog_exit=$?
        dialog_choice="$(sanitize_choice_value "$dialog_choice")"
        menu_debug_log "[dialog] title='$title' exit=$dialog_exit choice='${dialog_choice}'"
        if [ $dialog_exit -eq 0 ] && [ -n "$dialog_choice" ]; then
            echo "$dialog_choice"
            return
        fi
        echo "⚠️  Dialog UI unavailable, falling back to text menu." >&2
    fi

    while true; do
        >&2 echo -e "\n--- $title ---"
        for (( i=0; i<${#menu_options[@]}; i+=2 )); do
            >&2 echo "${menu_options[i]}. ${menu_options[i+1]}"
        done
        >&2 echo -n "Enter your choice: "
        if read -r selected_choice; then
            selected_choice="$(sanitize_choice_value "$selected_choice")"
            menu_debug_log "[text] title='$title' choice='${selected_choice}'"
            if [ -n "$selected_choice" ]; then
                echo "$selected_choice"
                return
            fi
        fi

        if [ $interactive -eq 0 ]; then
            menu_debug_log "[text] non-interactive fallback -> 0"
            echo "0"
            return
        fi

        >&2 echo "Please enter a valid option."
    done
}

function download_model_by_tag {
    local tag="$1"
    if [ -z "$tag" ]; then
        echo "Model tag cannot be empty."
        return 1
    fi

    local status
    status=$(ollama_service_status)
    if [ "$status" = "missing" ]; then
        echo "❌ Ollama CLI not installed. Install it and try again."
        return 1
    fi
    if [ "$status" = "stopped" ] || [ "$status" = "starting" ]; then
        start_ollama_service
    fi

    MODEL_TAG="$tag" PROJECT_ROOT="$PROJECT_ROOT" PYTHONPATH="$PROJECT_ROOT" python3 <<'PY'
import os
import sys
from core.model_manager import ModelManager, ModelManagerError

project_root = os.environ["PROJECT_ROOT"]
model_tag = os.environ["MODEL_TAG"]

try:
    mm = ModelManager(project_root)
    mm.download_model(model_tag)
except ModelManagerError as e:
    print(f"❌ Error: {e}", file=sys.stderr)
    sys.exit(1)
PY
}

# Function for Model Management menu
function menu_model_management {
    while true; do
        local active_project=$(get_active_project_name)
        local active_model=$(
            PROJECT_ROOT="$PROJECT_ROOT" PYTHONPATH="$PROJECT_ROOT" python3 <<'PY'
import os
from core.project_manager import ProjectManager, ProjectError

project_root = os.environ["PROJECT_ROOT"]

try:
    pm = ProjectManager(project_root)
    config = pm.get_active_project_config()
    print(config.get("active_model_tag", ""))
except (ProjectError, Exception):
    print("")
PY
        )
        local menu_options=(
            1 "Download a new model"
            2 "Select active model for '$active_project' (Current: $active_model)"
            3 "Browse recommended model catalog"
            0 "Back to Main Menu"
        )
        local choice=$(show_menu "Model Management" "${menu_options[@]}")

        case "$choice" in
            1)
                echo "Enter model tag to download (e.g., llama3:8b):"
                read -r model_tag
                download_model_by_tag "$model_tag"
                echo "Press Enter to continue..."
                read -r
                ;;
            2)
                echo "Fetching available models..."
                local models_json=$(
                    PROJECT_ROOT="$PROJECT_ROOT" PYTHONPATH="$PROJECT_ROOT" python3 <<'PY'
import os
import sys
from core.model_manager import ModelManager, ModelManagerError

project_root = os.environ["PROJECT_ROOT"]

try:
    mm = ModelManager(project_root)
    print(' '.join(mm.list_local_models()))
except ModelManagerError as e:
    print(f"❌ Error listing models: {e}", file=sys.stderr)
    sys.exit(1)
PY
                )
                local models=($models_json) # Convert string to array
                
                if [ ${#models[@]} -eq 0 ]; then
                    echo "No models downloaded yet. Please download one first."
                    echo "Press Enter to continue..."
                    read -r
                    continue
                fi

                local model_menu_options=()
                local count=1
                for model in "${models[@]}"; do
                    model_menu_options+=( "$count" "$model" )
                    count=$((count+1))
                done
                model_menu_options+=( 0 "Back" )

                local model_choice=$(show_menu "Select Active Model" "${model_menu_options[@]}")

                    if [ "$model_choice" -eq 0 ]; then
                        continue
                    elif [ "$model_choice" -ge 1 ] && [ "$model_choice" -lt "$count" ]; then
                        local selected_model="${models[$model_choice-1]}"
                        SELECTED_MODEL="$selected_model" PROJECT_ROOT="$PROJECT_ROOT" PYTHONPATH="$PROJECT_ROOT" python3 <<'PY'
import os
import sys
from core.project_manager import ProjectManager, ProjectError

project_root = os.environ["PROJECT_ROOT"]
selected_model = os.environ["SELECTED_MODEL"]

try:
    pm = ProjectManager(project_root)
    pm.set_active_model_for_project(selected_model)
    print(f"✅ Active model for current project set to: {selected_model}")
except (ProjectError, Exception) as e:
    print(f"❌ Error setting active model: {e}", file=sys.stderr)
    sys.exit(1)
PY
                    else
                        echo "Invalid model selection."
                    fi
                echo "Press Enter to continue..."
                read -r
                ;;
            3)
                local catalog_file="$PROJECT_ROOT/models/featured_models.json"
                if [ ! -f "$catalog_file" ]; then
                    echo "Recommended catalog not found at $catalog_file."
                    echo "Press Enter to continue..."
                    read -r
                    continue
                fi

                local catalog_entries=()
                mapfile -t catalog_entries < <(
                    CATALOG_FILE="$catalog_file" PYTHONPATH="$PROJECT_ROOT" python3 <<'PY'
import json
import os

catalog_file = os.environ["CATALOG_FILE"]

try:
    with open(catalog_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)
except Exception as exc:
    print(f"ERROR|Failed to read catalog: {exc}")
else:
    for item in data:
        tag = item.get("tag")
        if not tag:
            continue
        name = item.get("name", tag)
        size = item.get("size_gb")
        quant = item.get("quantization")
        best_for = item.get("best_for")
        parts = [name, f"[{tag}]"]
        if size:
            parts.append(f"{size}GB")
        if quant:
            parts.append(quant)
        if best_for:
            parts.append(f"- {best_for}")
        print(f"{tag}|{' '.join(parts)}")
PY
                )

                if [ ${#catalog_entries[@]} -eq 0 ]; then
                    echo "Recommended catalog is empty."
                    echo "Press Enter to continue..."
                    read -r
                    continue
                fi

                if [[ "${catalog_entries[0]}" == ERROR* ]]; then
                    echo "${catalog_entries[0]#ERROR|}"
                    echo "Press Enter to continue..."
                    read -r
                    continue
                fi

                local rec_menu_options=()
                local rec_tags=()
                local idx=1
                for entry in "${catalog_entries[@]}"; do
                    IFS='|' read -r rec_tag rec_label <<< "$entry"
                    if [ -z "$rec_tag" ]; then
                        continue
                    fi
                    rec_menu_options+=( "$idx" "$rec_label" )
                    rec_tags+=("$rec_tag")
                    idx=$((idx+1))
                done
                rec_menu_options+=( 0 "Back" )

                local rec_choice=$(show_menu "Recommended Models" "${rec_menu_options[@]}")

                if [ "$rec_choice" -eq 0 ]; then
                    continue
                elif [ "$rec_choice" -ge 1 ] && [ "$rec_choice" -le "${#rec_tags[@]}" ]; then
                    local catalog_tag="${rec_tags[$((rec_choice-1))]}"
                    download_model_by_tag "$catalog_tag"
                else
                    echo "Invalid option."
                fi
                echo "Press Enter to continue..."
                read -r
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid option. Please try again."
                echo "Press Enter to continue..."
                read -r
                ;;
        esac
    done
}

function menu_ollama_controls {
    while true; do
        local status=$(ollama_service_status)
        local menu_options=(
            1 "Start Ollama (Current: $status)"
            2 "Stop Ollama"
            3 "Show Ollama logs path"
            0 "Back to Main Menu"
        )
        local choice=$(show_menu "Ollama Service" "${menu_options[@]}")

        case "$choice" in
            1)
                start_ollama_service
                echo "Press Enter to continue..."
                read -r
                ;;
            2)
                stop_ollama_service
                echo "Press Enter to continue..."
                read -r
                ;;
            3)
                echo "Ollama logs typically live in ~/.ollama/logs. Current command: $OLLAMA_CMD"
                echo "Press Enter to continue..."
                read -r
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid option."
                echo "Press Enter to continue..."
                read -r
                ;;
        esac
    done
}

# Function for Project Management menu
function menu_project_management {
    while true; do
        local menu_options=(
            1 "Create New Project"
            2 "Switch Active Project"
            3 "List Projects"
            0 "Back to Main Menu"
        )
        local choice=$(show_menu "Project Management" "${menu_options[@]}")

        case "$choice" in
            1)
                echo "Enter new project name (alphanumeric, hyphens, underscores):"
                read -r project_name
                if [ -n "$project_name" ]; then
                    PROJECT_NAME="$project_name" PROJECT_ROOT="$PROJECT_ROOT" PYTHONPATH="$PROJECT_ROOT" python3 <<'PY'
import os
import sys
from core.project_manager import ProjectManager, ProjectError

project_root = os.environ["PROJECT_ROOT"]
project_name = os.environ["PROJECT_NAME"]

try:
    pm = ProjectManager(project_root)
    pm.create_project(project_name)
except ProjectError as e:
    print(f"❌ Error: {e}", file=sys.stderr)
    sys.exit(1)
PY
                else
                    echo "Project name cannot be empty."
                fi
                echo "Press Enter to continue..."
                read -r
                ;;
            2)
                echo "Fetching available projects..."
                local projects_output=$(
                    PROJECT_ROOT="$PROJECT_ROOT" PYTHONPATH="$PROJECT_ROOT" python3 <<'PY'
import os
import sys
from core.project_manager import ProjectManager, ProjectError

project_root = os.environ["PROJECT_ROOT"]

try:
    pm = ProjectManager(project_root)
    print(' '.join(pm.list_projects()))
except ProjectError as e:
    print(f"❌ Error listing projects: {e}", file=sys.stderr)
    sys.exit(1)
PY
                )
                local projects=($projects_output)

                if [ ${#projects[@]} -eq 0 ]; then
                    echo "No projects found. Please create one first."
                    echo "Press Enter to continue..."
                    read -r
                    continue
                fi
                
                local project_menu_options=()
                local count=1
                for proj in "${projects[@]}"; do
                    project_menu_options+=( "$count" "$proj" )
                    count=$((count+1))
                done
                project_menu_options+=( 0 "Back" )

                local project_choice=$(show_menu "Switch Active Project" "${project_menu_options[@]}")

                    if [ "$project_choice" -eq 0 ]; then
                        continue
                    elif [ "$project_choice" -ge 1 ] && [ "$project_choice" -lt "$count" ]; then
                        local selected_project="${projects[$project_choice-1]}"
                        SELECTED_PROJECT="$selected_project" PROJECT_ROOT="$PROJECT_ROOT" PYTHONPATH="$PROJECT_ROOT" python3 <<'PY'
import os
import sys
from core.project_manager import ProjectManager, ProjectError

project_root = os.environ["PROJECT_ROOT"]
selected_project = os.environ["SELECTED_PROJECT"]

try:
    pm = ProjectManager(project_root)
    pm.switch_project(selected_project)
    print(f"✅ Switched to project '{selected_project}'.")
except ProjectError as e:
    print(f"❌ Error: {e}", file=sys.stderr)
    sys.exit(1)
PY
                    else
                        echo "Invalid project selection."
                    fi
                echo "Press Enter to continue..."
                read -r
                ;;
            3)
                echo "Listing all projects:"
                PROJECT_ROOT="$PROJECT_ROOT" PYTHONPATH="$PROJECT_ROOT" python3 <<'PY'
import os
import sys
from core.project_manager import ProjectManager, ProjectError

project_root = os.environ["PROJECT_ROOT"]

try:
    pm = ProjectManager(project_root)
    print('\n'.join(pm.list_projects()))
except ProjectError as e:
    print(f"❌ Error listing projects: {e}", file=sys.stderr)
    sys.exit(1)
PY
                echo "Press Enter to continue..."
                read -r
                ;;
            0)
                break
                ;;
            *)
                echo "Invalid option. Please try again."
                echo "Press Enter to continue..."
                read -r
                ;;
        esac
    done
}


# --- Main Menu Loop ---
function main_menu_loop {
    while true; do
        local active_project=$(get_active_project_name)
        local menu_title="NovaForge AI Lab [Project: $active_project]"
        local menu_options=(
            1 "Setup/Update Environment (run setup.sh)"
            2 "Manage Projects"
            3 "Manage Models (Download, Select)"
            4 "Chat (Text-based conversation)"
            5 "Voice Assistant Mode (Hands-free AI)"
            6 "Train / Fine-tune Model"
            7 "Agent + Tools (Automation)"
            8 "Manage Tools (Add, Remove)"
            9 "Memory / Knowledge Base"
            10 "System Optimization"
            11 "Package/Export Project"
            12 "Ollama Service Controls"
            0 "Exit NovaForge"
        )
        local choice=$(show_menu "$menu_title" "${menu_options[@]}")
        
        case "$choice" in
            1)
                echo "Running setup.sh..."
                "$PROJECT_ROOT/setup.sh"
                echo "Press Enter to continue..."
                read -r
                ;;
            2)
                menu_project_management
                ;;
            3)
                menu_model_management
                ;;
            4)
                echo "Launching Text Chat..."
                PYTHONPATH="$PROJECT_ROOT" python3 "$PROJECT_ROOT/core/chat.py" "$PROJECT_ROOT"
                echo "Press Enter to continue..."
                read -r
                ;;
            5)
                echo "Launching Voice Assistant..."
                PYTHONPATH="$PROJECT_ROOT" python3 "$PROJECT_ROOT/voice/assistant.py" "$PROJECT_ROOT"
                echo "Press Enter to continue..."
                read -r
                ;;
            # Add cases for other menu options here as they are implemented
            12)
                menu_ollama_controls
                ;;
            0)
                echo "Exiting..."
                break
                ;;
            *)
                echo "Invalid option. Please try again."
                echo "Press Enter to continue..."
                read -r
                ;;
        esac
    done
}

main_menu_loop
