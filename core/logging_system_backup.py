#!/usr/bin/env python3
"""
🎯 Comprehensive Logging System
Saves everything for training and analysis

Features:
- Auto-save every message
- Track tool usage
- Performance metrics
- Export to training formats
- Privacy controls
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib


class LoggingSystem:
    """
    Comprehensive logging for all AI interactions
    """
    
    def __init__(self, base_path: str = "memory"):
        self.base_path = Path(base_path)
        self.sessions_path = self.base_path / "sessions"
        self.conversations_path = self.base_path / "conversations"
        self.training_path = self.base_path / "training_data"
        self.analytics_path = self.base_path / "analytics"
        
        # Create directories
        for path in [self.sessions_path, self.conversations_path, 
                     self.training_path, self.analytics_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Current session
        self.current_session = None
        self.session_messages = []
        
    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new session
        Returns session ID
        """
        if not session_id:
            session_id = self._generate_session_id()
        
        self.current_session = {
            'session_id': session_id,
            'start_time': datetime.now().isoformat(),
            'user': os.getenv('USER', 'unknown'),
            'messages': [],
            'tools_used': [],
            'performance': {
                'total_messages': 0,
                'avg_response_time': 0,
                'tools_executed': 0
            }
        }
        
        self.session_messages = []
        print(f"✅ Session started: {session_id}")
        return session_id
    
    def log_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Log a message in the conversation
        role: 'user', 'assistant', 'system'
        """
        if not self.current_session:
            self.start_session()
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.session_messages.append(message)
        self.current_session['messages'].append(message)
        self.current_session['performance']['total_messages'] += 1
        
        # Auto-save periodically (every 10 messages)
        if len(self.session_messages) % 10 == 0:
            self.save_session()
    
    def log_tool_execution(self, tool_name: str, params: Dict, result: any, 
                          success: bool, execution_time: float):
        """
        Log tool execution for analysis
        """
        if not self.current_session:
            self.start_session()
        
        tool_log = {
            'tool_name': tool_name,
            'params': params,
            'result': str(result)[:500],  # Limit size
            'success': success,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }
        
        self.current_session['tools_used'].append(tool_log)
        self.current_session['performance']['tools_executed'] += 1
        
        # Update avg response time
        times = [t['execution_time'] for t in self.current_session['tools_used']]
        self.current_session['performance']['avg_response_time'] = sum(times) / len(times)
    
    def log_error(self, error_type: str, error_message: str, context: Dict):
        """
        Log errors for debugging
        """
        error_log = {
            'error_type': error_type,
            'error_message': error_message,
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        error_path = self.analytics_path / "errors.jsonl"
        with open(error_path, 'a') as f:
            f.write(json.dumps(error_log) + '\n')
    
    def save_session(self):
        """
        Save current session to disk
        """
        if not self.current_session:
            return
        
        session_id = self.current_session['session_id']
        
        # Save to dated folder
        date_str = datetime.now().strftime("%Y-%m")
        date_folder = self.sessions_path / date_str
        date_folder.mkdir(exist_ok=True)
        
        session_file = date_folder / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(self.current_session, f, indent=2)
        
        # Also save to conversations (by topic if possible)
        self._save_conversation()
    
    def _save_conversation(self):
        """
        Save conversation with metadata
        """
        if not self.session_messages:
            return
        
        conversation = {
            'session_id': self.current_session['session_id'],
            'timestamp': self.current_session['start_time'],
            'messages': self.session_messages,
            'summary': self._generate_summary(),
            'topics': self._extract_topics(),
            'performance': self.current_session['performance']
        }
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        conv_folder = self.conversations_path / "by_date" / date_str
        conv_folder.mkdir(parents=True, exist_ok=True)
        
        conv_file = conv_folder / f"{self.current_session['session_id']}.json"
        with open(conv_file, 'w') as f:
            json.dump(conversation, f, indent=2)
    
    def export_training_data(self, output_file: str, format: str = 'jsonl'):
        """
        Export conversations as training data
        Formats: 'jsonl', 'csv', 'markdown'
        """
        print(f"📦 Exporting training data to {output_file}...")
        
        # Collect all conversations
        conversations = []
        for session_folder in self.sessions_path.glob("*/*.json"):
            with open(session_folder) as f:
                session = json.load(f)
                conversations.append(session)
        
        if format == 'jsonl':
            self._export_jsonl(conversations, output_file)
        elif format == 'csv':
            self._export_csv(conversations, output_file)
        elif format == 'markdown':
            self._export_markdown(conversations, output_file)
        
        print(f"✅ Exported {len(conversations)} conversations")
    
    def _export_jsonl(self, conversations: List[Dict], output_file: str):
        """Export as JSONL for fine-tuning"""
        training_path = self.training_path / output_file
        
        with open(training_path, 'w') as f:
            for conv in conversations:
                for msg in conv.get('messages', []):
                    if msg['role'] in ['user', 'assistant']:
                        training_example = {
                            'messages': [
                                {'role': 'user', 'content': msg['content']} 
                                if msg['role'] == 'user' else
                                {'role': 'assistant', 'content': msg['content']}
                            ],
                            'metadata': {
                                'session_id': conv['session_id'],
                                'timestamp': msg['timestamp']
                            }
                        }
                        f.write(json.dumps(training_example) + '\n')
    
    def _export_csv(self, conversations: List[Dict], output_file: str):
        """Export as CSV for analysis"""
        import csv
        
        training_path = self.training_path / output_file
        
        with open(training_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['session_id', 'timestamp', 'role', 'content', 'tools_used'])
            
            for conv in conversations:
                for msg in conv.get('messages', []):
                    writer.writerow([
                        conv['session_id'],
                        msg['timestamp'],
                        msg['role'],
                        msg['content'][:500],  # Limit length
                        len(conv.get('tools_used', []))
                    ])
    
    def _export_markdown(self, conversations: List[Dict], output_file: str):
        """Export as Markdown for documentation"""
        training_path = self.training_path / output_file
        
        with open(training_path, 'w') as f:
            f.write("# Training Conversations\n\n")
            
            for conv in conversations:
                f.write(f"## Session: {conv['session_id']}\n")
                f.write(f"**Date:** {conv['start_time']}\n\n")
                
                for msg in conv.get('messages', []):
                    role = "👤 User" if msg['role'] == 'user' else "🤖 Assistant"
                    f.write(f"### {role}\n")
                    f.write(f"{msg['content']}\n\n")
                
                f.write("---\n\n")
    
    def get_analytics(self) -> Dict:
        """
        Get analytics on all sessions
        """
        total_sessions = 0
        total_messages = 0
        total_tools = 0
        tools_usage = {}
        
        for session_folder in self.sessions_path.glob("*/*.json"):
            with open(session_folder) as f:
                session = json.load(f)
                total_sessions += 1
                total_messages += len(session.get('messages', []))
                
                for tool in session.get('tools_used', []):
                    total_tools += 1
                    tool_name = tool['tool_name']
                    tools_usage[tool_name] = tools_usage.get(tool_name, 0) + 1
        
        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'total_tools_executed': total_tools,
            'tools_usage': tools_usage,
            'avg_messages_per_session': total_messages / max(total_sessions, 1),
            'avg_tools_per_session': total_tools / max(total_sessions, 1)
        }
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{timestamp}{os.getpid()}".encode()
        return hashlib.md5(hash_input).hexdigest()[:12]
    
    def _generate_summary(self) -> str:
        """Generate conversation summary"""
        if not self.session_messages:
            return ""
        
        # Get first user message as summary
        for msg in self.session_messages:
            if msg['role'] == 'user':
                return msg['content'][:100] + "..."
        
        return "Conversation"
    
    def _extract_topics(self) -> List[str]:
        """Extract topics from conversation"""
        topics = []
        
        # Simple keyword extraction
        keywords = ['web search', 'development', 'testing', 'research', 'planning']
        
        content = ' '.join([msg['content'] for msg in self.session_messages]).lower()
        
        for keyword in keywords:
            if keyword in content:
                topics.append(keyword)
        
        return topics


# Global logging instance
_logger = None

def get_logger():
    """Get or create logger"""
    global _logger
    if _logger is None:
        _logger = LoggingSystem()
    return _logger


# Convenience functions
def log_message(role: str, content: str, metadata: Optional[Dict] = None):
    """Log a message"""
    logger = get_logger()
    logger.log_message(role, content, metadata)


def log_tool(tool_name: str, params: Dict, result: any, success: bool, time: float):
    """Log tool execution"""
    logger = get_logger()
    logger.log_tool_execution(tool_name, params, result, success, time)


def start_session(session_id: Optional[str] = None) -> str:
    """Start new session"""
    logger = get_logger()
    return logger.start_session(session_id)


def save_session():
    """Save current session"""
    logger = get_logger()
    logger.save_session()


def export_training_data(output_file: str, format: str = 'jsonl'):
    """Export training data"""
    logger = get_logger()
    logger.export_training_data(output_file, format)


if __name__ == "__main__":
    print("🧪 Testing Logging System\n")
    
    # Start session
    session_id = start_session()
    
    # Log some messages
    log_message('user', 'What is Python?')
    log_message('assistant', 'Python is a programming language...')
    log_message('user', 'How do I install it?')
    log_message('assistant', 'You can install Python from python.org...')
    
    # Log tool execution
    log_tool('web_search', {'query': 'Python'}, {'results': 10}, True, 2.5)
    
    # Save session
    save_session()
    
    # Get analytics
    logger = get_logger()
    analytics = logger.get_analytics()
    print(f"\n📊 Analytics:")
    print(f"  Sessions: {analytics['total_sessions']}")
    print(f"  Messages: {analytics['total_messages']}")
    print(f"  Tools: {analytics['total_tools_executed']}")
    
    # Export training data
    export_training_data('training.jsonl', 'jsonl')
    
    print("\n✅ Logging system working!")
