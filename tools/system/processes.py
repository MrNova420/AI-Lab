#!/usr/bin/env python3
"""
Process Management Tools
List, monitor, and manage system processes
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


def _check_psutil():
    """Check if psutil is available"""
    if not PSUTIL_AVAILABLE:
        return {
            'success': False,
            'message': 'psutil not installed. Install with: pip install psutil',
            'error': 'DEPENDENCY_MISSING'
        }
    return None


def list_processes():
    """
    List all running processes
    
    Returns:
        Dict with list of processes and their info
    """
    check = _check_psutil()
    if check:
        return check
    
    try:
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'user': info.get('username', 'unknown'),
                    'cpu': round(info.get('cpu_percent', 0), 1),
                    'memory': round(info.get('memory_percent', 0), 1)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage (descending)
        processes.sort(key=lambda p: p['cpu'], reverse=True)
        
        # Limit to top 50 processes
        processes = processes[:50]
        
        return {
            'success': True,
            'processes': processes,
            'count': len(processes),
            'message': f"Found {len(processes)} running processes (top 50 by CPU)"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error listing processes: {str(e)}",
            'error': 'LIST_ERROR'
        }


def process_info(pid):
    """
    Get detailed information about a specific process
    
    Args:
        pid: Process ID
        
    Returns:
        Dict with process details
    """
    check = _check_psutil()
    if check:
        return check
    
    try:
        pid = int(pid)
        proc = psutil.Process(pid)
        
        # Get process info
        info = {
            'success': True,
            'pid': proc.pid,
            'name': proc.name(),
            'exe': proc.exe() if proc.exe() else 'N/A',
            'status': proc.status(),
            'username': proc.username(),
            'cpu_percent': round(proc.cpu_percent(interval=0.1), 1),
            'memory_percent': round(proc.memory_percent(), 1),
            'memory_mb': round(proc.memory_info().rss / 1024 / 1024, 1),
            'num_threads': proc.num_threads(),
            'message': f"Process info for PID {pid}: {proc.name()}"
        }
        
        # Try to get command line (may fail for some processes)
        try:
            info['cmdline'] = ' '.join(proc.cmdline())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            info['cmdline'] = 'N/A'
        
        # Try to get create time
        try:
            import datetime
            info['created'] = datetime.datetime.fromtimestamp(proc.create_time()).isoformat()
        except:
            info['created'] = 'N/A'
        
        return info
        
    except psutil.NoSuchProcess:
        return {
            'success': False,
            'message': f"Process with PID {pid} not found",
            'error': 'PROCESS_NOT_FOUND'
        }
    except psutil.AccessDenied:
        return {
            'success': False,
            'message': f"Access denied to process {pid}",
            'error': 'ACCESS_DENIED'
        }
    except ValueError:
        return {
            'success': False,
            'message': f"Invalid PID: {pid}",
            'error': 'INVALID_PID'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error getting process info: {str(e)}",
            'error': 'INFO_ERROR'
        }


def find_process(name):
    """
    Find processes by name
    
    Args:
        name: Process name to search for (case-insensitive)
        
    Returns:
        Dict with list of matching processes
    """
    check = _check_psutil()
    if check:
        return check
    
    try:
        name_lower = name.lower()
        matches = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if name_lower in proc.info['name'].lower():
                    matches.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu': round(proc.info.get('cpu_percent', 0), 1),
                        'memory': round(proc.info.get('memory_percent', 0), 1)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not matches:
            return {
                'success': True,
                'processes': [],
                'count': 0,
                'message': f"No processes found matching '{name}'"
            }
        
        return {
            'success': True,
            'processes': matches,
            'count': len(matches),
            'message': f"Found {len(matches)} process(es) matching '{name}'"
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error finding process: {str(e)}",
            'error': 'FIND_ERROR'
        }


if __name__ == '__main__':
    # Test process tools
    print("🧪 Testing Process Management Tools\n")
    
    if not PSUTIL_AVAILABLE:
        print("❌ psutil not available - install with: pip install psutil")
        sys.exit(1)
    
    # Test list_processes
    print("1. List top processes:")
    result = list_processes()
    if result.get('success'):
        print(f"   Result: {result.get('message')}")
        # Show top 5
        for proc in result.get('processes', [])[:5]:
            print(f"   - PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu']}%)")
    print()
    
    # Test process_info on current process
    import os
    print(f"2. Get info for current process (PID {os.getpid()}):")
    result = process_info(os.getpid())
    if result.get('success'):
        print(f"   Name: {result.get('name')}")
        print(f"   CPU: {result.get('cpu_percent')}%")
        print(f"   Memory: {result.get('memory_mb')}MB")
    print()
    
    # Test find_process
    print("3. Find Python processes:")
    result = find_process('python')
    if result.get('success'):
        print(f"   Result: {result.get('message')}")
        for proc in result.get('processes', [])[:3]:
            print(f"   - PID {proc['pid']}: {proc['name']}")
    
    print("\n✅ Process management tests complete!")
