import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from io import StringIO
from typing import Dict, List, Iterator, Any

# File: tests/test_chat.py
# Description: Unit tests for core/chat.py module.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: pytest, unittest.mock, core.project_manager, core.runtime.manager
# Links: MASTER_PLAN.md, core/chat.py

from core.chat import start_chat, ChatError
from core.project_manager import ProjectError, ProjectManager
from core.runtime.manager import LLMRuntimeError, ModelDriver

# Mock objects for dependencies - Refactored for better control
# Removed MockDriverForChat class

@pytest.fixture
def mock_dependencies_for_chat(mock_project_root_env):
    """
    Mocks necessary external calls for chat tests.
    This fixture ensures project.json in mock_project_root_env has an active model tag.
    """
    project_root_path = Path(mock_project_root_env)
    default_project_json_path = project_root_path / "projects" / "default" / "project.json"
    
    # Update the default project.json to have an active_model_tag
    with open(default_project_json_path, 'r+') as f:
        data = json.load(f)
        data["active_model_tag"] = "test-model:latest"
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

    with patch('core.runtime.manager.ModelRuntimeManager') as mock_mrm_class, \
         patch('core.project_manager.ProjectManager') as mock_pm_class:
        
        # Configure the real ProjectManager instance to be returned by the patched class
        real_pm = MagicMock(spec=ProjectManager)
        real_pm.get_active_project_config.return_value = {
            "project_name": "default",
            "active_model_tag": "test-model:latest",
            "system_prompt": "You are a helpful AI assistant."
        }
        real_pm.get_active_project_name.return_value = "default"
        mock_pm_class.return_value = real_pm

        # Configure the ModelRuntimeManager to return our custom mock driver
        mock_driver_instance = MagicMock(spec=ModelDriver) # Directly create MagicMock
        mock_driver_instance.is_running.return_value = True # Default for successful tests
        mock_driver_instance.generate.side_effect = [
            iter(["Mock ", "greeting", ".\\n"]), # Initial greeting
            iter(["First ", "mock ", "response", ".\\n"]), # First user query
            iter(["Second ", "mock ", "response", ".\\n"]) # Second user query
        ]
        
        mock_mrm_instance = MagicMock() # Define mock_mrm_instance BEFORE use
        mock_mrm_instance.get_driver.return_value = mock_driver_instance
        mock_mrm_class.return_value = mock_mrm_instance

        yield real_pm, mock_mrm_class, mock_driver_instance # Yield the mock_driver_instance to tests for direct control

@patch('prompt_toolkit.prompt', side_effect=['user query 1', 'user query 2', '/exit'])
@patch('sys.stdout', new_callable=StringIO)
def test_start_chat_success(mock_stdout, mock_prompt, mock_dependencies_for_chat, mock_project_root_env):
    """Test a successful chat session flow."""
    _real_pm, _mock_mrm_class, mock_driver_instance = mock_dependencies_for_chat
    # mock_driver_instance.is_running.return_value is already True by default

    start_chat(mock_project_root_env)

    output = mock_stdout.getvalue()
    assert "🚀 Starting chat with 'test-model:latest' for project 'default'." in output
    assert "Type '/exit' or '/quit' to end the chat." in output
    assert "AI> Mock greeting.\n" in output
    assert "\nYOU> " in output # Ensure prompt is displayed
    assert "AI> First mock response.\n" in output
    assert "AI> Second mock response.\n" in output
    assert "👋 Ending chat session." in output

    # Verify history passed to driver
    expected_history_initial = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Hello! How can I assist you today?"}
    ]
    # Check that generate was called with expected initial history for greeting
    mock_driver_instance.generate.assert_any_call(expected_history_initial, stream=True)

    expected_history_q1 = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Hello! How can I assist you today?"},
        {"role": "assistant", "content": "Mock greeting.\n"},
        {"role": "user", "content": "user query 1"}
    ]
    # Check that generate was called with expected history after first user query
    mock_driver_instance.generate.assert_any_call(expected_history_q1, stream=True)


