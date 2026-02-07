#!/usr/bin/env python3
"""
Application Control Tools
Open, close, and manage desktop applications
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.commander import Commander

# Global commander instance
_commander = None

def get_commander():
    """Get or create commander instance"""
    global _commander
    if _commander is None:
        _commander = Commander()
    return _commander


def open_application(app):
    """
    Open a desktop application
    
    Args:
        app: Name of the application (e.g., 'steam', 'notepad', 'chrome')
        
    Returns:
        Dict with success status and message
    """
    try:
        commander = get_commander()
        result = commander.open_app(app)
        
        if result.get('success'):
            return {
                'success': True,
                'message': f"Opened {app}",
                'app': app
            }
        else:
            return {
                'success': False,
                'message': result.get('error', f"Failed to open {app}"),
                'app': app
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error opening {app}: {str(e)}",
            'app': app
        }


def close_application(app):
    """
    Close a running application
    
    Args:
        app: Name of the application to close
        
    Returns:
        Dict with success status and message
    """
    try:
        commander = get_commander()
        result = commander.close_app(app)
        
        if result.get('success'):
            return {
                'success': True,
                'message': f"Closed {app}",
                'app': app
            }
        else:
            return {
                'success': False,
                'message': result.get('error', f"Failed to close {app}"),
                'app': app
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error closing {app}: {str(e)}",
            'app': app
        }


def switch_to_application(app):
    """
    Switch focus to an application
    
    Args:
        app: Name of the application
        
    Returns:
        Dict with success status and message
    """
    try:
        commander = get_commander()
        result = commander.switch_app(app)
        
        if result.get('success'):
            return {
                'success': True,
                'message': f"Switched to {app}",
                'app': app
            }
        else:
            return {
                'success': False,
                'message': result.get('error', f"Failed to switch to {app}"),
                'app': app
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error switching to {app}: {str(e)}",
            'app': app
        }
