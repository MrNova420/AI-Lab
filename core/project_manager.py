import os
import json
from datetime import datetime
from pathlib import Path

# File: core/project_manager.py
# Description: Manages creation, switching, and retrieval of NovaForge projects.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: core.config.ConfigManager, pathlib, json
# Links: MASTER_PLAN.md, test_project_manager.py

from core.config import ConfigManager, ConfigError

class ProjectError(Exception):
    """Custom exception for project management related errors."""
    pass

class ProjectManager:
    """
    Manages the lifecycle and configuration of NovaForge projects.

    Purpose: Provides a centralized interface for creating, switching,
             and accessing project-specific settings, enabling different
             AI personalities and toolsets.

    Complexity: O(1) for most operations (file I/O for small config files).
                O(N) for listing projects (directory scan), where N is number of projects.
    Performance: Relies on ConfigManager for efficient file handling.
    Security Notes: Ensures project integrity. Does not handle sensitive data within
                    project.json; higher layers should manage that.
    """
    def __init__(self, project_root: str):
        """
        Initializes the ProjectManager.

        Args:
            project_root (str): The absolute path to the NovaForge project root directory.
        
        Throws:
            ProjectError: If project_root is not a valid directory.
        """
        self.project_root = Path(project_root).resolve()
        if not self.project_root.is_dir():
            raise ProjectError(f"Project root '{project_root}' is not a valid directory.")

        self.config_dir = self.project_root / "config"
        self.projects_base_dir = self.project_root / "projects"
        self.settings_file = self.config_dir / "settings.json"
        self.settings_manager = ConfigManager(self.settings_file)

    def _validate_project_name(self, name: str) -> str:
        """
        Validates a project name for allowed characters and length.

        Args:
            name (str): The proposed project name.

        Returns:
            str: The sanitized project name.

        Throws:
            ProjectError: If the project name is invalid or contains unsafe characters.
        """
        # Input validation for project name (security measure)
        if not isinstance(name, str) or not name.strip():
            raise ProjectError("Project name cannot be empty.")
        
        sanitized_name = name.strip()
        # Allow alphanumeric, hyphens, and underscores. No spaces or special chars for directory names.
        if not all(c.isalnum() or c in ['-', '_'] for c in sanitized_name):
            raise ProjectError("Project name can only contain alphanumeric characters, hyphens, and underscores.")
        
        if len(sanitized_name) > 64: # Max length for practicality and filesystem limits
            raise ProjectError("Project name exceeds maximum length of 64 characters.")

        return sanitized_name

    def create_project(self, name: str) -> bool:
        """
        Creates a new project directory and initializes its project.json file.

        Args:
            name (str): The name of the new project.

        Returns:
            bool: True if the project was created successfully, False otherwise.
        
        Throws:
            ProjectError: If validation fails or project already exists.
        """
        sanitized_name = self._validate_project_name(name)
        project_path = self.projects_base_dir / sanitized_name

        if project_path.exists():
            raise ProjectError(f"Project '{sanitized_name}' already exists.")

        try:
            project_path.mkdir(parents=True, exist_ok=False) # Only create if not exist
            project_config_file = project_path / "project.json"

            # Default project.json structure
            default_project_data = {
                "project_name": sanitized_name,
                "version": "1.0",
                "created_date": datetime.now().isoformat(timespec='seconds'),
                "active_model_tag": "",
                "system_prompt": f"You are a helpful AI assistant named {sanitized_name}. Always strive to provide concise and accurate information.",
                "active_tools": [],
                "memory": {
                    "enabled": False,
                    "vector_db_path": ""
                },
                "voice": {
                    "stt_model": "",
                    "tts_voice": ""
                }
            }
            ConfigManager(project_config_file)._write_json(default_project_data)
            print(f"✅ Project '{sanitized_name}' created successfully.")
            return True
        except Exception as e:
            # Clean up partial creation if an error occurs
            if project_path.exists() and not any(project_path.iterdir()):
                project_path.rmdir()
            raise ProjectError(f"Failed to create project '{sanitized_name}': {e}")

    def switch_project(self, name: str) -> bool:
        """
        Sets the given project as the active project in global settings.

        Args:
            name (str): The name of the project to activate.

        Returns:
            bool: True if the project was switched successfully.
        
        Throws:
            ProjectError: If the project does not exist or settings cannot be updated.
        """
        sanitized_name = self._validate_project_name(name)
        project_path = self.projects_base_dir / sanitized_name

        if not project_path.is_dir():
            raise ProjectError(f"Project '{sanitized_name}' does not exist.")
        if not (project_path / "project.json").is_file():
            raise ProjectError(f"Project '{sanitized_name}' is malformed (missing project.json).")

        try:
            self.settings_manager.set("active_project", sanitized_name)
            print(f"✅ Switched to project '{sanitized_name}'.")
            return True
        except ConfigError as e:
            raise ProjectError(f"Failed to update active project in settings: {e}")

    def get_active_project_name(self) -> str:
        """
        Retrieves the name of the currently active project.

        Returns:
            str: The name of the active project, or "default" if none is set.
        """
        try:
            return self.settings_manager.get("active_project", "default")
        except ConfigError:
            # If settings.json is corrupt or missing, fall back to default
            return "default"

    def get_active_project_config(self) -> dict:
        """
        Retrieves the full configuration of the currently active project.

        Returns:
            dict: The dictionary representation of the active project's project.json.
        
        Throws:
            ProjectError: If the active project's configuration cannot be loaded.
        """
        active_project_name = self.get_active_project_name()
        project_config_file = self.projects_base_dir / active_project_name / "project.json"
        
        if not project_config_file.is_file():
            raise ProjectError(f"Active project '{active_project_name}' config file not found: '{project_config_file}'. "
                                "It might be missing or corrupted. Consider creating a new project or switching.")
        try:
            return ConfigManager(project_config_file).to_dict()
        except ConfigError as e:
            raise ProjectError(f"Failed to load active project config for '{active_project_name}': {e}")

    def set_active_model_for_project(self, model_tag: str, project_name: str | None = None) -> bool:
        """
        Sets the active model tag for the specified (or current) project.
        """
        if not isinstance(model_tag, str) or not model_tag.strip():
            raise ProjectError("Model tag cannot be empty when setting the active model.")

        target_project = project_name or self.get_active_project_name()
        project_config_file = self.projects_base_dir / target_project / "project.json"

        if not project_config_file.is_file():
            raise ProjectError(f"Project '{target_project}' config file not found.")

        cleaned_tag = model_tag.strip()
        try:
            ConfigManager(project_config_file).update({"active_model_tag": cleaned_tag})
            print(f"✅ Active model for project '{target_project}' set to '{cleaned_tag}'.")
            return True
        except ConfigError as e:
            raise ProjectError(f"Failed to update active model for '{target_project}': {e}")

    def list_projects(self) -> list[str]:
        """
        Lists the names of all available projects.

        Returns:
            list[str]: A list of project names.
        """
        projects = []
        if not self.projects_base_dir.is_dir():
            return projects # Return empty if projects directory doesn't exist
        for item in self.projects_base_dir.iterdir():
            if item.is_dir() and (item / "project.json").is_file():
                projects.append(item.name)
        return sorted(projects)

# Usage Examples:
#
# 1. Initialize and get active project:
#    pm = ProjectManager(os.getenv("PROJECT_ROOT", "/path/to/novaforge"))
#    active_proj_name = pm.get_active_project_name()
#    print(f"Active project: {active_proj_name}")
#
# 2. Create a new project:
#    try:
#        if pm.create_project("my-new-agent"):
#            print("New project created!")
#    except ProjectError as e:
#        print(f"Error creating project: {e}")
#
# 3. Switch project:
#    try:
#        if pm.switch_project("my-new-agent"):
#            print("Switched to new project!")
#    except ProjectError as e:
#        print(f"Error switching project: {e}")
#
# 4. List all projects:
#    all_projects = pm.list_projects()
#    print(f"All projects: {all_projects}")
