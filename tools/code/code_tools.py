"""Code analysis and inspection tools."""

import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional


def analyze_file(file_path: str) -> Dict[str, Any]:
    """
    Analyze a code file for structure, metrics, and complexity.
    
    Args:
        file_path: Path to the code file to analyze
        
    Returns:
        Dictionary with file analysis including lines, functions, classes, complexity
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        if not path.is_file():
            return {
                "success": False,
                "error": f"Path is not a file: {file_path}"
            }
        
        # Read file content
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "File is not a text file or has incompatible encoding"
            }
        
        lines = content.splitlines()
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = 0
        code_lines = total_lines - blank_lines
        
        result = {
            "success": True,
            "file_path": str(path),
            "total_lines": total_lines,
            "blank_lines": blank_lines,
            "code_lines": code_lines,
            "file_size": path.stat().st_size,
            "extension": path.suffix
        }
        
        # Python-specific analysis using AST
        if path.suffix == '.py':
            try:
                tree = ast.parse(content)
                
                functions = []
                classes = []
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append({
                            "name": node.name,
                            "line": node.lineno,
                            "args": len(node.args.args),
                            "is_async": isinstance(node, ast.AsyncFunctionDef)
                        })
                    elif isinstance(node, ast.ClassDef):
                        classes.append({
                            "name": node.name,
                            "line": node.lineno,
                            "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                        })
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name)
                        elif node.module:
                            imports.append(node.module)
                
                # Count comment lines for Python
                comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
                
                result.update({
                    "functions": functions[:100],  # Limit output
                    "function_count": len(functions),
                    "classes": classes[:100],
                    "class_count": len(classes),
                    "imports": list(set(imports))[:50],
                    "import_count": len(set(imports)),
                    "comment_lines": comment_lines,
                    "code_lines": total_lines - blank_lines - comment_lines
                })
                
            except SyntaxError as e:
                result["syntax_error"] = f"Line {e.lineno}: {e.msg}"
        
        # Shell script analysis
        elif path.suffix == '.sh':
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            function_pattern = re.compile(r'^\s*(\w+)\s*\(\s*\)\s*\{', re.MULTILINE)
            functions = function_pattern.findall(content)
            
            result.update({
                "comment_lines": comment_lines,
                "code_lines": total_lines - blank_lines - comment_lines,
                "function_count": len(functions),
                "functions": functions[:100]
            })
        
        # JavaScript/TypeScript analysis
        elif path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
            comment_lines = sum(1 for line in lines 
                               if line.strip().startswith('//') or 
                                  line.strip().startswith('/*') or 
                                  line.strip().startswith('*'))
            
            # Basic function/class detection
            func_pattern = re.compile(r'(?:function\s+\w+|const\s+\w+\s*=\s*(?:async\s*)?\(|let\s+\w+\s*=\s*\(|var\s+\w+\s*=\s*\()', re.MULTILINE)
            class_pattern = re.compile(r'class\s+(\w+)', re.MULTILINE)
            
            functions = func_pattern.findall(content)
            classes = class_pattern.findall(content)
            
            result.update({
                "comment_lines": comment_lines,
                "code_lines": total_lines - blank_lines - comment_lines,
                "function_count": len(functions),
                "class_count": len(classes),
                "classes": classes[:50]
            })
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error analyzing file: {str(e)}"
        }


def find_todos(directory: str) -> Dict[str, Any]:
    """
    Find TODO, FIXME, HACK, and XXX comments in code files.
    
    Args:
        directory: Directory to search for TODO comments
        
    Returns:
        Dictionary with found TODO/FIXME comments organized by file
    """
    try:
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {
                "success": False,
                "error": f"Directory not found: {directory}"
            }
        
        if not dir_path.is_dir():
            return {
                "success": False,
                "error": f"Path is not a directory: {directory}"
            }
        
        # Patterns to search for
        todo_pattern = re.compile(
            r'(?:#|//|/\*|\*|<!--|;)\s*(TODO|FIXME|HACK|XXX|NOTE|BUG)[\s:]*(.+)',
            re.IGNORECASE
        )
        
        # File extensions to search
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', 
            '.hpp', '.cs', '.rb', '.go', '.rs', '.php', '.swift', '.kt', '.sh',
            '.bash', '.yml', '.yaml', '.xml', '.html', '.css', '.scss', '.md'
        }
        
        todos = {}
        total_found = 0
        max_results = 500  # Limit total results
        
        # Search through files
        for file_path in dir_path.rglob('*'):
            if total_found >= max_results:
                break
                
            if file_path.is_file() and file_path.suffix in code_extensions:
                # Skip hidden files and common directories to ignore
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if any(d in file_path.parts for d in ['node_modules', 'venv', '__pycache__', '.git']):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if total_found >= max_results:
                                break
                            
                            match = todo_pattern.search(line)
                            if match:
                                tag, message = match.groups()
                                rel_path = str(file_path.relative_to(dir_path))
                                
                                if rel_path not in todos:
                                    todos[rel_path] = []
                                
                                todos[rel_path].append({
                                    "line": line_num,
                                    "tag": tag.upper(),
                                    "message": message.strip()[:200]  # Limit message length
                                })
                                total_found += 1
                
                except (UnicodeDecodeError, PermissionError):
                    continue  # Skip files we can't read
        
        return {
            "success": True,
            "directory": str(dir_path),
            "total_found": total_found,
            "file_count": len(todos),
            "todos": todos,
            "truncated": total_found >= max_results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error searching for TODOs: {str(e)}"
        }


def count_lines(directory: str, extensions: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Count lines of code by file type in a directory.
    
    Args:
        directory: Directory to count lines in
        extensions: List of file extensions to include (e.g., ['.py', '.js'])
                   If None, counts all text files
        
    Returns:
        Dictionary with line counts by file type and totals
    """
    try:
        dir_path = Path(directory)
        
        if not dir_path.exists():
            return {
                "success": False,
                "error": f"Directory not found: {directory}"
            }
        
        if not dir_path.is_dir():
            return {
                "success": False,
                "error": f"Path is not a directory: {directory}"
            }
        
        # Default code extensions if none provided
        if extensions is None:
            extensions = [
                '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
                '.hpp', '.cs', '.rb', '.go', '.rs', '.php', '.swift', '.kt', '.sh',
                '.bash', '.html', '.css', '.scss', '.sass', '.less', '.sql', '.r'
            ]
        
        stats_by_extension = {}
        total_files = 0
        total_lines = 0
        total_blank = 0
        total_code = 0
        
        max_files = 5000  # Limit number of files to process
        
        # Process files
        for file_path in dir_path.rglob('*'):
            if total_files >= max_files:
                break
            
            if not file_path.is_file():
                continue
            
            # Skip hidden files and common directories to ignore
            if any(part.startswith('.') for part in file_path.parts):
                continue
            if any(d in file_path.parts for d in ['node_modules', 'venv', '__pycache__', '.git', 'build', 'dist']):
                continue
            
            ext = file_path.suffix
            if ext not in extensions:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                file_total = len(lines)
                file_blank = sum(1 for line in lines if not line.strip())
                file_code = file_total - file_blank
                
                if ext not in stats_by_extension:
                    stats_by_extension[ext] = {
                        "files": 0,
                        "total_lines": 0,
                        "blank_lines": 0,
                        "code_lines": 0
                    }
                
                stats_by_extension[ext]["files"] += 1
                stats_by_extension[ext]["total_lines"] += file_total
                stats_by_extension[ext]["blank_lines"] += file_blank
                stats_by_extension[ext]["code_lines"] += file_code
                
                total_files += 1
                total_lines += file_total
                total_blank += file_blank
                total_code += file_code
                
            except (UnicodeDecodeError, PermissionError):
                continue  # Skip files we can't read
        
        # Sort by code lines
        sorted_stats = dict(sorted(
            stats_by_extension.items(),
            key=lambda x: x[1]["code_lines"],
            reverse=True
        ))
        
        return {
            "success": True,
            "directory": str(dir_path),
            "total_files": total_files,
            "total_lines": total_lines,
            "blank_lines": total_blank,
            "code_lines": total_code,
            "by_extension": sorted_stats,
            "truncated": total_files >= max_files
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error counting lines: {str(e)}"
        }


