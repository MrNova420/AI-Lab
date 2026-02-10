#!/usr/bin/env python3
"""
Smart App Launcher - AI-Driven Application Management
Intelligently opens apps with web fallback when not installed
"""

import sys
import subprocess
import platform
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.system.analyzer import check_if_app_exists
from tools.system.apps import open_application


def open_url_simple(url):
    """
    Simple URL opener without importing full web module
    """
    try:
        system = platform.system()
        
        if system == "Linux":
            # Check if we're in WSL
            try:
                with open('/proc/version', 'r') as f:
                    if 'microsoft' in f.read().lower():
                        subprocess.run(['powershell.exe', 'Start-Process', url], check=True)
                        return {
                            'success': True,
                            'message': f"Opened {url} in Windows browser",
                            'url': url
                        }
            except:
                pass
            
            subprocess.run(['xdg-open', url], check=True)
            return {
                'success': True,
                'message': f"Opened {url} in browser",
                'url': url
            }
            
        elif system == "Darwin":  # macOS
            subprocess.run(['open', url], check=True)
            return {
                'success': True,
                'message': f"Opened {url} in browser",
                'url': url
            }
            
        elif system == "Windows":
            subprocess.run(['start', url], shell=True, check=True)
            return {
                'success': True,
                'message': f"Opened {url} in browser",
                'url': url
            }
        
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


# Common app to web URL mappings (AI can learn these)
COMMON_WEB_FALLBACKS = {
    'steam': 'https://store.steampowered.com',
    'discord': 'https://discord.com/app',
    'spotify': 'https://open.spotify.com',
    'netflix': 'https://www.netflix.com',
    'youtube': 'https://www.youtube.com',
    'twitch': 'https://www.twitch.tv',
    'github': 'https://github.com',
    'gitlab': 'https://gitlab.com',
    'slack': 'https://slack.com',
    'notion': 'https://www.notion.so',
    'obsidian': 'https://obsidian.md',
    'vscode': 'https://vscode.dev',
    'figma': 'https://www.figma.com',
    'blender': 'https://www.blender.org',
    'obs': 'https://obsproject.com'
}


def smart_open_app(app_name, web_url=None):
    """
    Intelligently open an application with web fallback
    
    This is the AI-driven approach:
    1. Check if app is installed
    2. If installed, open the app
    3. If not installed, open web version
    4. AI makes the decision based on results
    
    Args:
        app_name: Name of the application (e.g., 'steam', 'discord')
        web_url: Optional web URL to use as fallback. If not provided, uses common mappings.
        
    Returns:
        Dict with success status, action taken, and details
    """
    try:
        # Step 1: Check if app exists
        check_result = check_if_app_exists(app_name)
        
        if not check_result.get('success'):
            return {
                'success': False,
                'message': f"Error checking for {app_name}: {check_result.get('error')}",
                'error': 'CHECK_FAILED'
            }
        
        app_exists = check_result.get('exists', False)
        
        # Step 2: Open app if it exists
        if app_exists:
            open_result = open_application(app_name)
            
            if open_result.get('success'):
                return {
                    'success': True,
                    'action': 'OPENED_APP',
                    'message': f"Opened {app_name} application",
                    'app': app_name,
                    'method': 'application'
                }
            else:
                # App exists but failed to open - try web fallback
                app_exists = False  # Force fallback
        
        # Step 3: Fall back to web version if app doesn't exist or failed
        if not app_exists:
            # Determine web URL
            if web_url is None:
                web_url = COMMON_WEB_FALLBACKS.get(app_name.lower())
                
                if web_url is None:
                    return {
                        'success': False,
                        'message': f"{app_name} not installed and no web URL provided",
                        'error': 'NO_FALLBACK',
                        'suggestion': f"Provide a web_url parameter or install {app_name}"
                    }
            
            # Open web version
            web_result = open_url_simple(web_url)
            
            if web_result.get('success'):
                return {
                    'success': True,
                    'action': 'OPENED_WEB',
                    'message': f"{app_name} not installed. Opened web version instead: {web_url}",
                    'app': app_name,
                    'method': 'web',
                    'url': web_url
                }
            else:
                return {
                    'success': False,
                    'message': f"Failed to open web version: {web_result.get('error')}",
                    'error': 'WEB_FAILED'
                }
    
    except Exception as e:
        return {
            'success': False,
            'message': f"Error in smart_open_app: {str(e)}",
            'error': 'EXCEPTION'
        }


def get_app_info(app_name):
    """
    Get comprehensive information about an app
    
    Args:
        app_name: Name of the application
        
    Returns:
        Dict with app status, availability, and options
    """
    try:
        # Check if app exists
        check_result = check_if_app_exists(app_name)
        
        if not check_result.get('success'):
            return {
                'success': False,
                'error': check_result.get('error')
            }
        
        app_exists = check_result.get('exists', False)
        web_url = COMMON_WEB_FALLBACKS.get(app_name.lower())
        
        return {
            'success': True,
            'app': app_name,
            'installed': app_exists,
            'has_web_version': web_url is not None,
            'web_url': web_url,
            'status': check_result.get('status', 'UNKNOWN'),
            'options': {
                'can_open_app': app_exists,
                'can_open_web': web_url is not None
            }
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def list_common_apps():
    """
    List commonly used apps with their web alternatives
    
    Returns:
        Dict with list of apps and their status
    """
    apps_info = []
    
    for app_name in COMMON_WEB_FALLBACKS.keys():
        info = get_app_info(app_name)
        if info.get('success'):
            apps_info.append({
                'name': app_name,
                'installed': info.get('installed'),
                'web_url': info.get('web_url')
            })
    
    return {
        'success': True,
        'apps': apps_info,
        'count': len(apps_info)
    }
