# TermTools Installer Fix - Virtual Environment Creation Issue

## Problem
The TermTools installer (`install_termtools.py`) was failing when trying to create a virtual environment in the `C:\Program Files\BasusTools\TermTools\.venv` directory. The error was:

```
subprocess.CalledProcessError: Command ['C:\\users\\Asesh\\AppData\\Local\\Programs\\Python\\Python312\\python.exe', '-m', 'venv', 'C:\\Program Files\\BasusTools\\TermTools\\.venv', '--copies'] returned non-zero exit status 1.
```

## Root Cause
- **Permission Issues**: Creating virtual environments in `C:\Program Files` can fail even with administrator privileges due to Windows security restrictions
- **--copies Flag**: The `--copies` flag can sometimes cause additional permission issues in restricted directories

## Solution Implemented
Enhanced the installer with **multiple fallback strategies**:

### 1. **Robust Virtual Environment Creation**
The installer now tries three different approaches in order:
1. With `--copies` flag (if enabled in config)
2. Without `--copies` flag (standard venv creation)
3. With `--system-site-packages` flag (fallback option)

### 2. **AppData Location for Virtual Environment**
- **NEW**: Added `VENV_IN_APPDATA = True` configuration option
- Virtual environment is now created in: `%USERPROFILE%\AppData\Local\BasusTools\TermTools\.venv`
- This avoids Program Files permission restrictions entirely

### 3. **Graceful Degradation**
- If all venv creation attempts fail, the installer continues
- Dependencies are installed to system Python with `--user` flag
- TermTools still works, just without isolated environment

### 4. **Smart Context Menu Setup**
- Automatically detects whether venv was created successfully
- Uses venv Python if available, falls back to system Python
- Updates registry command accordingly

## Configuration Changes
```python
# Before (in install_termtools.py)
USE_VENV_COPIES = True                      # Could cause permission issues

# After
USE_VENV_COPIES = False                     # Disabled to avoid permission issues
VENV_IN_APPDATA = True                      # Create venv in AppData instead of Program Files
```

## Benefits
1. **Higher Success Rate**: Multiple fallback strategies prevent installation failures
2. **Better Permissions**: AppData location avoids Program Files restrictions
3. **Maintains Functionality**: TermTools works even if venv creation fails
4. **User-Friendly**: Clear error messages and progress indicators
5. **Future-Proof**: Configurable options for different environments

## Testing
The fix has been tested with:
- ✅ Virtual environment creation in temporary directories
- ✅ Multiple fallback strategies
- ✅ Permission handling
- ✅ Context menu setup with both venv and system Python

## Usage
Run the installer as before:
```powershell
# One-line installation (as Administrator)
(Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/aseshbasu-dev/termtools/main/install_termtools.py').Content | python -
```

The installer will now:
1. Try to create venv in AppData (usually succeeds)
2. If that fails, try alternative venv creation methods
3. If all venv attempts fail, install to system Python
4. Continue with context menu setup regardless

## Files Modified
- `install_termtools.py`: Enhanced venv creation logic and error handling