@patch('prompt_toolkit.prompt', side_effect=['/exit'])
@patch('sys.stdout', new_callable=StringIO)
def test_start_chat_no_active_model(mock_stdout, mock_prompt, mock_dependencies_for_chat, mock_project_root_env):
    """Test chat when no active model is configured."""
    real_pm, _mock_mrm_class, _mock_driver_instance = mock_dependencies_for_chat
    # Override the returned project config for this specific test
    real_pm.get_active_project_config.return_value = {
        "project_name": "test_project",
        "active_model_tag": "", # No active model
        "system_prompt": "You are a test AI."
    }
    # _mock_driver_instance.is_running.return_value = True # This is already default in MockDriverForChat

    start_chat(mock_project_root_env)
    output = mock_stdout.getvalue()
    assert "❌ No active model configured for project 'test_project'." in output
    assert "Please select a model using 'Manage Models' menu option." in output

@patch('prompt_toolkit.prompt', side_effect=['/exit'])
@patch('sys.stdout', new_callable=StringIO)
def test_start_chat_ollama_not_running(mock_stdout, mock_prompt, mock_dependencies_for_chat, mock_project_root_env):
    """Test chat when Ollama service is not running."""
    _real_pm, _mock_mrm_class, mock_driver_instance = mock_dependencies_for_chat
    mock_driver_instance.is_running.return_value = False # Explicitly set driver as not running

    start_chat(mock_project_root_env)
    output = mock_stdout.getvalue()
    assert "❌ Ollama service is not running or model 'test-model:latest' is unavailable." in output
    assert "Please ensure Ollama is running" in output

@patch('prompt_toolkit.prompt', side_effect=['/exit'])
@patch('sys.stdout', new_callable=StringIO)
def test_start_chat_exit_command(mock_stdout, mock_prompt, mock_dependencies_for_chat, mock_project_root_env):
    """Test exiting chat with /exit command."""
    _real_pm, _mock_mrm_class, mock_driver_instance = mock_dependencies_for_chat
    # mock_driver_instance.is_running.return_value is already True by default
    start_chat(mock_project_root_env)
    output = mock_stdout.getvalue()
    assert "👋 Ending chat session." in output
    assert mock_prompt.call_count >= 1 # Prompt called at least once

@patch('prompt_toolkit.prompt', side_effect=[' ' , '/exit']) # User enters empty string, then /exit
@patch('sys.stdout', new_callable=StringIO)
def test_start_chat_empty_input(mock_stdout, mock_prompt, mock_dependencies_for_chat, mock_project_root_env):
    """Test chat with empty user input (should continue)."""
    _real_pm, _mock_mrm_class, mock_driver_instance = mock_dependencies_for_chat
    # mock_driver_instance.is_running.return_value is already True by default
    start_chat(mock_project_root_env)
    output = mock_stdout.getvalue()
    assert "👋 Ending chat session." in output
    assert mock_prompt.call_count == 2 # Prompt called twice (once for empty, once for /exit)

def test_start_chat_invalid_project_root():
    """Test initialization with an invalid project root."""
    with pytest.raises(ChatError, match="Invalid project_root provided."):
        start_chat("/non/existent/path")

@patch('prompt_toolkit.prompt', side_effect=['user query 1', '/exit'])
@patch('sys.stdout', new_callable=StringIO)
def test_start_chat_llm_runtime_error_during_generation(mock_stdout, mock_prompt, mock_dependencies_for_chat, mock_project_root_env):
    """Test chat gracefully handles LLMRuntimeError during generation."""
    _real_pm, _mock_mrm_class, mock_driver_instance = mock_dependencies_for_chat
    # mock_driver_instance.is_running.return_value is already True by default
    mock_driver_instance.generate.side_effect = [
        iter(["Mock ", "greeting", ".\\n"]), # Initial greeting
        LLMRuntimeError("LLM choked!") # This will be raised on the first user query
    ]

    start_chat(mock_project_root_env)
    output = mock_stdout.getvalue()
    assert "AI> Mock greeting.\n" in output
    assert "❌ Chat Error: LLM choked!" in output
    assert "👋 Ending chat session." in output