"""
System Information Tools
Get current date, time, system info, etc.
"""

import datetime
import platform
import os

def get_current_date():
    """Get current date"""
    now = datetime.datetime.now()
    return {
        'success': True,
        'date': now.strftime('%Y-%m-%d'),
        'formatted': now.strftime('%A, %B %d, %Y'),
        'message': f"Today is {now.strftime('%A, %B %d, %Y')}"
    }

def get_current_time():
    """Get current time"""
    now = datetime.datetime.now()
    return {
        'success': True,
        'time': now.strftime('%H:%M:%S'),
        'formatted': now.strftime('%I:%M %p'),
        'message': f"The time is {now.strftime('%I:%M %p')}"
    }

def get_current_datetime():
    """Get current date and time"""
    now = datetime.datetime.now()
    return {
        'success': True,
        'datetime': now.isoformat(),
        'formatted': now.strftime('%A, %B %d, %Y at %I:%M %p'),
        'message': f"It is {now.strftime('%A, %B %d, %Y at %I:%M %p')}"
    }

def get_system_info():
    """Get system information"""
    return {
        'success': True,
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.machine(),
        'hostname': platform.node(),
        'python_version': platform.python_version(),
        'message': f"System: {platform.system()} {platform.version()} on {platform.machine()}"
    }

def get_user_info():
    """Get current user information"""
    username = os.getenv('USER') or os.getenv('USERNAME') or 'Unknown'
    home = os.path.expanduser('~')
    return {
        'success': True,
        'username': username,
        'home_dir': home,
        'message': f"Current user: {username}"
    }
