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