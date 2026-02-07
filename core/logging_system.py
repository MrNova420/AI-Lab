#!/usr/bin/env python3
"""
💾 Improved Logging - Save EVERY Message Immediately!
Graceful shutdown, organized by date, error tracking
"""

import json, os, signal, sys, atexit, hashlib
from pathlib import Path
from datetime import datetime


class LoggingSystem:
    def __init__(self, base_path: str = "memory"):
        self.base_path = Path(base_path)
        self.current_session = None
        self.session_file = None
        
        self.sessions_dir = self.base_path / "sessions"
        self.training_dir = self.base_path / "training_data"
        self.errors_dir = self.base_path / "errors"
        
        for d in [self.sessions_dir, self.training_dir, self.errors_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        atexit.register(self._save_on_exit)
        
        print("💾 Logging (saves immediately)")
    
    def _handle_shutdown(self, signum, frame):
        print("\n\n💾 Saving...")
        if self.current_session:
            self.save_session()
        print("✅ Saved!")
        sys.exit(0)
    
    def _save_on_exit(self):
        if self.current_session and len(self.current_session.get('messages', [])) > 0:
            self.save_session()
    
    def start_session(self, user_name: str = "User", metadata: dict = None):
        sid = hashlib.md5(f"{datetime.now().isoformat()}_{os.getpid()}".encode()).hexdigest()[:12]
        now = datetime.now()
        
        self.current_session = {
            'session_id': sid,
            'user_name': user_name,
            'started_at': now.isoformat(),
            'last_updated': now.isoformat(),
            'messages': [],
            'metadata': metadata or {},
            'stats': {'total_messages': 0, 'user_messages': 0, 'assistant_messages': 0, 'errors': 0},
            'errors': []
        }
        
        date_dir = self.sessions_dir / now.strftime('%Y-%m-%d')
        date_dir.mkdir(exist_ok=True)
        self.session_file = date_dir / f"{sid}.json"
        self._write()
        return sid
    
    def log_message(self, role: str, content: str, metadata: dict = None):
        if not self.current_session:
            self.start_session()
        
        msg = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.current_session['messages'].append(msg)
        self.current_session['last_updated'] = datetime.now().isoformat()
        self.current_session['stats']['total_messages'] += 1
        
        if role == 'user':
            self.current_session['stats']['user_messages'] += 1
        elif role == 'assistant':
            self.current_session['stats']['assistant_messages'] += 1
        
        self._write()
        return msg
    
    def log_error(self, error_type: str, error_msg: str, context: dict = None):
        if not self.current_session:
            self.start_session()
        
        now = datetime.now()
        error = {
            'type': error_type,
            'message': error_msg,
            'timestamp': now.isoformat(),
            'context': context or {}
        }
        
        self.current_session['errors'].append(error)
        self.current_session['stats']['errors'] += 1
        
        error_file = self.errors_dir / f"errors_{now.strftime('%Y-%m-%d')}.jsonl"
        with open(error_file, 'a') as f:
            f.write(json.dumps(error) + '\n')
        
        self._write()
        return error
    
    def _write(self):
        if self.session_file and self.current_session:
            try:
                with open(self.session_file, 'w') as f:
                    json.dump(self.current_session, f, indent=2)
            except Exception as e:
                print(f"❌ Save failed: {e}")
    
    def save_session(self):
        if not self.current_session:
            return None
        self.current_session['last_updated'] = datetime.now().isoformat()
        self._write()
        return self.session_file
    
    def export_for_training(self, format: str = 'jsonl'):
        now = datetime.now()
        output = self.training_dir / f"training_{now.strftime('%Y%m%d_%H%M%S')}.{format}"
        
        if format == 'jsonl':
            with open(output, 'w') as f:
                for date_dir in sorted(self.sessions_dir.glob("*")):
                    if date_dir.is_dir():
                        for sfile in sorted(date_dir.glob("*.json")):
                            try:
                                s = json.loads(sfile.read_text())
                                msgs = [{'role': m['role'], 'content': m['content']} 
                                       for m in s.get('messages', []) if m['role'] in ['user', 'assistant']]
                                if msgs:
                                    f.write(json.dumps({'messages': msgs}) + '\n')
                            except:
                                pass
        return str(output)
