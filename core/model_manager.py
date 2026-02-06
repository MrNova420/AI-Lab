import subprocess
import json
import os
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# File: core/model_manager.py
# Description: Manages local AI models, including listing, downloading, and registering them.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: core.config.ConfigManager
# Links: MASTER_PLAN.md, test_model_manager.py

from core.config import ConfigManager, ConfigError

class ModelManagerError(Exception):
    """Custom exception for model management related errors."""
    pass

class ModelManager:
    """
    Manages the lifecycle of AI models within NovaForge, primarily interacting
    with the Ollama CLI for downloads and maintaining a local manifest.

    Purpose: Centralizes operations for discovering, adding, and updating
             information about local models, making them available to projects.

    Complexity: O(N) for `ollama pull` (network/disk bound). O(1) for config reads/writes.
    Performance: `ollama pull` can be slow. Local operations are fast.
    Security Notes: Executes `ollama` as a subprocess; relies on `ollama`'s security.
                    Input validation prevents shell injection.
    """
    def __init__(self, project_root: str):
        """
        Initializes the ModelManager.

        Args:
            project_root (str): The absolute path to the NovaForge project root directory.
        
        Throws:
            ModelManagerError: If project_root is not a valid directory.
        """
        self.project_root = Path(project_root).resolve()
        if not self.project_root.is_dir():
            raise ModelManagerError(f"Project root '{project_root}' is not a valid directory.")

        self.models_file = self.project_root / "models" / "models.json"
        self.models_config_manager = ConfigManager(self.models_file)
        self.ollama_cmd = os.getenv("OLLAMA_CMD", "ollama") # Allow overriding ollama command
        self._ollama_hint = "Install Ollama from https://ollama.com/download or set OLLAMA_CMD to the binary path."

    def _ensure_ollama_available(self):
        """
        Ensures the configured Ollama CLI binary exists on PATH.
        """
        if shutil.which(self.ollama_cmd) is None:
            raise ModelManagerError(
                f"Ollama executable '{self.ollama_cmd}' was not found on PATH. {self._ollama_hint}"
            )

    def _validate_model_tag(self, model_tag: str) -> str:
        """
        Validates a model tag for basic format requirements.

        Args:
            model_tag (str): The model tag to validate.

        Returns:
            str: The validated and stripped model tag.

        Throws:
            ModelManagerError: If the model tag is invalid.
        """
        if not isinstance(model_tag, str) or not model_tag.strip():
            raise ModelManagerError("Model tag cannot be empty.")
        
        cleaned_tag = model_tag.strip()
        # Basic validation: must contain a colon (e.g., "model:tag")
        if ":" not in cleaned_tag:
            raise ModelManagerError(f"Invalid model tag format: '{model_tag}'. Expected format 'model_name:tag'.")
        # Further validation could include regex for allowed characters if needed
        return cleaned_tag

    def download_model(self, model_tag: str):
        """
        Downloads a model using the Ollama CLI and registers it in the local manifest.

        Args:
            model_tag (str): The tag of the model to download (e.g., "llama3:8b").
        
        Throws:
            ModelManagerError: If `ollama pull` fails or manifest update fails.
        """
        sanitized_model_tag = self._validate_model_tag(model_tag)
        self._ensure_ollama_available()
        print(f"🚀 Downloading model '{sanitized_model_tag}' using Ollama...")

        try:
            pull_cmd = [self.ollama_cmd, "pull", sanitized_model_tag]
            print(f"\n[Ollama] {' '.join(pull_cmd)}")
            with subprocess.Popen(
                pull_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            ) as process:
                streamed_output = []
                if process.stdout is not None:
                    for line in process.stdout:
                        streamed_output.append(line)
                        print(line, end="")
                return_code = process.wait()
                pull_log = "".join(streamed_output).strip()
                if return_code != 0:
                    raise subprocess.CalledProcessError(return_code, pull_cmd, output=pull_log)

            model_details = {}
            show_warning = None
            try:
                model_info_process = subprocess.run(
                    [self.ollama_cmd, "show", "--json", sanitized_model_tag],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                model_details = json.loads(model_info_process.stdout)
            except subprocess.CalledProcessError as e:
                show_warning = (e.output or e.stderr or "").strip()
            except json.JSONDecodeError as e:
                show_warning = f"Failed to parse model info JSON: {e}"

            if show_warning:
                print(f"⚠️  Warning: Could not fetch detailed metadata for '{sanitized_model_tag}'.")
                if show_warning:
                    print(show_warning)
                print("Proceeding with basic registration so the model is still usable.")
                model_details = model_details or {}
            
            size_bytes = model_details.get("size", 0)
            size_gb = round(size_bytes / (1024**3), 2) if size_bytes else 0

            new_model_entry = {
                "tag": sanitized_model_tag,
                "backend": "ollama",
                "download_date": datetime.now().isoformat(timespec='seconds'),
                "family": model_details.get("family", "unknown"),
                "size_gb": size_gb,
                "details": {
                    "format": model_details.get("format", "unknown"),
                    "quantization": model_details.get("quantization", "unknown")
                }
            }

            models_data = self.models_config_manager.to_dict()
            models_data[sanitized_model_tag] = new_model_entry
            self.models_config_manager.update(models_data)

            print(f"✅ Successfully downloaded and registered '{sanitized_model_tag}'.")

        except subprocess.CalledProcessError as e:
            error_output = (e.output or "").strip()
            print(f"❌ Ollama command failed for '{sanitized_model_tag}':")
            if error_output:
                print(error_output)
            raise ModelManagerError(
                f"Failed to download model '{sanitized_model_tag}': {error_output or e}"
            )
        except json.JSONDecodeError:
            raise ModelManagerError(f"Failed to parse model info from Ollama for '{sanitized_model_tag}'. Is Ollama running and the model tag correct?")
        except ConfigError as e:
            raise ModelManagerError(f"Failed to update models.json: {e}")
        except Exception as e:
            raise ModelManagerError(f"An unexpected error occurred during model download: {e}")

    def list_local_models(self) -> List[str]:
        """
        Lists all models registered in the local models.json manifest.

        Returns:
            List[str]: A sorted list of model tags.
        
        Throws:
            ModelManagerError: If models.json is unreadable.
        """
        try:
            models_data = self.models_config_manager.to_dict()
            return sorted(list(models_data.keys()))
        except ConfigError as e:
            raise ModelManagerError(f"Failed to read models.json: {e}")

    def get_model_details(self, model_tag: str) -> Dict:
        """
        Retrieves details for a specific model from the local manifest.

        Args:
            model_tag (str): The tag of the model.

        Returns:
            Dict: The dictionary containing model details.
        
        Throws:
            ModelManagerError: If model_tag is not found or models.json is unreadable.
        """
        try:
            models_data = self.models_config_manager.to_dict()
            if model_tag not in models_data:
                raise ModelManagerError(f"Model '{model_tag}' not found in local manifest.")
            return models_data[model_tag]
        except ConfigError as e:
            raise ModelManagerError(f"Failed to read models.json: {e}")

    def list_downloaded_models(self) -> List[Dict]:
        """
        Lists ALL models downloaded in Ollama, querying Ollama directly.
        This ensures we see all models even if not in our manifest.

        Returns:
            List[Dict]: List of model dictionaries with name, size, modified_at.
        
        Throws:
            ModelManagerError: If Ollama is not available or command fails.
        """
        self._ensure_ollama_available()
        
        try:
            # Query Ollama for list of models
            result = subprocess.run(
                [self.ollama_cmd, "list"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            models = []
            lines = result.stdout.strip().split('\n')
            
            # Skip header line
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 3:
                        name = parts[0]
                        # Try to parse size (could be "2.3 GB" or similar)
                        size_str = ' '.join(parts[1:3]) if len(parts) >= 3 else parts[1]
                        
                        # Convert size to bytes
                        size_bytes = 0
                        try:
                            if 'GB' in size_str:
                                size_bytes = int(float(size_str.split()[0]) * 1e9)
                            elif 'MB' in size_str:
                                size_bytes = int(float(size_str.split()[0]) * 1e6)
                        except:
                            pass
                        
                        # Get modified date if available
                        modified_at = None
                        if len(parts) > 3:
                            modified_at = ' '.join(parts[3:])
                        
                        models.append({
                            'name': name,
                            'size': size_bytes,
                            'modified_at': modified_at
                        })
            
            return models
            
        except subprocess.TimeoutExpired:
            raise ModelManagerError("Ollama list command timed out. Is Ollama running?")
        except subprocess.CalledProcessError as e:
            raise ModelManagerError(f"Failed to list Ollama models: {e.stderr or e}")
        except Exception as e:
            raise ModelManagerError(f"Unexpected error listing models: {e}")

    def remove_model(self, model_tag: str):
        """
        Removes a model from Ollama and the local manifest.

        Args:
            model_tag (str): The tag of the model to remove.
        
        Throws:
            ModelManagerError: If removal fails.
        """
        sanitized_model_tag = self._validate_model_tag(model_tag)
        self._ensure_ollama_available()
        
        try:
            # Remove from Ollama
            subprocess.run(
                [self.ollama_cmd, "rm", sanitized_model_tag],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            # Remove from manifest
            try:
                models_data = self.models_config_manager.to_dict()
                if sanitized_model_tag in models_data:
                    del models_data[sanitized_model_tag]
                    self.models_config_manager.update(models_data)
            except ConfigError:
                pass  # Don't fail if manifest update fails
            
            print(f"✅ Successfully removed '{sanitized_model_tag}'.")
            
        except subprocess.CalledProcessError as e:
            raise ModelManagerError(f"Failed to remove model '{sanitized_model_tag}': {e.stderr or e}")
        except Exception as e:
            raise ModelManagerError(f"Unexpected error removing model: {e}")

    def sync_models(self) -> Dict[str, int]:
        """
        Syncs Ollama models with the local manifest.
        Adds any models found in Ollama that aren't in the manifest.
        
        Returns:
            Dict with 'added', 'removed', 'total' counts.
        """
        self._ensure_ollama_available()
        
        try:
            # Get models from Ollama
            ollama_models = set()
            result = subprocess.run(
                [self.ollama_cmd, "list"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 1:
                        ollama_models.add(parts[0])
            
            # Get models from manifest
            try:
                models_data = self.models_config_manager.to_dict()
            except ConfigError:
                models_data = {}
            
            manifest_models = set(models_data.keys())
            
            # Find models to add (in Ollama but not in manifest)
            to_add = ollama_models - manifest_models
            
            # Find models to remove (in manifest but not in Ollama)
            to_remove = manifest_models - ollama_models
            
            added = 0
            removed = 0
            
            # Add missing models to manifest
            for model_tag in to_add:
                try:
                    # Get model info from Ollama
                    info_result = subprocess.run(
                        [self.ollama_cmd, "show", model_tag, "--modelfile"],
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=5
                    )
                    
                    # Try to get size info
                    size_bytes = 0
                    for line in lines[1:]:
                        if line.startswith(model_tag):
                            parts = line.split()
                            if len(parts) >= 2:
                                size_str = ' '.join(parts[1:3])
                                try:
                                    if 'GB' in size_str:
                                        size_bytes = int(float(size_str.split()[0]) * 1e9)
                                    elif 'MB' in size_str:
                                        size_bytes = int(float(size_str.split()[0]) * 1e6)
                                except:
                                    pass
                            break
                    
                    models_data[model_tag] = {
                        "tag": model_tag,
                        "backend": "ollama",
                        "download_date": datetime.now().isoformat(timespec='seconds'),
                        "family": "unknown",
                        "size_gb": round(size_bytes / (1024**3), 2) if size_bytes else 0,
                        "details": {
                            "format": "unknown",
                            "quantization": "unknown"
                        },
                        "synced": True
                    }
                    added += 1
                    print(f"✅ Added '{model_tag}' to manifest")
                    
                except Exception as e:
                    print(f"⚠️  Failed to sync '{model_tag}': {e}")
            
            # Remove models that no longer exist in Ollama
            for model_tag in to_remove:
                del models_data[model_tag]
                removed += 1
                print(f"🗑️  Removed '{model_tag}' from manifest (no longer in Ollama)")
            
            # Update manifest if changes were made
            if added > 0 or removed > 0:
                self.models_config_manager.update(models_data)
                print(f"📋 Synced: +{added} added, -{removed} removed, {len(ollama_models)} total")
            
            return {
                'added': added,
                'removed': removed,
                'total': len(ollama_models)
            }
            
        except subprocess.TimeoutExpired:
            raise ModelManagerError("Ollama sync timed out. Is Ollama running?")
        except subprocess.CalledProcessError as e:
            raise ModelManagerError(f"Failed to sync models: {e.stderr or e}")
        except Exception as e:
            raise ModelManagerError(f"Unexpected error syncing models: {e}")

# Usage Examples:
#
# 1. Initialize and list models:
#    # mm = ModelManager(os.getenv("PROJECT_ROOT", "/path/to/novaforge"))
#    # try:
#    #    available_models = mm.list_local_models()
#    #    print(f"Available models: {available_models}")
#    # except ModelManagerError as e:
#    #    print(f"Error: {e}")
#
# 2. Download a model:
#    # try:
#    #    mm.download_model("mistral:7b")
#    # except ModelManagerError as e:
#    #    print(f"Error downloading model: {e}")
