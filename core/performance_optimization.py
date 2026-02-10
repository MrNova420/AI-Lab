"""
Performance Optimizations for Development Capabilities
Caching, efficiency, and resource management
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib


class PerformanceCache:
    """High-performance caching system for development features"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".novaforge" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for speed
        self.memory_cache = {}
        self.cache_ttl = {}  # Time-to-live tracking
        
        # Default TTLs (in seconds)
        self.default_ttls = {
            "project_context": 300,      # 5 minutes
            "file_analysis": 60,          # 1 minute
            "git_status": 10,             # 10 seconds
            "tool_results": 30,           # 30 seconds
            "workflow_results": 120       # 2 minutes
        }
    
    def get(self, cache_type: str, key: str) -> Optional[Any]:
        """Get from cache with TTL check"""
        cache_key = f"{cache_type}:{key}"
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            ttl_key = f"{cache_key}:ttl"
            if ttl_key in self.cache_ttl:
                if time.time() < self.cache_ttl[ttl_key]:
                    return self.memory_cache[cache_key]
                else:
                    # Expired, remove
                    del self.memory_cache[cache_key]
                    del self.cache_ttl[ttl_key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{self._hash_key(cache_key)}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    
                if time.time() < data.get('expires_at', 0):
                    # Cache hit, load to memory
                    self.memory_cache[cache_key] = data['value']
                    self.cache_ttl[f"{cache_key}:ttl"] = data['expires_at']
                    return data['value']
                else:
                    # Expired, remove file
                    cache_file.unlink()
            except:
                pass
        
        return None
    
    def set(self, cache_type: str, key: str, value: Any, ttl: Optional[int] = None):
        """Set cache with TTL"""
        cache_key = f"{cache_type}:{key}"
        
        if ttl is None:
            ttl = self.default_ttls.get(cache_type, 60)
        
        expires_at = time.time() + ttl
        
        # Store in memory
        self.memory_cache[cache_key] = value
        self.cache_ttl[f"{cache_key}:ttl"] = expires_at
        
        # Store on disk for persistence
        cache_file = self.cache_dir / f"{self._hash_key(cache_key)}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'value': value,
                    'expires_at': expires_at,
                    'cached_at': time.time()
                }, f)
        except:
            pass
    
    def invalidate(self, cache_type: str, key: Optional[str] = None):
        """Invalidate cache entries"""
        if key:
            cache_key = f"{cache_type}:{key}"
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            
            ttl_key = f"{cache_key}:ttl"
            if ttl_key in self.cache_ttl:
                del self.cache_ttl[ttl_key]
            
            cache_file = self.cache_dir / f"{self._hash_key(cache_key)}.json"
            if cache_file.exists():
                cache_file.unlink()
        else:
            # Invalidate all of this type
            keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(f"{cache_type}:")]
            for k in keys_to_remove:
                del self.memory_cache[k]
                ttl_key = f"{k}:ttl"
                if ttl_key in self.cache_ttl:
                    del self.cache_ttl[ttl_key]
    
    def clear_all(self):
        """Clear all caches"""
        self.memory_cache.clear()
        self.cache_ttl.clear()
        
        # Clear disk cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
            except:
                pass
    
    def _hash_key(self, key: str) -> str:
        """Hash key for filename"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "memory_entries": len(self.memory_cache),
            "disk_entries": len(list(self.cache_dir.glob("*.json"))),
            "cache_types": list(set(k.split(':')[0] for k in self.memory_cache.keys()))
        }


# Global cache instance
_global_cache = None

def get_cache() -> PerformanceCache:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = PerformanceCache()
    return _global_cache


class OptimizedProjectContext:
    """Optimized project context with caching"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.cache = get_cache()
        self._cache_key = str(self.project_root.absolute())
    
    def get_context(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get project context with caching"""
        
        if not force_refresh:
            cached = self.cache.get("project_context", self._cache_key)
            if cached:
                return cached
        
        # Analyze project
        from core.project_context import ProjectContextAnalyzer
        
        analyzer = ProjectContextAnalyzer(str(self.project_root))
        context = analyzer.analyze_project()
        
        # Cache result
        self.cache.set("project_context", self._cache_key, context)
        
        return context
    
    def get_ai_context(self, force_refresh: bool = False) -> str:
        """Get AI context string with caching"""
        cache_key = f"{self._cache_key}:ai"
        
        if not force_refresh:
            cached = self.cache.get("project_context", cache_key)
            if cached:
                return cached
        
        from core.project_context import get_ai_context
        
        context = get_ai_context(str(self.project_root))
        self.cache.set("project_context", cache_key, context)
        
        return context
    
    def invalidate(self):
        """Invalidate cached context"""
        self.cache.invalidate("project_context", self._cache_key)
        self.cache.invalidate("project_context", f"{self._cache_key}:ai")


class OptimizedWorkflowExecutor:
    """Optimized workflow execution with intelligent caching"""
    
    def __init__(self, tool_executor, project_root: str):
        from core.development_workflows import DevelopmentWorkflow
        
        self.workflow = DevelopmentWorkflow(tool_executor, project_root)
        self.cache = get_cache()
        self.project_root = project_root
    
    def execute_workflow(self, workflow_name: str, params: Dict[str, Any], 
                        use_cache: bool = True) -> Dict[str, Any]:
        """Execute workflow with optional caching"""
        
        # Create cache key from workflow and params
        cache_key = f"{workflow_name}:{json.dumps(params, sort_keys=True)}"
        
        if use_cache:
            cached = self.cache.get("workflow_results", cache_key)
            if cached:
                cached['from_cache'] = True
                return cached
        
        # Execute workflow
        result = self.workflow.execute_workflow(workflow_name, params)
        
        # Cache result
        if use_cache:
            self.cache.set("workflow_results", cache_key, result)
        
        result['from_cache'] = False
        return result


class BatchOperationOptimizer:
    """Optimize batch operations for better performance"""
    
    def __init__(self, tool_executor):
        self.tool_executor = tool_executor
        self.cache = get_cache()
    
    def analyze_multiple_files(self, file_paths: list) -> Dict[str, Any]:
        """Analyze multiple files efficiently"""
        results = {}
        
        for file_path in file_paths:
            # Check cache first
            cached = self.cache.get("file_analysis", file_path)
            if cached:
                results[file_path] = cached
                continue
            
            # Analyze file
            result = self.tool_executor.execute_tool("analyze_file", {"file_path": file_path})
            
            if result.get("status") == "success":
                analysis = result.get("result", {})
                results[file_path] = analysis
                
                # Cache result
                self.cache.set("file_analysis", file_path, analysis)
        
        return results
    
    def check_multiple_syntax(self, file_paths: list) -> Dict[str, Any]:
        """Check syntax of multiple Python files efficiently"""
        results = {}
        
        python_files = [f for f in file_paths if f.endswith('.py')]
        
        for file_path in python_files:
            cached = self.cache.get("syntax_check", file_path)
            if cached:
                results[file_path] = cached
                continue
            
            result = self.tool_executor.execute_tool("check_syntax", {"file_path": file_path})
            
            if result.get("status") == "success":
                syntax_result = result.get("result", {})
                results[file_path] = syntax_result
                self.cache.set("syntax_check", file_path, syntax_result, ttl=30)
        
        return results


class IntelligentResourceManager:
    """Manage resources intelligently during development operations"""
    
    def __init__(self):
        self.operation_history = []
        self.max_history = 100
    
    def should_use_cache(self, operation_type: str, params: Dict[str, Any]) -> bool:
        """Decide if caching should be used based on context"""
        
        # Always cache expensive operations
        expensive_ops = ["analyze_codebase", "count_lines", "find_todos"]
        if operation_type in expensive_ops:
            return True
        
        # Cache file operations if file hasn't changed recently
        if operation_type in ["analyze_file", "check_syntax"]:
            # In production, would check file modification time
            return True
        
        # Don't cache git status (changes frequently)
        if operation_type == "git_status":
            return False
        
        return True
    
    def optimize_tool_sequence(self, tools: list) -> list:
        """Optimize sequence of tool executions"""
        
        # Reorder for efficiency
        # 1. Quick operations first
        # 2. Group similar operations
        # 3. Cache-friendly ordering
        
        quick_ops = []
        analysis_ops = []
        git_ops = []
        other_ops = []
        
        for tool in tools:
            if tool.startswith("git_"):
                git_ops.append(tool)
            elif tool in ["analyze_file", "check_syntax", "find_imports"]:
                analysis_ops.append(tool)
            elif tool in ["datetime", "system_info"]:
                quick_ops.append(tool)
            else:
                other_ops.append(tool)
        
        # Optimal order: quick -> git -> analysis -> others
        return quick_ops + git_ops + analysis_ops + other_ops
    
    def record_operation(self, operation: str, duration: float):
        """Record operation for performance tracking"""
        self.operation_history.append({
            "operation": operation,
            "duration": duration,
            "timestamp": time.time()
        })
        
        if len(self.operation_history) > self.max_history:
            self.operation_history.pop(0)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.operation_history:
            return {"message": "No operations recorded yet"}
        
        total_time = sum(op['duration'] for op in self.operation_history)
        avg_time = total_time / len(self.operation_history)
        
        # Group by operation type
        by_type = {}
        for op in self.operation_history:
            op_type = op['operation']
            if op_type not in by_type:
                by_type[op_type] = []
            by_type[op_type].append(op['duration'])
        
        stats = {
            "total_operations": len(self.operation_history),
            "total_time": round(total_time, 2),
            "average_time": round(avg_time, 3),
            "by_type": {
                op_type: {
                    "count": len(times),
                    "avg": round(sum(times) / len(times), 3),
                    "total": round(sum(times), 2)
                }
                for op_type, times in by_type.items()
            }
        }
        
        return stats


# Global resource manager
_resource_manager = None

def get_resource_manager() -> IntelligentResourceManager:
    """Get global resource manager"""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = IntelligentResourceManager()
    return _resource_manager


def clear_all_caches():
    """Clear all development caches"""
    cache = get_cache()
    cache.clear_all()
    print("✅ All caches cleared")


def get_cache_stats():
    """Get cache statistics"""
    cache = get_cache()
    return cache.get_stats()
