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
            
            if not message:
                self.send_error(400, "No message provided")
                return
            
            print(f"💬 Chat: {message[:50]}...")
            
            # USE CACHED DRIVER - DON'T RELOAD EVERY TIME
            driver, pm = get_cached_driver()
            
            if not driver:
                self.send_error(500, "Driver not initialized")
                return
            
            # Simple generate - no extra processing
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Transfer-Encoding', 'chunked')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            full_response = ""
            
            # Stream tokens directly from driver
            for token in driver.generate(message, history, stream=True):
                full_response += token
                
                # Send token as JSON line
                chunk = json.dumps({"type": "token", "token": token}) + "\n"
                self.wfile.write(chunk.encode())
                self.wfile.flush()
            
            # Send done
            done_chunk = json.dumps({"type": "done", "full_response": full_response}) + "\n"
            self.wfile.write(done_chunk.encode())
            self.wfile.flush()
            
            print(f"✅ Chat complete ({len(full_response)} chars)")
            
        except Exception as e:
            print(f"❌ Chat error: {e}")
            error_chunk = json.dumps({"type": "error", "message": str(e)}) + "\n"
            try:
                self.wfile.write(error_chunk.encode())
                self.wfile.flush()
            except:
                pass
            
            # If commander mode, add system prompt with tools + context
            if commander_mode or web_search_mode:
                import importlib.util
                
                # Build system prompt with AI-aware tools
                from tools import generate_tools_description  
                from core.ai_protocol import get_system_prompt
                
                tools_desc = generate_tools_description(commander_mode=commander_mode,
                                                       web_search_mode=web_search_mode)
                
                # Add context summary to help AI
                context_summary = context_mem.get_context_summary(detailed=False)
                if context_summary != "No context yet":
                    tools_desc += f"\n\n**🧠 Current Session Context:**\n{context_summary}\n"
                
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
            
            # Log user message to session
            logging_system.log_message(
                role="user",
                content=message,
                metadata={
                    "commander_mode": commander_mode,
                    "web_search_mode": web_search_mode
                }
            )
            
            # Store in memory system (use correct method)
            memory_system.short_term.store(f"user_msg_{len(memory_system.short_term.memory)}", message)
            
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
                from tools import TOOLS
                
                tool_calls = parse_tool_declarations(full_response)
                
                if tool_calls:
                    print(f"🔧 Executing {len(tool_calls)} tools: {[t['tool'] for t in tool_calls]}")
                    
                    # Analyze intent and plan execution with reasoning engine
                    intent_analysis = reasoning.analyze_intent(message, full_response, tool_calls)
                    print(f"🧠 Intent: {intent_analysis['user_intent']}, "
                          f"Complexity: {intent_analysis['complexity']}, "
                          f"Confidence: {intent_analysis.get('confidence', 1.0):.2f}")
                    
                    if intent_analysis.get('reasoning_trace'):
                        for trace in intent_analysis['reasoning_trace']:
                            print(f"   {trace}")
                    
                    # Plan optimal execution
                    execution_plan = reasoning.plan_execution(tool_calls)
                    if execution_plan['can_optimize']:
                        print(f"⚡ Can optimize! Using {len([s for s in execution_plan['steps'] if s['action']=='use_cache'])} cached results")
                    
                    # Send reasoning info to UI
                    reasoning_msg = json.dumps({
                        "type": "reasoning",
                        "intent": intent_analysis['user_intent'],
                        "complexity": intent_analysis['complexity'],
                        "confidence": intent_analysis.get('confidence', 1.0),
                        "can_optimize": execution_plan['can_optimize'],
                        "cached_count": len([s for s in execution_plan['steps'] if s['action']=='use_cache']),
                        "trace": intent_analysis.get('reasoning_trace', [])
                    }) + "\n"
                    self.wfile.write(reasoning_msg.encode())
                    self.wfile.flush()
                    
                    # Check if ANY tool requires verification (hybrid approach)
                    needs_verification = False
                    for call in tool_calls:
                        tool_name = call['tool']
                        # Find tool in registry
                        for category, tools in TOOLS.items():
                            if tool_name in tools:
                                if tools[tool_name].get('requires_verification', False):
                                    needs_verification = True
                                    print(f"🧠 {tool_name} requires AI verification (complex tool)")
                                    break
                        if needs_verification:
                            break
                    
                    # Execute tools (use cache when possible)
                    if 'commander' not in locals():
                        commander = Commander()
                    
                    results = []
                    for i, step in enumerate(execution_plan['steps']):
                        if step['action'] == 'use_cache':
                            print(f"💾 Using cached result for: {step['tool']}")
                            results.append({
                                'tool': step['tool'],
                                'result': step['result'],
                                'cached': True,
                                'execution_time': 0
                            })
                        else:
                            import time
                            start_time = time.time()
                            
                            # Execute the tool
                            tool_result = execute_tool_calls([tool_calls[step['index']]], commander)
                            execution_time = time.time() - start_time
                            
                            if tool_result:
                                result_data = tool_result[0]
                                result_data['cached'] = False
                                result_data['execution_time'] = execution_time
                                results.append(result_data)
                                
                                # Record for learning
                                tool_name = result_data['tool']
                                success = result_data['result'].get('success', False)
                                reasoning.record_result(tool_name, success, execution_time)
                                
                                # Verify result
                                verification = verifier.verify_result(tool_name, result_data['result'])
                                if not verification['valid'] or verification['warnings']:
                                    print(f"⚠️ Verification: Confidence {verification['confidence']:.2f}")
                                    if verification['issues']:
                                        print(f"   Issues: {verification['issues']}")
                                    if verification['warnings']:
                                        print(f"   Warnings: {verification['warnings']}")
                                
                                # Store in context memory
                                context_mem.add_tool_result(
                                    tool_name, 
                                    tool_calls[step['index']].get('params', {}),
                                    result_data['result']
                                )
                    
                    print(f"✅ Tool execution complete: {len(results)} results")
                    
                    # Format results with cache indicators
                    formatted = "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🛠️ Actions Taken:\n━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    for r in results:
                        icon = "✅" if r['result'].get('success') else "❌"
                        tool_name = r['tool']
                        msg = r['result'].get('message', 'Done')
                        
                        # Add cache indicator
                        cache_indicator = " 💾" if r.get('cached', False) else ""
                        
                        # Add execution time for new executions
                        time_info = ""
                        if not r.get('cached', False) and r.get('execution_time', 0) > 0:
                            time_info = f" ({r['execution_time']:.2f}s)"
                        
                        formatted += f"{icon} {tool_name}{cache_indicator}{time_info}: {msg}\n"
                    formatted += "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    
                    # Send tool results
                    tool_msg = json.dumps({
                        "type": "tool_results", 
                        "results": results,
                        "formatted": formatted
                    }) + "\n"
                    self.wfile.write(tool_msg.encode())
                    self.wfile.flush()
                    
                    # HYBRID APPROACH: Only do second pass for complex tools
                    clean_response = remove_tool_declarations(full_response)
                    
                    if needs_verification:
                        print("🧠 SMART MODE: AI will see results and correct itself")
                        # Complex tool - AI needs to see and verify results
                        tool_results_text = "\n\nTOOL RESULTS:\n"
                        for r in results:
                            tool_results_text += f"- {r['tool']}: {r['result'].get('message', str(r['result']))}\n"
                        
                        # Ask AI to provide final answer with tool results
                        followup = "Based on the tool results above, provide your final accurate answer. Be concise."
                        history.append({"role": "assistant", "content": clean_response + tool_results_text})
                        history.append({"role": "user", "content": followup})
                        
                        # Get corrected response
                        final_response = ""
                        for token in driver.generate(history, stream=True):
                            final_response += token
                            chunk = json.dumps({"type": "token", "token": token}) + "\n"
                            self.wfile.write(chunk.encode())
                            self.wfile.flush()
                        
                        full_response = final_response + formatted
                    else:
                        print("⚡ FAST MODE: Simple tool, just appending results")
                        # Simple tool - just append results (fast!)
                        full_response = clean_response + formatted
                else:
                    # No tools - just clean the response
                    full_response = remove_tool_declarations(full_response)
            
            # Store conversation turn in context
            tool_calls = []  # Initialize for later use
            if commander_mode or web_search_mode:
                if 'tool_calls' in locals() and tool_calls:
                    tools_used = [t['tool'] for t in tool_calls]
                else:
                    tools_used = []
                context_mem.add_conversation_turn(message, full_response, tools_used)
                
                # Save session periodically
                context_mem.save_session(session_id)
            
            # Log AI response to session (saves immediately!)
            logging_system.log_message(
                role="assistant",
                content=full_response,
                metadata={
                    "commander_mode": commander_mode,
                    "web_search_mode": web_search_mode
                }
            )
            
            # Store in memory system (use correct method)
            memory_system.short_term.store(f"ai_msg_{len(memory_system.short_term.memory)}", full_response)
            
            # No need to check "every 10" - already saving immediately!
            
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
            
            if 'cpu_threads' in data:
                result = performance_controller.set_cpu_threads(data['cpu_threads'])
                results['updated']['cpu_threads'] = result
            
            if 'memory_limit' in data:
                result = performance_controller.set_memory_limit(data['memory_limit'])
                results['updated']['memory_limit'] = result
            
            if 'gpu_usage_percent' in data:
                performance_controller.max_gpu_usage_percent = data['gpu_usage_percent']
                results['updated']['gpu_usage_percent'] = data['gpu_usage_percent']
                print(f"   Set GPU usage limit: {data['gpu_usage_percent']}%")
            
            if 'cpu_usage_percent' in data:
                performance_controller.max_cpu_usage_percent = data['cpu_usage_percent']
                results['updated']['cpu_usage_percent'] = data['cpu_usage_percent']
                print(f"   Set CPU usage limit: {data['cpu_usage_percent']}%")
            
            if 'usage_limiter_enabled' in data:
                performance_controller.usage_limiter_enabled = data['usage_limiter_enabled']
                results['updated']['usage_limiter_enabled'] = data['usage_limiter_enabled']
                print(f"   Usage limiter: {'ON' if data['usage_limiter_enabled'] else 'OFF'}")
            
            if 'safety_buffer_enabled' in data:
                performance_controller.safety_buffer_enabled = data['safety_buffer_enabled']
                results['updated']['safety_buffer_enabled'] = data['safety_buffer_enabled']
                print(f"   Safety buffer: {'ON' if data['safety_buffer_enabled'] else 'OFF'}")
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(results).encode())
            
        except Exception as e:
            self.send_json_error(str(e))
    
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
