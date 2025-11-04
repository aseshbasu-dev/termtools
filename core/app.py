"""
Main TermTools Application
Built by Asesh Basu

This module contains the main TermTools application class that uses the blueprint system
to manage modular functionality similar to Flask's application pattern.
"""

import os
from typing import Dict, List
from .blueprint import TermToolsApp
from .modules.project_templates import project_templates_bp
from .modules.power_manager import power_manager_bp
from .modules.python_env import python_env_bp
from .modules.cleanup import cleanup_bp
from .modules.git_operations import git_operations_bp
from .modules.folder_copy import folder_copy_bp
from .modules.pomodoro import pomodoro_bp


# ANSI Color codes for terminal styling (optimized for dark terminals)
class Colors:
    """ANSI color codes for terminal output - optimized for dark backgrounds"""
    # Basic colors
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors (lighter shades for dark backgrounds)
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Custom color scheme for TermTools (dark theme optimized)
    HEADER = '\033[1m\033[97m'        # Bold White for headers
    AUTHOR = '\033[1m\033[96m'        # Bold Cyan for author
    NUMBER = '\033[1m\033[93m'        # Bold Yellow for numbers (menu keys)
    ITEM = '\033[92m'                 # Bright Green for item names
    CATEGORY = '\033[1m\033[96m'      # Bold Cyan for categories
    DESCRIPTION = '\033[37m'          # Light Gray for descriptions
    PATH = '\033[94m'                 # Blue for paths
    
    # Status colors
    SUCCESS = '\033[92m'              # Bright Green for success
    ERROR = '\033[91m'                # Bright Red for errors
    WARNING = '\033[93m'              # Bright Yellow for warnings
    INFO = '\033[94m'                 # Blue for info


class TermTools(TermToolsApp):
    """
    Main TermTools application class
    Extends TermToolsApp to provide the complete terminal-based project manager
    """
    
    def __init__(self):
        super().__init__("TermTools")
        self.current_dir = os.getcwd()
        self.version = "2.0.0"
        self.author = "Asesh Basu"
        
        # Register all modules/blueprints
        self._register_blueprints()
        
    def _register_blueprints(self):
        """Register all available blueprints"""
        # Register blueprints in order
        blueprints = [
            git_operations_bp,
            python_env_bp,
            project_templates_bp,
            cleanup_bp,
            folder_copy_bp,
            pomodoro_bp,
            power_manager_bp
        ]
        
        for blueprint in blueprints:
            try:
                self.register_blueprint(blueprint)
            except Exception as e:
                print(f"❌ Error registering {blueprint.name}: {e}")
        
    def show_help(self):
        """Display help and menu tree diagram"""
        help_text = []
        help_text.append("="*55)
        help_text.append(f"        🌳 TERMTOOLS - HELP")
        help_text.append(f"    Python Project Manager by {self.author}")
        help_text.append("="*55)
        help_text.append("\n📂 Main Menu Tree Diagram:")
        help_text.append(f"├── ❓ HELP:")
        help_text.append(f"│   └── [0]. Show help and menu tree diagram")
        help_text.append("│")
        
        # Get menu items organized by category
        categories = self.get_menu_items_by_category()
        category_list = list(categories.items())
        
        for i, (category, items) in enumerate(category_list):
            is_last_category = (i == len(category_list) - 1)
            category_prefix = "└──" if is_last_category else "├──"
            
            help_text.append(f"{category_prefix} {category}:")
            
            for j, item in enumerate(items):
                is_last_item = (j == len(items) - 1)
                
                if is_last_category:
                    item_prefix = "    └──" if is_last_item else "    ├──"
                    desc_prefix = "        └──" if item.description else ""
                else:
                    item_prefix = "│   └──" if is_last_item else "│   ├──"
                    desc_prefix = "│       └──" if item.description else ""
                
                help_text.append(f"{item_prefix} [{item.key}]. {item.title}")
                if item.description:
                    help_text.append(f"{desc_prefix} ({item.description})")
            
            if not is_last_category:
                help_text.append("│")
        
        help_text.append("│")
        help_text.append(f"└── ❌ EXIT:")
        help_text.append(f"    └── [10]. Exit")
        help_text.append("")
        help_text.append("📋 Tree Diagram Legend:")
        help_text.append("├── Branch with more items below")
        help_text.append("└── Last item in branch")
        help_text.append("│   Vertical connection line")
        help_text.append("")
        help_text.append(f"💡 Tip: Use option [0] anytime to see this help diagram!")
        help_text.append(f"🏗️  Built by {self.author} - TermTools v{self.version}")
        
        # Print help text for GUI console
        print("\n".join(help_text))