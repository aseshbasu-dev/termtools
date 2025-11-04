# TermTools - AI Coding Agent Instructions

## Project Overview
TermTools is a Python project manager with a **Flask-inspired Blueprint architecture** and **wxPython GUI interface**. Built by Asesh Basu, it provides modular functionality for Git operations, Python environment management, project scaffolding, cleanup, and system power management through an intuitive GUI with buttons and split-button controls.

## Core Architecture Pattern: Blueprint System

### The Blueprint Lifecycle
TermTools uses a **decorator-based registration system** similar to Flask. Understanding this pattern is critical:

1. **Blueprint Creation**: Each module creates a `Blueprint` instance (e.g., `git_operations_bp = Blueprint("git_operations", "description")`)
2. **Route Registration**: Functions decorated with `@blueprint.route(key, title, description, category, order)` become menu items
3. **Blueprint Registration**: `TermTools.register_blueprint()` in `core/app.py` registers each blueprint
4. **Initialization Hooks**: Functions decorated with `@blueprint.on_init` run when blueprint registers

**Example from `core/modules/git_operations.py`:**
```python
git_operations_bp = Blueprint("git_operations", "Git repository management")

@git_operations_bp.route("1", "Quick Commit & Push", "Add, commit, and push changes", "🔧 GIT OPERATIONS", order=1)
def git_quick_commit_push(app=None):
    GitOperations.quick_commit_push()

@git_operations_bp.on_init
def init_git_module(app):
    app.set_config("git_enabled", True)
```

### Blueprint to Menu Item Flow
- `Blueprint.route()` decorator → creates `MenuItem` → stored in `Blueprint.menu_items`
- `TermTools.register_blueprint()` → extracts menu items → adds to `TermToolsApp.menu_items` dict
- Menu system reads from `self.menu_items` and organizes by `category` field
- User selects key → `execute_menu_item(key)` calls the handler with `app` parameter if signature expects it

## Adding New Features

### To add a new module:
1. Create `core/modules/your_module.py` with `your_module_bp = Blueprint("name", "desc")`
2. Add routes using `@your_module_bp.route()` decorator
3. Export in `core/modules/__init__.py`: add to `__all__` list
4. Register in `core/app.py._register_blueprints()`: add to `blueprints` list
5. Use `@your_module_bp.on_init` for module initialization if needed

**Module Template Pattern**:
```python
# core/modules/your_module.py
from ..blueprint import Blueprint

your_module_bp = Blueprint("your_module", "Description")

class YourOperations:
    @staticmethod
    def some_operation():
        print("🔧 Starting operation...")
        # Implementation here
        print("✅ Operation complete")

@your_module_bp.route("12", "Operation Name", "Description", "🔧 YOUR CATEGORY", order=1)
def handle_operation(app=None):
    YourOperations.some_operation()
```

### Menu Key Convention
- Git operations: `"1"`
- Python env: `"2"`, `"3"`, `"4"` 
- Project templates: `"5"`
- Cleanup: `"6"`, `"7"`, `"8"`
- Folder copy: `"11"` (newer module)
- Power manager: `"9"`
- Exit: `"10"`, Help: `"0"` (reserved)

Assign new features keys following existing categories or create new number ranges.

## Project-Specific Patterns

### User Interaction Style
- **Emoji prefixes**: All user messages use emojis (✅ success, ❌ error, 🔧 operations, 💡 tips)
- **Confirmation prompts**: Destructive operations (delete, shutdown) require explicit confirmation with GUI dialogs
- **Step indicators**: Multi-step operations show progress (`Step 1/3`, `Step 2/3`)
- **Detailed output**: Always show command output in the GUI console window

### Error Handling Pattern
```python
try:
    subprocess.run(['git', 'add', '.'], capture_output=True, text=True, check=True)
    print("✅ Operation successful")
except subprocess.CalledProcessError as e:
    print(f"❌ Error: {e}")
    if e.stderr:
        print(f"   {e.stderr.strip()}")
    return
```
Always capture both stdout and stderr, display them with indentation, and use early returns after errors.

### ANSI Color System
`Colors` class in `core/app.py` provides terminal styling for console output:
- Colors are automatically stripped in GUI mode via OutputRedirector
- Used for backend operations that print to console
- GUI uses wxPython theming for visual styling

