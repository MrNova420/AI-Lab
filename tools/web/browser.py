#!/usr/bin/env python3
"""
Browser control utilities
"""

import subprocess
import platform


def open_url(url):
    """
    Open a URL in the default browser
    """
    try:
        system = platform.system()
        
        if system == "Linux":
            # Check if we're in WSL
            try:
                with open('/proc/version', 'r') as f:
                    if 'microsoft' in f.read().lower():
                        # WSL - use PowerShell to open in Windows browser
                        subprocess.run(['powershell.exe', 'Start-Process', url], check=True)
                        return f"✅ Opened {url} in Windows browser"
            except:
                pass
            
            # Native Linux
            subprocess.run(['xdg-open', url], check=True)
            return f"✅ Opened {url} in browser"
            
        elif system == "Darwin":  # macOS
            subprocess.run(['open', url], check=True)
            return f"✅ Opened {url} in browser"
            
        elif system == "Windows":
            subprocess.run(['start', url], shell=True, check=True)
            return f"✅ Opened {url} in browser"
        
        else:
            return f"❌ Unsupported operating system: {system}"
    
    except Exception as e:
        return f"❌ Error opening URL: {e}"
