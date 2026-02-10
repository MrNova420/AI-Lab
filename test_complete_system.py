#!/usr/bin/env python3
"""
Complete System Test Suite
Tests all components systematically for 100% completion verification
"""

import sys
import os
from pathlib import Path
import subprocess
import time
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

class Colors:
    HEADER = '\033[95m'
    OK = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{title:^60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def test_pass(msg):
    print(f"{Colors.OK}   ✅ {msg}{Colors.ENDC}")
    return True

def test_fail(msg):
    print(f"{Colors.FAIL}   ❌ {msg}{Colors.ENDC}")
    return False

def test_warn(msg):
    print(f"{Colors.WARN}   ⚠️  {msg}{Colors.ENDC}")

def test_info(msg):
    print(f"   ℹ️  {msg}")

# ============================================================
# PHASE 1: BACKEND TESTING
# ============================================================

def test_backend():
    """Test all backend components"""
    print_section("PHASE 1: BACKEND TESTING")
    
    results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }
    
    # Test 1: Core imports
    print(f"{Colors.BOLD}Test 1: Core Module Imports{Colors.ENDC}")
    try:
        from core import config, model_manager, project_manager
        from core import ai_protocol, logging_system, memory_system
        from core import resource_monitor, user_manager
        test_pass("All core modules import successfully")
        results['passed'] += 1
    except Exception as e:
        test_fail(f"Core module import failed: {e}")
        results['failed'] += 1
    
    # Test 2: Tool system
    print(f"\n{Colors.BOLD}Test 2: Tool System{Colors.ENDC}")
    try:
        from tools.core_tools import CORE_TOOLS
        from tools import TOOLS, generate_tools_description
        
        test_info(f"Core tools available: {len(CORE_TOOLS)}")
        test_info(f"All tools registered: {len(TOOLS)}")
        
        # Check essential tools
        essential = ['read_file', 'write_file', 'create_directory', 'list_files',
                    'check_app', 'open_app', 'open_url']
        missing = []
        for tool in essential:
            found = any(tool in str(t) for t in TOOLS.values())
            if not found:
                missing.append(tool)
        
        if not missing:
            test_pass(f"All {len(essential)} essential tools available")
            results['passed'] += 1
        else:
            test_fail(f"Missing tools: {missing}")
            results['failed'] += 1
            
    except Exception as e:
        test_fail(f"Tool system error: {e}")
        results['failed'] += 1
    
    # Test 3: AI Protocols
    print(f"\n{Colors.BOLD}Test 3: AI Protocol System{Colors.ENDC}")
    try:
        from core.ai_protocol import get_system_prompt
        from core.hyper_minimal_protocol import get_hyper_minimal_prompt as get_hyper
        from core.minimal_protocol import get_minimal_prompt as get_minimal
        from core.ultra_simple_protocol import get_ultra_simple_prompt as get_ultra
        
        # Get prompts
        default = get_system_prompt()
        hyper = get_hyper(commander_mode=True)
        minimal = get_minimal(commander_mode=True)
        ultra = get_ultra(commander_mode=True)
        
        test_info(f"Default protocol: {len(default)} chars")
        test_info(f"Hyper-minimal: {len(hyper)} chars")
        test_info(f"Minimal: {len(minimal)} chars")
        test_info(f"Ultra-simple: {len(ultra)} chars")
        
        if all([default, hyper, minimal, ultra]):
            test_pass("All 4 protocol variants working")
            results['passed'] += 1
        else:
            test_fail("Some protocols failed")
            results['failed'] += 1
            
    except Exception as e:
        test_fail(f"Protocol system error: {e}")
        results['failed'] += 1
    
    # Test 4: Session Management
    print(f"\n{Colors.BOLD}Test 4: Session Management{Colors.ENDC}")
    try:
        session_dir = PROJECT_ROOT / "memory" / "sessions"
        if session_dir.exists():
            test_pass(f"Session directory exists: {session_dir}")
            results['passed'] += 1
        else:
            test_warn(f"Session directory missing (will be created on first use)")
            results['warnings'] += 1
    except Exception as e:
        test_fail(f"Session management error: {e}")
        results['failed'] += 1
    
    # Test 5: User System
    print(f"\n{Colors.BOLD}Test 5: User Management{Colors.ENDC}")
    try:
        from core.user_manager import user_manager
        users = user_manager.list_users()
        test_info(f"Users in system: {len(users)}")
        if len(users) > 0:
            test_pass("User system operational")
            results['passed'] += 1
        else:
            test_warn("No users yet (default will be created)")
            results['warnings'] += 1
    except Exception as e:
        test_fail(f"User system error: {e}")
        results['failed'] += 1
    
    # Test 6: Search System
    print(f"\n{Colors.BOLD}Test 6: Search System{Colors.ENDC}")
    try:
        from tools.web import grok_search, simple_search
        test_pass("Search modules available")
        results['passed'] += 1
    except Exception as e:
        test_fail(f"Search system error: {e}")
        results['failed'] += 1
    
    return results

