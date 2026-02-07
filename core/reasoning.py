"""
NovaForge Reasoning & Context Layer - ENHANCED VERSION
Provides intelligent context management, multi-step reasoning, and learning
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pickle

class ContextMemory:
    """Stores context from tools and conversations with persistence"""
    
    def __init__(self, max_size=20, session_dir=None):
        self.max_size = max_size
        self.tool_history = []  # Recent tool executions
        self.facts = {}  # Known facts (e.g., "system_os": "Ubuntu 24.04")
        self.session_start = time.time()
        self.conversation_history = []  # Full conversation for context
        self.user_preferences = {}  # Learned preferences
        self.session_dir = session_dir or Path(__file__).parent.parent / "memory" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def add_tool_result(self, tool_name: str, params: Dict, result: Dict):
        """Store a tool execution result"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'tool': tool_name,
            'params': params,
            'result': result,
            'success': result.get('success', False),
            'execution_time': result.get('execution_time', 0)
        }
        
        self.tool_history.append(entry)
        
        # Keep only last N entries
        if len(self.tool_history) > self.max_size:
            self.tool_history.pop(0)
        
        # Extract and store facts
        self._extract_facts(tool_name, result)
    
    def add_conversation_turn(self, user_msg: str, ai_msg: str, tools_used: List[str]):
        """Store a conversation turn"""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_msg,
            'assistant': ai_msg,
            'tools': tools_used
        })
        
        # Keep last 50 turns
        if len(self.conversation_history) > 50:
            self.conversation_history.pop(0)
    
    def _extract_facts(self, tool_name: str, result: Dict):
        """Extract important facts from tool results"""
        if tool_name == 'system_info' and result.get('success'):
            self.facts['system_os'] = result.get('os')
            self.facts['system_cpu'] = result.get('cpu')
            self.facts['system_ram'] = result.get('memory_gb')
            self.facts['system_kernel'] = result.get('kernel')
            self.facts['system_arch'] = result.get('architecture')
        
        elif tool_name == 'datetime' and result.get('success'):
            self.facts['current_date'] = result.get('date')
            self.facts['current_time'] = result.get('time')
            self.facts['timezone'] = result.get('timezone')
        
        elif tool_name == 'user_info' and result.get('success'):
            self.facts['username'] = result.get('username')
            self.facts['home_dir'] = result.get('home_dir')
            self.facts['shell'] = result.get('shell')
    
    def get_context_summary(self, detailed=False) -> str:
        """Get a summary of current context for AI"""
        summary = []
        
        # Add known facts
        if self.facts:
            summary.append("**Known Facts:**")
            if detailed:
                for key, value in self.facts.items():
                    summary.append(f"  - {key}: {value}")
            else:
                # Just highlight key facts
                if 'system_os' in self.facts:
                    summary.append(f"  - System: {self.facts['system_os']}")
                if 'current_date' in self.facts:
                    summary.append(f"  - Date: {self.facts['current_date']}")
        
        # Add recent tool executions
        if self.tool_history and detailed:
            summary.append("\n**Recent Actions (last 5):**")
            for entry in self.tool_history[-5:]:
                tool = entry['tool']
                success = "✅" if entry['success'] else "❌"
                time_ago = self._time_ago(entry['timestamp'])
                summary.append(f"  {success} {tool} ({time_ago})")
        
        # Add conversation context
        if self.conversation_history and detailed:
            summary.append(f"\n**Conversation: {len(self.conversation_history)} turns**")
        
        return "\n".join(summary) if summary else "No context yet"
    
    def _time_ago(self, timestamp_str: str) -> str:
        """Convert timestamp to 'X seconds ago' format"""
        ts = datetime.fromisoformat(timestamp_str).timestamp()
        diff = time.time() - ts
        if diff < 60:
            return f"{int(diff)}s ago"
        elif diff < 3600:
            return f"{int(diff/60)}m ago"
        else:
            return f"{int(diff/3600)}h ago"
    
    def get_fact(self, key: str) -> Optional[Any]:
        """Retrieve a stored fact"""
        return self.facts.get(key)
    
    def has_recent_tool(self, tool_name: str, max_age_seconds: int = 60) -> bool:
        """Check if a tool was recently used"""
        current_time = time.time()
        for entry in reversed(self.tool_history):
            if entry['tool'] == tool_name:
                entry_time = datetime.fromisoformat(entry['timestamp']).timestamp()
                if current_time - entry_time < max_age_seconds:
                    return True
        return False
    
    def save_session(self, session_id: str):
        """Save session to disk"""
        session_file = self.session_dir / f"{session_id}.pkl"
        with open(session_file, 'wb') as f:
            pickle.dump({
                'facts': self.facts,
                'tool_history': self.tool_history,
                'conversation_history': self.conversation_history,
                'user_preferences': self.user_preferences
            }, f)
    
    def load_session(self, session_id: str) -> bool:
        """Load session from disk"""
        session_file = self.session_dir / f"{session_id}.pkl"
        if session_file.exists():
            with open(session_file, 'rb') as f:
                data = pickle.load(f)
                self.facts = data.get('facts', {})
                self.tool_history = data.get('tool_history', [])
                self.conversation_history = data.get('conversation_history', [])
                self.user_preferences = data.get('user_preferences', {})
            return True
        return False
    
    def clear(self):
        """Clear all context"""
        self.tool_history = []
        self.facts = {}
        self.conversation_history = []


