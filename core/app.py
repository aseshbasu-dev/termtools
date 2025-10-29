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


# ANSI Color codes for terminal styling
class Colors:
    """ANSI color codes for terminal output"""
    # Basic colors
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Foreground colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Custom color scheme for TermTools
    HEADER = '\033[1m\033[96m'      # Bold Cyan for headers
    AUTHOR = '\033[1m\033[95m'      # Bold Magenta for author
    NUMBER = '\033[1m\033[93m'      # Bold Yellow for numbers
    ITEM = '\033[92m'               # Green for item names
    CATEGORY = '\033[1m\033[94m'    # Bold Blue for categories
    DESCRIPTION = '\033[90m'        # Gray for descriptions
    PATH = '\033[96m'               # Cyan for paths


class TermTools(TermToolsApp):
    """
    Main TermTools application class
    Extends TermToolsApp to provide the complete terminal-based project manager
    """
    
    def __init__(self):
        super().__init__("TermTools")
        self.current_dir = os.getcwd()
        self.version = "1.0.0"
        self.author = "Asesh Basu"
        
        # Register all modules/blueprints
        self._register_blueprints()
        
    def _register_blueprints(self):
        """Register all available blueprints"""
        # Register blueprints in order
        blueprints = [
            python_env_bp,
            project_templates_bp,
            cleanup_bp,
            power_manager_bp
        ]
        
        for blueprint in blueprints:
            try:
                self.register_blueprint(blueprint)
            except Exception as e:
                print(f"❌ Error registering {blueprint.name}: {e}")
        
    def display_menu(self):
        """Display the main menu with all registered modules"""
        print("\n" + "="*60)
        print(f"{Colors.HEADER}                TERMTOOLS{Colors.RESET}")
        print(f"{Colors.HEADER}        PYTHON PROJECT MANAGER{Colors.RESET}")
        print(f"{Colors.AUTHOR}          Built by {self.author}{Colors.RESET}")
        print("="*60)
        print(f"Current directory: {Colors.PATH}{self.current_dir}{Colors.RESET}")
        print("\nPlease select an option:")
        
        # Add help option first
        print(f"\n{Colors.CATEGORY}❓ HELP:{Colors.RESET}")
        print(f"{Colors.NUMBER}[0]{Colors.RESET}  {Colors.ITEM}Show help and menu tree diagram{Colors.RESET}")
        
        # Get menu items organized by category
        categories = self.get_menu_items_by_category()
        
        # Display each category
        for category, items in categories.items():
            print(f"\n{Colors.CATEGORY}{category}:{Colors.RESET}")
            for item in items:
                print(f"{Colors.NUMBER}[{item.key}]{Colors.RESET}  {Colors.ITEM}{item.title}{Colors.RESET}  {Colors.DESCRIPTION}({item.description}){Colors.RESET}")
        
        print(f"\n{Colors.CATEGORY}❌ EXIT:{Colors.RESET}")
        print(f"{Colors.NUMBER}[10]{Colors.RESET}  {Colors.ITEM}Exit{Colors.RESET}")
        print("-"*60)
        
    def show_help(self):
        """Display help and menu tree diagram"""
        print("\n" + "="*55)
        print(f"{Colors.HEADER}        🌳 TERMTOOLS - HELP{Colors.RESET}")
        print(f"{Colors.AUTHOR}    Python Project Manager by {self.author}{Colors.RESET}")
        print("="*55)
        print("\n📂 Main Menu Tree Diagram:")
        print(f"├── {Colors.CATEGORY}❓ HELP:{Colors.RESET}")
        print(f"│   └── {Colors.NUMBER}[0]{Colors.RESET}. {Colors.ITEM}Show help and menu tree diagram{Colors.RESET}")
        print("│")
        
        # Get menu items organized by category
        categories = self.get_menu_items_by_category()
        category_list = list(categories.items())
        
        for i, (category, items) in enumerate(category_list):
            is_last_category = (i == len(category_list) - 1)
            category_prefix = "└──" if is_last_category else "├──"
            
            print(f"{category_prefix} {Colors.CATEGORY}{category}:{Colors.RESET}")
            
            for j, item in enumerate(items):
                is_last_item = (j == len(items) - 1)
                
                if is_last_category:
                    item_prefix = "    └──" if is_last_item else "    ├──"
                    desc_prefix = "        └──" if item.description else ""
                else:
                    item_prefix = "│   └──" if is_last_item else "│   ├──"
                    desc_prefix = "│       └──" if item.description else ""
                
                print(f"{item_prefix} {Colors.NUMBER}[{item.key}]{Colors.RESET}. {Colors.ITEM}{item.title}{Colors.RESET}")
                if item.description:
                    print(f"{desc_prefix} {Colors.DESCRIPTION}({item.description}){Colors.RESET}")
            
            if not is_last_category:
                print("│")
        
        print("│")
        print(f"└── {Colors.CATEGORY}❌ EXIT:{Colors.RESET}")
        print(f"    └── {Colors.NUMBER}[10]{Colors.RESET}. {Colors.ITEM}Exit{Colors.RESET}")
        print()
        print("📋 Tree Diagram Legend:")
        print("├── Branch with more items below")
        print("└── Last item in branch")
        print("│   Vertical connection line")
        print()
        print(f"💡 Tip: Use option {Colors.NUMBER}[0]{Colors.RESET} anytime to see this help diagram!")
        print(f"🏗️  {Colors.AUTHOR}Built by {self.author}{Colors.RESET} - {Colors.HEADER}TermTools v{self.version}{Colors.RESET}")
        
    def run(self):
        """Main application loop"""
        while True:
            try:
                self.display_menu()
                choice = input(f"\n{Colors.YELLOW}Enter your choice (0-10): {Colors.RESET}").strip()
                
                if choice == "0":
                    self.show_help()
                elif choice == "10":
                    print(f"\n👋 {Colors.GREEN}Thank you for using TermTools!{Colors.RESET}")
                    print(f"🏗️  {Colors.AUTHOR}Built by {self.author}{Colors.RESET} - {Colors.CYAN}Happy coding!{Colors.RESET}")
                    self.cleanup()
                    break
                else:
                    # Try to execute the menu item
                    success = self.execute_menu_item(choice)
                    if not success:
                        print(f"\n{Colors.RED}❌ Invalid choice '{choice}'. Please enter 0-10.{Colors.RESET}")
                        
                # Wait for user to press Enter before showing menu again
                if choice in self.menu_items or choice == "0":
                    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.RESET}")
                    
            except KeyboardInterrupt:
                print(f"\n\n⚠️  {Colors.YELLOW}Operation cancelled by user.{Colors.RESET}")
                print(f"👋 {Colors.GREEN}Thank you for using TermTools!{Colors.RESET}")
                print(f"🏗️  {Colors.AUTHOR}Built by {self.author}{Colors.RESET}")
                self.cleanup()
                break
            except Exception as e:
                print(f"\n{Colors.RED}❌ An unexpected error occurred: {e}{Colors.RESET}")
                input(f"{Colors.CYAN}Press Enter to continue...{Colors.RESET}")


def create_app():
    """
    Application factory function (similar to Flask pattern)
    Creates and configures the TermTools application
    """
    app = TermTools()
    
    # Set additional configuration
    app.set_config("debug", False)
    app.set_config("version", app.version)
    app.set_config("author", app.author)
    
    return app