def find_imports(file_path: str) -> Dict[str, Any]:
    """
    Extract import statements from a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Dictionary with import information including modules and from imports
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        if not path.is_file():
            return {
                "success": False,
                "error": f"Path is not a file: {file_path}"
            }
        
        if path.suffix != '.py':
            return {
                "success": False,
                "error": f"File is not a Python file: {file_path}"
            }
        
        # Read and parse file
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "File encoding is not supported"
            }
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error in file at line {e.lineno}: {e.msg}"
            }
        
        imports = []
        from_imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "module": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    from_imports.append({
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno,
                        "level": node.level
                    })
        
        # Categorize imports
        stdlib_modules = set()
        third_party = set()
        local_imports = set()
        
        for imp in imports:
            module = imp["module"].split('.')[0]
            try:
                __import__(module)
                stdlib_modules.add(module)
            except ImportError:
                third_party.add(module)
        
        for imp in from_imports:
            if imp["level"] > 0:  # Relative import
                local_imports.add(imp["module"] if imp["module"] else ".")
            else:
                module = imp["module"].split('.')[0]
                try:
                    __import__(module)
                    stdlib_modules.add(module)
                except ImportError:
                    third_party.add(module)
        
        return {
            "success": True,
            "file_path": str(path),
            "imports": imports[:100],  # Limit output
            "from_imports": from_imports[:100],
            "total_imports": len(imports),
            "total_from_imports": len(from_imports),
            "stdlib_modules": sorted(list(stdlib_modules))[:50],
            "third_party_modules": sorted(list(third_party))[:50],
            "local_imports": sorted(list(local_imports))[:50]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error extracting imports: {str(e)}"
        }


def check_syntax(file_path: str) -> Dict[str, Any]:
    """
    Check Python file syntax without executing the code.
    
    Args:
        file_path: Path to the Python file to check
        
    Returns:
        Dictionary with syntax check results
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        if not path.is_file():
            return {
                "success": False,
                "error": f"Path is not a file: {file_path}"
            }
        
        if path.suffix != '.py':
            return {
                "success": False,
                "error": f"File is not a Python file: {file_path}"
            }
        
        # Read file
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return {
                "success": False,
                "error": "File encoding is not supported"
            }
        
        # Try to parse the file
        try:
            tree = ast.parse(content, filename=str(path))
            
            # Basic validation
            line_count = len(content.splitlines())
            
            return {
                "success": True,
                "file_path": str(path),
                "valid": True,
                "message": "Syntax is valid",
                "line_count": line_count,
                "ast_nodes": len(list(ast.walk(tree)))
            }
            
        except SyntaxError as e:
            return {
                "success": True,
                "file_path": str(path),
                "valid": False,
                "error_type": "SyntaxError",
                "line": e.lineno,
                "column": e.offset,
                "message": e.msg,
                "text": e.text.strip() if e.text else None
            }
        except Exception as e:
            return {
                "success": True,
                "file_path": str(path),
                "valid": False,
                "error_type": type(e).__name__,
                "message": str(e)
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error checking syntax: {str(e)}"
        }
