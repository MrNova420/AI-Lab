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
                'active_model': config.get('active_model_tag', 'No model selected'),
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
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({'success': True, 'model': model_tag}).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
    def handle_chat(self):
        """Handle chat requests"""
        
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            message = data.get('message', '')
            history = data.get('history', [])
            commander_mode = data.get('commander_mode', False)
            web_search_mode = data.get('web_search_mode', False)
            
            print(f"[API] Chat - Commander: {commander_mode}, Web Search: {web_search_mode}")
            
            if not message:
                self.send_error(400, "No message provided")
                return
            
            # Initialize managers
            pm = ProjectManager(str(PROJECT_ROOT))
            project_config = pm.get_active_project_config()
            
            runtime_mgr = ModelRuntimeManager(str(PROJECT_ROOT))
            driver = runtime_mgr.get_driver(project_config)
            
            # If commander mode, add system prompt with tools
            if commander_mode or web_search_mode:
                import importlib.util
                
                # Build system prompt with AI-aware tools
                from tools import generate_tools_description  
                from core.ai_protocol import get_system_prompt
                
                tools_desc = generate_tools_description(commander_mode=commander_mode,
                                                       web_search_mode=web_search_mode)
                
                system_msg = get_system_prompt(commander_mode=commander_mode,
                                              web_search_mode=web_search_mode,
                                              tools_description=tools_desc)
                
                # Inject system prompt into history
                if not history or history[0].get('role') != 'system':
                    history.insert(0, {"role": "system", "content": system_msg})
                else:
                    history[0] = {"role": "system", "content": system_msg}
                
                # Load commander for tool execution
                commander_path = PROJECT_ROOT / 'scripts' / 'commander.py'
                spec2 = importlib.util.spec_from_file_location("commander", commander_path)
                commander_module = importlib.util.module_from_spec(spec2)
                spec2.loader.exec_module(commander_module)
                Commander = commander_module.Commander
                
                # Load tool execution
                commander_chat_path = PROJECT_ROOT / 'scripts' / 'ai_commander_chat.py'
                spec = importlib.util.spec_from_file_location("ai_commander_chat", commander_chat_path)
                ai_commander_chat = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(ai_commander_chat)
                execute_tool_calls = ai_commander_chat.execute_tool_calls
            else:
                # Normal mode - no tools
                from core.ai_protocol import get_system_prompt
                system_msg = get_system_prompt(commander_mode=False, web_search_mode=False, tools_description="")
                if not history or history[0].get('role') != 'system':
                    history.insert(0, {"role": "system", "content": system_msg})
                else:
                    history[0]['content'] = system_msg
            
            # Add user message to history
            history.append({"role": "user", "content": message})
            
            # Send response headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            # Stream response
            full_response = ""
            for token in driver.generate(history, stream=True):
                full_response += token
                chunk = json.dumps({"type": "token", "token": token}) + "\n"
                self.wfile.write(chunk.encode())
                self.wfile.flush()
            
            # If commander/web mode enabled, parse AI's tool declarations
            if commander_mode or web_search_mode:
                # Use smart parser - AI decides which tools to use
                from scripts.smart_parser import parse_tool_declarations, remove_tool_declarations
                
                tool_calls = parse_tool_declarations(full_response)
                
                if tool_calls:
                    # Execute tools
                    if 'commander' not in locals():
                        commander = Commander()
                    
                    results = execute_tool_calls(tool_calls, commander)
                    print(f"✅ Executed {len(results)} tools")
                    
                    # Format results
                    formatted = "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🛠️ Actions Taken:\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    for r in results:
                        icon = "✅" if r['result'].get('success') else "❌"
                        tool_name = r['tool']
                        msg = r['result'].get('message', 'Done')
                        formatted += f"{icon} {tool_name}: {msg}\n"
                    formatted += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    
                    # Send tool results
                    tool_msg = json.dumps({
                        "type": "tool_results", 
                        "results": results,
                        "formatted": formatted
                    }) + "\n"
                    self.wfile.write(tool_msg.encode())
                    self.wfile.flush()
                    
                    # IMPORTANT: Remove <TOOLS> tags from response
                    clean_response = remove_tool_declarations(full_response)
                    
                    # Give AI a chance to see tool results and update its answer
                    # Build context: original response + tool results
                    tool_results_text = "\n\nTOOL RESULTS:\n"
                    for r in results:
                        tool_results_text += f"- {r['tool']}: {r['result'].get('message', str(r['result']))}\n"
                    
                    # Ask AI to provide final answer with tool results
                    followup = f"Based on the tool results above, provide your final answer to the user. Be concise and accurate."
                    history.append({"role": "assistant", "content": clean_response + tool_results_text})
                    history.append({"role": "user", "content": followup})
                    
                    # Get updated response
                    final_response = ""
                    for token in driver.generate(history, stream=True):
                        final_response += token
                        chunk = json.dumps({"type": "token", "token": token}) + "\n"
                        self.wfile.write(chunk.encode())
                        self.wfile.flush()
                    
                    # Append formatted results to final response
                    full_response = final_response + formatted
                else:
                    # No tools - just clean the response
                    full_response = remove_tool_declarations(full_response)
            
            # Send done message
            done = json.dumps({"type": "done", "full_response": full_response}) + "\n"
            
            self.wfile.write(done.encode())
            self.wfile.flush()
            
        except Exception as e:
            error_msg = json.dumps({"type": "error", "message": str(e)}) + "\n"
            self.wfile.write(error_msg.encode())
            self.wfile.flush()
    
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
    server.serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5174
    start_server(port)
