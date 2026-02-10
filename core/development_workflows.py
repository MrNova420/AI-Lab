"""
Development Workflow Automation
Orchestrates tools for common development workflows like Copilot/Claude
"""

from typing import Dict, List, Any, Optional
import json


class DevelopmentWorkflow:
    """Manages development workflows and tool orchestration"""
    
    def __init__(self, tool_executor, project_root: str):
        self.tool_executor = tool_executor
        self.project_root = project_root
        self.workflow_history = []
    
    def execute_workflow(self, workflow_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a predefined workflow"""
        
        workflows = {
            "analyze_codebase": self.workflow_analyze_codebase,
            "implement_feature": self.workflow_implement_feature,
            "fix_bug": self.workflow_fix_bug,
            "refactor_code": self.workflow_refactor_code,
            "write_tests": self.workflow_write_tests,
            "code_review": self.workflow_code_review,
            "project_setup": self.workflow_project_setup
        }
        
        workflow_func = workflows.get(workflow_name)
        if workflow_func:
            return workflow_func(params)
        else:
            return {"error": f"Unknown workflow: {workflow_name}"}
    
    def workflow_analyze_codebase(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze codebase workflow"""
        
        results = {
            "workflow": "analyze_codebase",
            "steps": [],
            "findings": {}
        }
        
        # Step 1: Get project context
        try:
            from core.project_context import ProjectContextAnalyzer
            analyzer = ProjectContextAnalyzer(self.project_root)
            context = analyzer.analyze_project()
            results["steps"].append({"step": "project_analysis", "status": "success"})
            results["findings"]["project_context"] = context
        except Exception as e:
            results["steps"].append({"step": "project_analysis", "status": "failed", "error": str(e)})
        
        # Step 2: Find TODOs
        if self.tool_executor:
            todo_result = self.tool_executor.execute_tool("find_todos", {"directory": self.project_root})
            if todo_result.get("status") == "success":
                results["steps"].append({"step": "find_todos", "status": "success"})
                results["findings"]["todos"] = todo_result.get("result", {}).get("todos", [])
        
        # Step 3: Count lines of code
        if self.tool_executor:
            loc_result = self.tool_executor.execute_tool("count_lines", {"directory": self.project_root})
            if loc_result.get("status") == "success":
                results["steps"].append({"step": "count_lines", "status": "success"})
                results["findings"]["code_stats"] = loc_result.get("result", {})
        
        return results
    
    def workflow_implement_feature(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Implement feature workflow"""
        
        feature_name = params.get("feature_name", "New Feature")
        files = params.get("files", [])
        
        results = {
            "workflow": "implement_feature",
            "feature": feature_name,
            "steps": [],
            "recommendations": []
        }
        
        # Step 1: Check Git status
        if self.tool_executor:
            git_status = self.tool_executor.execute_tool("git_status", {"repo_path": self.project_root})
            if git_status.get("status") == "success":
                results["steps"].append({"step": "git_status", "status": "success"})
                results["git_info"] = git_status.get("result", {})
                
                # Recommend creating a branch if not on one
                if git_status.get("result", {}).get("branch") == "main":
                    results["recommendations"].append("Consider creating a feature branch")
        
        # Step 2: Analyze files to modify
        for file_path in files:
            if self.tool_executor:
                analysis = self.tool_executor.execute_tool("analyze_file", {"file_path": file_path})
                if analysis.get("status") == "success":
                    results["steps"].append({"step": f"analyze_{file_path}", "status": "success"})
        
        results["recommendations"].append("Write code incrementally")
        results["recommendations"].append("Test after each change")
        results["recommendations"].append("Commit frequently with clear messages")
        
        return results
    
    def workflow_fix_bug(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Bug fix workflow"""
        
        bug_description = params.get("description", "Bug")
        file_path = params.get("file_path")
        
        results = {
            "workflow": "fix_bug",
            "bug": bug_description,
            "steps": [],
            "analysis": {}
        }
        
        # Step 1: Analyze the problematic file
        if file_path and self.tool_executor:
            analysis = self.tool_executor.execute_tool("analyze_file", {"file_path": file_path})
            if analysis.get("status") == "success":
                results["steps"].append({"step": "analyze_file", "status": "success"})
                results["analysis"]["file_info"] = analysis.get("result", {})
            
            # Step 2: Check syntax
            if file_path.endswith('.py'):
                syntax_check = self.tool_executor.execute_tool("check_syntax", {"file_path": file_path})
                if syntax_check.get("status") == "success":
                    results["steps"].append({"step": "check_syntax", "status": "success"})
                    results["analysis"]["syntax"] = syntax_check.get("result", {})
        
        # Step 3: Look for related TODOs/FIXMEs
        if file_path and self.tool_executor:
            import os
            directory = os.path.dirname(file_path) or "."
            todos = self.tool_executor.execute_tool("find_todos", {"directory": directory})
            if todos.get("status") == "success":
                results["steps"].append({"step": "find_todos", "status": "success"})
                results["analysis"]["related_todos"] = todos.get("result", {}).get("todos", [])[:5]
        
        results["recommendations"] = [
            "Understand the root cause before fixing",
            "Add tests to prevent regression",
            "Consider edge cases",
            "Document the fix"
        ]
        
        return results
    
    def workflow_refactor_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Code refactoring workflow"""
        
        file_path = params.get("file_path")
        goal = params.get("goal", "improve code quality")
        
        results = {
            "workflow": "refactor_code",
            "file": file_path,
            "goal": goal,
            "steps": [],
            "analysis": {}
        }
        
        # Step 1: Analyze current code
        if file_path and self.tool_executor:
            analysis = self.tool_executor.execute_tool("analyze_file", {"file_path": file_path})
            if analysis.get("status") == "success":
                results["steps"].append({"step": "analyze_before", "status": "success"})
                results["analysis"]["before"] = analysis.get("result", {})
        
        # Step 2: Check for imports (if Python)
        if file_path and file_path.endswith('.py') and self.tool_executor:
            imports = self.tool_executor.execute_tool("find_imports", {"file_path": file_path})
            if imports.get("status") == "success":
                results["steps"].append({"step": "analyze_imports", "status": "success"})
                results["analysis"]["imports"] = imports.get("result", {})
        
        results["recommendations"] = [
            "Maintain functionality during refactoring",
            "Run tests before and after",
            "Refactor in small increments",
            "Update documentation",
            "Consider backward compatibility"
        ]
        
        return results
    
    def workflow_write_tests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test writing workflow"""
        
        file_path = params.get("file_path")
        
        results = {
            "workflow": "write_tests",
            "file": file_path,
            "steps": [],
            "recommendations": []
        }
        
        # Step 1: Analyze code to test
        if file_path and self.tool_executor:
            analysis = self.tool_executor.execute_tool("analyze_file", {"file_path": file_path})
            if analysis.get("status") == "success":
                results["steps"].append({"step": "analyze_code", "status": "success"})
                code_info = analysis.get("result", {})
                results["code_info"] = code_info
                
                # Provide specific guidance based on code
                func_count = code_info.get("function_count", 0)
                class_count = code_info.get("class_count", 0)
                
                if func_count > 0:
                    results["recommendations"].append(f"Write tests for {func_count} functions")
                if class_count > 0:
                    results["recommendations"].append(f"Write tests for {class_count} classes")
        
        results["recommendations"].extend([
            "Test happy path scenarios",
            "Test edge cases",
            "Test error handling",
            "Aim for high coverage",
            "Make tests clear and maintainable"
        ])
        
        return results
    
    def workflow_code_review(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Code review workflow"""
        
        files = params.get("files", [])
        
        results = {
            "workflow": "code_review",
            "files_reviewed": len(files),
            "steps": [],
            "findings": []
        }
        
        for file_path in files[:5]:  # Limit to 5 files
            if self.tool_executor:
                # Analyze file
                analysis = self.tool_executor.execute_tool("analyze_file", {"file_path": file_path})
                if analysis.get("status") == "success":
                    results["steps"].append({"step": f"review_{file_path}", "status": "success"})
                    
                    code_info = analysis.get("result", {})
                    
                    # Check for issues
                    if code_info.get("total_lines", 0) > 500:
                        results["findings"].append({
                            "file": file_path,
                            "issue": "File is very large (>500 lines)",
                            "suggestion": "Consider breaking into smaller modules"
                        })
                    
                    if code_info.get("function_count", 0) > 20:
                        results["findings"].append({
                            "file": file_path,
                            "issue": "Many functions in one file",
                            "suggestion": "Consider organizing into classes or modules"
                        })
                
                # Check syntax if Python
                if file_path.endswith('.py'):
                    syntax = self.tool_executor.execute_tool("check_syntax", {"file_path": file_path})
                    if syntax.get("status") == "success":
                        if not syntax.get("result", {}).get("valid", True):
                            results["findings"].append({
                                "file": file_path,
                                "issue": "Syntax error detected",
                                "suggestion": "Fix syntax errors before proceeding"
                            })
        
        return results
    
    def workflow_project_setup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Project setup/initialization workflow"""
        
        results = {
            "workflow": "project_setup",
            "steps": [],
            "setup_complete": False
        }
        
        # Analyze project
        try:
            from core.project_context import ProjectContextAnalyzer
            analyzer = ProjectContextAnalyzer(self.project_root)
            context = analyzer.analyze_project()
            results["steps"].append({"step": "analyze_project", "status": "success"})
            results["project_info"] = context
            
            # Check Git
            if self.tool_executor:
                git_status = self.tool_executor.execute_tool("git_status", {"repo_path": self.project_root})
                if git_status.get("status") == "success":
                    results["steps"].append({"step": "check_git", "status": "success"})
                    results["git_initialized"] = True
            
            results["setup_complete"] = True
            results["recommendations"] = [
                "Project structure looks good",
                "Git repository initialized",
                "Ready for development"
            ]
            
        except Exception as e:
            results["steps"].append({"step": "setup", "status": "failed", "error": str(e)})
        
        return results


def get_workflow_recommendations(task_description: str) -> List[str]:
    """Get workflow recommendations based on task description"""
    
    task_lower = task_description.lower()
    
    if any(word in task_lower for word in ["bug", "fix", "error", "issue"]):
        return ["fix_bug"]
    
    if any(word in task_lower for word in ["feature", "implement", "add", "create"]):
        return ["implement_feature"]
    
    if any(word in task_lower for word in ["refactor", "improve", "clean", "optimize"]):
        return ["refactor_code"]
    
    if any(word in task_lower for word in ["test", "testing", "unittest"]):
        return ["write_tests"]
    
    if any(word in task_lower for word in ["review", "check", "audit"]):
        return ["code_review"]
    
    if any(word in task_lower for word in ["analyze", "understand", "explore"]):
        return ["analyze_codebase"]
    
    return ["analyze_codebase"]  # Default
