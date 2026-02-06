import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, List, Iterator

# File: tests/test_runtime_manager.py
# Description: Unit tests for core/runtime/manager.py module.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: pytest, unittest.mock
# Links: MASTER_PLAN.md, core/runtime/manager.py

from core.runtime.manager import ModelDriver, ModelRuntimeManager, LLMRuntimeError

# Mock concrete driver for testing purposes
class MockOllamaDriver(ModelDriver):
    def __init__(self, model_tag: str, project_config: Dict):
        self.model_tag = model_tag
        self.project_config = project_config
        self.is_running_status = True # Default for mock

    def generate(self, history: List[Dict], stream: bool = True) -> Iterator[str] | str:
        if stream:
            return iter([f"Mock stream for {self.model_tag}: ", history[0]['content']])
        else:
            return f"Mock response for {self.model_tag}: {history[0]['content']}"

    def is_running(self) -> bool:
        return self.is_running_status

@pytest.fixture
def mock_project_config():
    """Provides a mock project configuration."""
    return {
        "project_name": "test_project",
        "active_model_tag": "llama3:8b",
        "system_prompt": "Test prompt."
    }

@pytest.fixture
def model_runtime_manager(mock_project_root_env):
    """Provides a ModelRuntimeManager instance for testing."""
    return ModelRuntimeManager(mock_project_root_env)

def test_get_driver_no_active_model_tag_set(model_runtime_manager):
    """Test get_driver when active_model_tag is empty."""
    config_empty_model_tag = {"project_name": "test_project", "active_model_tag": ""}
    with pytest.raises(LLMRuntimeError, match="No active model is set for the current project"):
        model_runtime_manager.get_driver(config_empty_model_tag)

def test_get_driver_invalid_config_not_dict(model_runtime_manager):
    """Test get_driver with invalid project configuration (not a dict)."""
    with pytest.raises(LLMRuntimeError, match="Invalid project configuration"):
        model_runtime_manager.get_driver("not_a_dict") # type: ignore

def test_get_driver_invalid_config_missing_active_model_key(model_runtime_manager):
    """Test get_driver with invalid project configuration (missing active_model_tag key)."""
    config_missing_key = {"project_name": "test_project", "some_other_key": "value"}
    with pytest.raises(LLMRuntimeError, match="Invalid project configuration: 'active_model_tag' missing."):
        model_runtime_manager.get_driver(config_missing_key)


@patch('core.runtime.ollama_driver.OllamaDriver', new=MockOllamaDriver)
def test_get_driver_success(model_runtime_manager, mock_project_config):
    """Test successful retrieval of a driver."""
    driver = model_runtime_manager.get_driver(mock_project_config)
    assert isinstance(driver, MockOllamaDriver)
    assert driver.model_tag == "llama3:8b"
    assert driver.project_config == mock_project_config
    
    # Test caching
    driver2 = model_runtime_manager.get_driver(mock_project_config)
    assert driver is driver2

@patch('core.runtime.ollama_driver.OllamaDriver', side_effect=Exception("Mock driver init error"))
def test_get_driver_init_failure(mock_ollama_driver_class, model_runtime_manager, mock_project_config):
    """Test error during driver initialization."""
    with pytest.raises(LLMRuntimeError, match="Failed to initialize driver for model"):
        model_runtime_manager.get_driver(mock_project_config)

def test_mock_ollama_driver_generate_stream():
    """Test generate method of MockOllamaDriver in streaming mode."""
    driver = MockOllamaDriver("test-model:latest", {})
    history = [{"role": "user", "content": "Hello there!"}]
    tokens = list(driver.generate(history, stream=True))
    assert tokens == ["Mock stream for test-model:latest: ", "Hello there!"]

def test_mock_ollama_driver_generate_non_stream():
    """Test generate method of MockOllamaDriver in non-streaming mode."""
    driver = MockOllamaDriver("test-model:latest", {})
    history = [{"role": "user", "content": "Hello there!"}]
    response = driver.generate(history, stream=False)
    assert response == "Mock response for test-model:latest: Hello there!"

def test_mock_ollama_driver_is_running():
    """Test is_running method of MockOllamaDriver."""
    driver = MockOllamaDriver("test-model:latest", {})
    assert driver.is_running() is True
    driver.is_running_status = False
    assert driver.is_running() is False