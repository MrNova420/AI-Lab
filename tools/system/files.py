#!/usr/bin/env python3
"""
File Operations Tools
Read, write, list, and manage files
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def read_file(path):
    """
    Read contents of ANY text file on the system.
    User can specify any path - full Copilot-like access.
    
    Args:
        path: Path to file (anywhere: ~/Desktop/file.txt, /home/user/project/file.py, etc.)
        
    Returns:
        Dict with success status, content, and metadata
    """
    try:
        file_path = Path(path).expanduser().resolve()
        
        if not file_path.exists():
            return {
                'success': False,
                'error': f'File not found: {path}'
            }
        
        if not file_path.is_file():
            return {
                'success': False,
                'error': f'Not a file: {path}'
            }
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        return {
            'success': True,
            'path': str(file_path),
            'content': content,
            'size': len(content),
            'lines': len(content.splitlines())
        }
        
    except PermissionError:
        return {
            'success': False,
            'error': 'Permission denied'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def write_file(path, content):
    """
    Write or create a file ANYWHERE on the system.
    User can specify any path - full Copilot-like access.
    
    Args:
        path: Path where to write (anywhere: ~/Desktop/test.py, /home/user/project/app.py, etc.)
        content: Content to write
        
    Returns:
        Dict with success status
    """
    try:
        file_path = Path(path).expanduser().resolve()
        
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'success': True,
            'path': str(file_path),
            'size': len(content),
            'lines': len(content.splitlines())
        }
        
    except PermissionError:
        return {
            'success': False,
            'error': 'Permission denied'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def list_files(directory):
    """
    List files in ANY directory on the system.
    User can browse anywhere they want.
    
    Args:
        directory: Directory to list (anywhere: ~/Desktop, /home/user/projects, etc.)
        
    Returns:
        Dict with file listing
    """
    try:
        dir_path = Path(directory).expanduser().resolve()
        
        if not dir_path.exists():
            return {
                'success': False,
                'error': f'Directory not found: {directory}'
            }
        
        if not dir_path.is_dir():
            return {
                'success': False,
                'error': f'Not a directory: {directory}'
            }
        
        files = []
        dirs = []
        
        for item in sorted(dir_path.iterdir()):
            try:
                stat = item.stat()
                entry = {
                    'name': item.name,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'is_dir': item.is_dir()
                }
                
                if item.is_dir():
                    dirs.append(entry)
                else:
                    files.append(entry)
            except:
                continue
        
        return {
            'success': True,
            'path': str(dir_path),
            'directories': dirs,
            'files': files,
            'total': len(dirs) + len(files)
        }
        
    except PermissionError:
        return {
            'success': False,
            'error': 'Permission denied'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def file_info(path):
    """
    Get information about ANY file on the system.
    
    Args:
        path: Path to file (anywhere on the system)
        
    Returns:
        Dict with file information
    """
    try:
        file_path = Path(path).expanduser().resolve()

        
        # Security check: ensure path is within project root
        is_safe, error = _is_path_safe(file_path)
        if not is_safe:
            return error
        
        # Check if file exists
        if not file_path.exists():
            return {
                'success': False,
                'message': f"File not found: {path}",
                'error': 'FILE_NOT_FOUND'
            }
        
        # Check if it's a file (not directory)
        if not file_path.is_file():
            return {
                'success': False,
                'message': f"Path is not a file: {path}",
                'error': 'NOT_A_FILE'
            }
        
        # Check file size (limit to 10MB for safety)
        file_size = file_path.stat().st_size
        if file_size > 10 * 1024 * 1024:  # 10MB
            return {
                'success': False,
                'message': f"File too large: {file_size / 1024 / 1024:.1f}MB (max 10MB)",
                'error': 'FILE_TOO_LARGE'
            }
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try reading as binary if UTF-8 fails
            with open(file_path, 'rb') as f:
                content = f.read()
                return {
                    'success': False,
                    'message': f"File is binary (cannot display as text)",
                    'error': 'BINARY_FILE',
                    'size': file_size
                }
        
        return {
            'success': True,
            'content': content,
            'path': str(file_path),
            'size': file_size,
            'lines': len(content.splitlines()),
            'message': f"Read {len(content)} characters from {file_path.name}"
        }
        
    except PermissionError:
        return {
            'success': False,
            'message': f"Permission denied: {path}",
            'error': 'PERMISSION_DENIED'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error reading file: {str(e)}",
            'error': 'READ_ERROR'
        }


def write_file(path, content):
    """
    Write content to a file (creates or overwrites)
    
    Args:
        path: Path to the file
        content: Content to write
        
    Returns:
        Dict with success status and message
    """
    try:
        file_path = Path(path).expanduser().resolve()
        
        # Security check: ensure path is within project root
        is_safe, error = _is_path_safe(file_path)
        if not is_safe:
            return error
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_size = file_path.stat().st_size
        
        return {
            'success': True,
            'path': str(file_path),
            'size': file_size,
            'message': f"Wrote {len(content)} characters to {file_path.name}"
        }
        
    except PermissionError:
        return {
            'success': False,
            'message': f"Permission denied: {path}",
            'error': 'PERMISSION_DENIED'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error writing file: {str(e)}",
            'error': 'WRITE_ERROR'
        }


def list_files(directory="."):
    """
    List files and directories in a directory
    
    Args:
        directory: Path to directory (default: current directory)
        
    Returns:
        Dict with success status and list of files
    """
    try:
        dir_path = Path(directory).expanduser().resolve()
        
        # Security check: ensure path is within project root
        is_safe, error = _is_path_safe(dir_path)
        if not is_safe:
            return error
        
        # Check if directory exists
        if not dir_path.exists():
            return {
                'success': False,
                'message': f"Directory not found: {directory}",
                'error': 'DIR_NOT_FOUND'
            }
        
        # Check if it's a directory
        if not dir_path.is_dir():
            return {
                'success': False,
                'message': f"Path is not a directory: {directory}",
                'error': 'NOT_A_DIRECTORY'
            }
        
        # List files
        files = []
        dirs = []
        
        for item in sorted(dir_path.iterdir()):
            name = item.name
            
            # Skip hidden files by default
            if name.startswith('.'):
                continue
            
            if item.is_dir():
                dirs.append({
                    'name': name,
                    'type': 'directory',
                    'path': str(item)
                })
            else:
                try:
                    size = item.stat().st_size
                    modified = datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    files.append({
                        'name': name,
                        'type': 'file',
                        'size': size,
                        'modified': modified,
                        'path': str(item)
                    })
                except OSError:
                    # Skip files we can't stat (e.g., due to permission or race conditions)
                    continue
        
        return {
            'success': True,
            'directory': str(dir_path),
            'files': files,
            'directories': dirs,
            'total_files': len(files),
            'total_directories': len(dirs),
            'message': f"Found {len(files)} files and {len(dirs)} directories in {dir_path.name}"
        }
        
    except PermissionError:
        return {
            'success': False,
            'message': f"Permission denied: {directory}",
            'error': 'PERMISSION_DENIED'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error listing directory: {str(e)}",
            'error': 'LIST_ERROR'
        }


def file_info(path):
    """
    Get detailed information about a file
    
    Args:
        path: Path to the file
        
    Returns:
        Dict with file metadata
    """
    try:
        file_path = Path(path).expanduser().resolve()
        
        # Security check: ensure path is within project root
        is_safe, error = _is_path_safe(file_path)
        if not is_safe:
            return error
        
        # Check if path exists
        if not file_path.exists():
            return {
                'success': False,
                'message': f"File not found: {path}",
                'error': 'FILE_NOT_FOUND'
            }
        
        stat = file_path.stat()
        
        info = {
            'success': True,
            'name': file_path.name,
            'path': str(file_path),
            'type': 'directory' if file_path.is_dir() else 'file',
            'size': stat.st_size,
            'size_human': _format_bytes(stat.st_size),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
            'permissions': oct(stat.st_mode)[-3:],
            'message': f"File info for {file_path.name}"
        }
        
        # Add line count for text files
        if file_path.is_file() and stat.st_size < 10 * 1024 * 1024:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = sum(1 for _ in f)
                info['lines'] = lines
            except (OSError, UnicodeDecodeError):
                # Skip if not a readable text file or if an I/O error occurs
                pass
        
        return info
        
    except PermissionError:
        return {
            'success': False,
            'message': f"Permission denied: {path}",
            'error': 'PERMISSION_DENIED'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Error getting file info: {str(e)}",
            'error': 'INFO_ERROR'
        }


def _format_bytes(bytes_size):
    """Format bytes into human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


if __name__ == '__main__':
    # Test file operations
    print("🧪 Testing File Operations\n")
    
    # Test list_files
    print("1. List files in current directory:")
    result = list_files(".")
    print(f"   Result: {result.get('message')}")
    print(f"   Files: {result.get('total_files')}, Dirs: {result.get('total_directories')}\n")
    
    # Test file_info
    print("2. Get info for this file:")
    result = file_info(__file__)
    print(f"   Result: {result.get('message')}")
    print(f"   Size: {result.get('size_human')}\n")
    
    # Test read_file
    print("3. Read first 200 chars of this file:")
    result = read_file(__file__)
    if result.get('success'):
        content = result.get('content', '')[:200]
        print(f"   Content preview: {content}...\n")
    
    print("✅ File operations tests complete!")
