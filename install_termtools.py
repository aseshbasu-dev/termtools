'''
CONFIGURABLE PYTHON PROJECT INSTALLER

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

Installation Flow Now:
✅ Check admin privileges → elevate if needed
🧹 NEW: Clean up existing installation completely
📥 Download from GitHub
📦 Extract files
📂 Create fresh directory structure
📋 Copy files
🐍 Create virtual environment
📦 Install requirements
🖱️ Set up context menu

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
import json
from datetime import datetime

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
USE_VENV_COPIES = False                     # Use --copies flag for venv creation (disabled to avoid permission issues)
VENV_IN_APPDATA = True                      # Create venv in AppData to avoid Program Files permission issues

# Context Menu Configuration
CONTEXT_MENU_DISPLAY_TEXT = "Run TermTools"  # Text shown in right-click menu
REGISTRY_KEY_PATH = r"Software\Classes\Directory\Background\shell\TermTools"

# Installation Behavior
AUTO_UPGRADE_PIP = True                     # Upgrade pip in virtual environment
INSTALL_REQUIREMENTS = True                 # Install from requirements.txt if present
CLEANUP_ON_ERROR = True                     # Clean up temp files on error
REQUIRE_VENV = True                         # MANDATORY: TermTools requires virtual environment

# CRITICAL: TermTools ONLY runs with virtual environment. 
# No system Python fallback is allowed.
# VENV_IN_APPDATA=True helps avoid permission issues when creating
# virtual environments in Program Files. The venv will be created in:
# %USERPROFILE%\AppData\Local\BasusTools\TermTools\.venv

# ==========================================
# END CONFIGURATION VARIABLES
# ==========================================

def get_remote_head_sha(owner, repo, branch="main"):
    """Get the latest commit hash from GitHub API without installing git packages"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data["sha"]
    except Exception as e:
        print(f"Warning: Could not fetch remote commit hash: {e}")
        return None

def save_installation_metadata(target_app, repo_owner, repo_name, commit_hash):
    """Save installation timestamp and commit hash to user's AppData directory"""
    try:
        # Save to user's AppData\Local directory (writable without admin)
        appdata_local = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        data_dir = os.path.join(appdata_local, 'BasusTools', 'TermTools')
        os.makedirs(data_dir, exist_ok=True)
        
        metadata_file = os.path.join(data_dir, "installation_info.json")
        
        metadata = {
            "installation_timestamp": datetime.now().isoformat(),
            "repository": f"{repo_owner}/{repo_name}",
            "remote_commit_hash": commit_hash,
            "installer_version": "2.0",
            "installation_path": target_app,
            "data_directory": data_dir
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Installation metadata saved to {metadata_file}")
        if commit_hash:
            print(f"   Remote commit hash: {commit_hash[:8]}...")
        print(f"   Installation time: {metadata['installation_timestamp']}")
        print(f"   Data directory: {data_dir}")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not save installation metadata: {e}")




def setup_context_menu_with_venv(target_app, venv_path):
    """Set up Windows context menu to use virtual environment Python ONLY"""
    script_path = os.path.join(target_app, MAIN_SCRIPT_NAME)
    
    # CRITICAL: Only use virtual environment Python (no system Python fallback)
    if venv_path is None:
        raise RuntimeError("Cannot setup context menu without virtual environment")
    
    python_exe = os.path.join(venv_path, "Scripts", "pythonw.exe")
    print(f"   Using virtual environment Python: {python_exe}")
    
    # Verify the Python executable exists
    if not os.path.exists(python_exe):
        raise RuntimeError(f"Virtual environment Python not found at: {python_exe}")
    
    menu_key = REGISTRY_KEY_PATH
    command_key = menu_key + r"\command"
    
    cmd = f'"{python_exe}" "{script_path}" "%V"'
    
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
        icon_path = python_exe
    
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

# ==========================================
# CLEANUP EXISTING INSTALLATION
# ==========================================
print("\n🧹 Checking for existing installation...")

# Remove existing Program Files installation
target_base = os.path.join(program_files, TARGET_BASE_FOLDER)
target_app = os.path.join(target_base, TARGET_APP_FOLDER)

if os.path.exists(target_app):
    print(f"   Found existing installation at: {target_app}")
    print(f"   Removing old installation...")
    try:
        shutil.rmtree(target_app, ignore_errors=False)
        print(f"   ✅ Old installation removed successfully")
    except Exception as e:
        print(f"   ⚠️  Warning: Could not fully remove old installation: {e}")
        print(f"   Will attempt to overwrite...")

# Remove existing virtual environment in AppData (if using AppData location)
if VENV_IN_APPDATA:
    appdata_venv_dir = os.path.expanduser(f"~\\AppData\\Local\\{TARGET_BASE_FOLDER}\\{TARGET_APP_FOLDER}")
    if os.path.exists(appdata_venv_dir):
        print(f"   Found existing virtual environment at: {appdata_venv_dir}")
        print(f"   Removing old virtual environment...")
        try:
            shutil.rmtree(appdata_venv_dir, ignore_errors=False)
            print(f"   ✅ Old virtual environment removed successfully")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not fully remove old venv: {e}")
            print(f"   Will attempt to overwrite...")

print("✅ Cleanup complete, starting fresh installation...\n")

# ==========================================
# END CLEANUP
# ==========================================

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
    # (Cleanup already done at script start)
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
    print("🔧 Setting up virtual environment...")
    
    # Determine venv location
    if VENV_IN_APPDATA:
        # Create venv in AppData to avoid Program Files permission issues
        appdata_dir = os.path.expanduser("~\\AppData\\Local\\BasusTools\\TermTools")
        os.makedirs(appdata_dir, exist_ok=True)
        venv_path = os.path.join(appdata_dir, VENV_FOLDER_NAME)
        print(f"   Using AppData location for venv: {venv_path}")
    else:
        # Create venv in installation directory (original behavior)
        venv_path = os.path.join(target_app, VENV_FOLDER_NAME)
        print(f"   Using installation directory for venv: {venv_path}")
    
    # Check if venv already exists and is functional
    venv_python = os.path.join(venv_path, "Scripts", "python.exe")
    venv_exists_and_works = False
    
    if os.path.exists(venv_path) and os.path.exists(venv_python):
        print(f"   Existing venv found at {venv_path}")
        # Test if the venv is functional
        try:
            test_result = subprocess.run(
                [venv_python, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=True
            )
            print(f"   ✅ Existing venv is functional: {test_result.stdout.strip()}")
            print("   Skipping venv recreation to avoid permission conflicts")
            venv_exists_and_works = True
        except Exception as e:
            print(f"   ⚠️ Existing venv appears broken: {e}")
            print("   Will attempt to recreate...")
    
    # Try multiple approaches for venv creation (only if needed)
    venv_created = venv_exists_and_works
    
    # First attempt: with --copies flag (current behavior)
    if USE_VENV_COPIES and not venv_created:
        try:
            print("   Attempting with --copies flag...")
            venv_cmd = [python_executable, "-m", "venv", venv_path, "--copies"]
            result = subprocess.run(venv_cmd, capture_output=True, text=True, check=True, cwd=target_app)
            print("✅ Virtual environment created successfully (with --copies)")
            venv_created = True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  First attempt failed: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
    
    # Second attempt: without --copies flag
    if not venv_created:
        try:
            print("   Attempting without --copies flag...")
            venv_cmd = [python_executable, "-m", "venv", venv_path]
            result = subprocess.run(venv_cmd, capture_output=True, text=True, check=True, cwd=target_app)
            print("✅ Virtual environment created successfully (without --copies)")
            venv_created = True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Second attempt failed: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
    
    # Third attempt: with system-site-packages (fallback)
    if not venv_created:
        try:
            print("   Attempting with --system-site-packages flag...")
            venv_cmd = [python_executable, "-m", "venv", venv_path, "--system-site-packages"]
            result = subprocess.run(venv_cmd, capture_output=True, text=True, check=True, cwd=target_app)
            print("✅ Virtual environment created successfully (with --system-site-packages)")
            venv_created = True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Third attempt failed: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
    
    if not venv_created:
        print("❌ All virtual environment creation attempts failed")
        print("❌ CRITICAL ERROR: TermTools REQUIRES a virtual environment to run")
        print("   Installation cannot continue without a working virtual environment.")
        print("\n💡 Troubleshooting tips:")
        print("   1. Ensure Python was installed with 'pip' support")
        print("   2. Try running: python -m ensurepip --upgrade")
        print("   3. Check that you have write permissions to the AppData directory")
        print(f"   4. Attempted venv location: {venv_path}")
        raise RuntimeError("Failed to create virtual environment - TermTools installation aborted")
    else:
        print(f"✅ Virtual environment ready at: {venv_path}")

    # Install requirements if requirements.txt exists and enabled
    requirements_path = os.path.join(target_app, REQUIREMENTS_FILE)
    if INSTALL_REQUIREMENTS and os.path.exists(requirements_path):
        if venv_exists_and_works:
            print(f"🔧 Updating dependencies from {REQUIREMENTS_FILE}...")
        else:
            print(f"🔧 Installing requirements from {REQUIREMENTS_FILE}...")
        
        # CRITICAL: Only use virtual environment (system Python fallback removed)
        print("   Using virtual environment Python...")
        venv_python = os.path.join(venv_path, "Scripts", "python.exe")
        
        # Verify venv python exists (should always exist if we got here)
        if not os.path.exists(venv_python):
            print(f"❌ CRITICAL: Virtual environment Python not found at: {venv_python}")
            raise RuntimeError("Virtual environment is corrupted or incomplete")
        
        # Always use python -m pip instead of direct pip executable for reliability
        pip_cmd_base = [venv_python, "-m", "pip"]
        
        # Upgrade pip first if enabled
        if AUTO_UPGRADE_PIP:
            try:
                print("   Upgrading pip in virtual environment...")
                result = subprocess.run(pip_cmd_base + ["install", "--upgrade", "pip"], 
                                      capture_output=True, text=True, check=True, cwd=target_app)
                print("✅ Pip upgraded successfully")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Warning: Could not upgrade pip: {e}")
                if e.stderr:
                    print(f"   {e.stderr.strip()}")
                # Continue anyway - pip might still work for installation
        
        # Install requirements to virtual environment ONLY
        try:
            print("   Installing requirements to virtual environment...")
            result = subprocess.run(pip_cmd_base + ["install", "-r", REQUIREMENTS_FILE], 
                                  capture_output=True, text=True, check=True, cwd=target_app)
            print("✅ Requirements installed successfully")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Error installing requirements: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            
            # Try alternative installation method - bootstrap pip if missing
            if "No module named pip" in str(e) or "No module named pip" in (e.stderr or ""):
                print("   Attempting to bootstrap pip in virtual environment...")
                try:
                    # Try to bootstrap pip using ensurepip
                    subprocess.run([venv_python, "-m", "ensurepip", "--upgrade"], 
                                 capture_output=True, text=True, check=True)
                    print("   Pip bootstrapped successfully, retrying requirements installation...")
                    
                    # Retry installation
                    result = subprocess.run(pip_cmd_base + ["install", "-r", REQUIREMENTS_FILE], 
                                          capture_output=True, text=True, check=True, cwd=target_app)
                    print("✅ Requirements installed successfully after pip bootstrap")
                except subprocess.CalledProcessError as bootstrap_e:
                    print(f"❌ CRITICAL: Pip bootstrap failed: {bootstrap_e}")
                    raise RuntimeError("Failed to install requirements - TermTools needs wxPython to run")
            else:
                print(f"❌ CRITICAL: Requirements installation failed")
                raise RuntimeError("Failed to install requirements - TermTools needs wxPython to run")
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

    # Get remote commit hash and save installation metadata
    print("🔧 Saving installation metadata...")
    commit_hash = get_remote_head_sha(REPO_OWNER, REPO_NAME, REPO_BRANCH)
    save_installation_metadata(target_app, REPO_OWNER, REPO_NAME, commit_hash)

    print(f"\n🎉 {TARGET_APP_FOLDER} installation completed successfully!")
    print(f"📍 Installation location: {target_app}")
    print(f"🐍 Virtual environment: {venv_path}")
    print(f" Right-click context menu added - you can now run {TARGET_APP_FOLDER} from any folder")
    print(f"\n⚠️  IMPORTANT: TermTools runs ONLY from its virtual environment")
    print(f"   Do not delete the virtual environment at: {venv_path}")

finally:
    if CLEANUP_ON_ERROR:
        print("\n🧹 Cleaning up temporary files...")
        shutil.rmtree(tempdir, ignore_errors=True)
        print("✅ Cleanup completed")
    else:
        print(f"\n🧹 Temporary files left in: {tempdir} (cleanup disabled in configuration)")
