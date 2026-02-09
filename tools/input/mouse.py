#!/usr/bin/env python3
"""
Mouse Control Tools
Move cursor and click buttons
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.commander import Commander
from core.platform_detection import check_feature_available

# Global commander instance
_commander = None

def get_commander():
    """Get or create commander instance"""
    global _commander
    if _commander is None:
        _commander = Commander()
    return _commander




def _check_commander_available():
    """Check if commander features are available on this platform"""
    available, reason = check_feature_available('commander')
    if not available:
        return {
            'success': False,
            'message': f"Commander mode not available: {reason}",
            'error': 'PLATFORM_UNAVAILABLE'
        }
    return None


def move_mouse(x, y):
    """
    Move mouse cursor to coordinates
    
    Args:
        x: X coordinate
        y: Y coordinate
        
    Returns:
        Dict with success status and message
    """
    # Check platform availability
    unavailable = _check_commander_available()
    if unavailable:
        return unavailable
    
    try:
        commander = get_commander()
        result = commander.mouse_move(x, y)
        
        if result.get('success'):
            return {
                'success': True,
                'message': f"Moved mouse to ({x}, {y})",
                'x': x,
                'y': y
            }
        else:
            return {
                'success': False,
                'message': result.get('error', f"Failed to move mouse to ({x}, {y})")
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error moving mouse: {str(e)}"
        }


def click_mouse(button='left', double=False):
    """
    Click mouse button
    
    Args:
        button: Button to click ('left', 'right', 'middle')
        double: Whether to double-click
        
    Returns:
        Dict with success status and message
    """
    # Check platform availability
    unavailable = _check_commander_available()
    if unavailable:
        return unavailable
    
    try:
        commander = get_commander()
        result = commander.mouse_click(button, double)
        
        if result.get('success'):
            click_type = "double-clicked" if double else "clicked"
            return {
                'success': True,
                'message': f"{click_type.capitalize()} {button} mouse button",
                'button': button,
                'double': double
            }
        else:
            return {
                'success': False,
                'message': result.get('error', f"Failed to click {button} button")
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error clicking mouse: {str(e)}"
        }


def get_mouse_position():
    """
    Get current mouse position
    
    Returns:
        Dict with success status, message, and coordinates
    """
    # Check platform availability
    unavailable = _check_commander_available()
    if unavailable:
        return unavailable
    
    try:
        commander = get_commander()
        result = commander.get_mouse_position()
        
        if result.get('success'):
            x = result.get('x', 0)
            y = result.get('y', 0)
            return {
                'success': True,
                'message': f"Mouse at ({x}, {y})",
                'x': x,
                'y': y
            }
        else:
            return {
                'success': False,
                'message': result.get('error', 'Failed to get mouse position')
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error getting mouse position: {str(e)}"
        }
