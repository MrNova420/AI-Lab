#!/usr/bin/env python3
"""
Screenshot Tool
Capture screen for analysis or documentation
"""

import sys
from pathlib import Path
from datetime import datetime

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


def take_screenshot():
    """
    Capture a screenshot of the screen
    
    Returns:
        Dict with success status, message, and file path
    """
    try:
        commander = get_commander()
        result = commander.screenshot()
        
        if result.get('success'):
            filepath = result.get('filepath', 'screenshot saved')
            return {
                'success': True,
                'message': f"Screenshot saved to {filepath}",
                'filepath': filepath
            }
        else:
            return {
                'success': False,
                'message': result.get('error', 'Failed to capture screenshot')
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error capturing screenshot: {str(e)}"
        }


def take_region_screenshot(x, y, width, height):
    """
    Capture a screenshot of a specific region
    
    Args:
        x: X coordinate of top-left corner
        y: Y coordinate of top-left corner
        width: Width of region
        height: Height of region
        
    Returns:
        Dict with success status, message, and file path
    """
    try:
        commander = get_commander()
        result = commander.screenshot_region(x, y, width, height)
        
        if result.get('success'):
            filepath = result.get('filepath', 'screenshot saved')
            return {
                'success': True,
                'message': f"Region screenshot saved to {filepath}",
                'filepath': filepath,
                'region': {'x': x, 'y': y, 'width': width, 'height': height}
            }
        else:
            return {
                'success': False,
                'message': result.get('error', 'Failed to capture region screenshot')
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error capturing region screenshot: {str(e)}"
        }
