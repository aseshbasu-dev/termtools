"""
Python Environment Module for TermTools
Built by Asesh Basu

This module provides Python environment management functionality including
virtual environment creation, requirements file management, and cleanup operations.
"""

import os
import shutil
import venv
from pathlib import Path
from ..blueprint import Blueprint

# Create the blueprint for Python environment management
python_env_bp = Blueprint("python_env", "Python environment and dependency management")


class PythonEnvironment:
    """Python environment management operations"""
    
    @staticmethod
    def create_new_venv():
        """Create a new .venv with optional .gitignore and requirements.txt files."""
        print("\n🐍 Creating new virtual environment...")
        
        venv_path = Path(".venv")
        
        # Check if .venv already exists
        if venv_path.exists():
            print(f"⚠️  .venv already exists at: {venv_path.absolute()}")
            response = input("Do you want to delete it and create a new one? (y/N): ").strip().lower()
            if response != 'y':
                print("❌ Operation cancelled.")
                return
            
            # Delete existing .venv
            print(f"🗑️  Deleting existing .venv...")
            try:
                shutil.rmtree(venv_path)
                print("✅ Existing .venv deleted successfully.")
            except Exception as e:
                print(f"❌ Error deleting .venv: {e}")
                return
        
        # Create new virtual environment
        print("🔨 Creating new virtual environment...")
        try:
            venv.create(venv_path, with_pip=True)
            print(f"✅ New virtual environment created at: {venv_path.absolute()}")
            
            # Provide activation instructions
            if os.name == 'nt':  # Windows
                activate_script = venv_path / "Scripts" / "activate.bat"
                print(f"\n💡 To activate the virtual environment, run:")
                print(f"   {activate_script}")
            else:  # Unix-like systems
                activate_script = venv_path / "bin" / "activate"
                print(f"\n💡 To activate the virtual environment, run:")
                print(f"   source {activate_script}")
                
        except Exception as e:
            print(f"❌ Error creating virtual environment: {e}")
            return
        
        # Ask about creating .gitignore
        print("\n📄 Optional: Create .gitignore file?")
        gitignore_path = Path(".gitignore")
        
        if gitignore_path.exists():
            print(f"ℹ️  .gitignore already exists. Skipping.")
        else:
            response = input("Create .gitignore file? (Y/n): ").strip().lower()
            if response in ['y', 'yes', '']:
                try:
                    gitignore_content = """# Virtual Environment
.venv/
venv/
env/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Distribution / packaging
build/
dist/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment variables
.env
.env.local

# OS
.DS_Store
Thumbs.db
"""
                    with open(gitignore_path, 'w', encoding='utf-8') as f:
                        f.write(gitignore_content)
                    print(f"✅ .gitignore created at: {gitignore_path.absolute()}")
                except Exception as e:
                    print(f"❌ Error creating .gitignore: {e}")
            else:
                print("⏭️  Skipped .gitignore creation.")
        
        # Ask about creating requirements.txt
        print("\n📦 Optional: Create requirements.txt file?")
        requirements_path = Path("requirements.txt")
        
        if requirements_path.exists():
            print(f"ℹ️  requirements.txt already exists. Skipping.")
        else:
            response = input("Create requirements.txt file? (Y/n): ").strip().lower()
            if response in ['y', 'yes', '']:
                try:
                    requirements_content = "# Add your project dependencies here\n# Example:\n# requests>=2.25.1\n# flask>=2.0.0\n"
                    with open(requirements_path, 'w', encoding='utf-8') as f:
                        f.write(requirements_content)
                    print(f"✅ requirements.txt created at: {requirements_path.absolute()}")
                except Exception as e:
                    print(f"❌ Error creating requirements.txt: {e}")
            else:
                print("⏭️  Skipped requirements.txt creation.")
        
        print("\n🎉 Virtual environment setup complete!")
            
    @staticmethod
    def create_requirements_file():
        """Create a new requirements.txt file with template options."""
        print("\n📝 Creating requirements.txt file...")
        
        print("\nSelect requirements template:")
        print("1. Empty requirements.txt")
        print("2. Flask basic")
        print("3. Flask + Data Science (numpy, pandas, matplotlib, seaborn)")
        print("4. Cancel")
        
        while True:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                content = "# Add your project dependencies here\n# Example:\n# requests>=2.25.1\n# flask>=2.0.0\n"
                template_name = "Empty"
                break
            elif choice == "2":
                content = """# Flask Basic Dependencies
flask>=2.3.0
python-dotenv>=0.19.0
"""
                template_name = "Flask Basic"
                break
            elif choice == "3":
                content = """# Flask + Data Science Dependencies
flask>=2.3.0
python-dotenv>=0.19.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
"""
                template_name = "Flask + Data Science"
                break
            elif choice == "4":
                print("❌ Operation cancelled.")
                return
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
                
        # Write requirements.txt file
        requirements_path = Path("requirements.txt")
        
        if requirements_path.exists():
            response = input(f"requirements.txt already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operation cancelled.")
                return
                
        try:
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {template_name} requirements.txt created successfully at: {requirements_path.absolute()}")
        except Exception as e:
            print(f"❌ Error creating requirements.txt: {e}")
            
    @staticmethod
    def delete_all_venvs():
        """Delete all .venv folders in the current directory tree."""
        print("\n🗑️  Searching for .venv folders to delete...")
        
        deleted_count = 0
        total_size = 0
        current_dir = os.getcwd()
        
        # Walk through all directories recursively
        for root, dirs, files in os.walk(current_dir):
            # Check if .venv is in the current directory
            if ".venv" in dirs:
                venv_path = os.path.join(root, ".venv")
                try:
                    # Calculate size before deletion
                    folder_size = PythonEnvironment._get_folder_size(venv_path)
                    total_size += folder_size
                    
                    # Remove the .venv directory
                    shutil.rmtree(venv_path)
                    print(f"✅ Deleted: {venv_path}")
                    deleted_count += 1
                    
                    # Remove from dirs to prevent os.walk from entering it
                    dirs.remove(".venv")
                    
                except Exception as e:
                    print(f"❌ Error deleting {venv_path}: {e}")
                    
        if deleted_count == 0:
            print("❌ No .venv folders found.")
        else:
            size_mb = total_size / (1024 * 1024)
            print(f"\n📊 Summary: {deleted_count} .venv folders deleted.")
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
@python_env_bp.route("2", "Create new .venv", "With .gitignore and requirements.txt options", "🐍 PYTHON ENVIRONMENT MANAGEMENT", 1)
def create_new_venv(app=None):
    """Create new .venv with optional .gitignore and requirements.txt files"""
    PythonEnvironment.create_new_venv()


@python_env_bp.route("3", "Create new requirements.txt file", "Choose from templates", "🐍 PYTHON ENVIRONMENT MANAGEMENT", 2)
def create_requirements_file(app=None):
    """Create a new requirements.txt file with template options"""
    PythonEnvironment.create_requirements_file()


@python_env_bp.route("4", "Delete all .venv folders", "Recursive search", "🐍 PYTHON ENVIRONMENT MANAGEMENT", 3)
def delete_all_venvs(app=None):
    """Delete all .venv folders recursively"""
    PythonEnvironment.delete_all_venvs()


# Initialize blueprint on import
@python_env_bp.on_init
def init_python_env(app):
    """Initialize the Python environment module"""
    app.set_config("python_env_enabled", True)