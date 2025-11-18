"""
Blueprint System for TermTools
Built by Asesh Basu

Similar to Flask's blueprint functionality, this allows modules to be
registered with the main application in a modular, extensible way.
"""

from typing import Dict, List, Callable, Optional, Any
import inspect


class MenuItem:
    """Represents a menu item that can be registered by a blueprint"""
    
    def __init__(self, 
                 key: str, 
                 title: str, 
                 description: str, 
                 handler: Callable, 
                 category: str = "General",
                 order: int = 0):
        self.key = key
        self.title = title
        self.description = description
        self.handler = handler
        self.category = category
        self.order = order
        
    def __repr__(self):
        return f"MenuItem(key='{self.key}', title='{self.title}', category='{self.category}')"


class Blueprint:
    """
    Blueprint class for registering modular functionality
    Similar to Flask's Blueprint system
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.menu_items: List[MenuItem] = []
        self.init_handlers: List[Callable] = []
        self.cleanup_handlers: List[Callable] = []
        
    def add_menu_item(self, 
                     key: str, 
                     title: str, 
                     description: str, 
                     handler: Callable,
                     category: str = "General",
                     order: int = 0) -> None:
        """Add a menu item to this blueprint"""
        menu_item = MenuItem(key, title, description, handler, category, order)
        self.menu_items.append(menu_item)
        
    def route(self, key: str, title: str, description: str, category: str = "General", order: int = 0):
        """Decorator for registering menu handlers (similar to Flask's @app.route)"""
        def decorator(func: Callable):
            self.add_menu_item(key, title, description, func, category, order)
            return func
        return decorator
        
    def on_init(self, func: Callable):
        """Decorator for registering initialization handlers"""
        self.init_handlers.append(func)
        return func
        
    def on_cleanup(self, func: Callable):
        """Decorator for registering cleanup handlers"""
        self.cleanup_handlers.append(func)
        return func
        
    def call_init_handlers(self, app: 'TermToolsApp') -> None:
        """Call all initialization handlers"""
        for handler in self.init_handlers:
            try:
                # Check if handler expects app parameter
                sig = inspect.signature(handler)
                if len(sig.parameters) > 0:
                    handler(app)
                else:
                    handler()
            except Exception as e:
                print(f"❌ Error in {self.name} initialization: {e}")
                
    def call_cleanup_handlers(self, app: 'TermToolsApp') -> None:
        """Call all cleanup handlers"""
        for handler in self.cleanup_handlers:
            try:
                # Check if handler expects app parameter
                sig = inspect.signature(handler)
                if len(sig.parameters) > 0:
                    handler(app)
                else:
                    handler()
            except Exception as e:
                print(f"❌ Error in {self.name} cleanup: {e}")


class TermToolsApp:
    """
    Main TermTools application class
    Manages blueprints and provides the core application functionality
    """
    
    def __init__(self, name: str = "TermTools"):
        self.name = name
        self.blueprints: Dict[str, Blueprint] = {}
        self.menu_items: Dict[str, MenuItem] = {}
        self.categories: Dict[str, List[MenuItem]] = {}
        self.current_dir = None
        self.config: Dict[str, Any] = {}
        
    def register_blueprint(self, blueprint: Blueprint) -> None:
        """Register a blueprint with the application"""
        if blueprint.name in self.blueprints:
            raise ValueError(f"Blueprint '{blueprint.name}' is already registered")
            
        self.blueprints[blueprint.name] = blueprint
        
        # Register menu items from the blueprint
        for menu_item in blueprint.menu_items:
            if menu_item.key in self.menu_items:
                raise ValueError(f"Menu item key '{menu_item.key}' is already registered")
                
            self.menu_items[menu_item.key] = menu_item
            
            # Add to category
            if menu_item.category not in self.categories:
                self.categories[menu_item.category] = []
            self.categories[menu_item.category].append(menu_item)
            
        # Call blueprint initialization handlers
        blueprint.call_init_handlers(self)
            
    def get_menu_items_by_category(self) -> Dict[str, List[MenuItem]]:
        """Get menu items organized by category, sorted by order"""
        sorted_categories = {}
        for category, items in self.categories.items():
            sorted_items = sorted(items, key=lambda x: (x.order, x.title))
            sorted_categories[category] = sorted_items
        return sorted_categories
        
    def get_menu_item(self, key: str) -> Optional[MenuItem]:
        """Get a menu item by its key"""
        return self.menu_items.get(key)
        
    def execute_menu_item(self, key: str, *args, **kwargs) -> bool:
        """Execute a menu item handler"""
        menu_item = self.get_menu_item(key)
        if not menu_item:
            print(f"❌ Menu item '{key}' not found")
            return False
            
        try:
            # Check if handler expects app parameter
            sig = inspect.signature(menu_item.handler)
            if 'app' in sig.parameters:
                kwargs['app'] = self
                
            menu_item.handler(*args, **kwargs)
            return True
        except Exception as e:
            print(f"❌ Error executing '{menu_item.title}': {e}")
            return False
            
    def cleanup(self) -> None:
        """Cleanup all blueprints"""
        for blueprint in self.blueprints.values():
            blueprint.call_cleanup_handlers(self)
            
    def set_config(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        self.config[key] = value
        
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
        
    def __repr__(self):
        return f"TermToolsApp(name='{self.name}', blueprints={len(self.blueprints)}, menu_items={len(self.menu_items)})"