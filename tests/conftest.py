import pytest
import json
from pathlib import Path
from datetime import datetime
import os

# File: tests/conftest.py
# Description: Pytest fixtures for NovaForge AI Lab tests.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: pytest, pathlib, json
# Links: MASTER_PLAN.md

@pytest.fixture
def mock_project_root_env(tmp_path):
    """
    Creates a temporary NovaForge project root structure for tests
    and sets the PROJECT_ROOT environment variable.
    """
    # Base directories
    (tmp_path / "config").mkdir()
    (tmp_path / "projects").mkdir()
    (tmp_path / "models").mkdir()
    (tmp_path / "logs").mkdir()
    
    # Create initial settings.json
    settings_file = tmp_path / "config" / "settings.json"
    settings_data = {"active_project": "default", "theme": "dark"}
    with open(settings_file, 'w') as f:
        json.dump(settings_data, f)
    
    # Create default project.json
    (tmp_path / "projects" / "default").mkdir()
    default_project_file = tmp_path / "projects" / "default" / "project.json"
    default_project_data = {
        "project_name": "default",
        "version": "1.0",
        "created_date": datetime.now().isoformat(timespec='seconds'),
        "active_model_tag": "test-model:latest", # <-- Set an active model tag here for realistic defaults
        "system_prompt": "You are a helpful AI assistant.",
        "active_tools": [],
        "memory": {"enabled": False, "vector_db_path": ""},
        "voice": {"stt_model": "", "tts_voice": ""}
    }
    with open(default_project_file, 'w') as f:
        json.dump(default_project_data, f)
    
    # Create empty models.json
    models_file = tmp_path / "models" / "models.json"
    with open(models_file, 'w') as f:
        json.dump({}, f)

    # Set environment variable for tests
    os.environ["PROJECT_ROOT"] = str(tmp_path)
    yield str(tmp_path)
    # Clean up environment variable
    del os.environ["PROJECT_ROOT"]

@pytest.fixture
def mock_populated_models_json(mock_project_root_env):
    """
    Creates a temporary models.json with some pre-defined models.
    """
    models_dir = Path(mock_project_root_env) / "models"
    models_file = models_dir / "models.json"
    data = {
        "llama3:8b": {
            "tag": "llama3:8b",
            "backend": "ollama",
            "download_date": datetime(2025, 1, 1).isoformat(timespec='seconds'),
            "family": "llama",
            "size_gb": 4.7,
            "details": {"format": "gguf", "quantization": "q4_0"}
        },
        "mistral:7b": {
            "tag": "mistral:7b",
            "backend": "ollama",
            "download_date": datetime(2025, 1, 2).isoformat(timespec='seconds'),
            "family": "mistral",
            "size_gb": 4.1,
            "details": {"format": "gguf", "quantization": "q4_0"}
        }
    }
    with open(models_file, 'w') as f:
        json.dump(data, f)
    return models_file