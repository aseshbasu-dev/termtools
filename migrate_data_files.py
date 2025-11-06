"""
Migration script to move data files from old locations to new AppData directory
Run this script once after updating TermTools to the new version.
"""
import os
import shutil
import json
from pathlib import Path
from datetime import datetime


def get_data_directory():
    """Get the new data directory path"""
    if os.name == 'nt':  # Windows
        appdata_local = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        data_dir = Path(appdata_local) / 'BasusTools' / 'TermTools'
    else:  # Unix/Linux/Mac
        data_dir = Path.home() / '.local' / 'share' / 'BasusTools' / 'TermTools'
    return data_dir


def migrate_files():
    """Migrate data files from old locations to new AppData directory"""
    
    print("=" * 70)
    print("TermTools Data File Migration")
    print("=" * 70)
    print()
    
    # Get paths
    new_data_dir = get_data_directory()
    old_locations = [
        Path(__file__).parent / "core" / "data",  # Dev location
        Path(r"C:\Program Files\BasusTools\TermTools\core\data"),  # Old prod location
    ]
    
    files_to_migrate = [
        "installation_info.json",
        "pomodoro_stats.json",
        "shutdown_state.json"
    ]
    
    print(f"📁 New data directory: {new_data_dir}")
    print()
    
    # Create new data directory
    new_data_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created data directory: {new_data_dir}")
    
    # Migrate files
    migrated_count = 0
    skipped_count = 0
    
    for filename in files_to_migrate:
        target_file = new_data_dir / filename
        
        # Skip if already exists in new location
        if target_file.exists():
            print(f"⏭️  Skipped {filename} (already exists in new location)")
            skipped_count += 1
            continue
        
        # Try to find file in old locations
        found = False
        for old_location in old_locations:
            old_file = old_location / filename
            if old_file.exists():
                try:
                    # Copy file to new location
                    shutil.copy2(old_file, target_file)
                    print(f"✅ Migrated {filename}")
                    print(f"   From: {old_file}")
                    print(f"   To:   {target_file}")
                    migrated_count += 1
                    found = True
                    break
                except Exception as e:
                    print(f"❌ Error migrating {filename}: {e}")
        
        if not found and filename != "installation_info.json":
            print(f"ℹ️  {filename} not found in old locations (will be created on first use)")
    
    # Create logs directory
    logs_dir = new_data_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created logs directory: {logs_dir}")
    
    # Update installation_info.json if it was migrated
    installation_info_path = new_data_dir / "installation_info.json"
    if installation_info_path.exists():
        try:
            with open(installation_info_path, 'r') as f:
                metadata = json.load(f)
            
            # Update with new data directory info
            metadata['data_directory'] = str(new_data_dir)
            metadata['migration_date'] = datetime.now().isoformat()
            
            # Remove old dev_mode flag (no longer needed)
            if 'dev_mode' in metadata:
                del metadata['dev_mode']
            
            with open(installation_info_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Updated installation_info.json with new data directory")
        except Exception as e:
            print(f"⚠️  Warning: Could not update installation_info.json: {e}")
    
    print()
    print("=" * 70)
    print(f"Migration Summary:")
    print(f"  - Migrated: {migrated_count} files")
    print(f"  - Skipped: {skipped_count} files (already in new location)")
    print(f"  - Data directory: {new_data_dir}")
    print("=" * 70)
    print()
    print("✅ Migration complete! TermTools will now use the new data directory.")
    print()


if __name__ == "__main__":
    try:
        migrate_files()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
