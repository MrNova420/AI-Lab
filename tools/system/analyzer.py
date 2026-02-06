"""
System Analysis Tools
AI can analyze PC state, running processes, installed apps, etc.
"""

import subprocess
import json
from pathlib import Path

class SystemAnalyzer:
    """Analyzes system state for AI awareness"""
    
    def __init__(self):
        self.is_wsl = self._check_wsl()
    
    def _check_wsl(self):
        """Check if running in WSL"""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except:
            return False
    
    def get_running_processes(self):
        """
        Get list of running processes
        AI can see what's currently running
        """
        try:
            if self.is_wsl:
                # Get Windows processes via PowerShell
                cmd = "powershell.exe -Command \"Get-Process | Select-Object Name, Id | ConvertTo-Json\""
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                processes = json.loads(result.stdout)
                return {
                    "success": True,
                    "processes": processes[:50],  # Limit to 50 for performance
                    "count": len(processes)
                }
            else:
                # Linux processes
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                lines = result.stdout.split('\n')[1:51]  # First 50
                return {
                    "success": True,
                    "processes": lines,
                    "count": len(lines)
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_app_installed(self, app_name):
        """
        Check if an application is installed
        Returns detailed status
        """
        try:
            if self.is_wsl:
                # Check Windows apps
                from scripts.commander import Commander
                commander = Commander()
                result = commander.check_app_exists(app_name)
                return result
            else:
                # Check Linux apps
                import shutil
                exists = shutil.which(app_name) is not None
                return {
                    "success": True,
                    "exists": exists,
                    "status": "FOUND" if exists else "NOT_FOUND"
                }
        except Exception as e:
            return {"success": False, "error": str(e), "exists": False}
    
    def get_system_info(self):
        """
        Get system information
        AI knows what system it's running on
        """
        import platform
        import os
        
        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "is_wsl": self.is_wsl,
            "user": os.getenv('USER') or os.getenv('USERNAME'),
            "home": str(Path.home())
        }
        
        return {"success": True, "info": info}
    
    def analyze_command_result(self, command, result):
        """
        Analyze the result of a command execution
        AI can understand if something worked or failed
        """
        analysis = {
            "command": command,
            "success": result.get("success", False),
            "had_error": "error" in result,
        }
        
        # Analyze error messages
        if not analysis["success"]:
            error = result.get("error", "")
            analysis["error_type"] = self._classify_error(error)
            analysis["suggestion"] = self._suggest_fix(error)
        
        # Analyze success messages
        if analysis["success"]:
            analysis["action_taken"] = result.get("message", "Action completed")
        
        return analysis
    
    def _classify_error(self, error_msg):
        """Classify error type for AI understanding"""
        error_lower = error_msg.lower()
        
        if "not found" in error_lower or "does not exist" in error_lower:
            return "NOT_FOUND"
        elif "permission" in error_lower or "access denied" in error_lower:
            return "PERMISSION_DENIED"
        elif "timeout" in error_lower:
            return "TIMEOUT"
        elif "connection" in error_lower:
            return "CONNECTION_ERROR"
        else:
            return "UNKNOWN"
    
    def _suggest_fix(self, error_msg):
        """Suggest fixes for common errors"""
        error_type = self._classify_error(error_msg)
        
        suggestions = {
            "NOT_FOUND": "The app or file doesn't exist. Try installing it first.",
            "PERMISSION_DENIED": "Need administrator privileges. Try running as admin.",
            "TIMEOUT": "Operation took too long. Try again or check system load.",
            "CONNECTION_ERROR": "Network issue. Check internet connection.",
            "UNKNOWN": "Unknown error occurred. Check logs for details."
        }
        
        return suggestions.get(error_type, "Unable to determine fix.")
    
    def get_installed_apps(self):
        """
        Get list of commonly installed applications
        AI can see what apps are available
        """
        common_apps = [
            'steam', 'discord', 'chrome', 'firefox', 'code', 
            'spotify', 'obs', 'vlc', 'notepad', 'calc'
        ]
        
        installed = []
        not_installed = []
        
        for app in common_apps:
            result = self.check_app_installed(app)
            if result.get("exists"):
                installed.append(app)
            else:
                not_installed.append(app)
        
        return {
            "success": True,
            "installed": installed,
            "not_installed": not_installed,
            "total_checked": len(common_apps)
        }


# Global analyzer instance
_analyzer = None

def get_analyzer():
    """Get or create system analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = SystemAnalyzer()
    return _analyzer


# Tool functions for AI to use
def analyze_system():
    """AI tool: Get comprehensive system analysis"""
    analyzer = get_analyzer()
    return analyzer.get_system_info()


def check_what_is_running():
    """AI tool: See what processes are currently running"""
    analyzer = get_analyzer()
    return analyzer.get_running_processes()


def check_if_app_exists(app_name):
    """AI tool: Check if a specific app is installed"""
    analyzer = get_analyzer()
    return analyzer.check_app_installed(app_name)


def get_available_apps():
    """AI tool: Get list of commonly available applications"""
    analyzer = get_analyzer()
    return analyzer.get_installed_apps()


def analyze_result(command, result):
    """AI tool: Analyze the result of an action"""
    analyzer = get_analyzer()
    return analyzer.analyze_command_result(command, result)
