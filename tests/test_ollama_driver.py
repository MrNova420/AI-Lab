import pytest
import requests_mock
import json
import requests.exceptions as exc
from typing import Dict, List, Iterator
from urllib.parse import urljoin
from unittest.mock import patch, MagicMock # Added MagicMock, patch for potential future use

# File: tests/test_ollama_driver.py
# Description: Unit tests for core/runtime/ollama_driver.py module.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: pytest, requests_mock
# Links: MASTER_PLAN.md, core/runtime/ollama_driver.py

from core.runtime.ollama_driver import OllamaDriver, LLMRuntimeError
from core.runtime.manager import ModelDriver # For type checking

OLLAMA_BASE_URL = "http://localhost:11434"

@pytest.fixture
def ollama_driver():
    """Provides an OllamaDriver instance for testing."""
    return OllamaDriver("test-model:latest", {})

def test_ollama_driver_init(ollama_driver):
    """Test initialization of OllamaDriver."""
    assert isinstance(ollama_driver, ModelDriver)
    assert ollama_driver.model_tag == "test-model:latest"
    assert ollama_driver.ollama_base_url == OLLAMA_BASE_URL

    with pytest.raises(LLMRuntimeError, match="Invalid model_tag"):
        OllamaDriver("", {})
    with pytest.raises(LLMRuntimeError, match="Invalid model_tag"):
        OllamaDriver(123, {}) # type: ignore

def test_is_running_success(ollama_driver, requests_mock):
    """Test is_running when Ollama service is up."""
    requests_mock.get(urljoin(OLLAMA_BASE_URL, "/api/tags"), status_code=200, json={"models": []})
    assert ollama_driver.is_running() is True

def test_is_running_failure(ollama_driver, requests_mock):
    """Test is_running when Ollama service is down."""
    requests_mock.get(urljoin(OLLAMA_BASE_URL, "/api/tags"), exc=exc.ConnectionError)
    assert ollama_driver.is_running() is False

def test_generate_streaming_success(ollama_driver, requests_mock):
    """Test streaming generation success."""
    chat_url = urljoin(OLLAMA_BASE_URL, "/api/chat")
    mock_response_chunks = [
        {"model": "test-model", "message": {"role": "assistant", "content": "Hello"}},
        {"model": "test-model", "message": {"role": "assistant", "content": ", "}},
        {"model": "test-model", "message": {"role": "assistant", "content": "world!"}},
        {"model": "test-model", "done": True}
    ]
    # Build SSE-like data as a single string with newlines
    sse_data = "".join([json.dumps(chunk) + "\n" for chunk in mock_response_chunks])
    requests_mock.post(chat_url, text=sse_data, headers={'Content-Type': 'application/x-ndjson'})

    history = [{"role": "user", "content": "Hi"}]
    tokens = list(ollama_driver.generate(history, stream=True))
    assert tokens == ["Hello", ", ", "world!"]

def test_generate_non_streaming_success(ollama_driver, requests_mock):
    """Test non-streaming generation success."""
    chat_url = urljoin(OLLAMA_BASE_URL, "/api/chat")
    mock_response_chunks = [
        {"model": "test-model", "message": {"role": "assistant", "content": "Hello"}},
        {"model": "test-model", "message": {"role": "assistant", "content": ", "}},
        {"model": "test-model", "message": {"role": "assistant", "content": "world!"}},
        {"model": "test-model", "done": True}
    ]
    # Build SSE-like data, for non-streaming the driver will consume all of it.
    sse_data = "".join([json.dumps(chunk) + "\n" for chunk in mock_response_chunks])
    requests_mock.post(chat_url, text=sse_data, headers={'Content-Type': 'application/x-ndjson'})

    history = [{"role": "user", "content": "Hi"}]
    full_response = ollama_driver.generate(history, stream=False)
    assert full_response == "Hello, world!"

def test_generate_connection_error(ollama_driver, requests_mock):
    """Test generation with connection error."""
    chat_url = urljoin(OLLAMA_BASE_URL, "/api/chat")
    requests_mock.post(chat_url, exc=exc.ConnectionError)

    history = [{"role": "user", "content": "Test"}]
    with pytest.raises(LLMRuntimeError, match="Could not connect to Ollama service"):
        list(ollama_driver.generate(history, stream=True))

def test_generate_timeout_error(ollama_driver, requests_mock):
    """Test generation with timeout error."""
    chat_url = urljoin(OLLAMA_BASE_URL, "/api/chat")
    requests_mock.post(chat_url, exc=exc.Timeout)

    history = [{"role": "user", "content": "Test"}]
    with pytest.raises(LLMRuntimeError, match="Ollama service timed out"):
        list(ollama_driver.generate(history, stream=True))

def test_generate_http_error(ollama_driver, requests_mock):
    """Test generation with HTTP error from Ollama."""
    chat_url = urljoin(OLLAMA_BASE_URL, "/api/chat")
    requests_mock.post(chat_url, status_code=500, text="Internal Server Error")

    history = [{"role": "user", "content": "Test"}]
    with pytest.raises(LLMRuntimeError, match="Ollama API request failed"):
        list(ollama_driver.generate(history, stream=True))

def test_generate_malformed_response(ollama_driver, requests_mock):
    """Test generation with malformed JSON response from Ollama."""
    chat_url = urljoin(OLLAMA_BASE_URL, "/api/chat")
    # The driver's _stream_ollama_response should now raise LLMRuntimeError on json.JSONDecodeError
    requests_mock.post(chat_url, text="invalid json response", headers={'Content-Type': 'application/x-ndjson'})

    history = [{"role": "user", "content": "Test"}]
    with pytest.raises(LLMRuntimeError, match="Malformed JSON in Ollama stream"):
        list(ollama_driver.generate(history, stream=True))

def test_generate_invalid_history_input(ollama_driver):
    """Test generate with invalid history format."""
    with pytest.raises(LLMRuntimeError, match="History must be a list of messages."):
        ollama_driver.generate("invalid", stream=True) # type: ignore
    
    with pytest.raises(LLMRuntimeError, match="Each message in history must be a dict with 'role' and 'content'."):
        ollama_driver.generate([{"role": "user"}], stream=True)
    
    with pytest.raises(LLMRuntimeError, match="Each message in history must be a dict with 'role' and 'content'."):
        ollama_driver.generate([{"content": "hi"}], stream=True)