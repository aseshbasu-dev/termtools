'''
can be used as:
(Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/basu-10/installers/main/installer_termtools.py').Content | python -

or
(Invoke-WebRequest -UseBasicParsing "https://raw.githubusercontent.com/basu-10/termtools/main/install_termtools.py").Content | python -

(Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/basu-10/termtools/main/install_termtools.py').Content | python -

https://github.com/aseshbasu-dev/termtools.git

The install_termtools.py script is a complete installer that downloads, installs, and configures TermTools for Windows with right-click context menu integration.

Installs TermTools from GitHub to Program Files and sets up context menu.
Run once as Administrator.

'''


'''
1. Initial Setup & Security
    Admin Check: Verifies if running with administrator privileges
    Auto-Elevation: If not admin, re-launches itself with elevated permissions using ShellExecuteW
    Exit: Original non-admin process exits after launching elevated version
2. Configuration
    Target Path: C:\Program Files\BasusTools\TermTools\
3. Download & Extract
    Download: Fetches ZIP from https://github.com/basu-10/termtools/archive/refs/heads/main.zip
    Temp Directory: Creates temporary directory with prefix gh_install_
    Extract: Unzips to temporary extraction directory
4. Installation
    Directory Structure: Creates C:\Program Files\BasusTools\TermTools\
    Cleanup: Removes existing installation if present
    File Copy: Copies all files and directories from extracted source to target
    Preservation: Maintains directory structure and file permissions
5. Context Menu Integration
    Script Location: Looks for add_to_context_menu.py in installed location
    Registry Modification: If found, runs the context menu setup script
    Registry Keys Created:
    HKEY_LOCAL_MACHINE\Software\Classes\Directory\Background\shell\TermTools
    Command: "python.exe" "C:\Program Files\BasusTools\TermTools\TermTools.py" "%V"
    Display Text: "Run TermTools"
6. Cleanup
    Temp Removal: Deletes temporary directory and all downloaded/extracted files
    Error Handling: Uses ignore_errors=True for robust cleanup
    
'''

import os, shutil, tempfile, zipfile, urllib.request, subprocess
import ctypes, sys

# Check for admin privileges and re-run with elevation if needed
if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

REPO = "basu-10/termtools"     # e.g. "user/repo"
BRANCH = "main"
TARGET_BASE = "BasusTools"
TARGET_APP = "TermTools"

program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
tempdir = tempfile.mkdtemp(prefix="gh_install_")

try:
    zip_path = os.path.join(tempdir, "repo.zip")
    url = f"https://github.com/{REPO}/archive/refs/heads/{BRANCH}.zip"
    print("Downloading", url)
    urllib.request.urlretrieve(url, zip_path)

    extract_dir = os.path.join(tempdir, "extract")
    os.makedirs(extract_dir)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(extract_dir)
    print("Extracted to", extract_dir)

    root = next(os.scandir(extract_dir)).path

    # Create the target directory structure: BasusTools/TermTools
    target_base = os.path.join(program_files, TARGET_BASE)
    target_app = os.path.join(target_base, TARGET_APP)
    
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
    print(f"Installed to {target_app}.")

    print("Setting up context menu...")
    # run add_to_context_menu.py if found in installed location
    py = os.path.join(target_app, "add_to_context_menu.py")
    if os.path.exists(py):
        subprocess.run(["python", py], check=False)

finally:
    print("Cleaning up...")
    shutil.rmtree(tempdir, ignore_errors=True)
