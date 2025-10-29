"""
Cleanup Operations Module for TermTools
Built by Asesh Basu

This module provides cleanup functionality for Python projects including
cache files, build artifacts, and thumbnail files.
"""

import os
import shutil
import sys
import subprocess
import fnmatch
from ..blueprint import Blueprint

# Create the blueprint for cleanup operations
cleanup_bp = Blueprint("cleanup", "Clean up build artifacts and cache files")


class CleanupOperations:
    """Cleanup operations for Python projects"""
    
    @staticmethod
    def delete_pycache_only():
        """Delete only __pycache__ folders recursively from current directory."""
        print("\n🗑️  Deleting __pycache__ folders recursively...")
        
        deleted_count = 0
        total_size = 0
        current_dir = os.getcwd()
        
        # Walk through all directories recursively
        for root, dirs, files in os.walk(current_dir):
            # Check if __pycache__ is in the current directory
            if "__pycache__" in dirs:
                pycache_path = os.path.join(root, "__pycache__")
                try:
                    # Calculate size before deletion
                    folder_size = CleanupOperations._get_folder_size(pycache_path)
                    total_size += folder_size
                    
                    # Remove the __pycache__ directory
                    shutil.rmtree(pycache_path)
                    print(f"✅ Deleted: {pycache_path}")
                    deleted_count += 1
                    
                    # Remove from dirs to prevent os.walk from entering it
                    dirs.remove("__pycache__")
                    
                except Exception as e:
                    print(f"❌ Error deleting {pycache_path}: {e}")
                    
        if deleted_count == 0:
            print("❌ No __pycache__ folders found.")
        else:
            size_mb = total_size / (1024 * 1024)
            print(f"\n📊 Summary: {deleted_count} __pycache__ folders deleted.")
            print(f"💾 Total space freed: {size_mb:.2f} MB")
            
    @staticmethod
    def clean_build_artifacts():
        """Delete .pyc, .pyo, dist/, build/, .egg-info/ and __pycache__ folders."""
        print("\n🧹 Cleaning up build artifacts and cache files...")
        
        deleted_files = 0
        deleted_folders = 0
        total_size = 0
        current_dir = os.getcwd()
        
        # Patterns to clean
        file_patterns = ['*.pyc', '*.pyo']
        folder_patterns = ['__pycache__', 'dist', 'build', '*.egg-info']
        
        print("\n🔍 Scanning for build artifacts...")
        
        # Walk through all directories recursively
        for root, dirs, files in os.walk(current_dir):
            # Delete files matching patterns
            for pattern in file_patterns:
                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            print(f"✅ Deleted file: {file_path}")
                            deleted_files += 1
                            total_size += file_size
                        except Exception as e:
                            print(f"❌ Error deleting file {file_path}: {e}")
            
            # Delete directories matching patterns
            dirs_to_remove = []
            for pattern in folder_patterns:
                for dir_name in dirs[:]:  # Use slice to avoid modification during iteration
                    if fnmatch.fnmatch(dir_name, pattern):
                        dir_path = os.path.join(root, dir_name)
                        try:
                            # Calculate size before deletion
                            folder_size = CleanupOperations._get_folder_size(dir_path)
                            total_size += folder_size
                            
                            # Remove the directory
                            shutil.rmtree(dir_path)
                            print(f"✅ Deleted folder: {dir_path}")
                            deleted_folders += 1
                            dirs_to_remove.append(dir_name)
                            
                        except Exception as e:
                            print(f"❌ Error deleting folder {dir_path}: {e}")
            
            # Remove deleted directories from dirs list to prevent os.walk from entering them
            for dir_name in dirs_to_remove:
                if dir_name in dirs:
                    dirs.remove(dir_name)
                    
        if deleted_files == 0 and deleted_folders == 0:
            print("❌ No build artifacts found.")
        else:
            size_mb = total_size / (1024 * 1024)
            print(f"\n📊 Summary:")
            print(f"   Files deleted: {deleted_files}")
            print(f"   Folders deleted: {deleted_folders}")
            print(f"   Total space freed: {size_mb:.2f} MB")
            
    @staticmethod
    def delete_thumbnails():
        """Delete all thumbnail files recursively from current directory."""
        print("\n🗑️  Deleting thumbnail files recursively...")
        
        deleted_count = 0
        total_size = 0
        current_dir = os.getcwd()
        
        # Check if send2trash is available, try to install if not
        try:
            from send2trash import send2trash
            recycle_available = True
        except ImportError:
            print("⚠️  send2trash not available, attempting to install...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'send2trash'], 
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                from send2trash import send2trash
                recycle_available = True
                print("✅ send2trash installed successfully.")
            except subprocess.CalledProcessError:
                print("❌ Failed to install send2trash. Recycle bin will not be available.")
                recycle_available = False
        
        # Walk through all directories recursively
        for root, dirs, files in os.walk(current_dir):
            for file in files:
                if "thumb" in file.lower():
                    file_path = os.path.join(root, file)
                    try:
                        # Calculate size before deletion
                        file_size = os.path.getsize(file_path)
                        
                        # Skip files larger than 1MB to avoid deleting non-thumbnail files
                        if file_size > 1024 * 1024:
                            print(f"⏭️  Skipped large file: {file_path} ({file_size / (1024 * 1024):.2f} MB)")
                            continue
                        
                        # Try permanent deletion first
                        try:
                            os.remove(file_path)
                            print(f"✅ Permanently deleted: {file_path}")
                            deleted_count += 1
                            total_size += file_size
                        except Exception as e:
                            # If permanent fails, try recycle bin if available
                            if recycle_available:
                                try:
                                    send2trash(file_path)
                                    print(f"🗑️  Moved to recycle bin: {file_path}")
                                    deleted_count += 1
                                    total_size += file_size
                                except Exception as recycle_e:
                                    print(f"❌ Failed to delete {file_path}: {e} (permanent) and {recycle_e} (recycle)")
                            else:
                                print(f"❌ Failed to delete {file_path}: {e} (permanent) - recycle bin not available")
                        
                    except Exception as e:
                        print(f"❌ Error accessing {file_path}: {e}")
                        
        if deleted_count == 0:
            print("❌ No thumbnail files found.")
        else:
            size_mb = total_size / (1024 * 1024)
            print(f"\n📊 Summary: {deleted_count} thumbnail files deleted.")
            print(f"💾 Total space freed: {size_mb:.2f} MB")
    
    @staticmethod
    def _get_folder_size(folder_path):
        """Calculate the total size of a folder in bytes."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception:
            pass
        return total_size


# Register blueprint routes using decorators
@cleanup_bp.route("6", "Delete only __pycache__ folders", "Python cache cleanup", "🧹 CLEAN UP OPERATIONS", 1)
def delete_pycache_only(app=None):
    """Delete only __pycache__ folders recursively"""
    CleanupOperations.delete_pycache_only()


@cleanup_bp.route("7", "Clean up build artifacts", ".pyc, .pyo, dist/, build/, etc.", "🧹 CLEAN UP OPERATIONS", 2)
def clean_build_artifacts(app=None):
    """Delete build artifacts and cache files"""
    CleanupOperations.clean_build_artifacts()


@cleanup_bp.route("8", "Delete thumbnail files", "With safety checks", "🧹 CLEAN UP OPERATIONS", 3)
def delete_thumbnails(app=None):
    """Delete thumbnail files with safety checks"""
    CleanupOperations.delete_thumbnails()


# Initialize blueprint on import
@cleanup_bp.on_init
def init_cleanup(app):
    """Initialize the cleanup module"""
    app.set_config("cleanup_enabled", True)