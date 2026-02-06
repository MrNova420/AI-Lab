#!/usr/bin/env python3
"""
SMART AI Intent Parser with System Awareness
Checks if apps are installed before deciding desktop app vs website
"""

import re
import json

def parse_ai_intent(user_message, ai_response, commander=None):
    """
    Parse user intent with SMART fallback logic:
    1. Check if app is installed
    2. If yes → open app
    3. If no → open website instead
    
    Returns list of tool calls to execute
    """
    user_lower = user_message.lower()
    ai_lower = ai_response.lower() if ai_response else ""
    
    tools = []
    
    # ========== OPEN APP/WEBSITE WITH SMART FALLBACK ==========
    open_keywords = ['open', 'launch', 'start', 'run', 'load']
    
    # Service mapping: app command + fallback website
    services = {
        'steam': {'app': 'steam', 'url': 'https://store.steampowered.com'},
        'discord': {'app': 'Discord', 'url': 'https://discord.com'},
        'chrome': {'app': 'chrome', 'url': None},
        'firefox': {'app': 'firefox', 'url': None},
        'notepad': {'app': 'notepad', 'url': None},
        'calculator': {'app': 'calc', 'url': None},
        'calc': {'app': 'calc', 'url': None},
        'paint': {'app': 'mspaint', 'url': None},
        'explorer': {'app': 'explorer', 'url': None},
        'cmd': {'app': 'cmd', 'url': None},
        'powershell': {'app': 'powershell', 'url': None},
        'code': {'app': 'code', 'url': 'https://code.visualstudio.com'},
        'vscode': {'app': 'code', 'url': 'https://code.visualstudio.com'},
        'spotify': {'app': 'spotify', 'url': 'https://open.spotify.com'},
        'obs': {'app': 'obs64', 'url': 'https://obsproject.com'},
        'vlc': {'app': 'vlc', 'url': 'https://www.videolan.org'},
        'youtube': {'app': None, 'url': 'https://youtube.com'},
        'gmail': {'app': None, 'url': 'https://gmail.com'},
        'reddit': {'app': None, 'url': 'https://reddit.com'},
        'github': {'app': None, 'url': 'https://github.com'},
        'twitter': {'app': None, 'url': 'https://twitter.com'},
        'facebook': {'app': None, 'url': 'https://facebook.com'},
    }
    
    if any(kw in user_lower for kw in open_keywords):
        # Check if user explicitly wants website
        website_keywords = ['website', 'site', 'web', 'browser', 'online', '.com', 'http']
        force_website = any(kw in user_lower for kw in website_keywords)
        
        # Find which service user wants
        for service_name, service_info in services.items():
            if service_name in user_lower:
                app_cmd = service_info.get('app')
                fallback_url = service_info.get('url')
                
                # 1. User explicitly wants website
                if force_website and fallback_url:
                    tools.append({'tool': 'open_url', 'params': {'url': fallback_url}})
                    break
                
                # 2. Service only has website (no desktop app)
                if not app_cmd and fallback_url:
                    tools.append({'tool': 'open_url', 'params': {'url': fallback_url}})
                    break
                
                # 3. SMART MODE: Check if desktop app exists
                if app_cmd and commander:
                    check_result = commander.check_app_exists(app_cmd)
                    app_exists = check_result.get('exists', False)
                    
                    if app_exists:
                        # ✅ App installed → open it
                        tools.append({'tool': 'open_app', 'params': {'app': app_cmd}})
                        print(f"✅ {service_name} app FOUND - opening desktop app")
                    elif fallback_url:
                        # ⚠️ App NOT installed → open website instead
                        tools.append({'tool': 'open_url', 'params': {'url': fallback_url}})
                        print(f"⚠️ {service_name} app NOT FOUND - opening website instead")
                    else:
                        # No fallback - try opening anyway
                        tools.append({'tool': 'open_app', 'params': {'app': app_cmd}})
                        print(f"⚠️ {service_name} not found, trying anyway...")
                elif app_cmd:
                    # No commander - assume app exists
                    tools.append({'tool': 'open_app', 'params': {'app': app_cmd}})
                
                break
    
    # ========== DATE/TIME QUERIES ==========
    date_keywords = ['date', 'today', 'day', 'month', 'year', 'calendar']
    time_keywords = ['time', 'clock', "what time", "what's the time"]
    
    if any(keyword in user_lower for keyword in date_keywords):
        if any(keyword in user_lower for keyword in time_keywords):
            # Both date and time requested
            tools.append({'tool': 'current_datetime', 'params': {}})
        else:
            # Just date
            tools.append({'tool': 'current_date', 'params': {}})
    elif any(keyword in user_lower for keyword in time_keywords):
        # Just time
        tools.append({'tool': 'current_time', 'params': {}})
    
    # ========== SYSTEM INFO QUERIES ==========
    if any(word in user_lower for word in ['system', 'os', 'operating system', 'version', 'platform']):
        if 'info' in user_lower or 'what' in user_lower or 'tell me' in user_lower:
            tools.append({'tool': 'system_info', 'params': {}})
    
    if any(word in user_lower for word in ['user', 'username', 'who am i', "what's my name"]):
        tools.append({'tool': 'user_info', 'params': {}})
    
    # ========== SCREENSHOT ==========
    screenshot_keywords = ['screenshot', 'screen shot', 'capture screen', 'snap', 'take a picture']
    if any(kw in user_lower for kw in screenshot_keywords):
        tools.append({'tool': 'screenshot', 'params': {}})
    
    # ========== MOUSE MOVE ==========
    if 'move mouse' in user_lower or 'mouse to' in user_lower or 'move cursor' in user_lower:
        # Extract coordinates
        coord_match = re.search(r'(\d+)\s*,?\s*(\d+)', user_message)
        if coord_match:
            x, y = int(coord_match.group(1)), int(coord_match.group(2))
            tools.append({'tool': 'mouse_move', 'params': {'x': x, 'y': y}})
        else:
            # Named positions (1920x1080 screen assumed)
            if 'top left' in user_lower:
                tools.append({'tool': 'mouse_move', 'params': {'x': 0, 'y': 0}})
            elif 'top right' in user_lower:
                tools.append({'tool': 'mouse_move', 'params': {'x': 1920, 'y': 0}})
            elif 'bottom left' in user_lower:
                tools.append({'tool': 'mouse_move', 'params': {'x': 0, 'y': 1080}})
            elif 'bottom right' in user_lower:
                tools.append({'tool': 'mouse_move', 'params': {'x': 1920, 'y': 1080}})
            elif 'center' in user_lower or 'middle' in user_lower:
                tools.append({'tool': 'mouse_move', 'params': {'x': 960, 'y': 540}})
    
    # ========== MOUSE CLICK ==========
    if 'click' in user_lower:
        button = 'right' if 'right' in user_lower else 'left'
        double = 'double' in user_lower
        tools.append({'tool': 'mouse_click', 'params': {'button': button, 'double': double}})
    
    # ========== KEYBOARD TYPE ==========
    type_keywords = ['type', 'write', 'enter text']
    if any(kw in user_lower for kw in type_keywords):
        for kw in type_keywords:
            if kw in user_lower:
                idx = user_lower.index(kw) + len(kw)
                text = user_message[idx:].strip().strip('"\'')
                # Remove common trailing words
                for ending in ['please', 'for me', 'now', 'into']:
                    if text.lower().endswith(ending):
                        text = text[:-(len(ending)+1)].strip()
                if text:
                    tools.append({'tool': 'keyboard_type', 'params': {'text': text}})
                break
    
    # ========== KEYBOARD PRESS ==========
    key_map = {
        'enter': 'ENTER',
        'return': 'ENTER',
        'escape': 'ESC',
        'esc': 'ESC',
        'tab': 'TAB',
        'backspace': 'BACKSPACE',
        'delete': 'DELETE',
        'space': 'SPACE',
        'up': 'UP',
        'down': 'DOWN',
        'left': 'LEFT',
        'right': 'RIGHT',
    }
    
    press_keywords = ['press', 'hit', 'push']
    if any(kw in user_lower for kw in press_keywords):
        for key_name, key_code in key_map.items():
            if key_name in user_lower:
                tools.append({'tool': 'keyboard_press', 'params': {'key': key_code}})
                break
    
    # ========== CLIPBOARD COPY ==========
    if 'copy' in user_lower or 'clipboard' in user_lower:
        text_match = re.search(r'copy\s+["\']?(.+?)["\']?$', user_lower, re.IGNORECASE)
        if text_match:
            text = text_match.group(1).strip()
            tools.append({'tool': 'clipboard_copy', 'params': {'text': text}})
    
    return tools
