#!/usr/bin/env python3
"""
Commander Mode - Full System Control via Natural Language
Allows AI to control mouse, keyboard, applications, windows, and more
Uses PowerShell bridge to control Windows from WSL
"""

import json
import sys
import time
import os
import subprocess
import platform
from datetime import datetime
from pathlib import Path

# Detect if running in WSL
IS_WSL = 'microsoft' in platform.uname().release.lower()

class Commander:
    def __init__(self):
        self.activity_log = []
        self.max_log_size = 1000
        self.blacklist = self.load_blacklist()
        self.ps_script_path = Path(__file__).parent / "windows_commander.ps1"
        
    def call_windows_powershell(self, command, args_dict=None):
        """Call PowerShell script on Windows from WSL"""
        try:
            # Convert WSL path to Windows path
            ps_script = str(self.ps_script_path).replace('/mnt/c/', 'C:\\').replace('/mnt/d/', 'D:\\').replace('/', '\\')
            
            # For other paths in WSL
            if ps_script.startswith('/home/'):
                # Use wslpath to convert
                result = subprocess.run(['wslpath', '-w', str(self.ps_script_path)], 
                                      capture_output=True, text=True)
                ps_script = result.stdout.strip()
            
            args_json = json.dumps(args_dict) if args_dict else '{}'
            
            # Call PowerShell from WSL
            cmd = [
                'powershell.exe',
                '-ExecutionPolicy', 'Bypass',
                '-File', ps_script,
                '-Command', command,
                '-Args', args_json
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            else:
                return {
                    "success": False,
                    "error": result.stderr or "PowerShell execution failed"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
        
    def load_blacklist(self):
        """Load blacklist configuration"""
        return {
            "processes": [
                "System", "Registry", "csrss.exe", "winlogon.exe", 
                "systemd", "init", "kernel"
            ],
            "paths": [
                "/etc", "/sys", "/proc", "/boot",
                "C:\\Windows\\System32", "C:\\Windows\\SysWOW64"
            ],
            "apps_keywords": [
                "system32", "registry", "regedit"
            ]
        }
    
    def log_activity(self, action_type, details, success=True):
        """Log all activities for audit trail"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "details": details,
            "success": success
        }
        self.activity_log.append(entry)
        
        # Keep log size manageable
        if len(self.activity_log) > self.max_log_size:
            self.activity_log = self.activity_log[-self.max_log_size:]
        
        # Also write to file
        log_file = Path(__file__).parent.parent / "logs" / "commander_activity.log"
        log_file.parent.mkdir(exist_ok=True)
        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def is_safe_app(self, app_name):
        """Check if app is safe to interact with"""
        app_lower = app_name.lower()
        for keyword in self.blacklist["apps_keywords"]:
            if keyword in app_lower:
                return False
        return True
    
    def is_safe_path(self, path):
        """Check if path is safe to modify"""
        path_str = str(path).lower()
        for blocked in self.blacklist["paths"]:
            if blocked.lower() in path_str:
                return False
        return True
    
    # ==================== MOUSE CONTROL ====================
    
    def mouse_move(self, x=None, y=None, duration=0.2):
        """Move mouse to coordinates"""
        try:
            if IS_WSL:
                # Call Windows PowerShell
                # Handle special values
                if x == "max" or x == "right":
                    x = 1920  # Default screen width
                elif x == "center":
                    x = 960
                elif x == "min" or x == "left":
                    x = 10
                    
                if y == "max" or y == "bottom":
                    y = 1080  # Default screen height
                elif y == "center":
                    y = 540
                elif y == "min" or y == "top":
                    y = 10
                
                result = self.call_windows_powershell('mouse_move', {'x': x, 'y': y})
                self.log_activity("mouse_move", {"x": x, "y": y}, result.get('success', False))
                return result
            else:
                # Native Linux/Mac with pyautogui (not implemented for now)
                return {"success": False, "error": "Native Linux control not implemented"}
        except Exception as e:
            self.log_activity("mouse_move", {"error": str(e)}, False)
            return {"success": False, "error": str(e)}
    
    def mouse_click(self, button="left", clicks=1, interval=0.1):
        """Click mouse button"""
        try:
            if IS_WSL:
                result = self.call_windows_powershell('mouse_click', {'button': button, 'clicks': clicks})
                self.log_activity("mouse_click", {"button": button, "clicks": clicks}, result.get('success', False))
                return result
            else:
                return {"success": False, "error": "Native Linux control not implemented"}
        except Exception as e:
            self.log_activity("mouse_click", {"error": str(e)}, False)
            return {"success": False, "error": str(e)}
    
    def mouse_scroll(self, amount, direction="vertical"):
        """Scroll mouse wheel"""
        try:
            # Not implemented in PowerShell yet, return placeholder
            return {"success": False, "error": "Scroll not yet implemented"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== KEYBOARD CONTROL ====================
    
    def keyboard_type(self, text, interval=0.05):
        """Type text"""
        try:
            if IS_WSL:
                result = self.call_windows_powershell('keyboard_type', {'text': text})
                self.log_activity("keyboard_type", {"text": text[:50]}, result.get('success', False))
                return result
            else:
                return {"success": False, "error": "Native Linux control not implemented"}
        except Exception as e:
            self.log_activity("keyboard_type", {"error": str(e)}, False)
            return {"success": False, "error": str(e)}
    
    def keyboard_press(self, key):
        """Press a key"""
        try:
            if IS_WSL:
                result = self.call_windows_powershell('keyboard_press', {'key': key})
                self.log_activity("keyboard_press", {"key": key}, result.get('success', False))
                return result
            else:
                return {"success": False, "error": "Native Linux control not implemented"}
        except Exception as e:
            self.log_activity("keyboard_press", {"error": str(e)}, False)
            return {"success": False, "error": str(e)}
    
    def keyboard_shortcut(self, keys):
        """Press keyboard shortcut (e.g., ['ctrl', 'c'])"""
        try:
            # Not fully implemented yet
            return {"success": False, "error": "Keyboard shortcuts not yet implemented"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== APPLICATION CONTROL ====================
    
    def open_app(self, app_name):
        """Open application"""
        try:
            if not self.is_safe_app(app_name):
                return {"success": False, "error": "Application is blacklisted for safety"}
            
            if IS_WSL:
                result = self.call_windows_powershell('open_app', {'app': app_name})
                self.log_activity("open_app", {"app": app_name}, result.get('success', False))
                return result
            else:
                return {"success": False, "error": "Native Linux control not implemented"}
            
        except Exception as e:
            self.log_activity("open_app", {"error": str(e)}, False)
            return {"success": False, "error": str(e)}
    
    def check_app_exists(self, app_name):
        """Check if application is installed on the system"""
        try:
            if IS_WSL:
                result = self.call_windows_powershell('check_app', {'app': app_name})
                print(f"🔍 Check app result: {result}")
                
                # Handle different response formats
                if isinstance(result, dict):
                    status_msg = result.get('message', '')
                    is_found = 'FOUND' in status_msg
                    return {"success": True, "exists": is_found, "status": status_msg}
                else:
                    # Raw string response
                    is_found = 'FOUND' in str(result)
                    return {"success": True, "exists": is_found, "status": str(result)}
            else:
                # Linux check
                import shutil
                exists = shutil.which(app_name) is not None
                return {"success": True, "exists": exists, "status": "FOUND_INSTALLED" if exists else "NOT_FOUND"}
        except Exception as e:
            print(f"❌ Check app error: {e}")
            return {"success": False, "error": str(e), "exists": False}
    
    def close_app(self, app_name):
        """Close application by name"""
        try:
            if not self.is_safe_app(app_name):
                return {"success": False, "error": "Cannot close blacklisted application"}
            
            # Find and terminate process
            for proc in psutil.process_iter(['name']):
                if app_name.lower() in proc.info['name'].lower():
                    proc.terminate()
                    self.log_activity("close_app", {"app": app_name})
                    return {"success": True, "app": app_name}
            
            return {"success": False, "error": f"Application '{app_name}' not found"}
            
        except Exception as e:
            self.log_activity("close_app", {"error": str(e)}, False)
            return {"success": False, "error": str(e)}
    
    def list_running_apps(self):
        """List all running applications"""
        try:
            apps = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                apps.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "cpu": proc.info['cpu_percent']
                })
            self.log_activity("list_running_apps", {"count": len(apps)})
            return {"success": True, "apps": apps[:50]}  # Limit to 50
        except Exception as e:
            self.log_activity("list_running_apps", {"error": str(e)}, False)
            return {"success": False, "error": str(e)}
    
    # ==================== WINDOW MANAGEMENT ====================
    
    def list_windows(self):
        """List all open windows"""
        if not HAS_WINDOW_CONTROL:
            return {"success": False, "error": "Window control not available on this system"}
        
        try:
            windows = []
            for win in gw.getAllWindows():
                if win.title:  # Skip windows without titles
                    windows.append({
                        "title": win.title,
                        "left": win.left,
                        "top": win.top,
                        "width": win.width,
                        "height": win.height
                    })
            self.log_activity("list_windows", {"count": len(windows)})
            return {"success": True, "windows": windows}
        except Exception as e:
            self.log_activity("list_windows", {"error": str(e)}, False)
            return {"success": False, "error": str(e)}
    
    def focus_window(self, title_substring):
        """Focus window by title substring"""
        if not HAS_WINDOW_CONTROL:
            return {"success": False, "error": "Window control not available"}
        
        try:
            windows = gw.getWindowsWithTitle(title_substring)
            if windows:
                windows[0].activate()
                self.log_activity("focus_window", {"title": title_substring})
                return {"success": True, "window": windows[0].title}
            return {"success": False, "error": f"Window with '{title_substring}' not found"}
        except Exception as e:
            self.log_activity("focus_window", {"error": str(e)}, False)
            return {"success": False, "error": str(e)}
    
    # ==================== SYSTEM OPERATIONS ====================
    
    def open_url(self, url):
        """Open URL in default browser"""
        try:
            if IS_WSL:
                result = self.call_windows_powershell('open_url', {'url': url})
                self.log_activity("open_url", {"url": url}, result.get('success', False))
                return result
            else:
                import webbrowser
                webbrowser.open(url)
                self.log_activity("open_url", {"url": url})
                return {"success": True, "url": url}
        except Exception as e:
            self.log_activity("open_url", {"error": str(e)}, False)
            return {"success": False, "error": str(e)}
    
    def screenshot(self, filename=None):
        """Take screenshot"""
        try:
            if IS_WSL:
                result = self.call_windows_powershell('screenshot', {})
                self.log_activity("screenshot", result.get('message', ''), result.get('success', False))
                return result
            else:
                return {"success": False, "error": "Screenshot not implemented for native Linux"}
        except Exception as e:
            self.log_activity("screenshot", {"error": str(e)}, False)
            return {"success": False, "error": str(e)}
    
    def clipboard_copy(self, text):
        """Copy text to clipboard"""
        try:
            if IS_WSL:
                result = self.call_windows_powershell('clipboard_copy', {'text': text})
                self.log_activity("clipboard_copy", {"length": len(text)}, result.get('success', False))
                return result
            else:
                return {"success": False, "error": "Clipboard not implemented for native Linux"}
        except Exception as e:
            self.log_activity("clipboard_copy", {"error": str(e)}, False)
            return {"success": False, "error": str(e)}
    
    # ==================== COMMAND PARSER ====================
    
    def parse_command(self, user_input):
        """Parse natural language into commands"""
        user_lower = user_input.lower()
        commands = []
        
        # Mouse movement
        if "move mouse" in user_lower or "move cursor" in user_lower:
            x, y = "center", "center"
            if "top" in user_lower:
                y = "top"
            if "bottom" in user_lower:
                y = "bottom"
            if "left" in user_lower:
                x = "left"
            if "right" in user_lower:
                x = "right"
            if "corner" in user_lower:
                if "top" in user_lower and "left" in user_lower:
                    x, y = "left", "top"
                elif "top" in user_lower and "right" in user_lower:
                    x, y = "right", "top"
                elif "bottom" in user_lower and "left" in user_lower:
                    x, y = "left", "bottom"
                elif "bottom" in user_lower and "right" in user_lower:
                    x, y = "right", "bottom"
            commands.append({"action": "mouse_move", "x": x, "y": y})
        
        # Mouse click
        if "click" in user_lower:
            button = "left"
            if "right" in user_lower:
                button = "right"
            elif "middle" in user_lower:
                button = "middle"
            
            clicks = 2 if "double" in user_lower else 1
            commands.append({"action": "mouse_click", "button": button, "clicks": clicks})
        
        # Scroll
        if "scroll" in user_lower:
            amount = 3
            if "up" in user_lower:
                amount = 3
            elif "down" in user_lower:
                amount = -3
            commands.append({"action": "mouse_scroll", "amount": amount})
        
        # Typing
        if "type" in user_lower:
            # Extract text between quotes
            import re
            match = re.search(r'["\'](.+?)["\']', user_input)
            if match:
                text = match.group(1)
                commands.append({"action": "keyboard_type", "text": text})
        
        # Key press
        if "press enter" in user_lower or "press return" in user_lower:
            commands.append({"action": "keyboard_press", "key": "enter"})
        elif "press escape" in user_lower or "press esc" in user_lower:
            commands.append({"action": "keyboard_press", "key": "escape"})
        elif "press tab" in user_lower:
            commands.append({"action": "keyboard_press", "key": "tab"})
        
        # Keyboard shortcuts
        if "copy" in user_lower and ("ctrl" in user_lower or "command" in user_lower):
            commands.append({"action": "keyboard_shortcut", "keys": ["ctrl", "c"]})
        elif "paste" in user_lower and ("ctrl" in user_lower or "command" in user_lower):
            commands.append({"action": "keyboard_shortcut", "keys": ["ctrl", "v"]})
        
        # Open app
        if "open" in user_lower:
            apps = ["chrome", "firefox", "notepad", "calculator", "paint", "explorer"]
            for app in apps:
                if app in user_lower:
                    commands.append({"action": "open_app", "app": app})
                    break
        
        # Open URL
        if "open" in user_lower and ("http" in user_lower or ".com" in user_lower):
            import re
            url_match = re.search(r'https?://\S+|www\.\S+|\S+\.(com|org|net|edu)', user_input)
            if url_match:
                url = url_match.group(0)
                if not url.startswith('http'):
                    url = 'https://' + url
                commands.append({"action": "open_url", "url": url})
        
        # Screenshot
        if "screenshot" in user_lower or "screen shot" in user_lower or "capture screen" in user_lower:
            commands.append({"action": "screenshot"})
        
        # List windows
        if "list windows" in user_lower or "show windows" in user_lower:
            commands.append({"action": "list_windows"})
        
        # List apps
        if "list apps" in user_lower or "list programs" in user_lower or "running apps" in user_lower:
            commands.append({"action": "list_running_apps"})
        
        return commands
    
    def execute_command(self, command):
        """Execute a single command"""
        action = command.get("action")
        
        if action == "mouse_move":
            return self.mouse_move(command.get("x"), command.get("y"))
        elif action == "mouse_click":
            return self.mouse_click(command.get("button", "left"), command.get("clicks", 1))
        elif action == "mouse_scroll":
            return self.mouse_scroll(command.get("amount", 3))
        elif action == "keyboard_type":
            return self.keyboard_type(command.get("text"))
        elif action == "keyboard_press":
            return self.keyboard_press(command.get("key"))
        elif action == "keyboard_shortcut":
            return self.keyboard_shortcut(command.get("keys"))
        elif action == "open_app":
            return self.open_app(command.get("app"))
        elif action == "close_app":
            return self.close_app(command.get("app"))
        elif action == "open_url":
            return self.open_url(command.get("url"))
        elif action == "screenshot":
            return self.screenshot(command.get("filename"))
        elif action == "list_windows":
            return self.list_windows()
        elif action == "list_running_apps":
            return self.list_running_apps()
        elif action == "focus_window":
            return self.focus_window(command.get("title"))
        elif action == "clipboard_copy":
            return self.clipboard_copy(command.get("text"))
        elif action == "clipboard_paste":
            return self.clipboard_paste()
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def execute_user_command(self, user_input, auto_execute=False):
        """Parse and execute user's natural language command"""
        try:
            commands = self.parse_command(user_input)
            
            if not commands:
                return {
                    "success": False,
                    "error": "Could not parse command",
                    "suggestion": "Try commands like: 'move mouse to top right', 'click', 'open chrome', 'type hello', 'screenshot'"
                }
            
            results = []
            for cmd in commands:
                if auto_execute:
                    result = self.execute_command(cmd)
                    results.append({"command": cmd, "result": result})
                else:
                    # Preview mode - don't execute
                    results.append({"command": cmd, "will_execute": True})
            
            return {
                "success": True,
                "user_input": user_input,
                "commands": commands,
                "results": results if auto_execute else None,
                "preview": not auto_execute
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """CLI interface for testing"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: commander.py <command>"}))
        sys.exit(1)
    
    user_command = " ".join(sys.argv[1:])
    commander = Commander()
    
    # Check for special flags
    preview_mode = "--preview" in user_command
    user_command = user_command.replace("--preview", "").strip()
    
    result = commander.execute_user_command(user_command, auto_execute=not preview_mode)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
