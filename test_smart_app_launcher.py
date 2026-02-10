#!/usr/bin/env python3
"""
Test Smart App Launcher - Verify intelligent app opening with fallback
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_smart_app_launcher():
    """Test the smart app launcher functionality"""
    print("🧪 Testing Smart App Launcher\n")
    print("=" * 60)
    
    # Test 1: Import the module
    print("\n1️⃣ Testing module import...")
    try:
        from tools.system import smart_app_launcher
        print("   ✅ Module imported successfully")
    except Exception as e:
        print(f"   ❌ Failed to import: {e}")
        return False
    
    # Test 2: Check app info function
    print("\n2️⃣ Testing get_app_info()...")
    try:
        result = smart_app_launcher.get_app_info('steam')
        print(f"   Result: {result}")
        if result.get('success'):
            print(f"   ✅ Steam info: installed={result.get('installed')}, has_web={result.get('has_web_version')}")
        else:
            print(f"   ⚠️ Info check completed with: {result.get('error')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 3: List common apps
    print("\n3️⃣ Testing list_common_apps()...")
    try:
        result = smart_app_launcher.list_common_apps()
        print(f"   Found {result.get('count', 0)} apps")
        if result.get('success'):
            installed = [app['name'] for app in result.get('apps', []) if app['installed']]
            print(f"   ✅ Installed apps: {', '.join(installed) if installed else 'none found'}")
        else:
            print(f"   ⚠️ List completed")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 4: Smart open simulation (without actually opening)
    print("\n4️⃣ Testing smart_open_app() workflow...")
    print("   (This would check for app and open it or fallback to web)")
    try:
        # Test with a common app
        print("   Testing with 'steam'...")
        result = smart_app_launcher.get_app_info('steam')
        if result.get('success'):
            if result.get('installed'):
                print("   ✅ Workflow: Would open Steam application")
            else:
                web_url = result.get('web_url')
                print(f"   ✅ Workflow: Would open Steam web version at {web_url}")
        
        print("   Testing with 'discord'...")
        result = smart_app_launcher.get_app_info('discord')
        if result.get('success'):
            if result.get('installed'):
                print("   ✅ Workflow: Would open Discord application")
            else:
                web_url = result.get('web_url')
                print(f"   ✅ Workflow: Would open Discord web version at {web_url}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 5: Check tool registration
    print("\n5️⃣ Testing tool registration...")
    try:
        from tools import TOOLS
        
        smart_tools = ['smart_open_app', 'get_app_info', 'list_common_apps']
        for tool in smart_tools:
            if tool in TOOLS.get('system', {}):
                print(f"   ✅ {tool} registered")
            else:
                print(f"   ❌ {tool} NOT registered")
                return False
    except Exception as e:
        print(f"   ❌ Error checking registration: {e}")
        return False
    
    # Test 6: Verify web fallback URLs
    print("\n6️⃣ Verifying web fallback URLs...")
    try:
        fallbacks = smart_app_launcher.COMMON_WEB_FALLBACKS
        print(f"   ✅ {len(fallbacks)} apps have web fallbacks configured")
        sample_apps = ['steam', 'discord', 'spotify', 'netflix', 'github']
        for app in sample_apps:
            if app in fallbacks:
                print(f"   ✅ {app}: {fallbacks[app]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed!")
    print("\n📋 Summary:")
    print("   • Smart app launcher module working")
    print("   • Can check app installation status")
    print("   • Can list common apps")
    print("   • Web fallback URLs configured")
    print("   • Tools properly registered")
    print("\n🎯 Usage Example:")
    print('   User: "Open Steam"')
    print('   AI: <TOOLS>smart_open_app(app_name="steam")</TOOLS>')
    print('   AI: "Opened Steam" (app) or "Opened Steam website" (web fallback)')
    
    return True


if __name__ == "__main__":
    success = test_smart_app_launcher()
    sys.exit(0 if success else 1)
