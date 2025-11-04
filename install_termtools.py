'''
CONFIGURABLE PYTHON PROJECT INSTALLER

This script can be used as a one-line installer from GitHub:
Open PowerShell as Administrator and run:
(Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/aseshbasu-dev/termtools/main/install_termtools.py').Content | python -

OR download and run directly:
Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/aseshbasu-dev/termtools/main/install_termtools.py' -OutFile 'install_termtools.py'; python install_termtools.py

🔧 REUSABLE FOR ANY PROJECT:
Modify the configuration variables at the top of this script to adapt it for any GitHub repository.
Simply change REPO_OWNER, REPO_NAME, TARGET_BASE_FOLDER, TARGET_APP_FOLDER, and other settings.

Original project: TermTools - Python Project Manager
at: https://github.com/aseshbasu-dev/termtools.git

The install_termtools.py script is a complete installer that downloads, installs, and configures any Python project from GitHub with Windows context menu integration.

🔧 PREREQUISITES:
- Windows OS (required)
- Administrator privileges (auto-elevation)
- Python 3.8+ (must be installed and accessible via 'python' command)
- Internet connection (required for downloads)

Installs the configured project from GitHub to Program Files and sets up context menu.
Run once as Administrator.

'''


'''
1. Initial Setup & Security
    Admin Check: Verifies if running with administrator privileges
    Auto-Elevation: If not admin, re-launches itself with elevated permissions using ShellExecuteW
    Exit: Original non-admin process exits after launching elevated version
2. Configuration
    Target Path: C:\\Program Files\\BasusTools\\TermTools\\
    Python: Uses the current Python executable (since script is already running)
3. Download & Extract
    Download: Fetches ZIP from https://github.com/aseshbasu-dev/termtools/archive/refs/heads/main.zip
    Temp Directory: Creates temporary directory with prefix gh_install_
    Extract: Unzips to temporary extraction directory
4. Installation
    Directory Structure: Creates C:\\Program Files\\BasusTools\\TermTools\\
    Cleanup: Removes existing installation if present
    File Copy: Copies all files and directories from extracted source to target
    Preservation: Maintains directory structure and file permissions
5. Virtual Environment Setup
    Creates: .venv directory in installation folder using current Python
    Pip Upgrade: Updates pip to latest version in virtual environment
    Requirements: Installs dependencies from requirements.txt if present
    Error Handling: Clear error messages with emoji indicators for each step
6. Context Menu Integration
    Registry Modification: Creates HKEY_LOCAL_MACHINE\\Software\\Classes\\Directory\\Background\\shell\\TermTools
    Python Path: Uses virtual environment Python executable for consistent execution
    Command: "{venv_python}" "C:\\Program Files\\BasusTools\\TermTools\\TermTools.py" "%V"
    Display Text: "Run TermTools"
7. Cleanup & Completion
    Temp Removal: Deletes temporary directory and all downloaded/extracted files
    Success Report: Shows installation location, venv path, and context menu status
    Error Handling: Uses ignore_errors=True for robust cleanup
    
'''

import os, shutil, tempfile, zipfile, urllib.request, subprocess
import ctypes, sys
import winreg

# ==========================================
# CONFIGURATION VARIABLES - MODIFY AS NEEDED
# ==========================================

# Repository Information
REPO_OWNER = "aseshbasu-dev"
REPO_NAME = "termtools"
REPO_BRANCH = "main"

# Installation Paths
TARGET_BASE_FOLDER = "BasusTools"           # Base folder under Program Files
TARGET_APP_FOLDER = "TermTools"             # Application folder name
MAIN_SCRIPT_NAME = "TermTools.py"           # Main script filename
REQUIREMENTS_FILE = "requirements.txt"      # Requirements file name

# Virtual Environment Configuration
VENV_FOLDER_NAME = ".venv"                  # Virtual environment folder name
USE_VENV_COPIES = True                      # Use --copies flag for venv creation

# Context Menu Configuration
CONTEXT_MENU_DISPLAY_TEXT = "Run TermTools"  # Text shown in right-click menu
REGISTRY_KEY_PATH = r"Software\Classes\Directory\Background\shell\TermTools"

# Installation Behavior
AUTO_UPGRADE_PIP = True                     # Upgrade pip in virtual environment
INSTALL_REQUIREMENTS = True                 # Install from requirements.txt if present
CLEANUP_ON_ERROR = True                     # Clean up temp files on error

# ==========================================
# END CONFIGURATION VARIABLES
# ==========================================



