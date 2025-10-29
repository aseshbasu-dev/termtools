# TermTools - Modular Python Project Manager

A comprehensive terminal-based application for Python project management tasks, built with a modular blueprint architecture similar to Flask.

**Built by Asesh Basu**

## 🌟 Features

- ** Python Environment Management**: Virtual environment creation, requirements management
- **🧹 Clean Up Operations**: Remove cache files, build artifacts, and thumbnails
- **🏗️ Project Templates**: Generate complete Flask project scaffolds with blueprints
- **💻 System Power Management**: Schedule system shutdowns with various time options
- **🔧 Modular Architecture**: Blueprint system for easy extensibility

## 🏗️ Architecture

TermTools uses a modular blueprint architecture inspired by Flask, allowing for easy extension and maintenance:

```
TermTools/
├── TermTools.py           # Main entry point
├── core/                  # Core application framework
│   ├── __init__.py       
│   ├── blueprint.py       # Blueprint system (like Flask)
│   ├── app.py            # Main application class
│   └── modules/          # Individual feature modules
│       ├── __init__.py
│       ├── python_env.py
│       ├── project_templates.py
│       ├── cleanup.py
│       └── power_manager.py
├── setup_context_menu.py
└── start_project.bat
```

## 🚀 Quick Start

1. **Run the application**:
   ```bash
   python TermTools.py
   ```

2. **Navigate the menu** using the numbered options (0-10)

3. **Get help** anytime by selecting option `0`

## 📋 Available Modules

###  Python Environment Management  
- **2**: Delete and recreate .venv (with activation instructions)
- **3**: Create new requirements.txt file (choose from templates)
- **4**: Delete all .venv folders (recursive search)

### 🏗️ Project Templates
- **5**: Create Flask project scaffold (complete setup with blueprints)

### 🧹 Clean Up Operations
- **6**: Delete only __pycache__ folders
- **7**: Clean up build artifacts (.pyc, .pyo, dist/, build/, etc.)
- **8**: Delete thumbnail files (with safety checks)

### 💻 System Power Management
- **9**: Schedule system shutdown (1hr, 2hr, 3hr, custom)

## 🔧 Extending TermTools

The blueprint architecture makes it easy to add new modules:

### 1. Create a New Module

```python
# core/modules/my_module.py
from ..blueprint import Blueprint

# Create blueprint
my_module_bp = Blueprint("my_module", "Description of my module")

@my_module_bp.route("key", "Menu Title", "Description", "CATEGORY", order)
def my_function(app=None):
    """Your function implementation"""
    print("Hello from my module!")

@my_module_bp.on_init
def init_my_module(app):
    """Initialize the module"""
    print("My module initialized")
    app.set_config("my_module_enabled", True)
```

### 2. Register the Blueprint

Add to `core/app.py`:

```python
from .modules.my_module import my_module_bp

# In _register_blueprints method:
blueprints = [
    # ... existing blueprints
    my_module_bp,  # Add your blueprint
]
```

### 3. Update Module Exports

Add to `core/modules/__init__.py`:

```python
from .my_module import my_module_bp

__all__ = [
    # ... existing exports
    'my_module_bp',
]
```

## 🎯 Blueprint System Features

The blueprint system provides:

- **Menu Registration**: Easy menu item creation with categories and ordering
- **Route Decorators**: Flask-like `@blueprint.route()` decorators
- **Initialization Hooks**: `@blueprint.on_init` and `@blueprint.on_cleanup`
- **Application Context**: Access to the main app instance
- **Configuration Management**: Built-in config system
- **Error Handling**: Automatic error handling and reporting

## 📖 Example: Creating a Git Module

```python
# core/modules/git_operations.py
import subprocess
from ..blueprint import Blueprint

git_bp = Blueprint("git_operations", "Git repository management")

@git_bp.route("g1", "Initialize Git repository", "Create new git repo", "🔧 GIT OPERATIONS", 1)
def init_git_repo(app=None):
    """Initialize a new Git repository"""
    try:
        subprocess.run(['git', 'init'], check=True)
        print("✅ Git repository initialized successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error initializing Git repository: {e}")

@git_bp.route("g2", "Add all files", "Stage all changes", "🔧 GIT OPERATIONS", 2)  
def git_add_all(app=None):
    """Add all files to Git staging"""
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ All files added to staging!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error adding files: {e}")

@git_bp.on_init
def init_git_module(app):
    """Initialize Git module"""
    print("🔧 Git Operations module initialized")
    app.set_config("git_enabled", True)
```

## 📚 API Reference

### Blueprint Class

```python
class Blueprint:
    def __init__(name: str, description: str = "")
    def add_menu_item(key: str, title: str, description: str, handler: Callable, category: str = "General", order: int = 0)
    def route(key: str, title: str, description: str, category: str = "General", order: int = 0)  # Decorator
    def on_init(func: Callable)  # Decorator
    def on_cleanup(func: Callable)  # Decorator
```

### TermToolsApp Class

```python
class TermToolsApp:
    def register_blueprint(blueprint: Blueprint)
    def get_menu_item(key: str) -> Optional[MenuItem]
    def execute_menu_item(key: str, *args, **kwargs) -> bool
    def set_config(key: str, value: Any)
    def get_config(key: str, default: Any = None) -> Any
```

## 🛠️ Development

### Project Structure Philosophy

- **Separation of Concerns**: Each module handles a specific domain
- **Single Responsibility**: Blueprints focus on one area of functionality  
- **Easy Testing**: Modular design enables isolated unit testing
- **Plugin Architecture**: New modules can be added without modifying core code
- **Flask-like Patterns**: Familiar patterns for Python developers

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Include docstrings for all public functions
- Add emoji prefixes to user-facing messages for better UX
- Handle errors gracefully with informative messages

## 🤝 Contributing

1. Create a new module following the blueprint pattern
2. Add comprehensive error handling
3. Include user-friendly messages with emoji prefixes
4. Test your module thoroughly
5. Update documentation

## 📄 License

This project is built by Asesh Basu as a Python project management utility.

## 🙏 Acknowledgments

- Inspired by Flask's blueprint architecture
- Built for developers who love terminal-based tools
- Designed with extensibility and maintainability in mind

---

**Built with ❤️ by Asesh Basu**