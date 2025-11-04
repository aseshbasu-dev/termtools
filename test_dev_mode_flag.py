"""
Test script to verify dev_mode flag behavior in TermTools
"""
import json
from pathlib import Path

def test_dev_mode():
    """Test reading and displaying dev_mode configuration"""
    
    # Path to installation_info.json
    installation_info_path = Path(__file__).parent / "core" / "data" / "installation_info.json"
    
    print("=" * 60)
    print("TermTools Dev Mode Configuration Test")
    print("=" * 60)
    print()
    
    # Read installation info
    try:
        with open(installation_info_path, 'r') as f:
            installation_info = json.load(f)
        
        dev_mode = installation_info.get("dev_mode", True)
        
        print(f"📋 Installation Info Path: {installation_info_path}")
        print(f"📋 File exists: {installation_info_path.exists()}")
        print()
        print(f"⚙️  Current dev_mode setting: {dev_mode}")
        print()
        
        if dev_mode:
            print("✅ DEVELOPMENT MODE ACTIVE")
            print(f"   Log location: <current_directory>/core/data/logs/")
            print(f"   Actual path: {Path.cwd() / 'core' / 'data' / 'logs'}")
        else:
            print("✅ PRODUCTION MODE ACTIVE")
            print(f"   Log location: C:\\Program Files\\BasusTools\\TermTools\\core\\data\\logs\\")
        
        print()
        print("💡 To toggle modes:")
        print("   1. Open: core/data/installation_info.json")
        print("   2. Change: \"dev_mode\": true  (for dev) or false (for production)")
        print("   3. Restart TermTools")
        print()
        
        # Show all installation info
        print("📦 Full Installation Info:")
        print("-" * 60)
        for key, value in installation_info.items():
            print(f"   {key}: {value}")
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error reading installation_info.json: {e}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    test_dev_mode()
