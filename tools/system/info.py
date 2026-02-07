"""
System Information Tools - REAL DATA, NO FAKING
Get current date, time, system info with geolocation awareness
"""

import datetime
import platform
import os
import socket
import subprocess

def get_current_date():
    """Get REAL current date with timezone awareness"""
    now = datetime.datetime.now()
    
    # Get timezone info
    try:
        import time
        is_dst = time.daylight and time.localtime().tm_isdst > 0
        utc_offset = - (time.altzone if is_dst else time.timezone)
        tz_hours = utc_offset // 3600
        tz_name = time.tzname[time.daylight]
    except:
        tz_hours = 0
        tz_name = "UTC"
    
    return {
        'success': True,
        'date': now.strftime('%Y-%m-%d'),
        'formatted': now.strftime('%A, %B %d, %Y'),
        'day_of_week': now.strftime('%A'),
        'timezone': tz_name,
        'utc_offset': f"UTC{tz_hours:+d}",
        'message': f"Today is {now.strftime('%A, %B %d, %Y')} ({tz_name})"
    }

def get_current_time():
    """Get REAL current time"""
    now = datetime.datetime.now()
    return {
        'success': True,
        'time_24h': now.strftime('%H:%M:%S'),
        'time_12h': now.strftime('%I:%M:%S %p'),
        'formatted': now.strftime('%I:%M %p'),
        'message': f"The time is {now.strftime('%I:%M:%S %p')}"
    }

def get_current_datetime():
    """Get REAL current date and time together"""
    now = datetime.datetime.now()
    date_info = get_current_date()
    time_info = get_current_time()
    
    return {
        'success': True,
        'datetime': now.isoformat(),
        'date': date_info['formatted'],
        'time': time_info['formatted'],
        'timezone': date_info['timezone'],
        'message': f"It is {now.strftime('%A, %B %d, %Y at %I:%M %p')} ({date_info['timezone']})"
    }

def get_system_info():
    """Get REAL ACTUAL system information - NO FAKE DATA"""
    try:
        # Get REAL data
        hostname = socket.gethostname()
        
        # Get Linux distribution info
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = {}
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os_info[key] = value.strip('"')
                os_name = os_info.get('PRETTY_NAME', 'Linux')
        except:
            os_name = platform.system()
        
        # Get kernel version
        kernel = platform.release()
        
        # Get architecture
        arch = platform.machine()
        
        # Get Python version
        py_version = platform.python_version()
        
        # Get CPU info
        try:
            cpu_info = subprocess.check_output(['lscpu'], text=True)
            cpu_model = [line for line in cpu_info.split('\n') if 'Model name' in line][0].split(':')[1].strip()
        except:
            cpu_model = platform.processor() or "Unknown"
        
        # Get memory info
        try:
            with open('/proc/meminfo', 'r') as f:
                mem_total_kb = int([line for line in f if 'MemTotal' in line][0].split()[1])
                mem_total_gb = mem_total_kb / 1024 / 1024
        except:
            mem_total_gb = 0
        
        return {
            'success': True,
            'hostname': hostname,
            'os': os_name,
            'kernel': kernel,
            'architecture': arch,
            'cpu': cpu_model,
            'memory_gb': round(mem_total_gb, 2),
            'python_version': py_version,
            'message': f"System: {os_name} (Kernel {kernel}) on {arch} - {cpu_model} - {round(mem_total_gb, 1)}GB RAM"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"Error getting system info: {e}"
        }

def get_user_info():
    """Get REAL current user information"""
    username = os.getenv('USER') or os.getenv('USERNAME') or 'Unknown'
    home = os.path.expanduser('~')
    
    # Get real shell
    shell = os.getenv('SHELL', 'Unknown')
    
    # Get current directory
    cwd = os.getcwd()
    
    return {
        'success': True,
        'username': username,
        'home_dir': home,
        'shell': shell,
        'current_dir': cwd,
        'message': f"User: {username} (Home: {home}, Shell: {shell})"
    }