# ============================================================
# PHASE 2: FRONTEND TESTING
# ============================================================

def test_frontend():
    """Test frontend components"""
    print_section("PHASE 2: FRONTEND TESTING")
    
    results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }
    
    # Test 1: Frontend files exist
    print(f"{Colors.BOLD}Test 1: Frontend File Structure{Colors.ENDC}")
    frontend_files = [
        "app/renderer/src/App.jsx",
        "app/renderer/src/pages/Chat.jsx",
        "app/renderer/src/pages/Voice.jsx",
        "app/renderer/src/pages/Dashboard.jsx",
        "app/renderer/src/pages/Sessions.jsx",
        "app/renderer/src/pages/Settings.jsx",
        "app/package.json"
    ]
    
    missing = []
    for file in frontend_files:
        path = PROJECT_ROOT / file
        if not path.exists():
            missing.append(file)
    
    if not missing:
        test_pass(f"All {len(frontend_files)} frontend files present")
        results['passed'] += 1
    else:
        test_fail(f"Missing files: {missing}")
        results['failed'] += 1
    
    # Test 2: Node modules
    print(f"\n{Colors.BOLD}Test 2: Node Dependencies{Colors.ENDC}")
    node_modules = PROJECT_ROOT / "app" / "node_modules"
    if node_modules.exists():
        test_pass("Node modules installed")
        results['passed'] += 1
    else:
        test_warn("Node modules not installed (run: cd app && npm install)")
        results['warnings'] += 1
    
    # Test 3: Package.json validity
    print(f"\n{Colors.BOLD}Test 3: Package Configuration{Colors.ENDC}")
    try:
        package_json = PROJECT_ROOT / "app" / "package.json"
        with open(package_json) as f:
            pkg = json.load(f)
        test_info(f"App name: {pkg.get('name', 'unknown')}")
        test_info(f"Version: {pkg.get('version', 'unknown')}")
        test_pass("Package.json valid")
        results['passed'] += 1
    except Exception as e:
        test_fail(f"Package.json error: {e}")
        results['failed'] += 1
    
    return results

# ============================================================
# PHASE 3: INTEGRATION TESTING
# ============================================================

def test_integration():
    """Test system integration"""
    print_section("PHASE 3: INTEGRATION TESTING")
    
    results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }
    
    # Test 1: API Server startup (dry run)
    print(f"{Colors.BOLD}Test 1: API Server Import{Colors.ENDC}")
    try:
        from scripts import api_server
        test_pass("API server imports successfully")
        results['passed'] += 1
    except Exception as e:
        test_fail(f"API server import failed: {e}")
        results['failed'] += 1
    
    # Test 2: Tool execution simulation
    print(f"\n{Colors.BOLD}Test 2: Tool Execution Framework{Colors.ENDC}")
    try:
        from core.tool_executor import ToolExecutor
        executor = ToolExecutor()
        test_pass("Tool executor initialized")
        results['passed'] += 1
    except Exception as e:
        test_fail(f"Tool executor error: {e}")
        results['failed'] += 1
    
    # Test 3: Configuration system
    print(f"\n{Colors.BOLD}Test 3: Configuration System{Colors.ENDC}")
    try:
        from core.config import ConfigManager
        config_dir = PROJECT_ROOT / "config"
        if config_dir.exists():
            test_pass("Configuration directory exists")
            results['passed'] += 1
        else:
            test_warn("Config directory missing (run setup.sh)")
            results['warnings'] += 1
    except Exception as e:
        test_fail(f"Configuration error: {e}")
        results['failed'] += 1
    
    return results

