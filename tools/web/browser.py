#!/usr/bin/env python3
"""
Browser control utilities
"""

import subprocess
import platform


def open_url(url):
    """
    Open a URL in the default browser
    
    Args:
        url: The URL to open
        
    Returns:
        Dict with success status and message
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
                        return {
                            'success': True,
                            'message': f"Opened {url} in Windows browser",
                            'url': url,
                            'method': 'wsl_powershell'
                        }
            except:
                pass
            
            # Native Linux
            subprocess.run(['xdg-open', url], check=True)
            return {
                'success': True,
                'message': f"Opened {url} in browser",
                'url': url,
                'method': 'xdg-open'
            }
            
        elif system == "Darwin":  # macOS
            subprocess.run(['open', url], check=True)
            return {
                'success': True,
                'message': f"Opened {url} in browser",
                'url': url,
                'method': 'macos_open'
            }
            
        elif system == "Windows":
            subprocess.run(['start', url], shell=True, check=True)
            return {
                'success': True,
                'message': f"Opened {url} in browser",
                'url': url,
                'method': 'windows_start'
            }
        
        else:
            return {
                'success': False,
                'error': f"Unsupported operating system: {system}",
                'url': url
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': f"Error opening URL: {str(e)}",
            'url': url
        }
