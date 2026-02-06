import os
import sys
from pathlib import Path
from typing import List, Dict
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter

# File: core/chat.py
# Description: Provides an interactive text-based chat interface with the active LLM.
# Author: Gemini CLI
# Created: 2026-02-06
# Last Modified: 2026-02-06
# Dependencies: prompt_toolkit, core.project_manager.ProjectManager, core.runtime.manager.ModelRuntimeManager
# Links: MASTER_PLAN.md, test_chat.py

from core.project_manager import ProjectManager, ProjectError
from core.runtime.manager import ModelRuntimeManager, LLMRuntimeError

class ChatError(Exception):
    """Custom exception for chat related errors."""
    pass

def start_chat(project_root: str):
    """
    Starts an interactive text-based chat session with the active LLM.

    Purpose: Provides the primary text interaction interface for users to
             converse with the configured AI model for their project.

    Args:
        project_root (str): The absolute path to the NovaForge project root directory.

    Complexity: O(C * L * M) where C is number of chat turns, L is average
                response length, M is model generation complexity.
    Performance: Heavily dependent on LLM response time and streaming.
    Security Notes: Chat history is sent to the local LLM. No external network
                    requests beyond the local Ollama service.
    """
    if not isinstance(project_root, str) or not Path(project_root).is_dir():
        raise ChatError("Invalid project_root provided.")

    pm = ProjectManager(project_root)
    mrm = ModelRuntimeManager(project_root)

    try:
        active_project_config = pm.get_active_project_config()
        active_project_name = active_project_config.get("project_name", "default")
        model_tag = active_project_config.get("active_model_tag")
        system_prompt = active_project_config.get("system_prompt")

        if not model_tag:
            print(f"❌ No active model configured for project '{active_project_name}'.")
            print("Please select a model using 'Manage Models' menu option.")
            return

        driver = mrm.get_driver(active_project_config)

        if not driver.is_running():
            print(f"❌ Ollama service is not running or model '{model_tag}' is unavailable.")
            print("Please ensure Ollama is running (e.g., 'ollama serve') and the model is downloaded.")
            return

        print(f"🚀 Starting chat with '{model_tag}' for project '{active_project_name}'.")
        print("Type '/exit' or '/quit' to end the chat.")
        print("-" * 50)
        print("Start typing to begin the conversation.")

        history: List[Dict[str, str]] = []
        if system_prompt:
            history.append({"role": "system", "content": system_prompt})

        chat_history_completer = WordCompleter(['/exit', '/quit'], ignore_case=True)
        prompt_history = InMemoryHistory()
        
        while True:
            try:
                user_input = prompt("\nYOU> ", completer=chat_history_completer, history=prompt_history).strip()

                if user_input.lower() in ["/exit", "/quit"]:
                    print("👋 Ending chat session.")
                    break
                if not user_input:
                    continue

                history.append({"role": "user", "content": user_input})
                print("AI> ", end="", flush=True) # Removed f prefix

                response_content = ""
                for token in driver.generate(history, stream=True):
                    response_content += token
                    print(token, end="", flush=True)
                print("") # Newline after response

                history.append({"role": "assistant", "content": response_content})

            except (ProjectError, LLMRuntimeError) as e:
                print(f"❌ Chat Error: {e}")
                break
            except EOFError: # Ctrl+D
                print("\n👋 Ending chat session.")
                break
            except KeyboardInterrupt: # Ctrl+C
                print("\n👋 Ending chat session.")
                break
            except Exception as e:
                print(f"❌ An unexpected error occurred during chat: {e}")
                break

    except (ProjectError, LLMRuntimeError) as e:
        print(f"❌ Initialization Error: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

# Entry point for the script
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 core/chat.py <PROJECT_ROOT>")
        sys.exit(1)
    
    # Ensure project_root is passed correctly
    project_root_arg = sys.argv[1]
    start_chat(project_root_arg)

# Usage Examples:
#
# 1. Start chat from main script (assuming venv activated and PROJECT_ROOT set):
#    # python3 core/chat.py "$(pwd)"
#
# 2. Within another Python script:
#    # import os
#    # from core.chat import start_chat
#    # start_chat(os.getenv("PROJECT_ROOT", "/path/to/novaforge"))
#
# 3. Handling errors (example, not direct usage):
#    # try:
#    #    start_chat("/non/existent/path")
#    # except ChatError as e:
#    #    print(f"Chat failed: {e}")
