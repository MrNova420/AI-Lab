import abc
from typing import List, Dict, Iterator
from pathlib import Path

# File: core/runtime/manager.py
# Description: Abstract base classes and manager for LLM runtime drivers.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: abc, typing
# Links: MASTER_PLAN.md, test_runtime_manager.py

class LLMRuntimeError(Exception):
    """Custom exception for LLM runtime related errors."""
    pass

class ModelDriver(abc.ABC):
    """
    Abstract Base Class for all LLM model drivers.

    Purpose: Defines a consistent interface for interacting with different
             LLM backends (e.g., Ollama, llama.cpp), allowing the core
             application to switch implementations seamlessly.

    Complexity: O(1) for method signatures.
    Performance: N/A, as it's an interface.
    Security Notes: Implementations must handle safe interaction with their
                    respective backends.
    """

    @abc.abstractmethod
    def __init__(self, model_tag: str, project_config: Dict):
        """
        Initializes the model driver.

        Args:
            model_tag (str): The specific tag or identifier for the model.
            project_config (Dict): The configuration for the current project.
        """
        pass

    @abc.abstractmethod
    def generate(self, history: List[Dict], stream: bool = True) -> Iterator[str] | str:
        """
        Generates a response from the LLM based on conversation history.

        Args:
            history (List[Dict]): A list of message dictionaries (role, content).
            stream (bool): If True, returns an iterator of tokens. If False,
                           returns the complete response string.

        Returns:
            Iterator[str] | str: An iterator of string tokens if streaming,
                                 otherwise the complete response string.
        
        Throws:
            LLMRuntimeError: If there's an issue with generation or backend communication.
        """
        pass

    @abc.abstractmethod
    def is_running(self) -> bool:
        """
        Checks if the LLM backend service for this model is running and accessible.

        Returns:
            bool: True if the service is running, False otherwise.
        """
        pass

class ModelRuntimeManager:
    """
    Manages the selection and instantiation of LLM model drivers.

    Purpose: Provides a unified interface for the core application to
             obtain the correct ModelDriver based on the active project's
             configuration, abstracting away backend-specific details.

    Complexity: O(1) for driver instantiation.
    Performance: Fast, as it primarily involves object creation and lookup.
    Security Notes: Ensures valid driver is instantiated; relies on driver
                    implementations for secure backend interaction.
    """
    def __init__(self, project_root: str):
        """
        Initializes the ModelRuntimeManager.

        Args:
            project_root (str): The absolute path to the NovaForge project root directory.
        """
        self.project_root = Path(project_root)
        self.drivers = {} # Cache for instantiated drivers

    def get_driver(self, project_config: Dict) -> ModelDriver:
        """
        Instantiates and returns the appropriate ModelDriver for the
        active model in the given project configuration.

        Args:
            project_config (Dict): The configuration of the current project,
                                   containing `active_model_tag`.

        Returns:
            ModelDriver: An instance of the concrete ModelDriver.
        
        Throws:
            LLMRuntimeError: If `active_model_tag` is missing, unknown,
                             or the driver fails to initialize.
        """
        # Input validation
        if not isinstance(project_config, Dict) or "active_model_tag" not in project_config:
            raise LLMRuntimeError("Invalid project configuration: 'active_model_tag' missing.")

        model_tag = project_config.get("active_model_tag")
        if not model_tag:
            raise LLMRuntimeError("No active model is set for the current project. Please select one.")

        # Currently, only Ollama is supported. Extend this with a factory pattern for more drivers.
        if model_tag in self.drivers:
            return self.drivers[model_tag]
        
        # Determine which driver to use based on model_tag (can be enhanced with models.json lookup)
        # For now, assume Ollama for all models.
        from core.runtime.ollama_driver import OllamaDriver # Late import to avoid circular dependency

        try:
            driver = OllamaDriver(model_tag, project_config)
            self.drivers[model_tag] = driver # Cache the driver
            return driver
        except Exception as e:
            raise LLMRuntimeError(f"Failed to initialize driver for model '{model_tag}': {e}")

# Usage Examples:
#
# 1. Get a driver:
#    # Assume project_root and an active project config exist
#    # from core.project_manager import ProjectManager
#    # pm = ProjectManager(PROJECT_ROOT)
#    # active_project_config = pm.get_active_project_config()
#
#    # mrm = ModelRuntimeManager(PROJECT_ROOT)
#    # driver = mrm.get_driver(active_project_config)
#    # if driver.is_running():
#    #    for token in driver.generate([{"role": "user", "content": "Hello"}], stream=True):
#    #        print(token, end="")
#    # else:
#    #    print("Ollama service is not running.")
