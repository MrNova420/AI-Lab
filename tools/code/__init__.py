"""Code analysis and inspection tools.

Available functions:
- analyze_file(file_path: str) -> Dict[str, Any]
  Analyze a code file for structure, metrics, and complexity.
  
- find_todos(directory: str) -> Dict[str, Any]
  Find TODO, FIXME, HACK, and XXX comments in code files.
  
- count_lines(directory: str, extensions: List[str] = None) -> Dict[str, Any]
  Count lines of code by file type in a directory.
  
- find_imports(file_path: str) -> Dict[str, Any]
  Extract import statements from a Python file.
  
- check_syntax(file_path: str) -> Dict[str, Any]
  Check Python file syntax without executing the code.

All functions return dictionaries with 'success' status and error handling.
"""
