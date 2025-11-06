"""
Python Environment Module for TermTools
Built by Asesh Basu

This module provides Python environment management functionality including
virtual environment creation, requirements file management, and cleanup operations.
"""

import os
import shutil
import venv
import subprocess
import threading
from pathlib import Path
from ..blueprint import Blueprint

def _get_subprocess_flags():
    """Get subprocess creation flags to prevent console window flashing on Windows"""
    if os.name == 'nt':
        return {'creationflags': subprocess.CREATE_NO_WINDOW}
    return {}


# Import wx for GUI confirmations
try:
    import wx
except ImportError:
    wx = None

# Create the blueprint for Python environment management
python_env_bp = Blueprint("python_env", "Python environment and dependency management")


class PythonEnvironment:
    """Python environment management operations"""
    
    @staticmethod
    def _show_gui_confirmation(message, title="Confirm Action"):
        """Show GUI confirmation dialog, thread-safe for background operations"""
        try:
            # Check if we're in a GUI environment
            if wx and wx.GetApp():
                # If we're already on the main thread, show dialog directly
                if threading.current_thread() is threading.main_thread():
                    dlg = wx.MessageDialog(
                        None,
                        message,
                        title,
                        wx.YES_NO | wx.ICON_QUESTION | wx.NO_DEFAULT
                    )
                    result = dlg.ShowModal()
                    dlg.Destroy()
                    return result == wx.ID_YES
                else:
                    # We're on a background thread, use wx.CallAfter with event
                    result_holder = {'result': None, 'done': threading.Event()}
                    
                    def show_on_main_thread():
                        try:
                            dlg = wx.MessageDialog(
                                None,
                                message,
                                title,
                                wx.YES_NO | wx.ICON_QUESTION | wx.NO_DEFAULT
                            )
                            result_holder['result'] = (dlg.ShowModal() == wx.ID_YES)
                            dlg.Destroy()
                        except Exception as e:
                            print(f"❌ Dialog error: {e}")
                            result_holder['result'] = False
                        finally:
                            result_holder['done'].set()
                    
                    wx.CallAfter(show_on_main_thread)
                    result_holder['done'].wait(timeout=30)  # Wait up to 30 seconds
                    return result_holder['result'] if result_holder['result'] is not None else False
            else:
                PythonEnvironment._show_gui_unavailable_error("confirmation dialog", message, title)
                return False
        except Exception as e:
            PythonEnvironment._show_gui_error("confirmation dialog", str(e), message, title)
            return False
    
    @staticmethod
    def _show_terminal_confirmation(message):
        """Legacy method - now shows error instead of terminal input"""
        PythonEnvironment._show_gui_unavailable_error("confirmation dialog", message, "Confirm Action")
        return False
    
    @staticmethod
    def _show_gui_choice(message, title, choices, default_choice=0):
        """Show GUI choice dialog, thread-safe for background operations"""
        try:
            # Check if we're in a GUI environment
            if wx and wx.GetApp():
                # If we're already on the main thread, show dialog directly
                if threading.current_thread() is threading.main_thread():
                    dlg = wx.SingleChoiceDialog(
                        None,
                        message,
                        title,
                        choices
                    )
                    dlg.SetSelection(default_choice)
                    
                    if dlg.ShowModal() == wx.ID_OK:
                        selection = dlg.GetSelection()
                        dlg.Destroy()
                        return selection
                    else:
                        dlg.Destroy()
                        return -1  # Cancelled
                else:
                    # We're on a background thread, use wx.CallAfter with event
                    result_holder = {'result': -1, 'done': threading.Event()}
                    
                    def show_on_main_thread():
                        try:
                            dlg = wx.SingleChoiceDialog(
                                None,
                                message,
                                title,
                                choices
                            )
                            dlg.SetSelection(default_choice)
                            
                            if dlg.ShowModal() == wx.ID_OK:
                                result_holder['result'] = dlg.GetSelection()
                            else:
                                result_holder['result'] = -1
                            dlg.Destroy()
                        except Exception as e:
                            print(f"❌ Dialog error: {e}")
                            result_holder['result'] = -1
                        finally:
                            result_holder['done'].set()
                    
                    wx.CallAfter(show_on_main_thread)
                    result_holder['done'].wait(timeout=30)  # Wait up to 30 seconds
                    return result_holder['result']
            else:
                PythonEnvironment._show_gui_unavailable_error("choice dialog", message, title, choices)
                return -1
        except Exception as e:
            PythonEnvironment._show_gui_error("choice dialog", str(e), message, title, choices)
            return -1
    
    @staticmethod
    def _show_terminal_choice(message, choices):
        """Legacy method - now shows error instead of terminal input"""
        PythonEnvironment._show_gui_unavailable_error("choice dialog", message, "Select Option", choices)
        return -1
    
    @staticmethod
    def _show_gui_unavailable_error(dialog_type, message, title, choices=None):
        """Show comprehensive error when GUI is unavailable"""
        print(f"\n❌ GUI {dialog_type} unavailable - TermTools requires GUI mode")
        print(f"📋 Dialog details:")
        print(f"   Title: {title}")
        print(f"   Message: {message}")
        if choices:
            print(f"   Choices: {', '.join(choices)}")
        
        print(f"\n🐛 Error Report for GitHub Issue:")
        print(f"=" * 60)
        print(f"**Issue**: GUI {dialog_type} failed to display")
        print(f"**Component**: Python Environment Module")
        print(f"**OS**: Windows")
        print(f"**Python Version**: {__import__('sys').version}")
        print(f"**wxPython Available**: {'Yes' if wx else 'No'}")
        print(f"**wx.GetApp() Result**: {bool(wx.GetApp()) if wx else 'N/A'}")
        print(f"**Dialog Type**: {dialog_type}")
        print(f"**Dialog Title**: {title}")
        print(f"**Dialog Message**: {message}")
        if choices:
            print(f"**Dialog Choices**: {choices}")
        print(f"**Expected Behavior**: GUI dialog should appear for user interaction")
        print(f"**Actual Behavior**: No GUI dialog displayed, operation cancelled")
        print(f"**Workaround**: None available - requires GUI fix")
        print(f"=" * 60)
        print(f"\n💡 Please copy the above error report and submit it as a GitHub issue")
        print(f"   Repository: https://github.com/aseshbasu-dev/termtools/issues")
    
    @staticmethod
    def _show_gui_error(dialog_type, error_details, message, title, choices=None):
        """Show comprehensive error when GUI fails with exception"""
        print(f"\n❌ GUI {dialog_type} error - Exception occurred")
        print(f"📋 Dialog details:")
        print(f"   Title: {title}")
        print(f"   Message: {message}")
        if choices:
            print(f"   Choices: {', '.join(choices)}")
        print(f"   Error: {error_details}")
        
        print(f"\n🐛 Error Report for GitHub Issue:")
        print(f"=" * 60)
        print(f"**Issue**: GUI {dialog_type} exception")
        print(f"**Component**: Python Environment Module")
        print(f"**OS**: Windows")
        print(f"**Python Version**: {__import__('sys').version}")
        print(f"**wxPython Available**: {'Yes' if wx else 'No'}")
        print(f"**wx.GetApp() Result**: {bool(wx.GetApp()) if wx else 'N/A'}")
        print(f"**Dialog Type**: {dialog_type}")
        print(f"**Dialog Title**: {title}")
        print(f"**Dialog Message**: {message}")
        if choices:
            print(f"**Dialog Choices**: {choices}")
        print(f"**Exception Details**: {error_details}")
        print(f"**Expected Behavior**: GUI dialog should appear for user interaction")
        print(f"**Actual Behavior**: Exception thrown, operation cancelled")
        print(f"**Workaround**: None available - requires GUI fix")
        print(f"=" * 60)
        print(f"\n💡 Please copy the above error report and submit it as a GitHub issue")
        print(f"   Repository: https://github.com/aseshbasu-dev/termtools/issues")
    
    @staticmethod
    def create_new_venv():
        """Create a new .venv with optional .gitignore and requirements.txt files."""
        print("\n🐍 Creating new virtual environment...")
        
        venv_path = Path(".venv")
        
        # Check if .venv already exists
        if venv_path.exists():
            print(f"⚠️  .venv already exists at: {venv_path.absolute()}")
            
            message = f".venv already exists at:\n{venv_path.absolute()}\n\nDo you want to delete it and create a new one?"
            if not PythonEnvironment._show_gui_confirmation(message, "Virtual Environment Exists"):
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
            message = "Create .gitignore file?"
            choices = ["Yes", "No"]
            choice = PythonEnvironment._show_gui_choice(message, "Create .gitignore", choices, default_choice=0)
            
            if choice == 0:  # Yes
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
            message = "Create requirements.txt file?"
            choices = ["Yes", "No"]
            choice = PythonEnvironment._show_gui_choice(message, "Create requirements.txt", choices, default_choice=0)
            
            if choice == 0:  # Yes
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
    def create_venv_with_requirements():
        """Create a new .venv with requirements.txt file."""
        print("\n🐍 Creating new virtual environment with requirements.txt...")
        
        venv_path = Path(".venv")
        
        # Check if .venv already exists
        if venv_path.exists():
            print(f"⚠️  .venv already exists at: {venv_path.absolute()}")
            
            message = f".venv already exists at:\n{venv_path.absolute()}\n\nDo you want to delete it and create a new one?"
            if not PythonEnvironment._show_gui_confirmation(message, "Virtual Environment Exists"):
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
        
        # Create requirements.txt
        print("\n📦 Creating requirements.txt file...")
        requirements_path = Path("requirements.txt")
        
        if requirements_path.exists():
            print(f"⚠️  requirements.txt already exists. Overwriting...")
        
        try:
            requirements_content = "# Add your project dependencies here\n# Example:\n# requests>=2.25.1\n# flask>=2.0.0\n"
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write(requirements_content)
            print(f"✅ requirements.txt created at: {requirements_path.absolute()}")
        except Exception as e:
            print(f"❌ Error creating requirements.txt: {e}")
        
        print("\n🎉 Virtual environment with requirements.txt setup complete!")
        
    @staticmethod
    def create_venv_with_all_files():
        """Create a new .venv with requirements.txt, .gitignore, and README.md files."""
        print("\n🐍 Creating new virtual environment with requirements.txt, .gitignore, and README.md...")
        
        venv_path = Path(".venv")
        
        # Check if .venv already exists
        if venv_path.exists():
            print(f"⚠️  .venv already exists at: {venv_path.absolute()}")
            
            message = f".venv already exists at:\n{venv_path.absolute()}\n\nDo you want to delete it and create a new one?"
            if not PythonEnvironment._show_gui_confirmation(message, "Virtual Environment Exists"):
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
        
        # Create requirements.txt
        print("\n📦 Creating requirements.txt file...")
        requirements_path = Path("requirements.txt")
        
        if requirements_path.exists():
            print(f"⚠️  requirements.txt already exists. Overwriting...")
        
        try:
            requirements_content = "# Add your project dependencies here\n# Example:\n# requests>=2.25.1\n# flask>=2.0.0\n"
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write(requirements_content)
            print(f"✅ requirements.txt created at: {requirements_path.absolute()}")
        except Exception as e:
            print(f"❌ Error creating requirements.txt: {e}")
        
        # Create .gitignore
        print("\n📄 Creating .gitignore file...")
        gitignore_path = Path(".gitignore")
        
        if gitignore_path.exists():
            print(f"⚠️  .gitignore already exists. Overwriting...")
        
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
        
        # Create README.md
        print("\n📖 Creating README.md file...")
        readme_path = Path("README.md")
        
        if readme_path.exists():
            print(f"⚠️  README.md already exists. Overwriting...")
        
        try:
            project_name = Path.cwd().name
            readme_content = f"""# {project_name}

## Description
A Python project created with TermTools.

## Setup

### 1. Activate the virtual environment

**Windows:**
```bash
.venv\\Scripts\\activate.bat
```

**Unix/Linux/macOS:**
```bash
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

## Usage
Add your project usage instructions here.

## Contributing
Add your contribution guidelines here.

## License
Add your license information here.
"""
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print(f"✅ README.md created at: {readme_path.absolute()}")
        except Exception as e:
            print(f"❌ Error creating README.md: {e}")
        
        print("\n🎉 Complete virtual environment setup with all files complete!")
            
    @staticmethod
    def create_requirements_file():
        """Create a new requirements.txt file with template options."""
        print("\n📝 Creating requirements.txt file...")
        
        choices = [
            "Empty requirements.txt",
            "Flask basic",
            "Flask + Data Science (numpy, pandas, matplotlib, seaborn)"
        ]
        
        choice = PythonEnvironment._show_gui_choice(
            "Select requirements template:",
            "Create requirements.txt",
            choices
        )
        
        if choice == -1:  # Cancelled
            print("❌ Operation cancelled.")
            return
        elif choice == 0:
            content = "# Add your project dependencies here\n# Example:\n# requests>=2.25.1\n# flask>=2.0.0\n"
            template_name = "Empty"
        elif choice == 1:
            content = """# Flask Basic Dependencies
flask>=2.3.0
python-dotenv>=0.19.0
"""
            template_name = "Flask Basic"
        elif choice == 2:
            content = """# Flask + Data Science Dependencies
flask>=2.3.0
python-dotenv>=0.19.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
"""
            template_name = "Flask + Data Science"
        else:
            print("❌ Invalid choice.")
            return
                
        # Write requirements.txt file
        requirements_path = Path("requirements.txt")
        
        if requirements_path.exists():
            message = f"requirements.txt already exists.\n\nDo you want to overwrite it?"
            if not PythonEnvironment._show_gui_confirmation(message, "File Exists"):
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
    
    @staticmethod
    def create_gitignore_file():
        """Create a standalone .gitignore file."""
        print("\n📄 Creating .gitignore file...")
        
        gitignore_path = Path(".gitignore")
        
        if gitignore_path.exists():
            message = f".gitignore already exists.\n\nDo you want to overwrite it?"
            if not PythonEnvironment._show_gui_confirmation(message, "File Exists"):
                print("❌ Operation cancelled.")
                return
        
        gitignore_content = """# Virtual Environment
.venv/
env/
ENV/
venv/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
"""
        
        try:
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            print(f"✅ .gitignore created successfully at: {gitignore_path.absolute()}")
        except Exception as e:
            print(f"❌ Error creating .gitignore: {e}")
    
    @staticmethod
    def create_readme_file():
        """Create a standalone README.md file."""
        print("\n📋 Creating README.md file...")
        
        readme_path = Path("README.md")
        
        if readme_path.exists():
            message = f"README.md already exists.\n\nDo you want to overwrite it?"
            if not PythonEnvironment._show_gui_confirmation(message, "File Exists"):
                print("❌ Operation cancelled.")
                return
        
        # Get project name from current directory
        project_name = Path.cwd().name
        
        readme_content = f"""# {project_name}

## Description
Brief description of your project.

## Installation
1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\\Scripts\\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
Describe how to use your project.

## Contributing
Instructions for contributing to the project.

## License
Specify the license for your project.
"""
        
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print(f"✅ README.md created successfully at: {readme_path.absolute()}")
        except Exception as e:
            print(f"❌ Error creating README.md: {e}")
    
    @staticmethod
    def start_project():
        """
        Start project development environment:
        1. Create .venv if not exists (with optional overwrite)
        2. Activate the .venv
        3. Install requirements.txt if exists or create it if not
        4. Open VS Code with 'code .'
        
        VS Code opens regardless of previous step completion.
        """
        print("\n🚀 Starting project development environment...")
        
        venv_path = Path(".venv")
        
        # Step 1: Handle virtual environment
        print("[1/4] 🐍 Setting up virtual environment...")
        
        if venv_path.exists():
            print("ℹ️  A virtual environment already exists.")
            
            message = f"A virtual environment already exists at:\n{venv_path.absolute()}\n\nDo you want to delete it and create a new one?"
            if PythonEnvironment._show_gui_confirmation(message, "Virtual Environment Exists"):
                try:
                    print("🗑️  Deleting existing .venv...")
                    shutil.rmtree(venv_path)
                    print("✅ Existing .venv deleted.")
                    
                    print("🔨 Creating new virtual environment...")
                    venv.create(venv_path, with_pip=True)
                    print("✅ New virtual environment created.")
                except Exception as e:
                    print(f"❌ Error managing virtual environment: {e}")
                    print("⚠️  Continuing with remaining steps...")
            else:
                print("✅ Keeping existing virtual environment.")
        else:
            try:
                print("🔨 Creating virtual environment...")
                venv.create(venv_path, with_pip=True)
                print("✅ Virtual environment created successfully.")
            except Exception as e:
                print(f"❌ Error creating virtual environment: {e}")
                print("⚠️  Continuing with remaining steps...")
        
        # Step 2: Activate virtual environment (informational - actual activation in VS Code terminal)
        print("\n[2/4] 🔧 Virtual environment activation...")
        if os.name == 'nt':  # Windows
            activate_script = venv_path / "Scripts" / "activate.bat"
            print(f"💡 To manually activate: {activate_script}")
        else:  # Unix-like systems
            activate_script = venv_path / "bin" / "activate"
            print(f"💡 To manually activate: source {activate_script}")
        print("✅ VS Code will use this environment when opened.")
        
        # Step 3: Open VS Code (this should happen regardless)
        print("\n[3/4] 📝 Opening VS Code...")
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['code', '.'], shell=True, **_get_subprocess_flags())
            else:  # Unix-like systems
                subprocess.Popen(['code', '.'], **_get_subprocess_flags())
            print("✅ VS Code opened successfully.")
        except Exception as e:
            print(f"⚠️  Could not open VS Code automatically: {e}")
            print("💡 You can manually open VS Code by running: code .")
        
        # Step 4: Handle requirements.txt
        print("\n[4/4] 📦 Managing requirements...")
        requirements_path = Path("requirements.txt")
        
        if requirements_path.exists():
            print("ℹ️  Found existing requirements.txt file.")
            
            message = f"Found requirements.txt file at:\n{requirements_path.absolute()}\n\nDo you want to install the requirements?"
            choices = ["Yes, install requirements", "No, skip installation"]
            choice = PythonEnvironment._show_gui_choice(message, "Install Requirements", choices, default_choice=0)
            
            if choice == 0:  # Yes, install
                try:
                    # Get the appropriate pip path for the virtual environment
                    if os.name == 'nt':  # Windows
                        pip_path = venv_path / "Scripts" / "pip.exe"
                    else:  # Unix-like systems
                        pip_path = venv_path / "bin" / "pip"
                    
                    print("📥 Installing requirements...")
                    result = subprocess.run([str(pip_path), 'install', '-r', 'requirements.txt'], 
                                          capture_output=True, text=True, **_get_subprocess_flags())
                    
                    if result.returncode == 0:
                        print("✅ Requirements installed successfully.")
                        if result.stdout.strip():
                            # Show some output but not too verbose
                            lines = result.stdout.strip().split('\n')
                            for line in lines[-5:]:  # Show last 5 lines
                                print(f"   {line}")
                    else:
                        print(f"❌ Error installing requirements:")
                        if result.stderr:
                            print(f"   {result.stderr.strip()}")
                        print("💡 You can manually install by running: pip install -r requirements.txt")
                            
                except Exception as e:
                    print(f"❌ Error installing requirements: {e}")
                    print("💡 You can manually install by running: pip install -r requirements.txt")
            else:
                print("ℹ️  Skipped requirements installation.")
                print("💡 You can manually install later by running: pip install -r requirements.txt")
        else:
            print("ℹ️  No requirements.txt found.")
            
            message = "Create a basic requirements.txt file?"
            choices = ["Yes", "No"]
            choice = PythonEnvironment._show_gui_choice(message, "Create requirements.txt", choices, default_choice=0)
            
            if choice == 0:  # Yes
                try:
                    # Create basic requirements.txt
                    basic_requirements = """# Basic Python requirements
# Add your project dependencies here
# Example:
# flask>=2.0.0
# requests>=2.28.0
# python-dotenv>=0.19.0
"""
                    requirements_path.write_text(basic_requirements, encoding='utf-8')
                    print("✅ Basic requirements.txt created.")
                    print("💡 Edit the file to add your project dependencies.")
                except Exception as e:
                    print(f"❌ Error creating requirements.txt: {e}")
            else:
                print("ℹ️  Skipped requirements.txt creation.")
        
        print("\n🎉 Project startup completed!")
        print("💡 Next steps:")
        print("   1. VS Code should be opening automatically")
        print("   2. Select your .venv Python interpreter in VS Code")
        print("   3. Use the integrated terminal in VS Code for development")
        print("   4. Install additional packages as needed")


