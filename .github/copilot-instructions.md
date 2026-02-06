# Copilot Instructions for `ai-forge`

## Build, Run, and Test
- `./setup.sh` — recreates `venv/`, installs `core/requirements.txt`, and initializes `config/`, `projects/default/`, and `models/models.json` while logging to `logs/setup.log`.
- `source venv/bin/activate` before invoking any Python entry point; the launcher scripts assume the virtualenv is active.
- `./forge.sh` — activates the venv (running `setup.sh` if missing) and launches the interactive menu in `scripts/menu_main.sh`.
- `python3 core/chat.py "$(pwd)"` — starts the text chat directly for the current project root; ensure `ollama serve` is running or set `OLLAMA_HOST`.
- `pytest` — runs the full suite defined by `pytest.ini` (defaults to `tests/` with `-ra -q --strict-markers`).
- `pytest tests/test_config.py::test_set_value` (or `pytest tests -k "runtime"`) — runs a focused test or selection when iterating on a single module.

## High-Level Architecture
1. **Shell orchestrators (`setup.sh`, `forge.sh`, `scripts/menu_main.sh`)**  
   - `setup.sh` enforces prerequisites (python3.11+, git, wget), rebuilds the virtualenv, installs `core/requirements.txt`, and bootstraps JSON configs.  
   - `forge.sh` ensures the venv exists, activates it, and forwards control (and `PROJECT_ROOT`) to `scripts/menu_main.sh`, which provides a TUI via `dialog`/stdin and dispatches to Python helpers with `python3 -c` or module entry points.
2. **Configuration & data stores (`config/`, `projects/`, `models/`, `memory/`)**  
   - All JSON mutation flows through `core/config.py`’s `ConfigManager`, which adds `.lock` files via `filelock` to guard concurrent shell/Python access.  
   - Global preferences live in `config/settings.json`; per-project state lives under `projects/<name>/project.json`; the available-model manifest sits in `models/models.json`. Directories under `memory/`, `training/`, `tools/`, and `voice/` are reserved for future vector stores, datasets, automation tools, and STT/TTS assets respectively.
3. **Core services (`core/`)**  
   - `project_manager.py` sanitizes project names, provisions project folders, and updates `config/settings.json` with the active project.  
   - `model_manager.py` validates Ollama tags, shells out to `ollama pull/show`, and records metadata (size, quantization, etc.) back into `models/models.json`.  
   - `chat.py` builds the REPL via `prompt_toolkit`, pulling project context and the active model before streaming responses to the terminal.
4. **Runtime abstraction (`core/runtime/`)**  
   - `ModelRuntimeManager` caches driver instances keyed by `active_model_tag` and returns a `ModelDriver` implementation.  
   - `ollama_driver.py` is the only current driver; it talks to the local Ollama HTTP API (`OLLAMA_HOST`, `OLLAMA_CMD` configurable), streams tokens, and exposes `is_running()` for menu diagnostics. Extend this package with new drivers (e.g., llama.cpp) and branch in `ModelRuntimeManager.get_driver`.
5. **Testing layout (`tests/`)**  
   - Test modules mirror the core modules (config, project_manager, model_manager, runtime_manager, ollama_driver, chat) and share fixtures from `tests/conftest.py`, which fabricates a disposable project root and sets `PROJECT_ROOT`.  
   - When adding tests, lean on these fixtures instead of touching real data under `projects/` or `models/`.

## Key Conventions & Patterns
- **Use `ConfigManager` for JSON I/O**: it enforces `Path` inputs, writes via `json.dump(indent=2, ensure_ascii=False)`, and locks files (`*.lock`). Touching JSON files directly can deadlock menu operations and tests.
- **Custom exception per domain**: every module defines `<Domain>Error` (e.g., `ConfigError`, `ProjectError`, `ModelManagerError`, `LLMRuntimeError`). Propagate these upward so the shell menu can surface concise ❌ messages without stack traces.
- **Sanitize user input before touching disk**: project names must remain alphanumeric/hyphen/underscore (reuse `_validate_project_name`), and model tags must include a colon (reuse `_validate_model_tag`). Follow this pattern when adding new resources.
- **Pass `PROJECT_ROOT` explicitly**: shell scripts invoke Python helpers with the project root argument; new commands should follow the same pattern so modules resolve paths via `pathlib`.
- **Ollama integration defaults**: code assumes a locally running `ollama serve` on `http://localhost:11434`, but respects `OLLAMA_HOST`/`OLLAMA_CMD`. Document or surface these environment variables when wiring new runtime features.
- **Menu extensions**: add new capabilities by appending options in `scripts/menu_main.sh`, then dispatch to either another shell function or a Python module. Keep prompts non-blocking and fall back gracefully when `dialog` is absent.
- **Virtualenv lifecycle**: running `setup.sh` always nukes and recreates `venv/`. Update `core/requirements.txt` instead of installing ad hoc packages, then re-run setup so CI/dev machines stay aligned.
- **Testing discipline**: tests rely on fixtures that keep everything inside `tmp_path`; when writing new tests, import the fixture instead of pointing at the real workspace. Use `pytest -k "<keyword>"` for iterative runs to match existing workflow.