class ReasoningEngine:
    """Analyzes intent, plans execution, and learns from results"""
    
    def __init__(self, context_memory: ContextMemory):
        self.context = context_memory
        self.tool_success_rate = {}  # Track success rates
        self.tool_avg_time = {}  # Average execution times
    
    def analyze_intent(self, user_message: str, ai_response: str, tool_calls: List[Dict]) -> Dict:
        """Deep intent analysis with multi-step planning"""
        analysis = {
            'user_intent': self._classify_intent(user_message),
            'complexity': self._assess_complexity(user_message, tool_calls),
            'tool_count': len(tool_calls),
            'needs_verification': False,
            'needs_context': False,
            'can_optimize': False,
            'reasoning_trace': [],
            'confidence': 1.0,
            'estimated_time': 0
        }
        
        # Check if we need previous context
        context_keywords = ['remember', 'you said', 'earlier', 'before', 'last time', 
                           'what did', 'from before']
        if any(kw in user_message.lower() for kw in context_keywords):
            analysis['needs_context'] = True
            analysis['reasoning_trace'].append("📜 User referencing previous context")
            
            # Try to find relevant context
            relevant = self._find_relevant_context(user_message)
            if relevant:
                analysis['reasoning_trace'].append(f"💡 Found: {relevant}")
        
        # Analyze each tool
        for tool_call in tool_calls:
            tool_name = tool_call['tool']
            
            # Check for optimization opportunities
            if self.can_use_cache(tool_name):
                cached = self.get_cached_result(tool_name)
                if cached:
                    analysis['can_optimize'] = True
                    analysis['reasoning_trace'].append(f"⚡ Can use cached {tool_name} result")
                    analysis['estimated_time'] += 0.1  # Cache lookup time
                    continue
            
            # Estimate execution time
            avg_time = self.tool_avg_time.get(tool_name, 1.0)
            analysis['estimated_time'] += avg_time
            
            # Check success rate
            success_rate = self.tool_success_rate.get(tool_name, 1.0)
            if success_rate < 0.8:
                analysis['reasoning_trace'].append(f"⚠️ {tool_name} has {success_rate*100:.0f}% success rate")
                analysis['confidence'] *= success_rate
        
        return analysis
    
    def _assess_complexity(self, message: str, tool_calls: List[Dict]) -> str:
        """Assess query complexity"""
        if len(tool_calls) == 0:
            return 'simple'
        elif len(tool_calls) == 1:
            return 'medium'
        elif len(tool_calls) <= 3:
            return 'complex'
        else:
            return 'very_complex'
    
    def _find_relevant_context(self, message: str) -> Optional[str]:
        """Find relevant information from conversation history"""
        msg_lower = message.lower()
        
        # Check recent conversations
        for turn in reversed(self.context.conversation_history[-5:]):
            # Look for matching keywords
            if any(word in turn['user'].lower() for word in msg_lower.split()[:3]):
                return f"Previous Q: {turn['user'][:50]}..."
        
        return None
    
    def _classify_intent(self, message: str) -> str:
        """Classify user intent with confidence"""
        msg_lower = message.lower()
        
        # Information query
        if any(w in msg_lower for w in ['what', 'when', 'where', 'who', 'how', 'tell me', 'show me', 'get']):
            return 'information_query'
        
        # Action request
        if any(w in msg_lower for w in ['open', 'close', 'start', 'stop', 'run', 'execute', 'launch', 'kill']):
            return 'action_request'
        
        # Search request
        if any(w in msg_lower for w in ['search', 'find', 'look up', 'google', 'research']):
            return 'search_request'
        
        # System query
        if any(w in msg_lower for w in ['system', 'computer', 'pc', 'machine', 'specs']):
            return 'system_query'
        
        # General conversation
        return 'conversation'
    
    def can_use_cache(self, tool_name: str) -> bool:
        """Determine if we should use cached result (with intelligent timeouts)"""
        cache_timeouts = {
            'datetime': 30,  # Date changes slowly
            'system_info': 600,  # System rarely changes (10 min)
            'user_info': 3600,  # User info very stable (1 hour)
            'check_app': 300,  # Apps don't install/uninstall often (5 min)
        }
        
        timeout = cache_timeouts.get(tool_name, 60)
        return self.context.has_recent_tool(tool_name, timeout)
    
    def get_cached_result(self, tool_name: str) -> Optional[Dict]:
        """Get cached tool result if available"""
        for entry in reversed(self.context.tool_history):
            if entry['tool'] == tool_name and entry['success']:
                return entry['result']
        return None
    
    def plan_execution(self, tool_calls: List[Dict]) -> Dict:
        """Plan optimal tool execution with dependency analysis"""
        plan = {
            'steps': [],
            'estimated_time': 0,
            'can_optimize': False,
            'dependencies': [],
            'parallel_possible': False
        }
        
        # Check for dependencies (e.g., web_search needs internet check)
        dependencies = self._analyze_dependencies(tool_calls)
        plan['dependencies'] = dependencies
        
        for i, tool_call in enumerate(tool_calls):
            tool_name = tool_call['tool']
            
            # Check if we can use cache
            if self.can_use_cache(tool_name):
                cached = self.get_cached_result(tool_name)
                if cached:
                    plan['steps'].append({
                        'index': i,
                        'tool': tool_name,
                        'action': 'use_cache',
                        'result': cached,
                        'time': 0.1
                    })
                    plan['can_optimize'] = True
                    continue
            
            # Need to execute
            avg_time = self.tool_avg_time.get(tool_name, 1.0)
            plan['steps'].append({
                'index': i,
                'tool': tool_name,
                'action': 'execute',
                'time': avg_time
            })
            plan['estimated_time'] += avg_time
        
        # Check if tools can run in parallel (future feature)
        if len(tool_calls) > 1 and not dependencies:
            plan['parallel_possible'] = True
        
        return plan
    
    def _analyze_dependencies(self, tool_calls: List[Dict]) -> List[Tuple[str, str]]:
        """Analyze tool dependencies"""
        dependencies = []
        
        # Define known dependencies
        dep_rules = {
            'open_url': ['system_info'],  # May need to know OS for browser
            'web_search': [],  # Independent
        }
        
        # Check for actual dependencies in this execution
        tools_in_call = [t['tool'] for t in tool_calls]
        for tool in tools_in_call:
            if tool in dep_rules:
                for dep in dep_rules[tool]:
                    if dep in tools_in_call:
                        dependencies.append((tool, dep))
        
        return dependencies
    
    def record_result(self, tool_name: str, success: bool, execution_time: float):
        """Record tool execution for learning"""
        # Update success rate
        if tool_name not in self.tool_success_rate:
            self.tool_success_rate[tool_name] = 1.0 if success else 0.0
        else:
            # Exponential moving average
            alpha = 0.3
            self.tool_success_rate[tool_name] = (
                alpha * (1.0 if success else 0.0) + 
                (1 - alpha) * self.tool_success_rate[tool_name]
            )
        
        # Update average execution time
        if tool_name not in self.tool_avg_time:
            self.tool_avg_time[tool_name] = execution_time
        else:
            alpha = 0.3
            self.tool_avg_time[tool_name] = (
                alpha * execution_time + 
                (1 - alpha) * self.tool_avg_time[tool_name]
            )


