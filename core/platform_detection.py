#!/usr/bin/env python3
"""
Platform Detection and Compatibility Layer
Detects OS and provides appropriate implementations
"""

import platform
import sys
import subprocess
from pathlib import Path


class PlatformInfo:
    """Detect and provide platform information"""
    
    def __init__(self):
        self.system = platform.system()  # 'Linux', 'Windows', 'Darwin'
        self.release = platform.release()
        self.is_wsl = self._detect_wsl()
        self.is_linux_native = (self.system == 'Linux' and not self.is_wsl)
        self.is_windows = (self.system == 'Windows')
        self.is_macos = (self.system == 'Darwin')
        
    def _detect_wsl(self):
        """Detect if running in Windows Subsystem for Linux"""
        if platform.system() != 'Linux':
            return False
        
        # Check /proc/version for 'microsoft' or 'WSL'
        try:
            with open('/proc/version', 'r') as f:
                version = f.read().lower()
                return 'microsoft' in version or 'wsl' in version
        except:
            return False
    
    def has_tool(self, tool_name):
        """Check if a command-line tool is available"""
        try:
            result = subprocess.run(['which', tool_name], 
                                  capture_output=True, 
                                  timeout=1)
            return result.returncode == 0
        except:
            return False
    
    def get_capabilities(self):
        """Get platform capabilities"""
        caps = {
            'system': self.system,
            'is_wsl': self.is_wsl,
            'is_linux_native': self.is_linux_native,
            'is_windows': self.is_windows,
            'is_macos': self.is_macos,
            'commander_mode': 'none',
            'screenshot_method': 'none',
            'automation_available': False
        }
        
        # Determine commander mode support
        if self.is_wsl:
            # WSL can control Windows via PowerShell
            caps['commander_mode'] = 'wsl-powershell'
            caps['automation_available'] = True
            caps['screenshot_method'] = 'powershell'
        elif self.is_windows:
            # Native Windows
            caps['commander_mode'] = 'windows-native'
            caps['automation_available'] = True
            caps['screenshot_method'] = 'windows'
        elif self.is_linux_native:
            # Check for X11 tools
            if self.has_tool('xdotool'):
                caps['commander_mode'] = 'linux-x11'
                caps['automation_available'] = True
            if self.has_tool('scrot') or self.has_tool('gnome-screenshot'):
                caps['screenshot_method'] = 'linux'
        elif self.is_macos:
            # macOS with AppleScript
            caps['commander_mode'] = 'macos-applescript'
            caps['automation_available'] = True
            caps['screenshot_method'] = 'macos'
        
        return caps
    
    def get_unavailable_reason(self, feature):
        """Get human-readable reason why a feature is unavailable"""
        caps = self.get_capabilities()
        
        if feature == 'commander':
            if not caps['automation_available']:
                if self.is_linux_native:
                    return "Commander mode requires xdotool. Install with: sudo apt-get install xdotool"
                return f"Commander mode not available on {self.system}"
        
        elif feature == 'screenshot':
            if caps['screenshot_method'] == 'none':
                if self.is_linux_native:
                    return "Screenshot requires scrot or gnome-screenshot. Install with: sudo apt-get install scrot"
                return f"Screenshot not available on {self.system}"
        
        return "Feature not available on this platform"


# Global instance
_platform_info = None

def get_platform_info():
    """Get or create platform info instance"""
    global _platform_info
    if _platform_info is None:
        _platform_info = PlatformInfo()
    return _platform_info


def check_feature_available(feature):
    """
    Check if a feature is available
    
    Args:
        feature: 'commander', 'screenshot', 'web', etc.
    
    Returns:
        tuple: (available: bool, reason: str)
    """
    info = get_platform_info()
    caps = info.get_capabilities()
    
    if feature == 'commander':
        available = caps['automation_available']
        reason = "" if available else info.get_unavailable_reason('commander')
        return available, reason
    
    elif feature == 'screenshot':
        available = caps['screenshot_method'] != 'none'
        reason = "" if available else info.get_unavailable_reason('screenshot')
        return available, reason
    
    elif feature == 'web':
        # Web search always available if dependencies installed
        try:
            import aiohttp
            import bs4
            return True, ""
        except ImportError as e:
            return False, f"Missing dependency: {e.name}. Install with: pip install aiohttp beautifulsoup4"
    
    return False, "Unknown feature"


if __name__ == '__main__':
    # Test platform detection
    info = get_platform_info()
    caps = info.get_capabilities()
    
    print("🖥️ Platform Detection")
    print("=" * 60)
    print(f"System: {caps['system']}")
    print(f"WSL: {caps['is_wsl']}")
    print(f"Native Linux: {caps['is_linux_native']}")
    print(f"Commander Mode: {caps['commander_mode']}")
    print(f"Screenshot: {caps['screenshot_method']}")
    print(f"Automation: {caps['automation_available']}")
    print()
    
    # Test feature checks
    for feature in ['commander', 'screenshot', 'web']:
        available, reason = check_feature_available(feature)
        status = "✅" if available else "❌"
        print(f"{status} {feature}: {reason if reason else 'Available'}")
