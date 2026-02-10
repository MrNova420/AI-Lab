"""
Project Context Analyzer - Understands codebases for intelligent assistance
Similar to how GitHub Copilot understands your project
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import re


class ProjectContextAnalyzer:
    """Analyzes project structure and builds context for AI assistance"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.context = {
            "languages": set(),
            "frameworks": set(),
            "dependencies": {},
            "structure": {},
            "patterns": [],
            "conventions": {},
            "key_files": [],
            "technology_stack": []
        }
    
    def analyze_project(self) -> Dict[str, Any]:
        """Perform comprehensive project analysis"""
        print("🔍 Analyzing project structure...")
        
        # Analyze different aspects
        self._detect_languages()
        self._detect_frameworks()
        self._analyze_dependencies()
        self._analyze_structure()
        self._detect_patterns()
        self._identify_key_files()
        
        return self.get_context_summary()
    
    def _detect_languages(self):
        """Detect programming languages used"""
        language_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'React/JSX',
            '.ts': 'TypeScript',
            '.tsx': 'React/TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.sh': 'Shell',
            '.md': 'Markdown',
            '.json': 'JSON',
            '.yaml': 'YAML',
            '.yml': 'YAML'
        }
        
        file_counts = {}
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '.git', 'venv', '__pycache__', 
                'dist', 'build', '.next', 'target'
            }]
            
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in language_extensions:
                    lang = language_extensions[ext]
                    file_counts[lang] = file_counts.get(lang, 0) + 1
        
        # Add languages with significant presence
        for lang, count in file_counts.items():
            if count >= 3 or lang in ['Python', 'JavaScript', 'TypeScript']:
                self.context["languages"].add(lang)
    
    def _detect_frameworks(self):
        """Detect frameworks and libraries"""
        
        # Check for Python frameworks
        if (self.project_root / "requirements.txt").exists():
            with open(self.project_root / "requirements.txt") as f:
                content = f.read().lower()
                if 'flask' in content:
                    self.context["frameworks"].add('Flask')
                if 'django' in content:
                    self.context["frameworks"].add('Django')
                if 'fastapi' in content:
                    self.context["frameworks"].add('FastAPI')
                if 'pytest' in content:
                    self.context["frameworks"].add('pytest')
        
        # Check for Node.js frameworks
        if (self.project_root / "package.json").exists():
            try:
                with open(self.project_root / "package.json") as f:
                    pkg = json.load(f)
                    deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                    
                    if 'react' in deps:
                        self.context["frameworks"].add('React')
                    if 'vue' in deps:
                        self.context["frameworks"].add('Vue')
                    if 'angular' in deps or '@angular/core' in deps:
                        self.context["frameworks"].add('Angular')
                    if 'next' in deps:
                        self.context["frameworks"].add('Next.js')
                    if 'express' in deps:
                        self.context["frameworks"].add('Express')
                    if 'vite' in deps:
                        self.context["frameworks"].add('Vite')
                    if 'electron' in deps:
                        self.context["frameworks"].add('Electron')
            except:
                pass
        
        # Check for other indicators
        if (self.project_root / "Cargo.toml").exists():
            self.context["frameworks"].add('Rust/Cargo')
        
        if (self.project_root / "go.mod").exists():
            self.context["frameworks"].add('Go Modules')
    
    def _analyze_dependencies(self):
        """Extract key dependencies"""
        
        # Python dependencies
        if (self.project_root / "requirements.txt").exists():
            with open(self.project_root / "requirements.txt") as f:
                self.context["dependencies"]["python"] = [
                    line.strip() for line in f 
                    if line.strip() and not line.startswith('#')
                ][:10]  # Top 10
        
        # Node.js dependencies
        if (self.project_root / "package.json").exists():
            try:
                with open(self.project_root / "package.json") as f:
                    pkg = json.load(f)
                    deps = pkg.get('dependencies', {})
                    self.context["dependencies"]["node"] = list(deps.keys())[:10]
            except:
                pass
    
    def _analyze_structure(self):
        """Analyze project structure"""
        structure = {
            "directories": [],
            "total_files": 0,
            "code_files": 0
        }
        
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.go', '.rs'}
        
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '.git', 'venv', '__pycache__', 
                'dist', 'build', '.next'
            }]
            
            rel_path = Path(root).relative_to(self.project_root)
            if str(rel_path) != '.':
                structure["directories"].append(str(rel_path))
            
            structure["total_files"] += len(files)
            structure["code_files"] += sum(
                1 for f in files if Path(f).suffix in code_extensions
            )
        
        self.context["structure"] = structure
    
    def _detect_patterns(self):
        """Detect common coding patterns and conventions"""
        patterns = []
        
        # Check for common patterns
        if (self.project_root / "tests").exists() or (self.project_root / "test").exists():
            patterns.append("Has test suite")
        
        if (self.project_root / "docs").exists():
            patterns.append("Has documentation")
        
        if (self.project_root / ".github").exists():
            patterns.append("Uses GitHub Actions")
        
        if (self.project_root / "docker-compose.yml").exists():
            patterns.append("Uses Docker Compose")
        
        if (self.project_root / "Dockerfile").exists():
            patterns.append("Has Dockerfile")
        
        if (self.project_root / ".env.example").exists():
            patterns.append("Uses environment variables")
        
        self.context["patterns"] = patterns
    
    def _identify_key_files(self):
        """Identify important files in the project"""
        key_files = []
        
        important_files = [
            'README.md', 'package.json', 'requirements.txt',
            'setup.py', 'pyproject.toml', 'Cargo.toml',
            '.gitignore', 'docker-compose.yml', 'Dockerfile',
            'tsconfig.json', 'webpack.config.js', 'vite.config.js'
        ]
        
        for file in important_files:
            if (self.project_root / file).exists():
                key_files.append(file)
        
        self.context["key_files"] = key_files
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a human-readable context summary"""
        return {
            "languages": list(self.context["languages"]),
            "frameworks": list(self.context["frameworks"]),
            "dependencies": self.context["dependencies"],
            "structure": self.context["structure"],
            "patterns": self.context["patterns"],
            "key_files": self.context["key_files"],
            "technology_stack": self._build_tech_stack()
        }
    
    def _build_tech_stack(self) -> List[str]:
        """Build a technology stack description"""
        stack = []
        
        langs = list(self.context["languages"])
        frameworks = list(self.context["frameworks"])
        
        if langs:
            stack.append(f"Languages: {', '.join(langs)}")
        
        if frameworks:
            stack.append(f"Frameworks: {', '.join(frameworks)}")
        
        if self.context["patterns"]:
            stack.append(f"Features: {', '.join(self.context['patterns'][:3])}")
        
        return stack
    
    def generate_ai_context(self) -> str:
        """Generate context string for AI prompts"""
        context_str = []
        
        context_str.append("📁 **Project Context:**")
        
        if self.context["languages"]:
            langs = ', '.join(list(self.context["languages"])[:5])
            context_str.append(f"  • Languages: {langs}")
        
        if self.context["frameworks"]:
            fw = ', '.join(list(self.context["frameworks"])[:5])
            context_str.append(f"  • Frameworks: {fw}")
        
        if self.context["structure"]:
            struct = self.context["structure"]
            context_str.append(f"  • Files: {struct.get('code_files', 0)} code files")
        
        if self.context["patterns"]:
            context_str.append(f"  • Patterns: {', '.join(self.context['patterns'][:3])}")
        
        return "\n".join(context_str)
    
    def get_file_context(self, file_path: str) -> Dict[str, Any]:
        """Get context for a specific file"""
        full_path = self.project_root / file_path
        
        if not full_path.exists():
            return {"error": "File not found"}
        
        context = {
            "path": file_path,
            "language": self._detect_file_language(file_path),
            "size": full_path.stat().st_size,
            "lines": 0
        }
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                context["lines"] = len(lines)
                
                # Extract imports/includes
                if file_path.endswith('.py'):
                    context["imports"] = self._extract_python_imports(lines)
                elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    context["imports"] = self._extract_js_imports(lines)
        except:
            pass
        
        return context
    
    def _detect_file_language(self, file_path: str) -> str:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower()
        
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'React/JSX',
            '.ts': 'TypeScript',
            '.tsx': 'React/TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.go': 'Go',
            '.rs': 'Rust'
        }
        
        return lang_map.get(ext, 'Unknown')
    
    def _extract_python_imports(self, lines: List[str]) -> List[str]:
        """Extract Python imports"""
        imports = []
        for line in lines[:50]:  # Check first 50 lines
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        return imports
    
    def _extract_js_imports(self, lines: List[str]) -> List[str]:
        """Extract JavaScript/TypeScript imports"""
        imports = []
        for line in lines[:50]:
            line = line.strip()
            if line.startswith('import ') or line.startswith('require('):
                imports.append(line)
        return imports


def analyze_project(project_root: str) -> Dict[str, Any]:
    """Convenience function to analyze a project"""
    analyzer = ProjectContextAnalyzer(project_root)
    return analyzer.analyze_project()


def get_ai_context(project_root: str) -> str:
    """Get AI-ready context string"""
    analyzer = ProjectContextAnalyzer(project_root)
    analyzer.analyze_project()
    return analyzer.generate_ai_context()


if __name__ == "__main__":
    # Test the analyzer
    import sys
    
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"Analyzing project at: {root}\n")
    
    analyzer = ProjectContextAnalyzer(root)
    context = analyzer.analyze_project()
    
    print(json.dumps(context, indent=2, default=str))
    print("\n" + "="*60)
    print("AI Context String:")
    print("="*60)
    print(analyzer.generate_ai_context())
