"""
Folder Copy Operations Module for TermTools
Built by Asesh Basu

This module provides functionality to copy the current folder while excluding
.venv and __pycache__ directories, with user-defined naming.
"""

import os
import shutil
import sys
from pathlib import Path
import wx
from ..blueprint import Blueprint

# Create the blueprint for folder copy operations
folder_copy_bp = Blueprint("folder_copy", "Copy folder with custom naming and exclusions")


class FolderCopyOperations:
    """Folder copy operations with exclusions"""
    
    @staticmethod
    def copy_folder_with_exclusions(app=None):
        """Copy current folder without .venv and __pycache__ directories with user-defined naming."""
        print("\n📁 Starting folder copy with exclusions...")
        
        current_dir = Path(os.getcwd())
        parent_dir = current_dir.parent
        folder_name = current_dir.name
        
        print(f"🔍 Current folder: {current_dir}")
        print(f"📂 Parent directory: {parent_dir}")
        
        # Get modification text from user via GUI
        modification_text = FolderCopyOperations._get_modification_text_from_user()
        if not modification_text:
            print("❌ Operation cancelled by user")
            return
        
        # Generate new folder name
        base_name = f"{folder_name}_copy_{modification_text}"
        new_folder_path = parent_dir / base_name
        
        # Handle existing folder with incremental numbering
        final_folder_path = FolderCopyOperations._get_available_folder_name(new_folder_path)
        
        print(f"🎯 Target folder: {final_folder_path}")
        
        try:
            # Perform the copy with exclusions
            FolderCopyOperations._copy_with_exclusions(current_dir, final_folder_path)
            print(f"✅ Folder copied successfully!")
            print(f"📁 New folder location: {final_folder_path}")
            
            # Show summary
            FolderCopyOperations._show_copy_summary(current_dir, final_folder_path)
            
        except Exception as e:
            print(f"❌ Error copying folder: {e}")
            if final_folder_path.exists():
                try:
                    shutil.rmtree(final_folder_path)
                    print(f"🧹 Cleaned up partially copied folder")
                except:
                    pass
    
    @staticmethod
    def _get_modification_text_from_user():
        """Get modification text from user via GUI dialog."""
        try:
            # Get current folder name for dynamic example
            current_dir = Path(os.getcwd())
            folder_name = current_dir.name
            
            # Check if we're in a GUI environment
            if wx and wx.GetApp():
                dlg = wx.TextEntryDialog(
                    None,  # Use None as parent, wx will find appropriate parent
                    f"Enter modification text for the copied folder:\n\n"
                    f"The folder will be named: <folder_name>_copy_<your_text>\n"
                    f"Example: {folder_name}_copy_backup",
                    "Folder Copy - Enter Modification Text",
                    "backup"  # Default value
                )
                
                result = None
                if dlg.ShowModal() == wx.ID_OK:
                    text = dlg.GetValue().strip()
                    if text:
                        # Clean the text to be filesystem-safe
                        result = FolderCopyOperations._clean_filename(text)
                    else:
                        wx.MessageBox(
                            "Modification text cannot be empty!",
                            "Invalid Input",
                            wx.OK | wx.ICON_WARNING
                        )
                
                dlg.Destroy()
                return result
            else:
                print("❌ GUI text entry dialog unavailable - TermTools requires GUI mode")
                print("💡 Using default modification text: 'backup'")
                return "backup"
                
        except Exception as e:
            print(f"❌ Error showing GUI dialog: {e}")
            print("💡 Using default modification text: 'backup'")
            return "backup"
    
    @staticmethod
    def _clean_filename(text):
        """Clean text to be filesystem-safe."""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            text = text.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        text = text.strip(' .')
        
        # Limit length
        if len(text) > 50:
            text = text[:50]
        
        return text
    
    @staticmethod
    def _get_available_folder_name(base_path):
        """Get an available folder name using incremental numbering if needed."""
        if not base_path.exists():
            return base_path
        
        # Extract base name and try incremental numbers
        base_name = base_path.name
        parent = base_path.parent
        counter = 2
        
        while True:
            new_name = f"{base_name} ({counter})"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
            
            # Prevent infinite loop
            if counter > 1000:
                raise Exception("Too many existing folders with similar names")
    
    @staticmethod
    def _copy_with_exclusions(source_dir, dest_dir):
        """Copy directory with exclusions for .venv and __pycache__."""
        excluded_dirs = {'.venv', '__pycache__', '.git'}
        excluded_files = {'.gitignore'}  # You can add more if needed
        
        def should_exclude(path):
            """Check if a path should be excluded."""
            name = path.name
            
            # Exclude specific directory names
            if name in excluded_dirs:
                return True
            
            # Exclude specific file names
            if name in excluded_files:
                return True
            
            # Exclude Python bytecode files
            if name.endswith('.pyc') or name.endswith('.pyo'):
                return True
            
            return False
        
        print(f"📋 Exclusion rules:")
        print(f"   - Directories: {', '.join(excluded_dirs)}")
        print(f"   - Files: {', '.join(excluded_files)}")
        print(f"   - Python bytecode files (*.pyc, *.pyo)")
        print()
        
        copied_files = 0
        copied_dirs = 0
        excluded_items = 0
        
        # Create destination directory
        dest_dir.mkdir(parents=True, exist_ok=True)
        copied_dirs += 1
        
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)
            relative_path = root_path.relative_to(source_dir)
            current_dest = dest_dir / relative_path
            
            # Filter out excluded directories
            dirs_to_remove = []
            for dirname in dirs:
                dir_path = root_path / dirname
                if should_exclude(dir_path):
                    dirs_to_remove.append(dirname)
                    excluded_items += 1
                    print(f"⏭️  Excluding directory: {dir_path.relative_to(source_dir)}")
            
            for dirname in dirs_to_remove:
                dirs.remove(dirname)
            
            # Create directories
            for dirname in dirs:
                dir_dest = current_dest / dirname
                dir_dest.mkdir(parents=True, exist_ok=True)
                copied_dirs += 1
            
            # Copy files
            for filename in files:
                file_path = root_path / filename
                if should_exclude(file_path):
                    excluded_items += 1
                    print(f"⏭️  Excluding file: {file_path.relative_to(source_dir)}")
                    continue
                
                file_dest = current_dest / filename
                shutil.copy2(file_path, file_dest)
                copied_files += 1
        
        print(f"📊 Copy Statistics:")
        print(f"   📁 Directories copied: {copied_dirs}")
        print(f"   📄 Files copied: {copied_files}")
        print(f"   ⏭️  Items excluded: {excluded_items}")
    
    @staticmethod
    def _show_copy_summary(source_dir, dest_dir):
        """Show a summary of the copy operation."""
        try:
            source_size = FolderCopyOperations._get_folder_size(source_dir)
            dest_size = FolderCopyOperations._get_folder_size(dest_dir)
            
            print(f"\n📈 Size Comparison:")
            print(f"   📂 Original folder: {FolderCopyOperations._format_size(source_size)}")
            print(f"   📁 Copied folder: {FolderCopyOperations._format_size(dest_size)}")
            
            if source_size > dest_size:
                saved_size = source_size - dest_size
                percentage = (saved_size / source_size) * 100
                print(f"   💾 Space saved by exclusions: {FolderCopyOperations._format_size(saved_size)} ({percentage:.1f}%)")
            
        except Exception as e:
            print(f"⚠️  Could not calculate size comparison: {e}")
    
    @staticmethod
    def _get_folder_size(folder_path):
        """Calculate total size of a folder in bytes."""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, FileNotFoundError):
                    pass
        return total_size
    
    @staticmethod
    def _format_size(size_bytes):
        """Format size in bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} TB"


# Register menu items using the blueprint decorator
@folder_copy_bp.route("11", "Copy Folder (Exclude .venv & __pycache__)", 
                     "Copy current folder with custom naming, excluding .venv and __pycache__ directories",
                     "📁 FOLDER OPERATIONS", order=1)
def copy_folder_with_exclusions(app=None):
    """Menu handler for folder copy with exclusions"""
    FolderCopyOperations.copy_folder_with_exclusions(app)


@folder_copy_bp.on_init
def init_folder_copy_module(app):
    """Initialize the folder copy module"""
    app.set_config("folder_copy_enabled", True)
    print("🔧 Folder copy module initialized")