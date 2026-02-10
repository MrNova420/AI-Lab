"""Git repository integration and management tools."""

from typing import Dict, Any, Optional

try:
    import git
except ImportError:
    git = None


def git_status(repo_path: str) -> Dict[str, Any]:
    """
    Get repository status including modified, staged, and untracked files.
    
    Args:
        repo_path: Path to the git repository
        
    Returns:
        Dictionary with repository status including modified, staged, and untracked files
    """
    if git is None:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": "GitPython not installed. Install with: pip install gitpython"
        }
    
    try:
        # Open repository
        repo = git.Repo(repo_path)
        
        # Get status information
        modified_files = [item.a_path for item in repo.index.diff(None)]
        
        # Check if repository has commits before checking staged files
        try:
            staged_files = [item.a_path for item in repo.index.diff("HEAD")]
        except (git.exc.BadName, ValueError):
            # Repository has no commits yet (empty/new repository)
            staged_files = []
        
        untracked_files = repo.untracked_files
        
        # Check if repository is dirty
        is_dirty = repo.is_dirty(untracked_files=True)
        
        # Get current branch
        try:
            current_branch = repo.active_branch.name
        except TypeError:
            current_branch = "HEAD detached"
        
        return {
            "success": True,
            "repo_path": repo_path,
            "branch": current_branch,
            "is_dirty": is_dirty,
            "modified_files": modified_files[:50],  # Limit to avoid overwhelming output
            "staged_files": staged_files[:50],
            "untracked_files": untracked_files[:50],
            "summary": {
                "modified_count": len(modified_files),
                "staged_count": len(staged_files),
                "untracked_count": len(untracked_files)
            }
        }
        
    except git.exc.InvalidGitRepositoryError:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": "Not a valid git repository"
        }
    except git.exc.NoSuchPathError:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": "Repository path does not exist"
        }
    except Exception as e:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": f"Failed to get git status: {str(e)}"
        }


def git_log(repo_path: str, max_count: int = 10) -> Dict[str, Any]:
    """
    Get recent commit history from the repository.
    
    Args:
        repo_path: Path to the git repository
        max_count: Maximum number of commits to retrieve (default: 10)
        
    Returns:
        Dictionary with commit history including hash, author, date, and message
    """
    try:
        import git
        
        # Open repository
        repo = git.Repo(repo_path)
        
        # Check if repository has commits
        try:
            repo.head.commit
        except (ValueError, git.exc.BadName):
            return {
                "success": True,
                "repo_path": repo_path,
                "commit_count": 0,
                "commits": [],
                "message": "Repository has no commits yet"
            }
        
        # Get commits
        commits = list(repo.iter_commits(max_count=max_count))
        
        # Format commit information
        commit_list = []
        for commit in commits:
            commit_list.append({
                "hash": commit.hexsha[:8],  # Short hash
                "full_hash": commit.hexsha,
                "author": str(commit.author),
                "author_email": commit.author.email,
                "date": commit.committed_datetime.isoformat(),
                "message": commit.message.strip()[:200]  # Limit message length
            })
        
        return {
            "success": True,
            "repo_path": repo_path,
            "commit_count": len(commit_list),
            "commits": commit_list
        }
        
    except git.exc.InvalidGitRepositoryError:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": "Not a valid git repository"
        }
    except git.exc.NoSuchPathError:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": "Repository path does not exist"
        }
    except Exception as e:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": f"Failed to get git log: {str(e)}"
        }


