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
from core.platform_detection import check_feature_available

# Global commander instance
_commander = None

def get_commander():
    """Get or create commander instance"""
    global _commander
    if _commander is None:
        _commander = Commander()
    return _commander


def _check_screenshot_available():
    """Check if screenshot features are available on this platform"""
    available, reason = check_feature_available('screenshot')
    if not available:
        return {
            'success': False,
            'message': f"Screenshot not available: {reason}",
            'error': 'PLATFORM_UNAVAILABLE'
        }
    return None


def take_screenshot():
    """
    Capture a screenshot of the screen
    
    Returns:
        Dict with success status, message, and file path
    """
    # Check platform availability
    unavailable = _check_screenshot_available()
    if unavailable:
        return unavailable
    
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
                'message': result.get('error', 'Failed to capture screenshot'),
                'error': 'EXECUTION_ERROR'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error capturing screenshot: {str(e)}",
            'error': 'EXECUTION_ERROR'
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
    # Check platform availability
    unavailable = _check_screenshot_available()
    if unavailable:
        return unavailable
    
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
                'message': result.get('error', 'Failed to capture region screenshot'),
                'error': 'EXECUTION_ERROR'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error capturing region screenshot: {str(e)}",
            'error': 'EXECUTION_ERROR'
        }
