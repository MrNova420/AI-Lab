import requests
import json
import os
from typing import List, Dict, Iterator
from urllib.parse import urljoin
from requests.exceptions import ConnectionError, Timeout, RequestException

# File: core/runtime/ollama_driver.py
# Description: Concrete implementation of ModelDriver for Ollama LLM backend.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: requests
# Links: MASTER_PLAN.md, test_ollama_driver.py

from core.runtime.manager import ModelDriver, LLMRuntimeError

class OllamaDriver(ModelDriver):
    """
    Implements the ModelDriver interface for interacting with the Ollama API.

    Purpose: Provides a standardized way to communicate with a running Ollama
             instance, allowing the NovaForge core to send chat history
             and receive model generations.

    Complexity: O(N) for generation (dependent on response length).
    Performance: Network-bound (to Ollama service). Optimized for streaming.
    Security Notes: Assumes Ollama service is trusted and running locally.
                    Input history is passed directly to Ollama.
    """
    def __init__(self, model_tag: str, project_config: Dict):
        """
        Initializes the OllamaDriver.

        Args:
            model_tag (str): The specific tag of the Ollama model (e.g., "llama3:8b").
            project_config (Dict): The configuration for the current project.
                                   (Currently not directly used by OllamaDriver but required by interface).
        
        Throws:
            LLMRuntimeError: If model_tag is invalid.
        """
        # Input validation
        if not isinstance(model_tag, str) or not model_tag:
            raise LLMRuntimeError("Invalid model_tag provided to OllamaDriver.")
        
        self.model_tag = model_tag
        self.ollama_base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.timeout = 600 # 10 minutes for long generations

    def generate(self, history: List[Dict], stream: bool = True) -> Iterator[str] | str:
        """
        Generates a response from the Ollama model.

        Args:
            history (List[Dict]): A list of message dictionaries (role, content).
                                  Example: [{"role": "user", "content": "hello"}]
            stream (bool): If True, yields tokens as they are received.
                           If False, returns the complete response string.

        Returns:
            Iterator[str] | str: An iterator of string tokens if streaming,
                                 otherwise the complete response string.
        
        Throws:
            LLMRuntimeError: If there's a connection issue, API error, or malformed response.
        """
        # Input validation
        if not isinstance(history, list):
            raise LLMRuntimeError("History must be a list of messages.")
        for message in history:
            if not isinstance(message, dict) or "role" not in message or "content" not in message:
                raise LLMRuntimeError("Each message in history must be a dict with 'role' and 'content'.")

        chat_url = urljoin(self.ollama_base_url, "/api/chat")
        
        data = {
            "model": self.model_tag,
            "messages": history,
            "stream": stream,
        }

        try:
            response = requests.post(chat_url, json=data, stream=True, timeout=self.timeout)
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

            if stream:
                return self._stream_ollama_response(response)
            else:
                full_response_content = ""
                for chunk in self._stream_ollama_response(response):
                    full_response_content += chunk
                return full_response_content

        except ConnectionError as e:
            raise LLMRuntimeError(f"Could not connect to Ollama service at {self.ollama_base_url}. Is it running? Error: {e}")
        except Timeout:
            raise LLMRuntimeError(f"Ollama service timed out after {self.timeout} seconds.")
        except RequestException as e:
            raise LLMRuntimeError(f"Ollama API request failed: {e}")
        except Exception as e:
            raise LLMRuntimeError(f"An unexpected error occurred during Ollama generation: {e}")

    def _stream_ollama_response(self, response: requests.Response) -> Iterator[str]:
        """
        Helper to stream and parse SSE chunks from Ollama API response.

        Args:
            response (requests.Response): The requests response object.

        Yields:
            str: Individual text tokens from the model's response.
        
        Throws:
            LLMRuntimeError: If response format is unexpected.
        """
        for line in response.iter_lines():
            if line:
                try:
                    json_chunk = json.loads(line.decode('utf-8'))
                    if "message" in json_chunk and "content" in json_chunk["message"]: # Added check for "message"
                        yield json_chunk["message"]["content"]
                    elif "response" in json_chunk: # For older /api/generate format (should use /api/chat)
                        yield json_chunk["response"]
                except json.JSONDecodeError as e: # Catch JSONDecodeError
                    raise LLMRuntimeError(f"Malformed JSON in Ollama stream: {e}. Line: {line.decode('utf-8')}") # Raise error
                except KeyError as e:
                    raise LLMRuntimeError(f"Malformed Ollama stream response: missing key {e}. Response: {line.decode('utf-8')}")
    
    def is_running(self) -> bool:
        """
        Checks if the Ollama service is running and accessible.

        Returns:
            bool: True if the service is running, False otherwise.
        """
        try:
            health_url = urljoin(self.ollama_base_url, "/api/tags") # A lightweight endpoint
            response = requests.get(health_url, timeout=5)
            response.raise_for_status()
            return True
        except (ConnectionError, Timeout, RequestException):
            return False
        except Exception as e:
            # Catch any other unexpected errors during health check
            print(f"DEBUG: Unexpected error during Ollama health check: {e}") # Log for debugging
            return False