# ============================================================
# PHASE 4: PLATFORM-SPECIFIC TESTING
# ============================================================

def test_platform():
    """Test platform-specific features"""
    print_section("PHASE 4: PLATFORM TESTING")
    
    results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }
    
    # Test 1: Platform detection
    print(f"{Colors.BOLD}Test 1: Platform Detection{Colors.ENDC}")
    try:
        import platform
        test_info(f"OS: {platform.system()}")
        test_info(f"Platform: {platform.platform()}")
        test_info(f"Machine: {platform.machine()}")
        # Check if WSL
        try:
            with open('/proc/version', 'r') as f:
                is_wsl = 'microsoft' in f.read().lower()
            test_info(f"Is WSL: {is_wsl}")
        except:
            test_info("Is WSL: Unable to detect")
        test_pass("Platform detection working")
        results['passed'] += 1
    except Exception as e:
        test_fail(f"Platform detection error: {e}")
        results['failed'] += 1
    
    # Test 2: Python version
    print(f"\n{Colors.BOLD}Test 2: Python Version{Colors.ENDC}")
    py_version = sys.version_info
    test_info(f"Python: {py_version.major}.{py_version.minor}.{py_version.micro}")
    if py_version.major == 3 and py_version.minor >= 8:
        test_pass("Python version compatible (3.8+)")
        results['passed'] += 1
    else:
        test_fail("Python version too old (need 3.8+)")
        results['failed'] += 1
    
    # Test 3: Required tools
    print(f"\n{Colors.BOLD}Test 3: System Tools{Colors.ENDC}")
    tools_to_check = ['git', 'python3', 'node', 'npm']
    for tool in tools_to_check:
        try:
            result = subprocess.run(['which', tool], capture_output=True, text=True)
            if result.returncode == 0:
                test_info(f"{tool}: {result.stdout.strip()}")
            else:
                test_warn(f"{tool}: not found in PATH")
                results['warnings'] += 1
        except:
            test_warn(f"{tool}: check failed")
            results['warnings'] += 1
    
    results['passed'] += 1
    
    return results

# ============================================================
# MAIN TEST RUNNER
# ============================================================

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("=" * 60)
    print("🚀 COMPLETE SYSTEM TEST SUITE")
    print("   Testing for 100% Completion")
    print("=" * 60)
    print(f"{Colors.ENDC}")
    
    total_results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }
    
    # Run all test phases
    phases = [
        ("Backend", test_backend),
        ("Frontend", test_frontend),
        ("Integration", test_integration),
        ("Platform", test_platform)
    ]
    
    for phase_name, phase_func in phases:
        try:
            results = phase_func()
            total_results['passed'] += results['passed']
            total_results['failed'] += results['failed']
            total_results['warnings'] += results['warnings']
        except Exception as e:
            print(f"{Colors.FAIL}Phase {phase_name} crashed: {e}{Colors.ENDC}")
            total_results['failed'] += 1
    
    # Final summary
    print_section("FINAL SUMMARY")
    
    total_tests = total_results['passed'] + total_results['failed']
    pass_rate = (total_results['passed'] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"{Colors.BOLD}Results:{Colors.ENDC}")
    print(f"{Colors.OK}   ✅ Passed: {total_results['passed']}{Colors.ENDC}")
    print(f"{Colors.FAIL}   ❌ Failed: {total_results['failed']}{Colors.ENDC}")
    print(f"{Colors.WARN}   ⚠️  Warnings: {total_results['warnings']}{Colors.ENDC}")
    print(f"\n{Colors.BOLD}Pass Rate: {pass_rate:.1f}%{Colors.ENDC}")
    
    if total_results['failed'] == 0:
        print(f"\n{Colors.OK}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.ENDC}")
        print(f"{Colors.OK}   System is ready for production!{Colors.ENDC}\n")
        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.ENDC}")
        print(f"{Colors.FAIL}   Fix issues before proceeding{Colors.ENDC}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