def git_diff(repo_path: str, file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Show diff of changes in the repository or for a specific file.
    
    Args:
        repo_path: Path to the git repository
        file_path: Optional path to a specific file (relative to repo root)
        
    Returns:
        Dictionary with diff information
    """
    try:
        import git
        
        # Open repository
        repo = git.Repo(repo_path)
        
        # Check if repository has commits
        try:
            repo.head.commit
            has_commits = True
        except (ValueError, git.exc.BadName):
            has_commits = False
        
        # Get diff
        if file_path:
            # Diff for specific file
            diff_output = repo.git.diff(file_path) if has_commits else ""
            diff_type = f"file: {file_path}"
        else:
            # Diff for all changes
            diff_output = repo.git.diff() if has_commits else ""
            diff_type = "all changes"
        
        # Get staged diff if there are commits
        if has_commits:
            if file_path:
                staged_diff = repo.git.diff("--cached", file_path)
            else:
                staged_diff = repo.git.diff("--cached")
        else:
            staged_diff = ""
        
        return {
            "success": True,
            "repo_path": repo_path,
            "diff_type": diff_type,
            "has_commits": has_commits,
            "has_unstaged_changes": bool(diff_output),
            "has_staged_changes": bool(staged_diff),
            "unstaged_diff": diff_output[:3000] if diff_output else "No unstaged changes",
            "staged_diff": staged_diff[:3000] if staged_diff else "No staged changes"
        }
        
    except git.exc.InvalidGitRepositoryError:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": "Not a valid git repository"
        }
    except git.exc.GitCommandError as e:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": f"Git command failed: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": f"Failed to get git diff: {str(e)}"
        }


def git_branch_list(repo_path: str) -> Dict[str, Any]:
    """
    List all branches in the repository.
    
    Args:
        repo_path: Path to the git repository
        
    Returns:
        Dictionary with list of local and remote branches
    """
    try:
        import git
        
        # Open repository
        repo = git.Repo(repo_path)
        
        # Get local branches
        local_branches = [branch.name for branch in repo.branches]
        
        # Get remote branches
        remote_branches = []
        try:
            for ref in repo.remotes.origin.refs:
                remote_branches.append(ref.name)
        except AttributeError:
            # No remote named 'origin'
            pass
        
        # Get current branch
        try:
            current_branch = repo.active_branch.name
        except TypeError:
            current_branch = "HEAD detached"
        
        return {
            "success": True,
            "repo_path": repo_path,
            "current_branch": current_branch,
            "local_branches": local_branches[:100],  # Limit output
            "remote_branches": remote_branches[:100],
            "summary": {
                "local_count": len(local_branches),
                "remote_count": len(remote_branches)
            }
        }
        
    except git.exc.InvalidGitRepositoryError:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": "Not a valid git repository"
        }
    except git.exc.NoSuchPathError:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": "Repository path does not exist"
        }
    except Exception as e:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": f"Failed to list branches: {str(e)}"
        }


def git_current_branch(repo_path: str) -> Dict[str, Any]:
    """
    Get the current branch name and additional information.
    
    Args:
        repo_path: Path to the git repository
        
    Returns:
        Dictionary with current branch information
    """
    try:
        import git
        
        # Open repository
        repo = git.Repo(repo_path)
        
        # Get current branch
        try:
            active_branch = repo.active_branch
            branch_name = active_branch.name
            is_detached = False
            
            # Get tracking branch info
            tracking_branch = active_branch.tracking_branch()
            if tracking_branch:
                tracking_info = {
                    "remote": tracking_branch.remote_name,
                    "branch": tracking_branch.remote_head
                }
            else:
                tracking_info = None
            
        except TypeError:
            # HEAD is detached
            try:
                branch_name = repo.head.commit.hexsha[:8]
            except (ValueError, git.exc.BadName):
                branch_name = "No commits yet"
            is_detached = True
            tracking_info = None
        
        # Get HEAD commit info (if any commits exist)
        try:
            head_commit = repo.head.commit
            commit_info = {
                "hash": head_commit.hexsha[:8],
                "full_hash": head_commit.hexsha,
                "author": str(head_commit.author),
                "date": head_commit.committed_datetime.isoformat(),
                "message": head_commit.message.strip()[:200]
            }
        except (ValueError, git.exc.BadName):
            commit_info = None
        
        return {
            "success": True,
            "repo_path": repo_path,
            "branch": branch_name,
            "is_detached": is_detached,
            "tracking_branch": tracking_info,
            "head_commit": commit_info
        }
        
    except git.exc.InvalidGitRepositoryError:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": "Not a valid git repository"
        }
    except git.exc.NoSuchPathError:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": "Repository path does not exist"
        }
    except Exception as e:
        return {
            "success": False,
            "repo_path": repo_path,
            "error": f"Failed to get current branch: {str(e)}"
        }
