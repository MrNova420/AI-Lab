"""
Enhanced File System Tools - Full PC Access like Copilot
Create projects, directories, files anywhere the user specifies
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List


def create_directory(path: str, parents: bool = True) -> Dict[str, Any]:
    """
    Create a directory anywhere on the system.
    
    Args:
        path: Full path to directory to create
        parents: Create parent directories if needed (default: True)
        
    Returns:
        Dictionary with creation status
    """
    try:
        path_obj = Path(path).expanduser().resolve()
        
        if path_obj.exists():
            return {
                "success": True,
                "path": str(path_obj),
                "message": "Directory already exists",
                "created": False
            }
        
        if parents:
            path_obj.mkdir(parents=True, exist_ok=True)
        else:
            path_obj.mkdir(exist_ok=True)
        
        return {
            "success": True,
            "path": str(path_obj),
            "message": "Directory created successfully",
            "created": True
        }
        
    except PermissionError:
        return {
            "success": False,
            "path": path,
            "error": "Permission denied - try with sudo or in a different location"
        }
    except Exception as e:
        return {
            "success": False,
            "path": path,
            "error": str(e)
        }


def create_file_with_content(path: str, content: str, overwrite: bool = False) -> Dict[str, Any]:
    """
    Create a file with content anywhere on the system.
    
    Args:
        path: Full path to file
        content: File content
        overwrite: Whether to overwrite existing file
        
    Returns:
        Dictionary with creation status
    """
    try:
        path_obj = Path(path).expanduser().resolve()
        
        # Create parent directories if needed
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        if path_obj.exists() and not overwrite:
            return {
                "success": False,
                "path": str(path_obj),
                "error": "File already exists - set overwrite=True to replace"
            }
        
        with open(path_obj, 'w') as f:
            f.write(content)
        
        return {
            "success": True,
            "path": str(path_obj),
            "size": len(content),
            "created": True
        }
        
    except PermissionError:
        return {
            "success": False,
            "path": path,
            "error": "Permission denied"
        }
    except Exception as e:
        return {
            "success": False,
            "path": path,
            "error": str(e)
        }


def create_project_structure(base_path: str, structure: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create entire project structure from specification.
    Like Copilot - creates full project layouts.
    
    Args:
        base_path: Base directory for project
        structure: Dict describing the structure
                  {"dirs": ["src", "tests"], "files": {"README.md": "content"}}
    
    Returns:
        Dictionary with creation results
    """
    try:
        base = Path(base_path).expanduser().resolve()
        base.mkdir(parents=True, exist_ok=True)
        
        results = {
            "success": True,
            "base_path": str(base),
            "created_dirs": [],
            "created_files": [],
            "errors": []
        }
        
        # Create directories
        for dir_path in structure.get("dirs", []):
            try:
                full_path = base / dir_path
                full_path.mkdir(parents=True, exist_ok=True)
                results["created_dirs"].append(str(full_path))
            except Exception as e:
                results["errors"].append(f"Failed to create {dir_path}: {e}")
        
        # Create files
        for file_path, content in structure.get("files", {}).items():
            try:
                full_path = base / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(content)
                results["created_files"].append(str(full_path))
            except Exception as e:
                results["errors"].append(f"Failed to create {file_path}: {e}")
        
        if results["errors"]:
            results["success"] = False
        
        return results
        
    except Exception as e:
        return {
            "success": False,
            "base_path": base_path,
            "error": str(e)
        }


def get_current_directory() -> Dict[str, Any]:
    """
    Get current working directory.
    
    Returns:
        Dictionary with current directory
    """
    try:
        cwd = Path.cwd()
        
        return {
            "success": True,
            "path": str(cwd),
            "absolute": str(cwd.resolve())
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def change_directory(path: str) -> Dict[str, Any]:
    """
    Change current working directory.
    
    Args:
        path: Directory to change to
        
    Returns:
        Dictionary with change status
    """
    try:
        path_obj = Path(path).expanduser().resolve()
        
        if not path_obj.exists():
            return {
                "success": False,
                "error": f"Directory not found: {path}"
            }
        
        if not path_obj.is_dir():
            return {
                "success": False,
                "error": f"Not a directory: {path}"
            }
        
        os.chdir(path_obj)
        
        return {
            "success": True,
            "path": str(path_obj),
            "changed": True
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
