#!/usr/bin/env python3
"""
Simple HTTP API server for browser access.
Provides chat and model management endpoints.
"""
import json
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.project_manager import ProjectManager
from core.runtime.manager import ModelRuntimeManager
from core.model_manager import ModelManager
from core.reasoning import (
    get_context, get_reasoning, get_verifier,
    init_reasoning_layer
)
from core.logging_system import LoggingSystem
from core.memory_system import AdvancedMemory
from core.resource_monitor import get_monitor, get_controller
from core.comprehensive_status import status_monitor as comprehensive_monitor
from core.tool_executor import ToolExecutor
from scripts.smart_parser import parse_tool_declarations, remove_tool_declarations
from core.ai_protocol import get_system_prompt
from tools import generate_tools_description

# Initialize logging and memory
logging_system = LoggingSystem()
memory_system = AdvancedMemory()

# Initialize resource monitoring
resource_monitor = get_monitor()
performance_controller = get_controller()

# Initialize driver ONCE at startup (not on every request)
_cached_driver = None
_cached_pm = None

def get_cached_driver():
    """Get or create cached driver instance"""
    global _cached_driver, _cached_pm
    if _cached_driver is None:
        try:
            _cached_pm = ProjectManager(str(PROJECT_ROOT))
            project_config = _cached_pm.get_active_project_config()
            runtime_mgr = ModelRuntimeManager(str(PROJECT_ROOT))
            _cached_driver = runtime_mgr.get_driver(project_config)
        except Exception as e:
            print(f"⚠️ Failed to initialize driver: {e}")
    return _cached_driver, _cached_pm

class APIHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path == '/api/models':
            self.handle_list_models()
        elif path == '/api/project/config':
            self.handle_get_project_config()
        elif path == '/api/resources/stats':
            self.handle_get_resources()
        elif path == '/api/resources/settings':
            self.handle_get_settings()
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        
        if path == '/api/chat':
            self.handle_chat()
        elif path == '/api/models/sync':
            self.handle_sync_models()
        elif path == '/api/models/download':
            self.handle_download_model()
        elif path == '/api/models/remove':
            self.handle_remove_model()
        elif path == '/api/models/select':
            self.handle_select_model()
        elif path == '/api/commander/parse':
            self.handle_commander_parse()
        elif path == '/api/commander/execute':
            self.handle_commander_execute()
        elif path == '/api/sessions/start':
            self.handle_start_session()
        elif path == '/api/sessions/save':
            self.handle_save_session()
        elif path == '/api/sessions/list':
            self.handle_list_sessions()
        elif path == '/api/sessions/load':
            self.handle_load_session()
        elif path == '/api/sessions/export':
            self.handle_export_session()
        elif path == '/api/resources/switch':
            self.handle_switch_device()
        elif path == '/api/resources/configure':
            self.handle_configure_resources()
        else:
            self.send_error(404)
    
    def handle_list_models(self):
        """List all models"""
        try:
            mm = ModelManager(str(PROJECT_ROOT))
            models = mm.list_downloaded_models()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(models).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_get_project_config(self):
        """Get current project config"""
        try:
            pm = ProjectManager(str(PROJECT_ROOT))
            config = pm.get_active_project_config()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Config is a dict
            config_dict = {
                'project_name': config.get('project_name', 'default'),
                'active_model_tag': config.get('active_model_tag', 'No model selected'),
                'active_model': config.get('active_model_tag', 'No model selected'),  # Alias
                'system_prompt': config.get('system_prompt', '')
            }
            
            self.wfile.write(json.dumps(config_dict).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_sync_models(self):
        """Sync models with Ollama"""
        try:
            mm = ModelManager(str(PROJECT_ROOT))
            result = mm.sync_models()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_download_model(self):
        """Download a model"""
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            model_name = data.get('model_name', '')
            if not model_name:
                self.send_json_error("No model_name provided")
                return
            
            mm = ModelManager(str(PROJECT_ROOT))
            result = mm.download_model(model_name)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_remove_model(self):
        """Remove a model"""
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            model_tag = data.get('model_tag', '')
            if not model_tag:
                self.send_json_error("No model_tag provided")
                return
            
            mm = ModelManager(str(PROJECT_ROOT))
            result = mm.remove_model(model_tag)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_select_model(self):
        """Select/activate a model"""
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            model_tag = data.get('model_tag', '')
            if not model_tag:
                self.send_json_error("No model_tag provided")
                return
            
            # Update project config with selected model
            pm = ProjectManager(str(PROJECT_ROOT))
            
            # Use the set_active_model_for_project method
            success = pm.set_active_model_for_project(model_tag)
            
            if not success:
                self.send_json_error("Failed to set active model")
                return
            
            # CRITICAL: Clear driver cache to force reload with new model
            global _cached_driver, _cached_pm
            _cached_driver = None
            _cached_pm = None
            print(f"🔄 Model switched to: {model_tag}")
            print(f"   Driver cache cleared - will reload on next chat")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({'success': True, 'model': model_tag}).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_chat(self):
        """
        Handle chat requests with intelligent tool execution
        Supports normal, web, and commander modes
        """
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            message = data.get('message', '')
            history = data.get('history', [])
            web_mode = data.get('web_search_mode', False)
            commander_mode = data.get('commander_mode', False)
            
            if not message:
                self.send_error(400, "No message provided")
                return
            
            # Determine mode
            if web_mode:
                mode = "web"
            elif commander_mode:
                mode = "commander"
            else:
                mode = "normal"
            
            print(f"💬 Chat [{mode}]: {message[:50]}...")
            
            # Get driver
            driver, pm = get_cached_driver()
            if not driver:
                self.send_error(500, "Driver not initialized")
                return
            
            # Create tool executor for this request
            tool_executor = ToolExecutor(
                commander_mode=commander_mode,
                web_search_mode=web_mode
            )
            
            # Generate tools description for system prompt
            tools_desc = generate_tools_description(
                commander_mode=commander_mode,
                web_search_mode=web_mode
            )
            
            # Get system prompt with tools
            system_prompt = get_system_prompt(
                commander_mode=commander_mode,
                web_search_mode=web_mode,
                tools_description=tools_desc
            )
            
            # Build chat history with system prompt
            chat_history = [{"role": "system", "content": system_prompt}]
            chat_history.extend(history)
            chat_history.append({"role": "user", "content": message})
            
            # Start streaming response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            
            # Send mode indicator
            mode_indicator = ""
            if commander_mode:
                mode_indicator = "⚡ **Commander Mode Active**\n\n"
            elif web_mode:
                mode_indicator = "🌐 **Web Search Mode Active**\n\n"
            
            if mode_indicator:
                chunk = json.dumps({"type": "token", "token": mode_indicator}) + "\n"
                self.wfile.write(chunk.encode())
                self.wfile.flush()
            
            # Phase 1: Get AI response (may contain tool declarations)
            ai_response = ""
            for token in driver.generate(chat_history, stream=True):
                ai_response += token
                # Stream tokens to user in real-time
                chunk = json.dumps({"type": "token", "token": token}) + "\n"
                try:
                    self.wfile.write(chunk.encode())
                    self.wfile.flush()
                except BrokenPipeError:
                    break
            
            # Phase 2: Check for tool declarations
            tool_declarations = parse_tool_declarations(ai_response)
            
            if tool_declarations:
                print(f"🛠️ AI requested {len(tool_declarations)} tools")
                
                # Execute tools
                tool_results = tool_executor.execute_tools(tool_declarations)
                
                # Format results for user
                user_results = tool_executor.format_for_user(tool_results)
                if user_results:
                    result_chunk = json.dumps({"type": "token", "token": f"\n{user_results}\n"}) + "\n"
                    try:
                        self.wfile.write(result_chunk.encode())
                        self.wfile.flush()
                    except BrokenPipeError:
                        pass
                
                # Phase 3: Give AI the tool results for final response
                ai_results = tool_executor.format_results(tool_results)
                clean_ai_response = remove_tool_declarations(ai_response)
                
                # Add tool results to history and ask AI to provide final answer
                follow_up = f"""Previous AI response: {clean_ai_response}

{ai_results}

Now provide a natural, helpful response based on the tool results above. Be concise and informative."""
                
                chat_history.append({"role": "assistant", "content": ai_response})
                chat_history.append({"role": "user", "content": follow_up})
                
                # Get final response from AI
                final_intro = "\n💭 "
                final_chunk = json.dumps({"type": "token", "token": final_intro}) + "\n"
                try:
                    self.wfile.write(final_chunk.encode())
                    self.wfile.flush()
                except BrokenPipeError:
                    pass
                
                for token in driver.generate(chat_history, stream=True):
                    chunk = json.dumps({"type": "token", "token": token}) + "\n"
                    try:
                        self.wfile.write(chunk.encode())
                        self.wfile.flush()
                    except BrokenPipeError:
                        break
            
            # Send done signal
            done_chunk = json.dumps({"type": "done"}) + "\n"
            try:
                self.wfile.write(done_chunk.encode())
                self.wfile.flush()
            except BrokenPipeError:
                pass
            
            print(f"✅ Chat complete")
            
        except Exception as e:
            print(f"❌ Chat error: {e}")
            import traceback
            traceback.print_exc()
            error_chunk = json.dumps({"type": "error", "message": str(e)}) + "\n"
            try:
                self.wfile.write(error_chunk.encode())
                self.wfile.flush()
            except:
                pass
    
    def handle_commander_parse(self):
        """Parse natural language command (preview mode)"""
        try:
            content_length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(content_length))
            
            user_input = body.get('prompt', '')
            
            # Import Commander
            commander_path = PROJECT_ROOT / 'scripts' / 'commander.py'
            import subprocess
            
            # Run in preview mode (don't execute)
            result = subprocess.run(
                [sys.executable, str(commander_path), user_input, '--preview'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
            else:
                response = {"success": False, "error": result.stderr}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_commander_execute(self):
        """Execute natural language command"""
        try:
            content_length = int(self.headers['Content-Length'])
            body = json.loads(self.rfile.read(content_length))
            
            user_input = body.get('prompt', '')
            
            # Import Commander
            commander_path = PROJECT_ROOT / 'scripts' / 'commander.py'
            import subprocess
            
            # Execute command
            result = subprocess.run(
                [sys.executable, str(commander_path), user_input],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
            else:
                response = {"success": False, "error": result.stderr}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def send_json_error(self, message):
        """Send JSON error response"""
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())
    
    def handle_start_session(self):
        """Start a new chat session"""
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            user_name = data.get('user_name', 'User')
            metadata = data.get('metadata', {})
            
            session_id = logging_system.start_session(user_name, metadata)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({
                'session_id': session_id,
                'started_at': logging_system.current_session['started_at']
            }).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_save_session(self):
        """Save current session"""
        try:
            logging_system.save_session()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({'success': True}).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_list_sessions(self):
        """List all saved sessions"""
        try:
            sessions_dir = logging_system.base_path / "sessions"
            sessions = []
            
            if sessions_dir.exists():
                for month_dir in sorted(sessions_dir.iterdir(), reverse=True):
                    if month_dir.is_dir():
                        for session_file in sorted(month_dir.glob("*.json"), reverse=True):
                            try:
                                import json
                                session_data = json.loads(session_file.read_text())
                                sessions.append({
                                    'session_id': session_data['session_id'],
                                    'started_at': session_data['started_at'],
                                    'user_name': session_data.get('user_name', 'Unknown'),
                                    'message_count': len(session_data.get('messages', [])),
                                    'file_path': str(session_file)
                                })
                            except:
                                continue
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({'sessions': sessions[:50]}).encode())  # Limit to 50
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_load_session(self):
        """Load a specific session"""
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            session_id = data.get('session_id')
            if not session_id:
                self.send_json_error("No session_id provided")
                return
            
            # Find session file
            sessions_dir = logging_system.base_path / "sessions"
            session_file = None
            
            for month_dir in sessions_dir.iterdir():
                if month_dir.is_dir():
                    potential_file = month_dir / f"{session_id}.json"
                    if potential_file.exists():
                        session_file = potential_file
                        break
            
            if not session_file:
                self.send_json_error("Session not found")
                return
            
            session_data = json.loads(session_file.read_text())
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(session_data).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_export_session(self):
        """Export session for training"""
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            export_format = data.get('format', 'jsonl')
            session_id = data.get('session_id')
            
            if session_id:
                # Export specific session
                result = logging_system.export_session(session_id, export_format)
            else:
                # Export all
                result = logging_system.export_for_training(export_format)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({
                'success': True,
                'export_path': result
            }).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_get_resources(self):
        """Get current resource usage with comprehensive monitoring"""
        try:
            # Use comprehensive monitor for detailed stats
            stats = comprehensive_monitor.get_all_status()
            
            # Format for dashboard compatibility
            formatted_stats = {
                "cpu": stats["hardware"]["cpu"],
                "gpu": stats["hardware"]["gpu"],
                "memory": stats["hardware"]["memory"],
                "disk": stats["hardware"]["storage"],
                "system": stats["system"],
                "processes": stats["processes"],
                "uptime": stats["uptime"],
                "network": stats["network"],
                "health": stats["health"]
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(formatted_stats).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_get_settings(self):
        """Get current performance settings including usage limits"""
        try:
            # Get base settings from performance controller
            settings = performance_controller.get_current_settings()
            
            # Get driver settings if available (use cached driver)
            try:
                driver, pm = get_cached_driver()
                if driver and hasattr(driver, 'get_settings'):
                    driver_settings = driver.get_settings()
                    settings.update(driver_settings)
            except:
                pass
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(settings).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_switch_device(self):
        """Switch between CPU and GPU"""
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            device = data.get('device', 'cpu')
            print(f"🔄 Switching to {device.upper()}...")
            
            result = performance_controller.switch_device(device)
            
            # Clear cached driver to force reload with new device
            global _cached_driver, _cached_pm
            _cached_driver = None
            _cached_pm = None
            print(f"   Cleared driver cache - will reload with {device.upper()} on next request")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_configure_resources(self):
        """Configure resource settings"""
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            print(f"🔧 Configuring resources: {data}")
            
            results = {'success': True, 'updated': {}}
            
            # Performance controls
            if 'context_size' in data:
                performance_controller.context_size = int(data['context_size'])
                results['updated']['context_size'] = data['context_size']
                print(f"   Context size: {data['context_size']}")
                # Clear driver cache to apply new settings
                global _cached_driver, _cached_pm
                _cached_driver = None
                _cached_pm = None
            
            if 'max_tokens' in data:
                performance_controller.max_tokens = int(data['max_tokens'])
                results['updated']['max_tokens'] = data['max_tokens']
                print(f"   Max tokens: {data['max_tokens']}")
                # Clear driver cache
                _cached_driver = None
                _cached_pm = None
            
            if 'cpu_threads' in data:
                result = performance_controller.set_cpu_threads(data['cpu_threads'])
                results['updated']['cpu_threads'] = result
            
            if 'memory_limit' in data:
                result = performance_controller.set_memory_limit(data['memory_limit'])
                results['updated']['memory_limit'] = result
            
            if 'gpu_usage_percent' in data:
                performance_controller.max_gpu_usage_percent = data['gpu_usage_percent']
                results['updated']['gpu_usage_percent'] = data['gpu_usage_percent']
                print(f"   GPU usage limit: {data['gpu_usage_percent']}%")
            
            if 'cpu_usage_percent' in data:
                performance_controller.max_cpu_usage_percent = data['cpu_usage_percent']
                results['updated']['cpu_usage_percent'] = data['cpu_usage_percent']
                print(f"   CPU usage limit: {data['cpu_usage_percent']}%")
            
            if 'usage_limiter_enabled' in data:
                performance_controller.usage_limiter_enabled = data['usage_limiter_enabled']
                results['updated']['usage_limiter_enabled'] = data['usage_limiter_enabled']
                print(f"   Usage limiter: {'ON' if data['usage_limiter_enabled'] else 'OFF'}")
            
            if 'safety_buffer_enabled' in data:
                performance_controller.safety_buffer_enabled = data['safety_buffer_enabled']
                results['updated']['safety_buffer_enabled'] = data['safety_buffer_enabled']
                print(f"   Safety buffer: {'ON' if data['safety_buffer_enabled'] else 'OFF'}")
            
            # SAVE TO DISK - Persist settings
            self._save_settings_to_disk()
            print("💾 Settings saved to disk")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(results).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def _save_settings_to_disk(self):
        """Save performance settings to project config"""
        try:
            project_config_path = PROJECT_ROOT / "projects" / "default" / "project.json"
            
            # Read current config
            if project_config_path.exists():
                with open(project_config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Update performance settings
            config['num_threads'] = performance_controller.cpu_threads
            config['memory_limit_gb'] = performance_controller.max_memory_gb
            config['context_size'] = performance_controller.context_size
            config['max_tokens'] = performance_controller.max_tokens
            config['gpu_usage_percent'] = performance_controller.max_gpu_usage_percent
            config['cpu_usage_percent'] = performance_controller.max_cpu_usage_percent
            config['usage_limiter_enabled'] = performance_controller.usage_limiter_enabled
            config['safety_buffer_enabled'] = performance_controller.safety_buffer_enabled
            
            # Write back to disk
            with open(project_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"   Saved to: {project_config_path}")
            
        except Exception as e:
            print(f"   ⚠️  Failed to save to disk: {e}")
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[API] {format % args}")

def start_server(port=5174):
    """Start the API server"""
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"🚀 API Server running on http://0.0.0.0:{port}")
    print(f"📡 Accessible from Windows at: http://localhost:{port}")
    print(f"📡 Endpoints:")
    print(f"   POST /api/chat - Chat with AI")
    print(f"   GET  /api/models - List models")
    print(f"   POST /api/models/sync - Sync models")
    print(f"   POST /api/models/download - Download model")
    print(f"   POST /api/models/remove - Remove model")
    print(f"   POST /api/commander/parse - Parse command (preview)")
    print(f"   POST /api/commander/execute - Execute command")
    print(f"   POST /api/sessions/start - Start new session")
    print(f"   POST /api/sessions/save - Save current session")
    print(f"   POST /api/sessions/list - List all sessions")
    print(f"   POST /api/sessions/load - Load specific session")
    print(f"   POST /api/sessions/export - Export for training")
    print(f"   GET  /api/resources/stats - Get resource usage")
    print(f"   GET  /api/resources/settings - Get performance settings")
    print(f"   POST /api/resources/switch - Switch CPU/GPU")
    print(f"   POST /api/resources/configure - Configure resources")
    print(f"\n💾 Session Storage: memory/sessions/")
    print(f"🧠 Memory System: Active")
    print(f"📊 Training Data: memory/training_data/")
    print(f"🎛️ Resource Monitoring: Active")
    server.serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5174
    start_server(port)