def setup_context_menu_with_venv(target_app, venv_path):
    """Set up Windows context menu to use virtual environment Python"""
    script_path = os.path.join(target_app, MAIN_SCRIPT_NAME)
    venv_python = os.path.join(venv_path, "Scripts", "python.exe")
    
    menu_key = REGISTRY_KEY_PATH
    command_key = menu_key + r"\command"
    
    cmd = f'"{venv_python}" "{script_path}" "%V"'
    
    # Try to find an icon file in the installation directory
    icon_path = None
    possible_icons = ["termtools.ico", "logo.ico", "icon.ico"]
    for icon_name in possible_icons:
        potential_path = os.path.join(target_app, "core", "data", icon_name)
        if os.path.exists(potential_path):
            icon_path = potential_path
            break
    
    # Fallback to Python executable icon if no custom icon found
    if not icon_path:
        icon_path = venv_python
    
    with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as hk:
        # create menu key and set its displayed text
        with winreg.CreateKeyEx(hk, menu_key, 0, winreg.KEY_WRITE) as k:
            winreg.SetValueEx(k, None, 0, winreg.REG_SZ, CONTEXT_MENU_DISPLAY_TEXT)
            # Add icon to the context menu entry
            winreg.SetValueEx(k, "Icon", 0, winreg.REG_SZ, icon_path)
        # create command subkey and set the command
        with winreg.CreateKeyEx(hk, command_key, 0, winreg.KEY_WRITE) as k:
            winreg.SetValueEx(k, None, 0, winreg.REG_SZ, cmd)

# Check for admin privileges and re-run with elevation if needed
if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# Use the current Python executable (script is already running, so Python exists)
python_executable = sys.executable
print(f"🐍 Using Python: {python_executable}")

# Build repository URL from configuration
REPO_FULL_NAME = f"{REPO_OWNER}/{REPO_NAME}"

program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
tempdir = tempfile.mkdtemp(prefix="gh_install_")

try:
    zip_path = os.path.join(tempdir, "repo.zip")
    url = f"https://github.com/{REPO_FULL_NAME}/archive/refs/heads/{REPO_BRANCH}.zip"
    print("Downloading", url)
    urllib.request.urlretrieve(url, zip_path)

    extract_dir = os.path.join(tempdir, "extract")
    os.makedirs(extract_dir)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(extract_dir)
    print("Extracted to", extract_dir)

    root = next(os.scandir(extract_dir)).path

    # Create the target directory structure using configuration
    target_base = os.path.join(program_files, TARGET_BASE_FOLDER)
    target_app = os.path.join(target_base, TARGET_APP_FOLDER)
    
    if os.path.exists(target_app):
        shutil.rmtree(target_app, ignore_errors=True)
    os.makedirs(target_app, exist_ok=True)
    
    # Copy all files to the TermTools subdirectory
    for item in os.listdir(root):
        s = os.path.join(root, item)
        d = os.path.join(target_app, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    print(f"✅ Files copied to {target_app}")

    # Create virtual environment using configuration
    print("🔧 Creating virtual environment...")
    venv_path = os.path.join(target_app, VENV_FOLDER_NAME)
    try:
        venv_cmd = [python_executable, "-m", "venv", venv_path]
        if USE_VENV_COPIES:
            venv_cmd.append("--copies")
        
        result = subprocess.run(venv_cmd, capture_output=True, text=True, check=True, cwd=target_app)
        print("✅ Virtual environment created successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating virtual environment: {e}")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        raise

    # Install requirements if requirements.txt exists and enabled
    requirements_path = os.path.join(target_app, REQUIREMENTS_FILE)
    if INSTALL_REQUIREMENTS and os.path.exists(requirements_path):
        print(f"🔧 Installing requirements from {REQUIREMENTS_FILE}...")
        venv_python = os.path.join(venv_path, "Scripts", "python.exe")
        venv_pip = os.path.join(venv_path, "Scripts", "pip.exe")
        
        # Upgrade pip first if enabled
        if AUTO_UPGRADE_PIP:
            try:
                result = subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], 
                                      capture_output=True, text=True, check=True, cwd=target_app)
                print("✅ Pip upgraded successfully")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Warning: Could not upgrade pip: {e}")
                if e.stderr:
                    print(f"   {e.stderr.strip()}")
        
        # Install requirements
        try:
            result = subprocess.run([venv_pip, "install", "-r", REQUIREMENTS_FILE], 
                                  capture_output=True, text=True, check=True, cwd=target_app)
            print("✅ Requirements installed successfully")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing requirements: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            raise
    else:
        if not INSTALL_REQUIREMENTS:
            print("ℹ️  Requirements installation disabled in configuration")
        else:
            print(f"ℹ️  No {REQUIREMENTS_FILE} found, skipping dependency installation")

    # Set up context menu with venv Python
    print("🔧 Setting up context menu with virtual environment Python...")
    try:
        setup_context_menu_with_venv(target_app, venv_path)
        print("✅ Context menu configured successfully")
    except Exception as e:
        print(f"❌ Error setting up context menu: {e}")
        raise

    print(f"\n🎉 {TARGET_APP_FOLDER} installation completed successfully!")
    print(f"📍 Installation location: {target_app}")
    print(f"🐍 Virtual environment: {venv_path}")
    print(f"📋 Right-click context menu added - you can now run {TARGET_APP_FOLDER} from any folder")

finally:
    if CLEANUP_ON_ERROR:
        print("\n🧹 Cleaning up temporary files...")
        shutil.rmtree(tempdir, ignore_errors=True)
        print("✅ Cleanup completed")
    else:
        print(f"\n🧹 Temporary files left in: {tempdir} (cleanup disabled in configuration)")