class ResultVerifier:
    """Verifies tool results with advanced sanity checks"""
    
    def verify_result(self, tool_name: str, result: Dict) -> Dict:
        """Verify a tool result and return detailed confidence score"""
        verification = {
            'valid': True,
            'confidence': 1.0,
            'issues': [],
            'warnings': [],
            'suggestions': []
        }
        
        if not result.get('success'):
            verification['valid'] = False
            verification['confidence'] = 0.0
            verification['issues'].append("Tool execution failed")
            
            # Add suggestions based on error
            error = result.get('error', '')
            if 'permission' in error.lower():
                verification['suggestions'].append("Try enabling Commander mode")
            elif 'not found' in error.lower():
                verification['suggestions'].append("Check if application is installed")
            
            return verification
        
        # Tool-specific verification
        if tool_name == 'system_info':
            return self._verify_system_info(result)
        elif tool_name == 'datetime':
            return self._verify_datetime(result)
        elif tool_name == 'web_search':
            return self._verify_web_search(result)
        
        return verification
    
    def _verify_system_info(self, result: Dict) -> Dict:
        """Verify system info makes sense"""
        verification = {
            'valid': True,
            'confidence': 1.0,
            'issues': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Check OS
        valid_os = ['Ubuntu', 'Debian', 'Fedora', 'Arch', 'Windows', 'macOS', 'Linux']
        os_name = result.get('os', '')
        if not any(os in os_name for os in valid_os):
            verification['warnings'].append(f"Unusual OS: {os_name}")
            verification['confidence'] -= 0.2
        
        # Check RAM (should be reasonable: 1GB - 256GB)
        ram = result.get('memory_gb', 0)
        if ram < 1 or ram > 256:
            verification['warnings'].append(f"Unusual RAM amount: {ram}GB")
            verification['confidence'] -= 0.3
        elif ram < 2:
            verification['suggestions'].append("Low RAM detected, may affect performance")
        
        # Check CPU
        cpu = result.get('cpu', '')
        known_vendors = ['Intel', 'AMD', 'ARM', 'Apple']
        if not any(vendor in cpu for vendor in known_vendors):
            verification['warnings'].append(f"Unknown CPU vendor: {cpu}")
            verification['confidence'] -= 0.2
        
        # Check architecture
        arch = result.get('architecture', '')
        valid_arch = ['x86_64', 'amd64', 'arm64', 'aarch64']
        if arch not in valid_arch:
            verification['warnings'].append(f"Unusual architecture: {arch}")
            verification['confidence'] -= 0.1
        
        verification['confidence'] = max(0.0, verification['confidence'])
        return verification
    
    def _verify_datetime(self, result: Dict) -> Dict:
        """Verify datetime is reasonable"""
        verification = {
            'valid': True,
            'confidence': 1.0,
            'issues': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Check year (should be 2024-2030 range for current system)
        date_str = result.get('date', '')
        if '202' not in date_str and '203' not in date_str:
            verification['issues'].append(f"Invalid date: {date_str}")
            verification['valid'] = False
            verification['confidence'] = 0.0
            verification['suggestions'].append("System clock may be wrong")
        
        # Check timezone
        tz = result.get('timezone', '')
        if not tz:
            verification['warnings'].append("No timezone info")
            verification['confidence'] -= 0.1
        
        return verification
    
    def _verify_web_search(self, result: Dict) -> Dict:
        """Verify web search results"""
        verification = {
            'valid': True,
            'confidence': 1.0,
            'issues': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Check if we got results
        results_count = len(result.get('results', []))
        if results_count == 0:
            verification['warnings'].append("No search results found")
            verification['confidence'] = 0.5
            verification['suggestions'].append("Try different search terms")
        elif results_count < 3:
            verification['warnings'].append(f"Only {results_count} results found")
            verification['confidence'] = 0.7
        
        return verification


# Global instances (initialized per session)
_sessions = {}  # session_id -> (context, reasoning, verifier)

def init_reasoning_layer(session_id="default"):
    """Initialize the reasoning layer for a session"""
    context_memory = ContextMemory()
    reasoning_engine = ReasoningEngine(context_memory)
    result_verifier = ResultVerifier()
    
    _sessions[session_id] = (context_memory, reasoning_engine, result_verifier)
    
    # Try to load previous session
    context_memory.load_session(session_id)
    
    return context_memory, reasoning_engine, result_verifier

def get_session(session_id="default"):
    """Get or create session"""
    if session_id not in _sessions:
        init_reasoning_layer(session_id)
    return _sessions[session_id]

def get_context(session_id="default") -> ContextMemory:
    """Get context memory instance"""
    return get_session(session_id)[0]

def get_reasoning(session_id="default") -> ReasoningEngine:
    """Get reasoning engine instance"""
    return get_session(session_id)[1]

def get_verifier(session_id="default") -> ResultVerifier:
    """Get result verifier instance"""
    return get_session(session_id)[2]

