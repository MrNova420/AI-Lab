#!/usr/bin/env python3
"""
🧠 Advanced Memory System
Multi-layered memory for context awareness

Types:
- Short-term: Session only
- Long-term: Persistent
- Working: Task context
- Episodic: Conversation history
"""

import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict


class ShortTermMemory:
    """
    Session-only memory
    Duration: Until session ends
    """
    
    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self.memory = []
    
    def store(self, key: str, value: Any):
        """Store in short-term memory"""
        self.memory.append({
            'key': key,
            'value': value,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only recent items
        if len(self.memory) > self.capacity:
            self.memory = self.memory[-self.capacity:]
    
    def recall(self, key: str) -> Optional[Any]:
        """Recall from short-term memory"""
        for item in reversed(self.memory):
            if item['key'] == key:
                return item['value']
        return None
    
    def clear(self):
        """Clear short-term memory"""
        self.memory = []


class LongTermMemory:
    """
    Persistent memory
    Duration: Forever
    """
    
    def __init__(self, storage_path: str = "memory/long_term.pkl"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory = self._load()
    
    def _load(self) -> Dict:
        """Load from disk"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'rb') as f:
                    return pickle.load(f)
            except:
                return {}
        return {}
    
    def _save(self):
        """Save to disk"""
        with open(self.storage_path, 'wb') as f:
            pickle.dump(self.memory, f)
    
    def store(self, key: str, value: Any, category: str = 'general'):
        """Store in long-term memory"""
        if category not in self.memory:
            self.memory[category] = {}
        
        self.memory[category][key] = {
            'value': value,
            'stored_at': datetime.now().isoformat(),
            'accessed_count': 0
        }
        
        self._save()
    
    def recall(self, key: str, category: str = 'general') -> Optional[Any]:
        """Recall from long-term memory"""
        if category in self.memory and key in self.memory[category]:
            item = self.memory[category][key]
            item['accessed_count'] += 1
            item['last_accessed'] = datetime.now().isoformat()
            self._save()
            return item['value']
        return None
    
    def get_category(self, category: str) -> Dict:
        """Get all items in category"""
        return self.memory.get(category, {})
    
    def forget(self, key: str, category: str = 'general'):
        """Remove from memory"""
        if category in self.memory and key in self.memory[category]:
            del self.memory[category][key]
            self._save()


class WorkingMemory:
    """
    Active task context
    Duration: Until task complete
    """
    
    def __init__(self):
        self.tasks = {}
        self.current_task = None
    
    def start_task(self, task_id: str, task_data: Dict):
        """Start new task"""
        self.current_task = task_id
        self.tasks[task_id] = {
            'data': task_data,
            'status': 'active',
            'started_at': datetime.now().isoformat(),
            'context': {},
            'steps': []
        }
    
    def update_context(self, key: str, value: Any):
        """Update task context"""
        if self.current_task:
            self.tasks[self.current_task]['context'][key] = value
    
    def add_step(self, step: str, result: Any):
        """Add task step"""
        if self.current_task:
            self.tasks[self.current_task]['steps'].append({
                'step': step,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
    
    def complete_task(self):
        """Mark current task as complete"""
        if self.current_task:
            self.tasks[self.current_task]['status'] = 'complete'
            self.tasks[self.current_task]['completed_at'] = datetime.now().isoformat()
            self.current_task = None
    
    def get_task_context(self, task_id: Optional[str] = None) -> Dict:
        """Get task context"""
        task = task_id or self.current_task
        if task and task in self.tasks:
            return self.tasks[task]
        return {}


class EpisodicMemory:
    """
    Conversation history
    Duration: Permanent archive
    """
    
    def __init__(self, storage_path: str = "memory/episodic"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.episodes = []
    
    def store_episode(self, episode: Dict):
        """Store conversation episode"""
        episode['stored_at'] = datetime.now().isoformat()
        self.episodes.append(episode)
        
        # Save to disk
        date_str = datetime.now().strftime("%Y-%m")
        episode_file = self.storage_path / f"{date_str}.jsonl"
        
        with open(episode_file, 'a') as f:
            f.write(json.dumps(episode) + '\n')
    
    def search_episodes(self, query: str, limit: int = 10) -> List[Dict]:
        """Search conversation history"""
        results = []
        
        # Search recent episodes in memory
        for episode in reversed(self.episodes[-50:]):  # Last 50 episodes
            content = json.dumps(episode).lower()
            if query.lower() in content:
                results.append(episode)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_recent_episodes(self, count: int = 10) -> List[Dict]:
        """Get recent episodes"""
        return self.episodes[-count:] if self.episodes else []


class AdvancedMemory:
    """
    Unified memory system with all layers
    """
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
        
        print("🧠 Advanced Memory System initialized")
    
    def remember(self, key: str, value: Any, memory_type: str = 'short'):
        """
        Store in appropriate memory type
        Types: 'short', 'long', 'working'
        """
        if memory_type == 'short':
            self.short_term.store(key, value)
        elif memory_type == 'long':
            self.long_term.store(key, value)
        elif memory_type == 'working':
            self.working.update_context(key, value)
    
    def recall(self, key: str, memory_types: List[str] = None) -> Optional[Any]:
        """
        Recall from memory (checks all types if not specified)
        """
        if memory_types is None:
            memory_types = ['working', 'short', 'long']
        
        for mem_type in memory_types:
            if mem_type == 'short':
                result = self.short_term.recall(key)
                if result is not None:
                    return result
            elif mem_type == 'long':
                result = self.long_term.recall(key)
                if result is not None:
                    return result
            elif mem_type == 'working':
                context = self.working.get_task_context()
                if 'context' in context and key in context['context']:
                    return context['context'][key]
        
        return None
    
    def consolidate(self):
        """
        Move important short-term memories to long-term
        Called periodically
        """
        # Get frequently accessed short-term memories
        access_counts = defaultdict(int)
        
        for item in self.short_term.memory:
            access_counts[item['key']] += 1
        
        # Move high-access items to long-term
        for key, count in access_counts.items():
            if count >= 3:  # Accessed 3+ times
                value = self.short_term.recall(key)
                if value:
                    self.long_term.store(key, value, category='consolidated')
    
    def get_context_summary(self) -> Dict:
        """
        Get summary of current context across all memory types
        """
        return {
            'short_term_items': len(self.short_term.memory),
            'long_term_categories': list(self.long_term.memory.keys()),
            'current_task': self.working.current_task,
            'active_tasks': len([t for t in self.working.tasks.values() if t['status'] == 'active']),
            'recent_episodes': len(self.episodic.get_recent_episodes(10))
        }
    
    def save_episode(self, conversation: List[Dict], metadata: Dict):
        """
        Save conversation to episodic memory
        """
        episode = {
            'conversation': conversation,
            'metadata': metadata,
            'summary': self._generate_episode_summary(conversation)
        }
        
        self.episodic.store_episode(episode)
    
    def _generate_episode_summary(self, conversation: List[Dict]) -> str:
        """Generate summary of conversation"""
        if not conversation:
            return ""
        
        # Get first user message
        for msg in conversation:
            if msg.get('role') == 'user':
                return msg.get('content', '')[:100] + "..."
        
        return "Conversation"


# Global memory instance
_memory = None

def get_memory():
    """Get or create memory system"""
    global _memory
    if _memory is None:
        _memory = AdvancedMemory()
    return _memory


# Convenience functions
def remember(key: str, value: Any, memory_type: str = 'short'):
    """Store in memory"""
    memory = get_memory()
    memory.remember(key, value, memory_type)


def recall(key: str) -> Optional[Any]:
    """Recall from memory"""
    memory = get_memory()
    return memory.recall(key)


def start_task(task_id: str, task_data: Dict):
    """Start new task"""
    memory = get_memory()
    memory.working.start_task(task_id, task_data)


def complete_task():
    """Complete current task"""
    memory = get_memory()
    memory.working.complete_task()


if __name__ == "__main__":
    print("🧪 Testing Memory System\n")
    
    memory = AdvancedMemory()
    
    # Test short-term memory
    print("📝 Testing short-term memory...")
    memory.remember('user_query', 'What is Python?', 'short')
    result = memory.recall('user_query')
    print(f"   Recalled: {result}")
    
    # Test long-term memory
    print("\n💾 Testing long-term memory...")
    memory.remember('user_preference', {'theme': 'dark', 'voice': True}, 'long')
    result = memory.recall('user_preference')
    print(f"   Recalled: {result}")
    
    # Test working memory
    print("\n⚙️ Testing working memory...")
    memory.working.start_task('task_001', {'goal': 'Build feature'})
    memory.working.add_step('Research', 'Found 10 examples')
    memory.working.add_step('Design', 'Created architecture')
    context = memory.working.get_task_context()
    print(f"   Task steps: {len(context['steps'])}")
    
    # Test episodic memory
    print("\n📚 Testing episodic memory...")
    conversation = [
        {'role': 'user', 'content': 'Hello'},
        {'role': 'assistant', 'content': 'Hi! How can I help?'}
    ]
    memory.save_episode(conversation, {'session_id': 'test_001'})
    
    # Get context summary
    print("\n📊 Context Summary:")
    summary = memory.get_context_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Memory system working!")
