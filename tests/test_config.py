import pytest
import json
from pathlib import Path
from datetime import datetime
from filelock import FileLock # Import FileLock for direct use in test

# File: tests/test_config.py
# Description: Unit tests for core/config.py module.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: pytest, pathlib, json, filelock
# Links: MASTER_PLAN.md, core/config.py

from core.config import ConfigManager, ConfigError

@pytest.fixture
def temp_config_file(tmp_path):
    """Provides a temporary, empty config.json file for testing."""
    config_file = tmp_path / "test_config.json"
    return config_file

@pytest.fixture
def populated_config_file(tmp_path):
    """Provides a temporary, pre-populated config.json file for testing."""
    config_file = tmp_path / "populated_config.json"
    data = {
        "key1": "value1",
        "key2": 123,
        "nested": {"a": True, "b": "hello"},
        "list": [1, 2, 3]
    }
    with open(config_file, 'w') as f:
        json.dump(data, f)
    return config_file

def test_config_manager_init(temp_config_file):
    """Test ConfigManager initialization with valid and invalid paths."""
    cm = ConfigManager(temp_config_file)
    assert cm.file_path == temp_config_file
    assert cm.lock_path == temp_config_file.with_suffix(temp_config_file.suffix + ".lock")

    with pytest.raises(ConfigError, match="file_path must be a pathlib.Path object."):
        ConfigManager("/invalid/path/string.json")

def test_read_non_existent_file(temp_config_file):
    """Test reading a config file that does not exist."""
    cm = ConfigManager(temp_config_file)
    assert cm.to_dict() == {}

def test_write_and_read_data(temp_config_file):
    """Test writing data to a new file and then reading it back."""
    cm = ConfigManager(temp_config_file)
    test_data = {"setting_a": "value_a", "setting_b": 42}
    cm._write_json(test_data)
    
    read_data = cm._read_json()
    assert read_data == test_data

    # Verify file content directly
    with open(temp_config_file, 'r') as f:
        content = json.load(f)
    assert content == test_data

def test_read_populated_file(populated_config_file):
    """Test reading from a pre-populated config file."""
    cm = ConfigManager(populated_config_file)
    expected_data = {
        "key1": "value1",
        "key2": 123,
        "nested": {"a": True, "b": "hello"},
        "list": [1, 2, 3]
    }
    assert cm.to_dict() == expected_data

def test_get_value(populated_config_file):
    """Test retrieving individual values with get()."""
    cm = ConfigManager(populated_config_file)
    assert cm.get("key1") == "value1"
    assert cm.get("key2") == 123
    assert cm.get("nested") == {"a": True, "b": "hello"}
    assert cm.get("non_existent_key") is None
    assert cm.get("non_existent_key", "default_val") == "default_val"

def test_set_value(temp_config_file):
    """Test setting individual values with set()."""
    cm = ConfigManager(temp_config_file)
    cm.set("new_key", "new_value")
    assert cm.get("new_key") == "new_value"
    assert cm.to_dict() == {"new_key": "new_value"}

    cm.set("existing_key", "updated_value")
    assert cm.get("existing_key") == "updated_value"
    assert cm.to_dict() == {"new_key": "new_value", "existing_key": "updated_value"}

def test_update_data(populated_config_file):
    """Test updating multiple values with update()."""
    cm = ConfigManager(populated_config_file)
    update_data = {"key1": "new_value1", "key3": "value3"}
    cm.update(update_data)
    
    expected_data = {
        "key1": "new_value1", # Updated
        "key2": 123,
        "nested": {"a": True, "b": "hello"},
        "list": [1, 2, 3],
        "key3": "value3" # Added
    }
    assert cm.to_dict() == expected_data

def test_update_with_invalid_data(temp_config_file):
    """Test update() with non-dictionary input."""
    cm = ConfigManager(temp_config_file)
    with pytest.raises(ConfigError, match="new_data must be a dictionary."):
        cm.update("invalid_data")

def test_corrupt_file_read(temp_config_file):
    """Test reading from a corrupt JSON file."""
    with open(temp_config_file, 'w') as f:
        f.write("{'key': 'value'") # Invalid JSON

    cm = ConfigManager(temp_config_file)
    with pytest.raises(ConfigError, match="contains invalid JSON"):
        cm.to_dict()

def test_concurrent_access_with_lock(temp_config_file):
    """Simulate concurrent access to ensure file locking works."""
    cm1 = ConfigManager(temp_config_file)
    cm2 = ConfigManager(temp_config_file)

    # cm1 writes, cm2 tries to read/write concurrently
    cm1.set("counter", 0)

    def writer_func():
        try:
            for i in range(5):
                current = cm2.get("counter", 0)
                cm2.set("counter", current + 1)
        except ConfigError as e:
            print(f"Concurrent writer error: {e}")
            pytest.fail(f"Concurrent writer failed: {e}")

    import threading
    writer_thread = threading.Thread(target=writer_func)
    writer_thread.start()
    writer_thread.join()

    # After concurrent writes, verify final count
    assert cm1.get("counter") == 5

def test_lock_timeout(temp_config_file):
    """Test if the lock times out when held by another process/thread."""
    cm = ConfigManager(temp_config_file)
    
    # Manually acquire the lock and hold it
    lock = FileLock(cm.lock_path, timeout=5)
    lock.acquire()
    try:
        # Try to read/write from another ConfigManager instance
        # This should trigger a timeout
        cm2 = ConfigManager(temp_config_file)
        with pytest.raises(ConfigError, match="could not be acquired"): # Changed to ConfigError
            cm2.set("test_key", "test_value")
    finally:
        lock.release()