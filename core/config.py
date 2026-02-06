import json
from pathlib import Path
from filelock import FileLock
from datetime import datetime

# File: core/config.py
# Description: Handles reading from and writing to JSON configuration files with file locking.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: json, pathlib, filelock
# Links: MASTER_PLAN.md, test_config.py

class ConfigError(Exception):
    """Custom exception for configuration related errors."""
    pass

class ConfigManager:
    """
    Manages reading and writing operations for JSON configuration files,
    ensuring thread-safe access using file locks.

    Purpose: Provides a robust way to interact with application settings
             and project-specific configurations, preventing data corruption
             from concurrent access.

    Complexity: O(N) for file I/O operations, where N is file size.
    Performance: Optimized with file locking for integrity, but still disk-bound.
    Security Notes: Ensures data integrity during writes. Does not handle encryption
                    or sensitive data redaction; higher layers must manage that.
    """

    def __init__(self, file_path: Path):
        """
        Initializes the ConfigManager with the path to the JSON file.

        Args:
            file_path (Path): The absolute path to the JSON configuration file.
        
        Throws:
            ConfigError: If file_path is not a Path object.
        """
        if not isinstance(file_path, Path):
            raise ConfigError("file_path must be a pathlib.Path object.")
        self.file_path = file_path
        self.lock_path = file_path.with_suffix(file_path.suffix + ".lock")

    def _read_json(self) -> dict:
        """
        Reads the JSON file, acquiring a file lock.

        Returns:
            dict: The loaded JSON data.
        
        Throws:
            ConfigError: If the file is not valid JSON or cannot be read.
        """
        try:
            with FileLock(self.lock_path, timeout=5): # Timeout after 5 seconds
                if not self.file_path.exists():
                    return {} # Return empty dict if file doesn't exist yet
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Configuration file '{self.file_path}' contains invalid JSON: {e}")
        except FileNotFoundError:
            return {} # Handled above, but good for defensive programming
        except Exception as e:
            raise ConfigError(f"Failed to read configuration file '{self.file_path}': {e}")

    def _write_json(self, data: dict):
        """
        Writes data to the JSON file, acquiring a file lock.

        Args:
            data (dict): The dictionary to write to the JSON file.
        
        Throws:
            ConfigError: If the data cannot be written or serialized.
        """
        try:
            # Ensure parent directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with FileLock(self.lock_path, timeout=5):
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigError(f"Failed to write configuration file '{self.file_path}': {e}")

    def get(self, key: str, default=None):
        """
        Retrieves a value from the configuration.

        Args:
            key (str): The key of the value to retrieve.
            default: The default value to return if the key is not found.

        Returns:
            Any: The value associated with the key, or the default value.
        """
        config_data = self._read_json()
        return config_data.get(key, default)

    def set(self, key: str, value):
        """
        Sets a value in the configuration and writes it back to the file.

        Args:
            key (str): The key to set.
            value: The value to associate with the key.
        
        Throws:
            ConfigError: If the configuration cannot be updated.
        """
        config_data = self._read_json()
        config_data[key] = value
        self._write_json(config_data)

    def update(self, new_data: dict):
        """
        Updates the configuration with new data, merging existing keys.

        Args:
            new_data (dict): A dictionary of new key-value pairs to merge.
        
        Throws:
            ConfigError: If the configuration cannot be updated.
        """
        if not isinstance(new_data, dict):
            raise ConfigError("new_data must be a dictionary.")
        config_data = self._read_json()
        config_data.update(new_data)
        self._write_json(config_data)

    def to_dict(self) -> dict:
        """
        Returns the entire configuration as a dictionary.

        Returns:
            dict: The complete configuration data.
        """
        return self._read_json()

# Usage Examples (for docstring)
# 1. Basic usage:
#    settings_path = Path("/path/to/novaforge/config/settings.json")
#    settings_manager = ConfigManager(settings_path)
#    active_project = settings_manager.get("active_project", "default")
#    settings_manager.set("last_opened", datetime.now().isoformat())
#
# 2. Handling non-existent files:
#    non_existent_path = Path("/tmp/non_existent.json")
#    non_existent_manager = ConfigManager(non_existent_path)
#    data = non_existent_manager.get("some_key", "default_value") # Returns "default_value"
#    non_existent_manager.set("new_key", "new_value") # Creates the file
#
# 3. Error handling:
#    try:
#        corrupt_path = Path("/path/to/corrupt.json")
#        corrupt_manager = ConfigManager(corrupt_path)
#        corrupt_manager.to_dict()
#    except ConfigError as e:
#        print(f"Error: {e}")
