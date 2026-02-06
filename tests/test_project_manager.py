import pytest
import os
import json
from pathlib import Path
from datetime import datetime

# File: tests/test_project_manager.py
# Description: Unit tests for core/project_manager.py module.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: pytest, pathlib
# Links: MASTER_PLAN.md, core/project_manager.py

from core.project_manager import ProjectManager, ProjectError
from core.config import ConfigManager, ConfigError

@pytest.fixture
def mock_project_root(tmp_path):
    """Provides a temporary NovaForge project root structure for testing."""
    (tmp_path / "config").mkdir()
    (tmp_path / "projects").mkdir()
    
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
        "active_model_tag": "",
        "system_prompt": "You are a helpful AI assistant.",
        "active_tools": [],
        "memory": {"enabled": False, "vector_db_path": ""},
        "voice": {"stt_model": "", "tts_voice": ""}
    }
    with open(default_project_file, 'w') as f:
        json.dump(default_project_data, f)

    return str(tmp_path)

def test_project_manager_init(mock_project_root):
    """Test ProjectManager initialization."""
    pm = ProjectManager(mock_project_root)
    assert pm.project_root == Path(mock_project_root)
    assert pm.settings_file.exists()
    assert pm.projects_base_dir.exists()

    with pytest.raises(ProjectError, match="not a valid directory."):
        ProjectManager("/non/existent/path")

def test_validate_project_name():
    """Test project name validation."""
    pm = ProjectManager(os.getcwd()) # Use current working dir for validation only
    assert pm._validate_project_name("my-new-project_1") == "my-new-project_1"

    with pytest.raises(ProjectError, match="cannot be empty."):
        pm._validate_project_name("   ")
    with pytest.raises(ProjectError, match="alphanumeric characters, hyphens, and underscores."):
        pm._validate_project_name("my project")
    with pytest.raises(ProjectError, match="alphanumeric characters, hyphens, and underscores."):
        pm._validate_project_name("my!project")
    with pytest.raises(ProjectError, match="exceeds maximum length"):
        pm._validate_project_name("a" * 65)

def test_create_project(mock_project_root):
    """Test creating a new project."""
    pm = ProjectManager(mock_project_root)
    assert pm.create_project("test-project") == True
    
    new_project_path = Path(mock_project_root) / "projects" / "test-project"
    assert new_project_path.is_dir()
    assert (new_project_path / "project.json").is_file()

    # Verify content of new project.json
    new_project_config = ConfigManager(new_project_path / "project.json").to_dict()
    assert new_project_config["project_name"] == "test-project"
    assert "created_date" in new_project_config
    assert new_project_config["system_prompt"] == "You are a helpful AI assistant named test-project. Always strive to provide concise and accurate information."

    # Test creating existing project
    with pytest.raises(ProjectError, match="already exists."):
        pm.create_project("test-project")

def test_list_projects(mock_project_root):
    """Test listing available projects."""
    pm = ProjectManager(mock_project_root)
    assert pm.list_projects() == ["default"] # Only default exists initially

    pm.create_project("alpha-proj")
    pm.create_project("beta-proj")
    assert pm.list_projects() == ["alpha-proj", "beta-proj", "default"] # Sorted list

    # Test with empty projects dir
    (Path(mock_project_root) / "projects").rename(Path(mock_project_root) / "projects_old")
    pm_empty = ProjectManager(mock_project_root)
    assert pm_empty.list_projects() == []

def test_get_active_project_name(mock_project_root):
    """Test retrieving the active project name."""
    pm = ProjectManager(mock_project_root)
    assert pm.get_active_project_name() == "default"

    pm.create_project("new-active")
    pm.switch_project("new-active")
    assert pm.get_active_project_name() == "new-active"

    # Test with missing settings.json
    (Path(mock_project_root) / "config" / "settings.json").unlink()
    assert pm.get_active_project_name() == "default"

def test_switch_project(mock_project_root):
    """Test switching to a different project."""
    pm = ProjectManager(mock_project_root)
    pm.create_project("new-proj-to-switch")
    
    assert pm.switch_project("new-proj-to-switch") == True
    settings = ConfigManager(Path(mock_project_root) / "config" / "settings.json").to_dict()
    assert settings["active_project"] == "new-proj-to-switch"

    # Test switching to non-existent project
    with pytest.raises(ProjectError, match="does not exist."):
        pm.switch_project("non-existent")
    
    # Test switching to malformed project (missing project.json)
    (Path(mock_project_root) / "projects" / "malformed").mkdir()
    with pytest.raises(ProjectError, match="is malformed"):
        pm.switch_project("malformed")

def test_get_active_project_config(mock_project_root):
    """Test retrieving the configuration of the active project."""
    pm = ProjectManager(mock_project_root)
    config = pm.get_active_project_config()
    assert config["project_name"] == "default"
    assert "system_prompt" in config

    pm.create_project("another-project")
    pm.switch_project("another-project")
    config = pm.get_active_project_config()
    assert config["project_name"] == "another-project"

    # Test with missing project.json for active project
    active_proj_path = Path(mock_project_root) / "projects" / pm.get_active_project_name()
    (active_proj_path / "project.json").unlink()
    with pytest.raises(ProjectError, match="config file not found"):
        pm.get_active_project_config()
