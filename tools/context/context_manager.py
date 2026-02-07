#!/usr/bin/env python3
"""
🧠 Context Tools - Full Conversation Context Management
See entire conversation history, search context, reference past exchanges
"""

from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path


class ContextManager:
    """Manage full conversation context"""
    
    def __init__(self):
        self.current_context = []
        self.context_window = 50  # Last 50 exchanges
        print("🧠 Context Manager initialized")
    
    def add_exchange(self, user_msg: str, ai_response: str, metadata: dict = None):
        """Add a conversation exchange to context"""
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user': user_msg,
            'assistant': ai_response,
            'metadata': metadata or {}
        }
        
        self.current_context.append(exchange)
        
        # Keep only last N exchanges
        if len(self.current_context) > self.context_window:
            self.current_context = self.current_context[-self.context_window:]
        
        return exchange
    
    def get_full_context(self) -> List[Dict]:
        """Get complete conversation context"""
        return self.current_context
    
    def search_context(self, query: str) -> List[Dict]:
        """Search through conversation history"""
        results = []
        query_lower = query.lower()
        
        for exchange in self.current_context:
            if query_lower in exchange['user'].lower() or query_lower in exchange['assistant'].lower():
                results.append(exchange)
        
        return results
    
    def get_context_summary(self) -> str:
        """Get a summary of the conversation"""
        if not self.current_context:
            return "No context yet"
        
        total = len(self.current_context)
        recent = self.current_context[-5:] if len(self.current_context) >= 5 else self.current_context
        
        summary = f"Conversation: {total} exchanges\n\nRecent:\n"
        for ex in recent:
            summary += f"• User: {ex['user'][:50]}...\n"
            summary += f"  AI: {ex['assistant'][:50]}...\n"
        
        return summary
    
    def export_context(self, filepath: str):
        """Export full context to file"""
        Path(filepath).write_text(json.dumps(self.current_context, indent=2))
        return filepath


def get_full_conversation_context():
    """Tool: Get full conversation context"""
    manager = ContextManager()
    context = manager.get_full_context()
    
    return {
        'success': True,
        'context': context,
        'total_exchanges': len(context),
        'message': f'Retrieved {len(context)} conversation exchanges'
    }


def search_conversation(query: str):
    """Tool: Search through conversation history"""
    manager = ContextManager()
    results = manager.search_context(query)
    
    return {
        'success': True,
        'results': results,
        'count': len(results),
        'message': f'Found {len(results)} matching exchanges'
    }


def get_context_summary():
    """Tool: Get conversation summary"""
    manager = ContextManager()
    summary = manager.get_context_summary()
    
    return {
        'success': True,
        'summary': summary,
        'message': 'Context summary generated'
    }
