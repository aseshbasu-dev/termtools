"""
Test script to verify data directory configuration in TermTools
"""
import json
import os
from pathlib import Path

def get_data_directory():
    """Get the data directory path (same logic as wx_app.py)"""
    if os.name == 'nt':  # Windows
        appdata_local = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        data_dir = Path(appdata_local) / 'BasusTools' / 'TermTools'
    else:  # Unix/Linux/Mac
        data_dir = Path.home() / '.local' / 'share' / 'BasusTools' / 'TermTools'
    return data_dir

def test_data_directory():
    """Test data directory configuration"""
    
    # Get data directory
    data_dir = get_data_directory()
    installation_info_path = data_dir / "installation_info.json"
    
    print("=" * 60)
    print("TermTools Data Directory Configuration Test")
    print("=" * 60)
    print()
    
    print(f"📁 Data Directory: {data_dir}")
    print(f"📁 Directory exists: {data_dir.exists()}")
    print()
    
    # Read installation info
    try:
        if installation_info_path.exists():
            with open(installation_info_path, 'r') as f:
                installation_info = json.load(f)
            
            print(f"✅ Installation info found at: {installation_info_path}")
            print()
            
            # Show all installation info
            print("📦 Installation Info:")
            print("-" * 60)
            for key, value in installation_info.items():
                print(f"   {key}: {value}")
            print("-" * 60)
        else:
            print(f"⚠️  Installation info not found at: {installation_info_path}")
            print("💡 Run the installer to create this file")
        
        print()
        print("� Expected Data Files:")
        print(f"   - {data_dir / 'installation_info.json'}")
        print(f"   - {data_dir / 'pomodoro_stats.json'}")
        print(f"   - {data_dir / 'shutdown_state.json'}")
        print(f"   - {data_dir / 'logs' / 'termtools_YYYYMMDD.log'}")
        
    except Exception as e:
        print(f"❌ Error reading installation_info.json: {e}")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    test_data_directory()