### GUI Architecture: Dual-Mode Operation
TermTools operates in **GUI mode only** (no terminal mode), with sophisticated dual-input handling:
- **GUI Dialogs**: Interactive inputs use `wx.TextEntryDialog`, `wx.MessageDialog` for user interaction
- **Output Redirection**: `OutputRedirector` in `wx_app.py` captures `print()` statements and displays them in GUI console
- **DarkTheme**: Professional color scheme defined in `core/wx_app.py` with category-specific colors
- **SplitButton**: Custom control for menu items with multiple sub-options (dropdown menus)

**Critical GUI Pattern**: Functions detect GUI mode and switch input methods:
```python
try:
    import wx
    wx_app = wx.GetApp()
    if wx_app is not None:
        return get_input_gui()  # Use wx dialogs
except ImportError:
    pass
return get_input_terminal()  # Fallback (rarely used)
```

## Windows-Specific Implementation Details

### Context Menu Integration
- Installation places TermTools in `C:\Program Files\BasusTools\TermTools\`
- `add_to_context_menu.py` creates Windows Registry entries in `HKEY_LOCAL_MACHINE\Software\Classes\Directory\Background\shell\TermTools`
- Right-click menu command: `python.exe "C:\Program Files\BasusTools\TermTools\TermTools.py" "%V"`
- Requires admin elevation (uses `ctypes.windll.shell32.IsUserAnAdmin()` check)

### Admin Elevation Pattern
```python
if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()
```
This pattern appears in `install_termtools.py` and `add_to_context_menu.py`.

### Platform Detection
Use `os.name == 'nt'` for Windows-specific paths/commands:
- Windows venv activation: `.venv/Scripts/activate.bat`
- Unix venv activation: `.venv/bin/activate`
- Windows shutdown: `shutdown /s /t <seconds>`
- Unix shutdown: `sudo shutdown -h +<minutes>`

## Key File Responsibilities

- **`TermTools.py`**: Entry point, calls `run_wx_app()` to start GUI
- **`core/app.py`**: Contains `TermTools` class (extends `TermToolsApp`), blueprint registration, ANSI color system
- **`core/wx_app.py`**: wxPython GUI application with `DarkTheme`, `SplitButton` custom controls, and output redirection
- **`core/blueprint.py`**: Defines `Blueprint`, `MenuItem`, `TermToolsApp` base class with blueprint management
- **`core/modules/__init__.py`**: Exports all blueprints in `__all__` list for easy import
- **`core/modules/*.py`**: Individual feature modules, each exports a blueprint (e.g., `git_operations_bp`)
- **`install_termtools.py`**: Downloads from GitHub, installs to Program Files, sets up context menu

## Testing & Running

### Run TermTools
```powershell
python TermTools.py
```

### One-line installation (Windows, as Administrator)
```powershell
(Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/aseshbasu-dev/termtools/main/install_termtools.py').Content | python -
```

### No test suite exists
When adding features, manually test through the GUI interface. Test both success and error paths (e.g., run Git commands in non-git directories).

## Configuration System

The `TermToolsApp` provides a simple key-value config store:
```python
app.set_config("key", value)
app.get_config("key", default=None)
```
Used for feature flags (e.g., `git_enabled`) and application metadata. Access via the `app` parameter passed to route handlers.

## Common Pitfalls

1. **Forgetting to register blueprints**: New modules must be added to `_register_blueprints()` in `core/app.py`
2. **Menu key collisions**: Check existing keys before assigning new ones
3. **Missing app parameter**: If route handler needs config access, signature must include `app=None`
4. **Cross-platform commands**: Always check `os.name` before using platform-specific commands
5. **Subprocess output handling**: Git and other commands output to stderr even on success, don't treat it as error

## Dependencies & External Tools

- **Standard library only for core**: No external dependencies required to run TermTools
- **External commands called**: `git`, `shutdown`, `python` (for venv creation)
- **Context menu requires**: Windows OS, admin privileges, `winreg` module

## Code Style Conventions

- PEP 8 compliant
- Static methods in classes for operations (e.g., `GitOperations.quick_commit_push()`)
- Docstrings on all modules, classes, and public functions
- Menu handlers are thin wrappers calling class methods
- Use `Path` from `pathlib` for file paths, not string concatenation
- Emoji first in print statements, followed by space and message
