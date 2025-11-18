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
from ..blueprint import Blueprint
import threading
import logging

# Setup logger for this module
logger = logging.getLogger(__name__)

# Create the blueprint for folder copy operations
folder_copy_bp = Blueprint("folder_copy", "Copy folder with custom naming and exclusions")


class FolderCopyOperations:
    """Folder copy operations with exclusions"""
    
    @staticmethod
    def copy_folder_with_exclusions(app=None):
        """Copy current folder without .venv and __pycache__ directories with user-defined naming."""
        logger.info("Starting folder copy with exclusions operation")
        print("\n📁 Starting folder copy with exclusions...")
        
        try:
            current_dir = Path(os.getcwd())
            parent_dir = current_dir.parent
            folder_name = current_dir.name
            
            logger.debug(f"Current folder: {current_dir}")
            logger.debug(f"Parent directory: {parent_dir}")
            print(f"🔍 Current folder: {current_dir}")
            print(f"📂 Parent directory: {parent_dir}")
            
            # Check if modification text was pre-captured (from GUI)
            modification_text = None
            if app:
                modification_text = app.get_config('_folder_copy_modification_text')
                if modification_text:
                    logger.info(f"Using pre-captured modification text: '{modification_text}'")
            
            # If not pre-captured, get from user via GUI
            if not modification_text:
                logger.debug("Requesting modification text from user")
                modification_text = FolderCopyOperations._get_modification_text_from_user()
                if not modification_text:
                    logger.info("Operation cancelled by user")
                    print("❌ Operation cancelled by user")
                    return
                
                logger.info(f"User entered modification text: {modification_text}")
        except Exception as e:
            logger.error(f"Error during folder copy initialization: {e}", exc_info=True)
            print(f"❌ Error during initialization: {e}")
            return
        
        try:
            # Generate new folder name
            base_name = f"{folder_name}_copy_{modification_text}"
            new_folder_path = parent_dir / base_name
            
            logger.debug(f"Generated base folder name: {base_name}")
            
            # Handle existing folder with incremental numbering
            final_folder_path = FolderCopyOperations._get_available_folder_name(new_folder_path)
            
            logger.info(f"Target folder path: {final_folder_path}")
            print(f"🎯 Target folder: {final_folder_path}")
            
            # Perform the copy with exclusions
            logger.info("Starting file copy operation")
            FolderCopyOperations._copy_with_exclusions(current_dir, final_folder_path)
            
            logger.info("Copy operation completed successfully")
            print(f"✅ Folder copied successfully!")
            print(f"📁 New folder location: {final_folder_path}")
            
            # Show summary
            FolderCopyOperations._show_copy_summary(current_dir, final_folder_path)
            
        except Exception as e:
            logger.error(f"Error during folder copy operation: {e}", exc_info=True)
            print(f"❌ Error copying folder: {e}")
            if final_folder_path.exists():
                try:
                    logger.debug(f"Cleaning up partially copied folder: {final_folder_path}")
                    shutil.rmtree(final_folder_path)
                    logger.info("Cleanup completed")
                    print(f"🧹 Cleaned up partially copied folder")
                except Exception as cleanup_error:
                    logger.error(f"Error during cleanup: {cleanup_error}", exc_info=True)
                    pass
    
    @staticmethod
    def _get_modification_text_from_user():
        """Get modification text from user via GUI dialog.
        
        IMPORTANT: This must be called from the main GUI thread.
        """
        logger.debug("Entering _get_modification_text_from_user")
        try:
            from PyQt6.QtWidgets import QApplication, QInputDialog, QMessageBox
            import threading
            
            # Get current folder name for dynamic example
            current_dir = Path(os.getcwd())
            folder_name = current_dir.name
            
            logger.debug(f"Current thread: {threading.current_thread().name}")
            logger.debug(f"Main thread: {threading.main_thread().name}")
            
            # Check if we're in a PyQt6 GUI environment
            app = QApplication.instance()
            if not app:
                logger.warning("No QApplication instance found")
                print("❌ GUI text entry dialog unavailable - TermTools requires GUI mode")
                print("💡 Using default modification text: 'backup'")
                return "backup"
            
            # MUST be called from main thread
            if threading.current_thread() is not threading.main_thread():
                logger.error("_get_modification_text_from_user called from worker thread!")
                print("❌ Dialog cannot be shown from worker thread")
                print("💡 Using default modification text: 'backup'")
                return "backup"
            
            logger.debug("Showing input dialog")
            text, ok = QInputDialog.getText(
                None,
                "Folder Copy - Enter Modification Text",
                f"Enter modification text for the copied folder:\n\n"
                f"The folder will be named: {folder_name}_copy_<your_text>\n"
                f"Example: {folder_name}_copy_backup",
                text="backup"  # Default value
            )
            
            logger.debug(f"Dialog result - ok: {ok}, text: {text if ok else 'N/A'}")
            
            if ok and text.strip():
                cleaned = FolderCopyOperations._clean_filename(text.strip())
                logger.info(f"User input accepted: '{cleaned}'")
                return cleaned
            elif ok and not text.strip():
                logger.warning("User provided empty text")
                QMessageBox.warning(
                    None,
                    "Invalid Input",
                    "Modification text cannot be empty!"
                )
                return None
            else:
                logger.info("User cancelled dialog")
                return None  # User cancelled
                
        except ImportError as e:
            logger.error(f"PyQt6 not available: {e}")
            print("❌ PyQt6 not available - using default modification text")
            print("💡 Using default modification text: 'backup'")
            return "backup"
        except Exception as e:
            logger.error(f"Error showing GUI dialog: {e}", exc_info=True)
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
        logger.debug(f"Checking availability of path: {base_path}")
        if not base_path.exists():
            logger.debug("Path is available")
            return base_path
        
        # Extract base name and try incremental numbers
        base_name = base_path.name
        parent = base_path.parent
        counter = 2
        
        logger.debug(f"Path exists, finding alternative with counter")
        while True:
            new_name = f"{base_name} ({counter})"
            new_path = parent / new_name
            if not new_path.exists():
                logger.debug(f"Found available path: {new_path}")
                return new_path
            counter += 1
            
            # Prevent infinite loop
            if counter > 1000:
                logger.error("Too many existing folders with similar names")
                raise Exception("Too many existing folders with similar names")
    
    @staticmethod
    def _copy_with_exclusions(source_dir, dest_dir):
        """Copy directory with exclusions for .venv and __pycache__."""
        logger.info(f"Copying from {source_dir} to {dest_dir}")
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