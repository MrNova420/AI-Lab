"""
Project Workspace Manager - Smart Default Location
Provides a convenient default workspace, but allows working ANYWHERE
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional


def get_default_workspace() -> Path:
    """
    Get the default workspace directory for NovaForge projects.
    Creates it if it doesn't exist.
    
    Default: ~/NovaForge/projects
    But users can always work elsewhere if they specify!
    """
    workspace = Path.home() / "NovaForge" / "projects"
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace


def get_workspace_info() -> Dict[str, Any]:
    """
    Get information about the workspace.
    """
    workspace = get_default_workspace()
    
    try:
        # Count projects in workspace
        projects = [d for d in workspace.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        return {
            "success": True,
            "workspace_path": str(workspace),
            "exists": workspace.exists(),
            "project_count": len(projects),
            "projects": [p.name for p in projects]
        }
    except Exception as e:
        return {
            "success": False,
            "workspace_path": str(workspace),
            "error": str(e)
        }


def create_project_in_workspace(project_name: str, template: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new project in the default workspace.
    Convenience function - user can also specify full paths elsewhere!
    
    Args:
        project_name: Name of the project
        template: Optional template name (python-cli, python-api, etc.)
        
    Returns:
        Dictionary with creation status
    """
    try:
        workspace = get_default_workspace()
        project_path = workspace / project_name
        
        if project_path.exists():
            return {
                "success": False,
                "error": f"Project '{project_name}' already exists in workspace",
                "path": str(project_path)
            }
        
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)
        
        result = {
            "success": True,
            "project_name": project_name,
            "path": str(project_path),
            "created": True
        }
        
        # If template specified, use it
        if template:
            from tools.filesystem.project_templates import create_project_from_template
            template_result = create_project_from_template(template, str(project_path))
            
            if template_result.get("success"):
                result["template_used"] = template
                result["files_created"] = template_result.get("created_files", [])
                result["dirs_created"] = template_result.get("created_dirs", [])
            else:
                result["template_error"] = template_result.get("error")
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def list_workspace_projects() -> Dict[str, Any]:
    """
    List all projects in the default workspace.
    """
    try:
        workspace = get_default_workspace()
        
        projects = []
        for item in workspace.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                try:
                    # Get project info
                    project_info = {
                        "name": item.name,
                        "path": str(item),
                        "modified": item.stat().st_mtime
                    }
                    
                    # Check for common project indicators
                    if (item / "package.json").exists():
                        project_info["type"] = "Node.js"
                    elif (item / "requirements.txt").exists():
                        project_info["type"] = "Python"
                    elif (item / "Cargo.toml").exists():
                        project_info["type"] = "Rust"
                    elif (item / "go.mod").exists():
                        project_info["type"] = "Go"
                    else:
                        project_info["type"] = "Other"
                    
                    projects.append(project_info)
                except:
                    continue
        
        return {
            "success": True,
            "workspace": str(workspace),
            "projects": projects,
            "count": len(projects)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def resolve_project_path(user_input: str) -> str:
    """
    Resolve a project path from user input.
    
    If user specifies a full path (starts with / or ~), use that.
    Otherwise, assume it's a project name in the workspace.
    
    Args:
        user_input: User's input (either full path or project name)
        
    Returns:
        Resolved full path
        
    Examples:
        "/home/user/my-project" -> "/home/user/my-project" (use as-is)
        "~/Desktop/app" -> "/home/user/Desktop/app" (expand ~)
        "my-api" -> "~/NovaForge/projects/my-api" (workspace)
    """
    user_path = user_input.strip()
    
    # If it's a full path or uses ~, use it as-is
    if user_path.startswith('/') or user_path.startswith('~'):
        return str(Path(user_path).expanduser().resolve())
    
    # If it looks like a Windows path
    if len(user_path) > 2 and user_path[1] == ':':
        return str(Path(user_path).resolve())
    
    # Otherwise, treat as project name in workspace
    workspace = get_default_workspace()
    return str(workspace / user_path)


def get_usage_instructions() -> str:
    """
    Get instructions for using the workspace system.
    """
    workspace = get_default_workspace()
    
    return f"""
📁 NovaForge Workspace System

**Default Workspace:** {workspace}
This is a convenient default location for your projects.

**How It Works:**

1️⃣ **Simple Project Names** (use default workspace):
   • "Create a Flask API called my-api"
   → Creates in {workspace}/my-api

2️⃣ **Full Paths** (work anywhere):
   • "Create a React app in ~/Desktop/my-app"
   → Creates in ~/Desktop/my-app
   
   • "Work on /home/bob/projects/existing-app"
   → Works in that exact location

3️⃣ **You're Always in Control:**
   • Just specify where you want things
   • Default workspace is just for convenience
   • You can work ANYWHERE on your system

**Examples:**

✅ In workspace: "Create my-api" 
   → {workspace}/my-api

✅ Custom location: "Create ~/Documents/work/my-api"
   → ~/Documents/work/my-api

✅ Desktop: "Create ~/Desktop/test-app"
   → ~/Desktop/test-app

✅ WSL: "Create /mnt/c/Users/You/Desktop/app"
   → Windows Desktop via WSL

**The workspace is optional - you're the boss! 🎯**
"""
