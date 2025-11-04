# TermTools - Modular Python Project Manager

A comprehensive Python project manager with **wxPython GUI** and modular blueprint architecture similar to Flask.

**Built by Asesh Basu**

## 🌟 Features

- **🎨 Modern GUI**: wxPython interface with button-based navigation and split buttons for multi-option features
- **🐍 Python Environment Management**: Virtual environment creation, requirements management
- **🔧 Git Operations**: Quick commit & push with interactive prompts
- **🧹 Clean Up Operations**: Remove cache files, build artifacts, and thumbnails
- **🏗️ Project Templates**: Generate complete Flask project scaffolds with blueprints
- **💻 System Power Management**: Schedule system shutdowns with various time options
- **📊 Real-time Output Console**: See command results as they execute
- **🔧 Modular Architecture**: Blueprint system for easy extensibility

## 🏗️ Architecture

TermTools uses a modular blueprint architecture inspired by Flask, allowing for easy extension and maintenance

## 🚀 Quick Start

### Run TermTools

Open PowerShell as Administrator and run:

Install python first with: 

```powershell
(Invoke-WebRequest -UseBasicParsing 'https://raw.githubusercontent.com/aseshbasu-dev/termtools/main/install_termtools.py').Content | python -
```

## 📋 Available Modules

### 🔧 Git Operations

- **1**: Quick Commit & Push (add, commit, and push in one command)

### Python Environment Management

- **2**: Delete and recreate .venv (with activation instructions)
- **3**: Create new requirements.txt file (choose from templates)
- **4**: Delete all .venv folders (recursive search)

### 🏗️ Project Templates

- **5**: Create Flask project scaffold (complete setup with blueprints)

### 🧹 Clean Up Operations

- **6**: Delete only **__pycache__** folders
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