# Register blueprint routes using decorators
@python_env_bp.route("2", "Create new .venv", "With .gitignore and requirements.txt options", "🐍 PYTHON ENVIRONMENT MANAGEMENT", 1)
def create_new_venv(app=None):
    """Create new .venv with optional .gitignore and requirements.txt files"""
    PythonEnvironment.create_new_venv()


@python_env_bp.route("2.5", "Start Project", "Create .venv if not exist, activate .venv, install requirements.txt if exists or create it, run code .", "🚀 PROJECT DEVELOPMENT", 0)
def start_project(app=None):
    """Start project development environment"""
    PythonEnvironment.start_project()


@python_env_bp.route("3", "Create new requirements.txt file", "Choose from templates", "🐍 PYTHON ENVIRONMENT MANAGEMENT", 2)
def create_requirements_file(app=None):
    """Create a new requirements.txt file with template options"""
    PythonEnvironment.create_requirements_file()


@python_env_bp.route("4", "Delete .venv folders recursively", "Recursive search", "🐍 PYTHON ENVIRONMENT MANAGEMENT", 3)
def delete_all_venvs(app=None):
    """Delete all .venv folders recursively"""
    PythonEnvironment.delete_all_venvs()


# Initialize blueprint on import
@python_env_bp.on_init
def init_python_env(app):
    """Initialize the Python environment module"""
    app.set_config("python_env_enabled", True)