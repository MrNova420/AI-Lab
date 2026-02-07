#!/usr/bin/env python3
"""
Keyboard Control Tools
Type text and press keys
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


def type_text(text):
    """
    Type text using keyboard
    
    Args:
        text: Text to type
        
    Returns:
        Dict with success status and message
    """
    try:
        commander = get_commander()
        result = commander.keyboard_type(text)
        
        if result.get('success'):
            return {
                'success': True,
                'message': f"Typed: {text[:50]}..." if len(text) > 50 else f"Typed: {text}",
                'text': text
            }
        else:
            return {
                'success': False,
                'message': result.get('error', 'Failed to type text')
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error typing text: {str(e)}"
        }


def press_key(key):
    """
    Press a special key
    
    Args:
        key: Key name (e.g., 'ENTER', 'TAB', 'ESC', 'BACKSPACE', 'DELETE')
        
    Returns:
        Dict with success status and message
    """
    try:
        commander = get_commander()
        result = commander.keyboard_press(key)
        
        if result.get('success'):
            return {
                'success': True,
                'message': f"Pressed {key}",
                'key': key
            }
        else:
            return {
                'success': False,
                'message': result.get('error', f"Failed to press {key}")
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error pressing key: {str(e)}"
        }


def press_combo(keys):
    """
    Press a key combination
    
    Args:
        keys: List of keys to press together (e.g., ['CTRL', 'C'])
        
    Returns:
        Dict with success status and message
    """
    try:
        commander = get_commander()
        result = commander.keyboard_combo(keys)
        
        if result.get('success'):
            combo_str = '+'.join(keys)
            return {
                'success': True,
                'message': f"Pressed {combo_str}",
                'keys': keys
            }
        else:
            return {
                'success': False,
                'message': result.get('error', 'Failed to press key combination')
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error pressing key combo: {str(e)}"
        }
