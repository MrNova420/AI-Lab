#!/usr/bin/env python3
"""
👤 User Management System
Handles user creation, authentication, and preferences
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from core.config import ConfigManager


class UserManager:
    def __init__(self, base_path: str = "memory"):
        self.base_path = Path(base_path)
        self.users_dir = self.base_path / "users"
        self.users_file = self.users_dir / "users.json"
        self.current_user_file = self.users_dir / "current_user.json"
        
        # Ensure directories exist
        self.users_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ConfigManager instances for thread-safe file access
        self.users_config = ConfigManager(self.users_file)
        self.current_user_config = ConfigManager(self.current_user_file)
        
        # Initialize users file if doesn't exist
        if not self.users_file.exists():
            self._init_users_file()
        
        # Initialize current user
        self.current_user = self._load_current_user()
        if not self.current_user:
            # Auto-create and set default user
            default_user = self.create_user("default", "Default User")
            self.set_current_user(default_user['id'])
        
        print(f"👤 User Manager initialized (current: {self.current_user['username']})")
    
    def _init_users_file(self):
        """Initialize users file with empty list"""
        users_data = {
            'users': [],
            'last_updated': datetime.now().isoformat()
        }
        # Use ConfigManager for thread-safe write
        self.users_config.update(users_data)
    
    def _load_users(self) -> Dict:
        """Load all users from file with proper error handling"""
        try:
            # Use ConfigManager for thread-safe read
            data = self.users_config.to_dict()
            if not data or 'users' not in data:
                self._init_users_file()
                return self.users_config.to_dict()
            return data
        except (OSError, json.JSONDecodeError) as exc:
            # If the users file is unreadable or corrupted, log and reinitialize
            print(f"⚠️  Failed to load users: {exc}. Reinitializing users file.")
            self._init_users_file()
            return self.users_config.to_dict()
    
    def _save_users(self, users_data: Dict):
        """Save users to file with proper locking"""
        users_data['last_updated'] = datetime.now().isoformat()
        # Use ConfigManager for thread-safe write
        self.users_config.update(users_data)
    
    def _load_current_user(self) -> Optional[Dict]:
        """Load current user from file with proper error handling"""
        try:
            if self.current_user_file.exists():
                current_data = self.current_user_config.to_dict()
                user_id = current_data.get('user_id')
                if user_id:
                    return self.get_user(user_id)
        except (OSError, json.JSONDecodeError) as exc:
            # If the current user file is unreadable or corrupted, log and fall back to no current user
            print(f"⚠️  Failed to load current user: {exc}")
            return None
        return None
    
    def _save_current_user(self, user_id: str):
        """Save current user to file with proper locking"""
        self.current_user_config.update({
            'user_id': user_id,
            'set_at': datetime.now().isoformat()
        })
    
    def create_user(self, username: str, display_name: str = None, preferences: Dict = None) -> Dict:
        """Create a new user"""
        users_data = self._load_users()
        
        # Check if username already exists
        for user in users_data['users']:
            if user['username'] == username:
                raise ValueError(f"Username '{username}' already exists")
        
        # Generate user ID
        user_id = hashlib.md5(f"{username}_{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # Create user object
        user = {
            'id': user_id,
            'username': username,
            'display_name': display_name or username,
            'created_at': datetime.now().isoformat(),
            'preferences': preferences or {
                'theme': 'dark',
                'commander_mode': False,
                'web_search_mode': False
            },
            'stats': {
                'sessions_created': 0,
                'messages_sent': 0,
                'total_conversations': 0
            }
        }
        
        users_data['users'].append(user)
        self._save_users(users_data)
        
        print(f"✅ Created user: {username} (ID: {user_id})")
        return user
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        users_data = self._load_users()
        for user in users_data['users']:
            if user['id'] == user_id:
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        users_data = self._load_users()
        for user in users_data['users']:
            if user['username'] == username:
                return user
        return None
    
    def list_users(self) -> List[Dict]:
        """List all users"""
        users_data = self._load_users()
        return users_data['users']
    
    def update_user(self, user_id: str, updates: Dict) -> Dict:
        """Update user information"""
        users_data = self._load_users()
        
        for i, user in enumerate(users_data['users']):
            if user['id'] == user_id:
                # Update allowed fields
                allowed_fields = ['display_name', 'preferences', 'stats']
                for field in allowed_fields:
                    if field in updates:
                        user[field] = updates[field]
                
                users_data['users'][i] = user
                self._save_users(users_data)
                
                # If updating current user, reload it
                if self.current_user and self.current_user['id'] == user_id:
                    self.current_user = user
                
                return user
        
        raise ValueError(f"User ID '{user_id}' not found")
    
    def delete_user(self, user_id: str):
        """Delete a user (cannot delete current user or default)"""
        users_data = self._load_users()
        
        # Find user
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User ID '{user_id}' not found")
        
        # Prevent deletion of current user
        if self.current_user and self.current_user['id'] == user_id:
            raise ValueError("Cannot delete current user. Switch to another user first.")
        
        # Prevent deletion of default user
        if user['username'] == 'default':
            raise ValueError("Cannot delete default user")
        
        # Remove user
        users_data['users'] = [u for u in users_data['users'] if u['id'] != user_id]
        self._save_users(users_data)
        
        print(f"🗑️ Deleted user: {user['username']} (ID: {user_id})")
    
    def set_current_user(self, user_id: str) -> Dict:
        """Set the current active user"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User ID '{user_id}' not found")
        
        self.current_user = user
        self._save_current_user(user_id)
        
        print(f"👤 Current user set to: {user['username']}")
        return user
    
    def get_current_user(self) -> Dict:
        """Get the current active user"""
        if not self.current_user:
            # Fallback: create and set default user
            default_user = self.create_user("default", "Default User")
            self.set_current_user(default_user['id'])
        return self.current_user
    
    def increment_stat(self, stat_name: str, increment: int = 1):
        """Increment a stat for current user"""
        if not self.current_user:
            return
        
        user_id = self.current_user['id']
        user = self.get_user(user_id)
        
        if stat_name in user['stats']:
            user['stats'][stat_name] += increment
            self.update_user(user_id, {'stats': user['stats']})



class _LazyUserManager:
    """Lazy proxy for UserManager to avoid I/O at import time."""
    
    def __init__(self):
        self._instance: Optional[UserManager] = None
    
    def _get_instance(self) -> UserManager:
        if self._instance is None:
            self._instance = UserManager()
        return self._instance
    
    def __getattr__(self, name):
        # Delegate attribute access to the underlying UserManager instance
        return getattr(self._get_instance(), name)


# Global instance (lazy-initialized)
user_manager = _LazyUserManager()
