import requests
import json
import os
from typing import List, Dict, Iterator
from urllib.parse import urljoin
from requests.exceptions import ConnectionError, Timeout, RequestException

# File: core/runtime/ollama_driver.py
# Description: Concrete implementation of ModelDriver for Ollama LLM backend with GPU/CPU controls
# Author: Gemini CLI + AI-Forge Team
# Created: 2026-02-06
# Last Modified: 2026-02-07
# Dependencies: requests
# Links: MASTER_PLAN.md, test_ollama_driver.py

from core.runtime.manager import ModelDriver, LLMRuntimeError

class OllamaDriver(ModelDriver):
    """
    Implements the ModelDriver interface for interacting with the Ollama API.
    NOW WITH FULL GPU/CPU CONTROL AND USAGE LIMITS!
    
    New Features (2026-02-07):
    - GPU/CPU device switching with enforcement
    - Usage percentage controls (0-100%)
    - Safety buffer (reserves 5-10% for system stability)
    - Toggle for usage limiter
    - Environment variable management for CUDA
    """
    def __init__(self, model_tag: str, project_config: Dict):
        """
        Initializes the OllamaDriver with GPU/CPU controls.
        
        Args:
            model_tag (str): The specific tag of the Ollama model (e.g., "llama3:8b").
            project_config (Dict): The configuration for the current project.
        
        Throws:
            LLMRuntimeError: If model_tag is invalid.
        """
        # Input validation
        if not isinstance(model_tag, str) or not model_tag:
            raise LLMRuntimeError("Invalid model_tag provided to OllamaDriver.")
        
        self.model_tag = model_tag
        self.ollama_base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.timeout = 600  # 10 minutes for long generations
        
        # GPU/CPU settings
        self.use_gpu = project_config.get('use_gpu', True)
        self.num_gpu = project_config.get('num_gpu', 1)
        self.num_threads = project_config.get('num_threads', 8)
        
        # NEW: Usage percentage controls (0-100%)
        self.max_gpu_usage_percent = 100  # User-controllable
        self.max_cpu_usage_percent = 100  # User-controllable
        self.usage_limiter_enabled = False  # Toggle for usage limiter
        
        # NEW: Safety buffer (reserves 5-10% to prevent system freeze)
        self.safety_buffer_enabled = True
        self.gpu_safety_buffer = 10  # Reserve 10% for system
        self.cpu_safety_buffer = 5   # Reserve 5% for system
        
        print(f"🔧 Ollama Driver initialized")
        print(f"   Model: {model_tag}")
        print(f"   GPU: {'Enabled' if self.use_gpu else 'Disabled'}")
        print(f"   GPU Layers: {self.num_gpu if self.use_gpu else 0}")
        print(f"   CPU Threads: {self.num_threads}")
        print(f"   Usage Limiter: {'ON' if self.usage_limiter_enabled else 'OFF'}")
        print(f"   Safety Buffer: {'ON' if self.safety_buffer_enabled else 'OFF'}")
    
    def set_device(self, use_gpu: bool, num_gpu: int = 1):
        """Switch between GPU and CPU with environment variable enforcement"""
        self.use_gpu = use_gpu
        self.num_gpu = num_gpu if use_gpu else 0
        
        # Force environment variables to ensure proper device usage
        if use_gpu:
            os.environ['CUDA_VISIBLE_DEVICES'] = '0'
            print(f"🎮 Device switched to: GPU")
            print(f"   GPU Layers: {self.num_gpu}")
            print(f"   CUDA_VISIBLE_DEVICES: 0")
        else:
            os.environ['CUDA_VISIBLE_DEVICES'] = ''
            print(f"🖥️ Device switched to: CPU")
            print(f"   CUDA_VISIBLE_DEVICES: (empty - CPU only)")
        
        return True
    
    def set_threads(self, num_threads: int):
        """Set number of CPU threads"""
        self.num_threads = max(1, min(num_threads, 32))
        print(f"🔧 CPU Threads set to: {self.num_threads}")
        return True
    
    def set_usage_limit(self, device: str, percent: int):
        """
        Set maximum usage percentage for GPU or CPU
        
        Args:
            device: 'gpu' or 'cpu'
            percent: 0-100 (will be capped with safety buffer if enabled)
        """
        percent = max(0, min(100, percent))
        
        if device == 'gpu':
            self.max_gpu_usage_percent = percent
            actual = self._apply_safety_buffer(percent, 'gpu')
            print(f"🎮 GPU usage limit: {percent}% (actual: {actual}% with buffer)")
        else:
            self.max_cpu_usage_percent = percent
            actual = self._apply_safety_buffer(percent, 'cpu')
            print(f"🖥️ CPU usage limit: {percent}% (actual: {actual}% with buffer)")
        
        return True
    
    def toggle_usage_limiter(self, enabled: bool):
        """Enable/disable usage percentage limiter"""
        self.usage_limiter_enabled = enabled
        print(f"🎚️ Usage limiter: {'ENABLED' if enabled else 'DISABLED'}")
        return True
    
    def toggle_safety_buffer(self, enabled: bool):
        """Enable/disable safety buffer (reserves 5-10% for system)"""
        self.safety_buffer_enabled = enabled
        print(f"🛡️ Safety buffer: {'ENABLED' if enabled else 'DISABLED'}")
        return True
    
    def _apply_safety_buffer(self, percent: int, device: str) -> int:
        """Apply safety buffer to usage percentage"""
        if not self.safety_buffer_enabled:
            return percent
        
        buffer = self.gpu_safety_buffer if device == 'gpu' else self.cpu_safety_buffer
        actual = max(0, percent - buffer)
        return actual
    
    def get_settings(self) -> Dict:
        """Get current device settings including usage limits"""
        return {
            'use_gpu': self.use_gpu,
            'num_gpu': self.num_gpu,
            'num_threads': self.num_threads,
            'device': 'GPU' if self.use_gpu else 'CPU',
            'max_gpu_usage_percent': self.max_gpu_usage_percent,
            'max_cpu_usage_percent': self.max_cpu_usage_percent,
            'usage_limiter_enabled': self.usage_limiter_enabled,
            'safety_buffer_enabled': self.safety_buffer_enabled,
            'gpu_safety_buffer': self.gpu_safety_buffer,
            'cpu_safety_buffer': self.cpu_safety_buffer,
            'actual_gpu_usage': self._apply_safety_buffer(self.max_gpu_usage_percent, 'gpu'),
            'actual_cpu_usage': self._apply_safety_buffer(self.max_cpu_usage_percent, 'cpu')
        }
    
    def generate(self, history: List[Dict], stream: bool = True) -> Iterator[str] | str:
        """
        Generates a response from the Ollama model with GPU/CPU control.
        
        Args:
            history (List[Dict]): A list of message dictionaries (role, content).
            stream (bool): If True, yields tokens as they are received.
        
        Returns:
            Iterator[str] | str: An iterator of string tokens if streaming,
                                 otherwise the complete response string.
        """
        # Input validation
        if not isinstance(history, list):
            raise LLMRuntimeError("History must be a list of messages.")
        for message in history:
            if not isinstance(message, dict) or "role" not in message or "content" not in message:
                raise LLMRuntimeError("Each message in history must be a dict with 'role' and 'content'.")

        chat_url = urljoin(self.ollama_base_url, "/api/chat")
        
        # Build options with GPU/CPU settings and usage limits
        options = {
            'num_thread': self.num_threads,
            'temperature': 0.7,
        }
        
        # GPU configuration with usage limits
        if self.use_gpu:
            options['num_gpu'] = self.num_gpu
            
            # Apply usage limiter if enabled
            if self.usage_limiter_enabled:
                actual_percent = self._apply_safety_buffer(self.max_gpu_usage_percent, 'gpu')
                # Convert percentage to memory fraction (0.0 to 1.0)
                options['gpu_memory_fraction'] = actual_percent / 100.0
            
            # Force GPU usage
            os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        else:
            options['num_gpu'] = 0
            
            # Apply CPU usage limiter if enabled
            if self.usage_limiter_enabled:
                actual_percent = self._apply_safety_buffer(self.max_cpu_usage_percent, 'cpu')
                # Adjust context size based on CPU usage limit
                max_ctx = int(2048 * (actual_percent / 100.0))
                options['num_ctx'] = max(512, max_ctx)
            
            # Force CPU only
            os.environ['CUDA_VISIBLE_DEVICES'] = ''
        
        data = {
            "model": self.model_tag,
            "messages": history,
            "stream": stream,
            "options": options
        }
        
        print(f"🚀 Generating response...")
        print(f"   Model: {self.model_tag}")
        print(f"   Device: {'GPU' if self.use_gpu else 'CPU'}")
        if self.usage_limiter_enabled:
            device_name = 'GPU' if self.use_gpu else 'CPU'
            percent = self.max_gpu_usage_percent if self.use_gpu else self.max_cpu_usage_percent
            actual = self._apply_safety_buffer(percent, device_name.lower())
            print(f"   Usage Limit: {percent}% (actual: {actual}% with buffer)")

        try:
            response = requests.post(chat_url, json=data, stream=True, timeout=self.timeout)
            response.raise_for_status()

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
        """
        for line in response.iter_lines():
            if line:
                try:
                    json_chunk = json.loads(line.decode('utf-8'))
                    
                    if 'message' in json_chunk and 'content' in json_chunk['message']:
                        yield json_chunk['message']['content']
                    
                    if json_chunk.get('done', False):
                        # Print performance stats if available
                        if 'total_duration' in json_chunk:
                            duration_s = json_chunk['total_duration'] / 1e9
                            print(f"✅ Response complete ({duration_s:.2f}s)")
                        break
                        
                except json.JSONDecodeError as e:
                    # Skip malformed JSON lines
                    continue

    def is_running(self) -> bool:
        """
        Checks if the Ollama service is running and accessible.
        
        Returns:
            bool: True if the service is running, False otherwise.
        """
        try:
            health_url = urljoin(self.ollama_base_url, "/api/tags")
            response = requests.get(health_url, timeout=5)
            response.raise_for_status()
            return True
        except (ConnectionError, Timeout, RequestException):
            return False
        except Exception as e:
            print(f"DEBUG: Unexpected error during Ollama health check: {e}")
            return False
