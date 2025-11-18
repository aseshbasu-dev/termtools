"""
PyQt6 GUI Application for TermTools
Built by Asesh Basu

This module provides a modern GUI interface for TermTools using PyQt6,
replacing the terminal-based menu with buttons and split buttons.
"""

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLabel, QSplitter, QScrollArea, QFrame,
    QMessageBox, QInputDialog, QDialog, QDialogButtonBox, QSizePolicy,
    QMenu, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon, QCursor, QTextCursor, QLinearGradient
import sys
import os
import io
import subprocess
import threading
import logging
from datetime import datetime
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, List
from pathlib import Path
from .app import TermTools


def get_data_directory():
    """
    Get the appropriate data directory for writable files.
    
    In both dev and production modes, writable data files (logs, stats, state files)
    are stored in the user's AppData\Local directory to avoid permission issues.
    
    Returns:
        Path: Path to the data directory (C:\\Users\\<username>\\AppData\\Local\\BasusTools\\TermTools)
    """
    if os.name == 'nt':  # Windows
        appdata_local = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        data_dir = Path(appdata_local) / 'BasusTools' / 'TermTools'
    else:  # Unix/Linux/Mac
        data_dir = Path.home() / '.local' / 'share' / 'BasusTools' / 'TermTools'
    
    # Ensure directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_subprocess_creation_flags():
    """
    Get appropriate subprocess creation flags to prevent console windows on Windows.
    
    Returns:
        dict: Dictionary with 'creationflags' key for Windows, empty dict otherwise
    """
    if os.name == 'nt':  # Windows
        return {'creationflags': subprocess.CREATE_NO_WINDOW}
    return {}


class DarkTheme:
    """Professional dark theme color palette for TermTools GUI"""
    
    # Main backgrounds
    MAIN_BG = QColor(32, 34, 37)          # Dark charcoal main background
    PANEL_BG = QColor(40, 42, 46)         # Slightly lighter panel background
    HEADER_BG = QColor(45, 47, 51)        # Header background
    SIDEBAR_BG = QColor(36, 38, 41)       # Sidebar/button area background
    
    # Text colors
    TEXT_PRIMARY = QColor(220, 221, 222)   # Primary text (light gray)
    TEXT_SECONDARY = QColor(180, 181, 182) # Secondary text (medium gray)
    TEXT_MUTED = QColor(140, 141, 142)     # Muted text (darker gray)
    TEXT_ACCENT = QColor(88, 166, 255)     # Accent text (blue)
    TEXT_SUCCESS = QColor(46, 204, 113)    # Success text (green)
    TEXT_WARNING = QColor(241, 196, 15)    # Warning text (yellow)
    TEXT_ERROR = QColor(231, 76, 60)       # Error text (red)
    TEXT_DARK = QColor(18, 19, 21)         # Dark text for light backgrounds
    
    # Button colors
    BUTTON_BG = QColor(52, 54, 58)         # Button background
    BUTTON_BG_HOVER = QColor(62, 64, 68)   # Button hover background
    BUTTON_BG_ACTIVE = QColor(72, 74, 78)  # Button active background
    BUTTON_TEXT = QColor(220, 221, 222)    # Button text
    
    # Accent colors (professional blue scheme)
    ACCENT_PRIMARY = QColor(88, 166, 255)  # Primary accent (blue)
    ACCENT_SECONDARY = QColor(74, 144, 226) # Secondary accent (darker blue)
    ACCENT_TERTIARY = QColor(102, 187, 255) # Tertiary accent (lighter blue)
    
    # Output console (Carbon Teal theme)
    CONSOLE_BG = QColor(0, 77, 64)         # Teal console background
    CONSOLE_BG_GRADIENT_START = QColor(0, 105, 92)  # Lighter teal for gradient
    CONSOLE_BG_GRADIENT_END = QColor(0, 60, 48)     # Darker teal for gradient
    CONSOLE_TEXT = QColor(224, 242, 241)   # Light teal-tinted text
    
    # Borders and separators
    BORDER = QColor(60, 62, 66)            # Border color
    SEPARATOR = QColor(70, 72, 76)         # Separator lines
    
    # Category colors (muted professional palette)
    CATEGORY_GIT = QColor(255, 123, 114)   # Git operations (coral)
    CATEGORY_PYTHON = QColor(52, 168, 83)  # Python env (green)
    CATEGORY_PROJECT = QColor(255, 193, 7) # Project templates (amber)
    CATEGORY_CLEANUP = QColor(156, 39, 176) # Cleanup (purple)
    CATEGORY_POWER = QColor(244, 67, 54)   # Power management (red)
    CATEGORY_HELP = QColor(96, 125, 139)   # Help (blue-gray)


class SplitButton(QWidget):
    """
    Custom split button control with main action and dropdown menu.
    Used for menu items with multiple sub-options.
    """
    
    def __init__(self, label, main_handler, sub_items=None, parent=None):
        """
        Initialize split button
        
        Args:
            label: Button label text
            main_handler: Callback for main button click
            sub_items: List of tuples (label, handler) for dropdown items
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.main_handler = main_handler
        self.sub_items = sub_items or []
        
        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, DarkTheme.SIDEBAR_BG)
        self.setPalette(palette)
        
        # Create horizontal layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Main button (70% width)
        self.main_button = QPushButton(label)
        self.main_button.setMinimumHeight(35)
        self.main_button.clicked.connect(self.on_main_click)
        self._style_button(self.main_button)
        layout.addWidget(self.main_button, 7)
        
        if self.sub_items:
            # Dropdown arrow button (30% width)
            self.dropdown_button = QPushButton("▼")
            self.dropdown_button.setFixedWidth(30)
            self.dropdown_button.setMinimumHeight(35)
            self.dropdown_button.clicked.connect(self.on_dropdown_click)
            self._style_button(self.dropdown_button, DarkTheme.BUTTON_BG_HOVER)
            layout.addWidget(self.dropdown_button, 0)
        
    def _style_button(self, button, bg_color=None):
        """Apply dark theme styling to button"""
        if bg_color is None:
            bg_color = DarkTheme.BUTTON_BG
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color.name()};
                color: {DarkTheme.BUTTON_TEXT.name()};
                border: none;
                padding: 5px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {DarkTheme.BUTTON_BG_HOVER.name()};
            }}
            QPushButton:pressed {{
                background-color: {DarkTheme.BUTTON_BG_ACTIVE.name()};
            }}
        """)
        
    def on_main_click(self):
        """Handle main button click"""
        if self.main_handler:
            self.main_handler()
    
    def on_dropdown_click(self):
        """Show dropdown menu with sub-options"""
        if not self.sub_items:
            return
        
        # Create dropdown menu
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {DarkTheme.PANEL_BG.name()};
                color: {DarkTheme.TEXT_PRIMARY.name()};
                border: 1px solid {DarkTheme.BORDER.name()};
            }}
            QMenu::item:selected {{
                background-color: {DarkTheme.ACCENT_TERTIARY.name()};
                color: {DarkTheme.TEXT_DARK.name()};
            }}
        """)
        
        for label, handler in self.sub_items:
            action = menu.addAction(label)
            action.triggered.connect(handler)
        
        # Show menu at button position
        menu.exec(self.dropdown_button.mapToGlobal(self.dropdown_button.rect().bottomLeft()))


class OutputRedirector:
    """Redirects stdout/stderr to both QTextEdit and log file"""
    
    def __init__(self, text_edit, log_file_path=None):
        self.text_edit = text_edit
        self.log_file_path = log_file_path
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def write(self, text):
        """Write text to both text control and log file"""
        # Write to GUI (thread-safe)
        if self.text_edit:
            # Strip ANSI color codes
            import re
            clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
            
            # Use Qt's thread-safe mechanism
            QApplication.instance().postEvent(
                self.text_edit,
                AppendTextEvent(clean_text)
            )
        
        # Write to log file
        if self.log_file_path:
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    # Strip ANSI color codes for file
                    import re
                    clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
                    f.write(clean_text)
                    f.flush()
            except Exception:
                pass  # Silently fail if logging fails
            
    def flush(self):
        """Flush the buffer"""
        pass


from PyQt6.QtCore import QEvent

class AppendTextEvent(QEvent):
    """Custom event for thread-safe text appending"""
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, text):
        super().__init__(self.EVENT_TYPE)
        self.text = text


class OutputTextEdit(QTextEdit):
    """Custom QTextEdit that handles append text events"""
    
    def event(self, event):
        if isinstance(event, AppendTextEvent):
            self.moveCursor(QTextCursor.MoveOperation.End)
            self.insertPlainText(event.text)
            self.moveCursor(QTextCursor.MoveOperation.End)
            return True
        return super().event(event)


class TermToolsMainWindow(QMainWindow):
    """Main application window for TermTools GUI"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("TermTools - Python Project Manager v2.10 GUI")
        self.resize(900, 600)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Initialize TermTools backend
        self.app = TermTools()
        self.current_dir = os.getcwd()
        
        # Create UI
        self._create_ui()
        
        # Setup logging
        self.log_file_path = self._setup_logging()
        
        # Setup output redirection
        self.stdout_redirector = OutputRedirector(self.output_text, self.log_file_path)
        self.stderr_redirector = OutputRedirector(self.output_text, self.log_file_path)
        
        # Redirect sys.stdout and sys.stderr
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stderr_redirector
        
        # Status bar
        self.statusBar().showMessage(f"Ready - Current directory: {self.current_dir}")
        
        # Setup timer for periodic updates
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.on_status_timer)
        self.status_timer.start(1000)  # Update every second
        
    def apply_dark_theme(self):
        """Apply dark theme to the entire application"""
        # Set modern default font to avoid DirectWrite warnings
        app = QApplication.instance()
        if os.name == 'nt':  # Windows
            app.setFont(QFont("Segoe UI", 9))
        else:  # Unix/Linux/Mac
            app.setFont(QFont("Sans Serif", 9))
        
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, DarkTheme.MAIN_BG)
        palette.setColor(QPalette.ColorRole.WindowText, DarkTheme.TEXT_PRIMARY)
        palette.setColor(QPalette.ColorRole.Base, DarkTheme.CONSOLE_BG)
        palette.setColor(QPalette.ColorRole.AlternateBase, DarkTheme.PANEL_BG)
        palette.setColor(QPalette.ColorRole.Text, DarkTheme.TEXT_PRIMARY)
        palette.setColor(QPalette.ColorRole.Button, DarkTheme.BUTTON_BG)
        palette.setColor(QPalette.ColorRole.ButtonText, DarkTheme.BUTTON_TEXT)
        palette.setColor(QPalette.ColorRole.Highlight, DarkTheme.ACCENT_PRIMARY)
        palette.setColor(QPalette.ColorRole.HighlightedText, DarkTheme.TEXT_DARK)
        
        app.setPalette(palette)
        
    def _create_ui(self):
        """Create the user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Header section
        header_widget = self._create_header()
        main_layout.addWidget(header_widget)
        
        # Create splitter for buttons and output
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Menu buttons
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        left_widget = QWidget()
        left_widget.setAutoFillBackground(True)
        palette = left_widget.palette()
        palette.setColor(QPalette.ColorRole.Window, DarkTheme.SIDEBAR_BG)
        left_widget.setPalette(palette)
        
        # Use vertical layout to contain grid layouts
        self.button_container_layout = QVBoxLayout(left_widget)
        self.button_container_layout.setSpacing(5)
        
        # Create menu buttons in grid
        self._create_menu_buttons()
        
        self.button_container_layout.addStretch()
        left_scroll.setWidget(left_widget)
        
        # Right panel - Output console
        right_widget = QWidget()
        right_widget.setAutoFillBackground(True)
        palette = right_widget.palette()
        palette.setColor(QPalette.ColorRole.Window, DarkTheme.PANEL_BG)
        right_widget.setPalette(palette)
        
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(3, 3, 3, 3)
        
        # Output label
        output_label = QLabel("Output Console:")
        output_label.setFont(QFont("", 9, QFont.Weight.Bold))
        output_label.setStyleSheet(f"color: {DarkTheme.TEXT_PRIMARY.name()};")
        right_layout.addWidget(output_label)
        
        # Output text control with teal gradient
        self.output_text = OutputTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 9))
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {DarkTheme.CONSOLE_BG_GRADIENT_START.name()},
                    stop:1 {DarkTheme.CONSOLE_BG_GRADIENT_END.name()});
                color: {DarkTheme.CONSOLE_TEXT.name()};
                border: 1px solid {DarkTheme.BORDER.name()};
            }}
        """)
        right_layout.addWidget(self.output_text)
        
        # Clear button
        clear_button = QPushButton("Clear Output")
        clear_button.clicked.connect(self.on_clear_output)
        self._style_button(clear_button)
        right_layout.addWidget(clear_button, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Add panels to splitter
        splitter.addWidget(left_scroll)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter, 1)
        
    def _create_header(self):
        """Create the header section with title and info"""
        header_widget = QWidget()
        header_widget.setAutoFillBackground(True)
        palette = header_widget.palette()
        palette.setColor(QPalette.ColorRole.Window, DarkTheme.HEADER_BG)
        header_widget.setPalette(palette)
        
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(1)
        header_layout.setContentsMargins(3, 3, 3, 3)
        
        # Title
        title = QLabel("🔧 TERMTOOLS")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {DarkTheme.TEXT_PRIMARY.name()};")
        header_layout.addWidget(title)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {DarkTheme.SEPARATOR.name()};")
        header_layout.addWidget(separator)
        
        # Status section
        status_widget = QWidget()
        status_widget.setAutoFillBackground(True)
        palette = status_widget.palette()
        palette.setColor(QPalette.ColorRole.Window, DarkTheme.PANEL_BG)
        status_widget.setPalette(palette)
        
        status_layout = QVBoxLayout(status_widget)
        status_layout.setSpacing(1)
        status_layout.setContentsMargins(2, 2, 2, 2)
        
        # Status title with date/time
        from datetime import datetime
        current_datetime = datetime.now().strftime("%b %d, %Y %I:%M %p")
        self.status_title_label = QLabel(f"📁 {self.current_dir}")
        self.status_title_label.setFont(QFont("", 8))
        self.status_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_title_label.setStyleSheet(f"color: {DarkTheme.TEXT_PRIMARY.name()};")
        status_layout.addWidget(self.status_title_label)
        
        # Git repository status
        self.git_repo_label = QLabel("")
        self.git_repo_label.setFont(QFont("Consolas", 8))
        self.git_repo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.git_repo_label.setStyleSheet(f"color: {DarkTheme.CATEGORY_GIT.name()};")
        self.git_repo_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.git_repo_label.mousePressEvent = self._on_git_repo_click
        status_layout.addWidget(self.git_repo_label)
        self.git_remote_url = None
        
        # Git commit status
        self.git_commit_label = QLabel("")
        self.git_commit_label.setFont(QFont("Consolas", 8))
        self.git_commit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.git_commit_label.setStyleSheet(f"color: {DarkTheme.TEXT_SECONDARY.name()};")
        status_layout.addWidget(self.git_commit_label)
        
        # Shutdown timer status
        self.shutdown_status_label = QLabel("⚡ Not Scheduled")
        self.shutdown_status_label.setFont(QFont("", 8, QFont.Weight.Bold))
        self.shutdown_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.shutdown_status_label.setStyleSheet(f"color: {DarkTheme.TEXT_SUCCESS.name()};")
        status_layout.addWidget(self.shutdown_status_label)
        
        status_widget.setLayout(status_layout)
        header_layout.addWidget(status_widget)
        
        # Bottom separator
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet(f"background-color: {DarkTheme.SEPARATOR.name()};")
        header_layout.addWidget(separator2)
        
        # Update status displays
        self._update_shutdown_status()
        self._update_git_status()
        
        return header_widget
        
    def _create_menu_buttons(self):
        """Create buttons for all menu items organized by category in grid layout"""
        categories = self.app.get_menu_items_by_category()
        
        # Define category colors and icons
        category_info = {
            "🔧 GIT OPERATIONS": {"color": DarkTheme.CATEGORY_GIT, "icon": "🔧"},
            "🐍 PYTHON ENVIRONMENT": {"color": DarkTheme.CATEGORY_PYTHON, "icon": "🐍"},
            "📁 PROJECT TEMPLATES": {"color": DarkTheme.CATEGORY_PROJECT, "icon": "📁"},
            "🧹 CLEANUP": {"color": DarkTheme.CATEGORY_CLEANUP, "icon": "🧹"},
            "🎯 PRODUCTIVITY": {"color": QColor(255, 179, 71), "icon": "🎯"},
            "⚡ POWER MANAGEMENT": {"color": DarkTheme.CATEGORY_POWER, "icon": "⚡"},
        }
        
        # Icon mapping for menu items
        item_icons = {
            "quick commit": "📤",
            "git status": "📊",
            "undo last commit": "↩️",
            "create new .venv": "🆕",
            "activate .venv": "✅",
            "create new requirements.txt": "📝",
            "install from requirements.txt": "⬇️",
            "project template": "📋",
            "cleanup .pyc": "🗑️",
            "cleanup __pycache__": "🗑️",
            "cleanup all": "🧹",
            "copy folder": "📂",
            "pomodoro": "⏱️",
            "shutdown": "🔌",
        }
        
        for category, items in categories.items():
            # Category header
            category_label = QLabel(category)
            category_label.setFont(QFont("", 9, QFont.Weight.Bold))
            cat_info = category_info.get(category, {"color": DarkTheme.TEXT_ACCENT})
            category_color = cat_info["color"]
            category_label.setStyleSheet(f"color: {category_color.name()}; padding: 5px 3px 2px 3px;")
            self.button_container_layout.addWidget(category_label)
            
            # Create grid layout for this category (2 columns)
            grid_layout = QGridLayout()
            grid_layout.setSpacing(4)
            grid_layout.setContentsMargins(3, 0, 3, 0)
            
            # Add items in this category to grid
            row = 0
            col = 0
            for item in items:
                # Determine if this item needs a split button
                sub_options = self._get_sub_options(item)
                
                # Get icon for this item
                icon = self._get_item_icon(item.title, item_icons)
                
                if sub_options:
                    # Create split button widget
                    if "shutdown" in item.title.lower():
                        main_handler = lambda: self.execute_power_custom()
                    else:
                        main_handler = lambda h=item.handler: self.execute_handler(h)
                    
                    split_btn = self._create_grid_split_button(icon, item.title, item.description, main_handler, sub_options)
                    grid_layout.addWidget(split_btn, row, col)
                else:
                    # Create grid button with icon and label
                    button = self._create_grid_button(icon, item.title, item.description, item.handler)
                    grid_layout.addWidget(button, row, col)
                
                # Update grid position
                col += 1
                if col >= 2:  # 2 columns
                    col = 0
                    row += 1
            
            self.button_container_layout.addLayout(grid_layout)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {DarkTheme.SEPARATOR.name()}; margin: 5px 0;")
        self.button_container_layout.addWidget(separator)
        
        # Bottom action buttons in grid
        bottom_grid = QGridLayout()
        bottom_grid.setSpacing(4)
        bottom_grid.setContentsMargins(3, 0, 3, 0)
        
        # Settings button
        settings_button = self._create_grid_button("⚙️", "Settings", "Application settings", None)
        settings_button.clicked.connect(self.on_show_settings)
        bottom_grid.addWidget(settings_button, 0, 0)
        
        # Help button
        help_button = self._create_grid_button("❓", "Help", "Show help and documentation", None)
        help_button.clicked.connect(self.on_show_help)
        bottom_grid.addWidget(help_button, 0, 1)
        
        # Exit button (full width)
        exit_button = self._create_grid_button("❌", "Exit", "Close TermTools", None)
        exit_button.clicked.connect(self.on_exit)
        self._style_grid_button(exit_button, text_color=DarkTheme.TEXT_ERROR)
        bottom_grid.addWidget(exit_button, 1, 0, 1, 2)  # Span 2 columns
        
        self.button_container_layout.addLayout(bottom_grid)
    
    def _get_item_icon(self, title, icon_map):
        """Get icon for a menu item based on title"""
        title_lower = title.lower()
        for key, icon in icon_map.items():
            if key in title_lower:
                return icon
        return "📌"  # Default icon
    
    def _create_grid_button(self, icon, label, tooltip, handler):
        """Create a grid-style button with icon and label"""
        button = QPushButton()
        button.setMinimumSize(QSize(130, 60))
        button.setMaximumHeight(70)
        button.setToolTip(tooltip)
        
        # Create layout for icon and label
        layout = QVBoxLayout(button)
        layout.setSpacing(3)
        layout.setContentsMargins(3, 5, 3, 5)
        
        # Icon label
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("", 18))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Text label
        text_label = QLabel(label)
        text_label.setFont(QFont("", 7))
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)
        layout.addWidget(text_label)
        
        # Connect handler
        if handler:
            button.clicked.connect(lambda checked, h=handler: self.execute_handler(h))
        
        self._style_grid_button(button)
        return button
    
    def _create_grid_split_button(self, icon, label, tooltip, main_handler, sub_items):
        """Create a grid-style split button with icon and label"""
        container = QWidget()
        container.setMinimumSize(QSize(130, 60))
        container.setMaximumHeight(70)
        
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(1)
        
        # Main button (80% width)
        main_button = QPushButton()
        main_button.setMinimumHeight(60)
        main_button.setToolTip(tooltip)
        main_button.clicked.connect(main_handler)
        
        # Layout for main button
        btn_layout = QVBoxLayout(main_button)
        btn_layout.setSpacing(3)
        btn_layout.setContentsMargins(3, 5, 3, 5)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("", 18))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(icon_label)
        
        text_label = QLabel(label)
        text_label.setFont(QFont("", 7))
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)
        btn_layout.addWidget(text_label)
        
        self._style_grid_button(main_button)
        main_layout.addWidget(main_button, 4)
        
        # Dropdown button (20% width)
        dropdown_button = QPushButton("▼")
        dropdown_button.setMinimumHeight(60)
        dropdown_button.setMaximumWidth(25)
        dropdown_button.setToolTip("More options")
        self._style_grid_button(dropdown_button, bg_color=DarkTheme.BUTTON_BG_HOVER)
        
        # Connect dropdown menu
        dropdown_button.clicked.connect(lambda: self._show_split_menu(dropdown_button, sub_items))
        main_layout.addWidget(dropdown_button, 1)
        
        return container
    
    def _show_split_menu(self, button, sub_items):
        """Show dropdown menu for split button"""
        menu = QMenu(button)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {DarkTheme.PANEL_BG.name()};
                color: {DarkTheme.TEXT_PRIMARY.name()};
                border: 1px solid {DarkTheme.BORDER.name()};
            }}
            QMenu::item:selected {{
                background-color: {DarkTheme.ACCENT_TERTIARY.name()};
                color: {DarkTheme.TEXT_DARK.name()};
            }}
        """)
        
        for label, handler in sub_items:
            action = menu.addAction(label)
            action.triggered.connect(handler)
        
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
    
    def _style_grid_button(self, button, bg_color=None, text_color=None):
        """Apply grid-style button theme"""
        bg = bg_color or DarkTheme.BUTTON_BG
        fg = text_color or DarkTheme.BUTTON_TEXT
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg.name()};
                color: {fg.name()};
                border: 1px solid {DarkTheme.BORDER.name()};
                border-radius: 6px;
                padding: 3px;
            }}
            QPushButton:hover {{
                background-color: {DarkTheme.ACCENT_TERTIARY.name()};
                color: {DarkTheme.TEXT_DARK.name()};
                border: 1px solid {DarkTheme.ACCENT_PRIMARY.name()};
            }}
            QPushButton:pressed {{
                background-color: {DarkTheme.BUTTON_BG_ACTIVE.name()};
            }}
            QLabel {{
                background: transparent;
                color: {fg.name()};
            }}
        """)
    
    def _style_button(self, button, bg_color=None, text_color=None, hover_bg=None, hover_text=None):
        """Apply dark theme styling to button"""
        bg = bg_color or DarkTheme.BUTTON_BG
        fg = text_color or DarkTheme.BUTTON_TEXT
        hover_bg_color = hover_bg or DarkTheme.ACCENT_TERTIARY
        hover_fg_color = hover_text or DarkTheme.TEXT_DARK
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg.name()};
                color: {fg.name()};
                border: none;
                padding: 8px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: {hover_bg_color.name()};
                color: {hover_fg_color.name()};
            }}
            QPushButton:pressed {{
                background-color: {DarkTheme.BUTTON_BG_ACTIVE.name()};
            }}
        """)
    
    def _get_sub_options(self, menu_item):
        """Determine if a menu item has sub-options and return them"""
        # Power manager has sub-options
        if "shutdown" in menu_item.title.lower():
            return [
                ("Shutdown in 1 hour", lambda: self.execute_power_option(60, "1 hour")),
                ("Shutdown in 2 hours", lambda: self.execute_power_option(120, "2 hours")),
                ("Shutdown in 3 hours", lambda: self.execute_power_option(180, "3 hours")),
                ("Cancel shutdown", lambda: self.execute_power_cancel()),
            ]
        
        # Python environment create has options
        if "create new .venv" in menu_item.title.lower():
            return [
                ("Create .venv w/ requirements file", lambda: self.execute_venv_with_requirements()),
                ("Create .venv w/ requirements, .gitignore, readme.md files", lambda: self.execute_venv_with_all_files()),
            ]
        
        # Requirements file has additional options
        if "create new requirements.txt file" in menu_item.title.lower():
            return [
                ("Create .gitignore file", lambda: self.execute_create_gitignore()),
                ("Create README.md file", lambda: self.execute_create_readme()),
            ]
        
        return None
    
    def execute_handler(self, handler):
        """Execute a menu item handler in a separate thread"""
        logger = logging.getLogger(__name__)
        logger.info(f"Executing handler: {handler.__name__ if hasattr(handler, '__name__') else str(handler)}")
        
        # Special handling for folder copy - get user input BEFORE starting thread
        if hasattr(handler, '__name__') and 'copy_folder' in handler.__name__:
            logger.debug("Detected folder copy handler - getting user input in main thread")
            self.execute_folder_copy_handler(handler)
            return
        
        # Special handling for start_project - get user input BEFORE starting thread
        if hasattr(handler, '__name__') and 'start_project' in handler.__name__:
            logger.debug("Detected start_project handler - getting user input in main thread")
            self.execute_start_project_handler(handler)
            return
        
        # Special handling for handlers that need user input in main thread
        if hasattr(handler, '__name__'):
            handler_name = handler.__name__
            
            # Git operations that need input
            if handler_name in ['git_initialize_repo', 'git_quick_commit_push', 'git_switch_repo', 'git_untrack_commit_push']:
                logger.debug(f"Detected {handler_name} - getting user input in main thread")
                self.execute_git_handler_with_input(handler)
                return
            
            # Python environment operations that need input
            if handler_name in ['create_new_venv', 'create_requirements_file', 'delete_all_venvs']:
                logger.debug(f"Detected {handler_name} - getting user input in main thread")
                self.execute_python_env_handler_with_input(handler)
                return
            
            # Project templates that need input
            if handler_name == 'create_flask_project_scaffold':
                logger.debug("Detected Flask scaffold - getting user input in main thread")
                self.execute_flask_scaffold_handler(handler)
                return
        
        def run():
            with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                try:
                    import inspect
                    sig = inspect.signature(handler)
                    logger.debug(f"Handler signature: {sig}")
                    if len(sig.parameters) > 0:
                        handler(self.app)
                    else:
                        handler()
                    logger.info("Handler completed successfully")
                    print("\n✅ Operation completed.\n")
                except Exception as e:
                    logger.error(f"Error in handler: {e}", exc_info=True)
                    print(f"\n❌ Error: {e}\n")
                    import traceback
                    traceback.print_exc()
        
        thread = threading.Thread(target=run, daemon=True, name=f"Handler-{handler.__name__ if hasattr(handler, '__name__') else 'Unknown'}")
        logger.debug(f"Starting thread: {thread.name}")
        thread.start()
    
    def execute_folder_copy_handler(self, handler):
        """Execute folder copy with user input from main thread"""
        logger = logging.getLogger(__name__)
        logger.info("Executing folder copy handler with main-thread input")
        
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        from pathlib import Path
        
        try:
            # Get user input in main thread
            current_dir = Path(os.getcwd())
            folder_name = current_dir.name
            
            logger.debug(f"Showing input dialog for folder: {folder_name}")
            text, ok = QInputDialog.getText(
                self,
                "Folder Copy - Enter Modification Text",
                f"Enter modification text for the copied folder:\n\n"
                f"The folder will be named: {folder_name}_copy_<your_text>\n"
                f"Example: {folder_name}_copy_backup",
                text="backup"
            )
            
            if not ok:
                logger.info("User cancelled folder copy dialog")
                print("❌ Operation cancelled by user")
                return
            
            if not text.strip():
                logger.warning("User provided empty modification text")
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Modification text cannot be empty!"
                )
                return
            
            modification_text = text.strip()
            logger.info(f"User entered modification text: '{modification_text}'")
            
            # Now run the actual operation in worker thread with the user input
            def run():
                with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                    try:
                        from .modules.folder_copy import FolderCopyOperations
                        import inspect
                        
                        # Call the handler directly with pre-captured user input
                        # We'll modify folder_copy.py to accept modification_text parameter
                        logger.debug("Starting folder copy operation in worker thread")
                        
                        # For now, temporarily set a global or pass through app config
                        self.app.set_config('_folder_copy_modification_text', modification_text)
                        
                        sig = inspect.signature(handler)
                        if len(sig.parameters) > 0:
                            handler(self.app)
                        else:
                            handler()
                        
                        logger.info("Folder copy completed successfully")
                        print("\n✅ Operation completed.\n")
                    except Exception as e:
                        logger.error(f"Error in folder copy: {e}", exc_info=True)
                        print(f"\n❌ Error: {e}\n")
                        import traceback
                        traceback.print_exc()
                    finally:
                        # Clean up temp config
                        self.app.set_config('_folder_copy_modification_text', None)
            
            thread = threading.Thread(target=run, daemon=True, name="FolderCopy-Worker")
            logger.debug(f"Starting folder copy thread: {thread.name}")
            thread.start()
            
        except Exception as e:
            logger.error(f"Error in execute_folder_copy_handler: {e}", exc_info=True)
            print(f"❌ Error setting up folder copy: {e}")
    
    def execute_git_handler_with_input(self, handler):
        """Execute git handler with user input from main thread"""
        logger = logging.getLogger(__name__)
        logger.info(f"Executing git handler with main-thread input: {handler.__name__}")
        
        from PyQt6.QtWidgets import QMessageBox, QInputDialog
        
        try:
            handler_name = handler.__name__
            user_input = {}
            
            # Get specific input based on handler
            if handler_name == 'git_initialize_repo':
                # Get remote URL
                text, ok = QInputDialog.getText(
                    self,
                    "Initialize Git Repository",
                    "Enter the remote repository URL:\n(e.g., https://github.com/username/repo.git)",
                    text=""
                )
                if not ok:
                    print("❌ Operation cancelled by user")
                    return
                user_input['remote_url'] = text.strip() if text.strip() else None
                
            elif handler_name == 'git_quick_commit_push':
                # Get commit message
                text, ok = QInputDialog.getText(
                    self,
                    "Git Commit Message",
                    "Enter commit message:",
                    text="bug fixes"
                )
                if not ok:
                    print("❌ Operation cancelled by user")
                    return
                user_input['commit_message'] = text.strip() if text.strip() else "bug fixes"
                
            elif handler_name == 'git_switch_repo':
                # Get new remote URL
                text, ok = QInputDialog.getText(
                    self,
                    "Switch Git Repository",
                    "Enter new remote repository URL:",
                    text=""
                )
                if not ok:
                    print("❌ Operation cancelled by user")
                    return
                user_input['new_remote_url'] = text.strip()
                
            elif handler_name == 'git_untrack_commit_push':
                # Get path to untrack
                text, ok = QInputDialog.getText(
                    self,
                    "Untrack Files/Folders",
                    "Enter path to untrack (file or folder):",
                    text=""
                )
                if not ok:
                    print("❌ Operation cancelled by user")
                    return
                user_input['untrack_path'] = text.strip()
                
                # Get commit message
                text, ok = QInputDialog.getText(
                    self,
                    "Git Commit Message",
                    "Enter commit message:",
                    text="Removed tracked files"
                )
                if not ok:
                    print("❌ Operation cancelled by user")
                    return
                user_input['commit_message'] = text.strip() if text.strip() else "Removed tracked files"
            
            # Store input in app config for worker thread to access
            self.app.set_config('_git_user_input', user_input)
            
            # Run handler in worker thread
            def run():
                with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                    try:
                        import inspect
                        sig = inspect.signature(handler)
                        if len(sig.parameters) > 0:
                            handler(self.app)
                        else:
                            handler()
                        logger.info("Git handler completed successfully")
                        print("\n✅ Operation completed.\n")
                    except Exception as e:
                        logger.error(f"Error in git handler: {e}", exc_info=True)
                        print(f"\n❌ Error: {e}\n")
                        import traceback
                        traceback.print_exc()
                    finally:
                        self.app.set_config('_git_user_input', None)
            
            thread = threading.Thread(target=run, daemon=True, name=f"Git-{handler_name}")
            thread.start()
            
        except Exception as e:
            logger.error(f"Error in execute_git_handler_with_input: {e}", exc_info=True)
            print(f"❌ Error setting up git operation: {e}")
    
    def execute_python_env_handler_with_input(self, handler):
        """Execute python environment handler with user input from main thread"""
        logger = logging.getLogger(__name__)
        logger.info(f"Executing python env handler with main-thread input: {handler.__name__}")
        
        from PyQt6.QtWidgets import QMessageBox, QInputDialog
        from pathlib import Path
        
        try:
            handler_name = handler.__name__
            user_input = {}
            
            if handler_name == 'create_new_venv':
                venv_path = Path(".venv")
                if venv_path.exists():
                    reply = QMessageBox.question(
                        self,
                        "Virtual Environment Exists",
                        f"A virtual environment already exists at:\n{venv_path.absolute()}\n\n"
                        f"Do you want to delete it and create a new one?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    user_input['overwrite'] = (reply == QMessageBox.StandardButton.Yes)
                    
                    if not user_input['overwrite']:
                        print("❌ Operation cancelled by user")
                        return
                
                # Ask about .gitignore
                reply = QMessageBox.question(
                    self,
                    "Create .gitignore",
                    "Do you want to create a .gitignore file?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                user_input['create_gitignore'] = (reply == QMessageBox.StandardButton.Yes)
                
                # Ask about requirements.txt
                reply = QMessageBox.question(
                    self,
                    "Create requirements.txt",
                    "Do you want to create a requirements.txt file?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                user_input['create_requirements'] = (reply == QMessageBox.StandardButton.Yes)
                
            elif handler_name == 'create_requirements_file':
                items = ["Empty", "Flask", "Django", "FastAPI", "Data Science", "Web Scraping"]
                item, ok = QInputDialog.getItem(
                    self,
                    "Create requirements.txt",
                    "Choose a template:",
                    items,
                    0,
                    False
                )
                if not ok:
                    print("❌ Operation cancelled by user")
                    return
                user_input['template'] = item
                
                # Check if file exists
                if Path("requirements.txt").exists():
                    reply = QMessageBox.question(
                        self,
                        "File Exists",
                        "requirements.txt already exists. Overwrite?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        print("❌ Operation cancelled by user")
                        return
                    user_input['overwrite'] = True
                
            elif handler_name == 'delete_all_venvs':
                reply = QMessageBox.question(
                    self,
                    "Delete All Virtual Environments",
                    "⚠️  This will recursively search and delete all .venv folders!\n\n"
                    "Are you sure you want to continue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    print("❌ Operation cancelled by user")
                    return
                user_input['confirmed'] = True
            
            # Store input in app config
            self.app.set_config('_python_env_user_input', user_input)
            
            # Run handler in worker thread
            def run():
                with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                    try:
                        import inspect
                        sig = inspect.signature(handler)
                        if len(sig.parameters) > 0:
                            handler(self.app)
                        else:
                            handler()
                        logger.info("Python env handler completed successfully")
                        print("\n✅ Operation completed.\n")
                    except Exception as e:
                        logger.error(f"Error in python env handler: {e}", exc_info=True)
                        print(f"\n❌ Error: {e}\n")
                        import traceback
                        traceback.print_exc()
                    finally:
                        self.app.set_config('_python_env_user_input', None)
            
            thread = threading.Thread(target=run, daemon=True, name=f"PythonEnv-{handler_name}")
            thread.start()
            
        except Exception as e:
            logger.error(f"Error in execute_python_env_handler_with_input: {e}", exc_info=True)
            print(f"❌ Error setting up python environment operation: {e}")
    
    def execute_flask_scaffold_handler(self, handler):
        """Execute Flask scaffold with user input from main thread"""
        logger = logging.getLogger(__name__)
        logger.info("Executing Flask scaffold handler with main-thread input")
        
        from PyQt6.QtWidgets import QMessageBox, QInputDialog
        
        try:
            # Get project name
            text, ok = QInputDialog.getText(
                self,
                "Flask Project Scaffold",
                "Enter project name:",
                text="flask_project"
            )
            
            if not ok:
                print("❌ Operation cancelled by user")
                return
            
            project_name = text.strip() if text.strip() else "flask_project"
            
            # Validate project name
            if not project_name.replace('_', '').replace('-', '').isalnum():
                QMessageBox.critical(
                    self,
                    "Invalid Project Name",
                    "Project name should contain only letters, numbers, underscores, and hyphens."
                )
                return
            
            # Store input
            self.app.set_config('_flask_scaffold_project_name', project_name)
            
            # Run handler in worker thread
            def run():
                with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                    try:
                        import inspect
                        sig = inspect.signature(handler)
                        if len(sig.parameters) > 0:
                            handler(self.app)
                        else:
                            handler()
                        logger.info("Flask scaffold completed successfully")
                        print("\n✅ Operation completed.\n")
                    except Exception as e:
                        logger.error(f"Error in Flask scaffold: {e}", exc_info=True)
                        print(f"\n❌ Error: {e}\n")
                        import traceback
                        traceback.print_exc()
                    finally:
                        self.app.set_config('_flask_scaffold_project_name', None)
            
            thread = threading.Thread(target=run, daemon=True, name="FlaskScaffold-Worker")
            thread.start()
            
        except Exception as e:
            logger.error(f"Error in execute_flask_scaffold_handler: {e}", exc_info=True)
            print(f"❌ Error setting up Flask scaffold: {e}")
    
    def execute_start_project_handler(self, handler):
        """Execute start_project with user input from main thread"""
        logger = logging.getLogger(__name__)
        logger.info("Executing start_project handler with main-thread input")
        
        from PyQt6.QtWidgets import QMessageBox
        from pathlib import Path
        
        try:
            venv_path = Path(".venv")
            requirements_path = Path("requirements.txt")
            
            # Gather all user input in main thread
            recreate_venv = False
            create_requirements = False
            
            # Check if .venv exists and ask user
            if venv_path.exists():
                logger.debug("Existing .venv found, asking user if they want to recreate it")
                reply = QMessageBox.question(
                    self,
                    "Virtual Environment Exists",
                    f"A virtual environment already exists at:\n{venv_path.absolute()}\n\n"
                    f"Do you want to delete it and create a new one?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                recreate_venv = (reply == QMessageBox.StandardButton.Yes)
                logger.info(f"User chose to recreate venv: {recreate_venv}")
            
            # Check if requirements.txt exists, if not ask user
            if not requirements_path.exists():
                logger.debug("No requirements.txt found, asking user if they want to create one")
                reply = QMessageBox.question(
                    self,
                    "Create requirements.txt",
                    "No requirements.txt found.\n\nCreate a basic requirements.txt file?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                create_requirements = (reply == QMessageBox.StandardButton.Yes)
                logger.info(f"User chose to create requirements.txt: {create_requirements}")
            
            # Now run the actual operation in worker thread with pre-gathered user input
            def run():
                with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                    try:
                        from .modules.python_env import PythonEnvironment
                        
                        logger.debug(f"Starting start_project in worker thread (recreate_venv={recreate_venv}, create_requirements={create_requirements})")
                        
                        # Call with pre-determined choices
                        PythonEnvironment.start_project(
                            recreate_venv=recreate_venv,
                            create_requirements=create_requirements
                        )
                        
                        logger.info("Start project completed successfully")
                        print("\n✅ Operation completed.\n")
                    except Exception as e:
                        logger.error(f"Error in start_project: {e}", exc_info=True)
                        print(f"\n❌ Error: {e}\n")
                        import traceback
                        traceback.print_exc()
            
            thread = threading.Thread(target=run, daemon=True, name="StartProject-Worker")
            logger.debug(f"Starting start_project thread: {thread.name}")
            thread.start()
            
        except Exception as e:
            logger.error(f"Error in execute_start_project_handler: {e}", exc_info=True)
            print(f"❌ Error setting up start project: {e}")
    
    def execute_power_option(self, minutes, description):
        """Execute power management shutdown option"""
        power_manager = self.app.get_config("power_manager_instance")
        if not power_manager:
            QMessageBox.critical(self, "Error", "Power manager not initialized")
            return
        
        # Show confirmation dialog
        confirmation_message = f"You are about to schedule a shutdown in {description}.\n\nThe system will shut down in {minutes} minutes."
        
        reply = QMessageBox.question(
            self,
            "Confirm Shutdown",
            confirmation_message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Execute in thread
        def run():
            with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                try:
                    from datetime import datetime, timedelta
                    import subprocess
                    
                    scheduled_time = datetime.now() + timedelta(minutes=minutes)
                    
                    if os.name == 'nt':  # Windows
                        subprocess.run(['shutdown', '/s', '/t', str(minutes * 60)], check=True, **get_subprocess_creation_flags())
                        print(f"✅ Shutdown scheduled successfully!")
                        print(f"🕒 System will shutdown in {description}")
                        print(f"💡 Use 'shutdown /a' in command prompt to cancel")
                    else:
                        subprocess.run(['sudo', 'shutdown', '-h', f"+{minutes}"], check=True, **get_subprocess_creation_flags())
                        print(f"✅ Shutdown scheduled successfully!")
                        print(f"🕒 System will shutdown in {description}")
                        print(f"💡 Use 'sudo shutdown -c' to cancel")
                    
                    power_manager.shutdown_active = True
                    power_manager._save_shutdown_state(
                        scheduled=True,
                        scheduled_time=scheduled_time,
                        description=description
                    )
                    
                    # Update status display
                    QApplication.instance().postEvent(self, UpdateShutdownStatusEvent())
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def execute_power_custom(self):
        """Execute custom shutdown time dialog"""
        minutes, ok = QInputDialog.getInt(
            self,
            "Custom Shutdown Time",
            "Enter minutes until shutdown (1-1440):",
            25, 1, 1440, 1
        )
        
        if ok:
            hours = minutes // 60
            remaining = minutes % 60
            if hours > 0:
                desc = f"{hours} hour{'s' if hours > 1 else ''}"
                if remaining > 0:
                    desc += f" and {remaining} minute{'s' if remaining > 1 else ''}"
            else:
                desc = f"{minutes} minute{'s' if minutes > 1 else ''}"
            
            self.execute_power_option(minutes, desc)
    
    def execute_power_cancel(self):
        """Cancel scheduled shutdown"""
        power_manager = self.app.get_config("power_manager_instance")
        if not power_manager:
            QMessageBox.critical(self, "Error", "Power manager not initialized")
            return
        
        status = power_manager.get_shutdown_status()
        if not status.get('scheduled'):
            QMessageBox.information(self, "No Shutdown Found", "No shutdown is currently scheduled.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Cancel Shutdown",
            "Are you sure you want to cancel the scheduled shutdown?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        def run():
            with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                try:
                    import subprocess
                    
                    if os.name == 'nt':
                        result = subprocess.run(['shutdown', '/a'], capture_output=True, text=True, **get_subprocess_creation_flags())
                        if result.returncode == 0:
                            print("✅ Shutdown cancelled successfully!")
                        else:
                            print("ℹ️  No shutdown was scheduled or shutdown already cancelled.")
                    else:
                        result = subprocess.run(['sudo', 'shutdown', '-c'], capture_output=True, text=True, **get_subprocess_creation_flags())
                        if result.returncode == 0:
                            print("✅ Shutdown cancelled successfully!")
                        else:
                            print("ℹ️  No shutdown was scheduled or shutdown already cancelled.")
                    
                    power_manager.shutdown_active = False
                    power_manager._save_shutdown_state(scheduled=False)
                    
                    QApplication.instance().postEvent(self, UpdateShutdownStatusEvent())
                    
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def execute_venv_with_requirements(self):
        """Create venv with requirements.txt"""
        def run():
            with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                from .modules.python_env import PythonEnvironment
                PythonEnvironment.create_venv_with_requirements()
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def execute_venv_with_all_files(self):
        """Create venv with requirements.txt, .gitignore, and README.md"""
        def run():
            with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                from .modules.python_env import PythonEnvironment
                PythonEnvironment.create_venv_with_all_files()
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def execute_create_gitignore(self):
        """Create standalone .gitignore file"""
        def run():
            with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                from .modules.python_env import PythonEnvironment
                PythonEnvironment.create_gitignore_file()
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def execute_create_readme(self):
        """Create standalone README.md file"""
        def run():
            with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                from .modules.python_env import PythonEnvironment
                PythonEnvironment.create_readme_file()
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def _update_git_status(self):
        """Update the git repository status display"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                capture_output=True,
                text=True,
                cwd=self.current_dir,
                **get_subprocess_creation_flags()
            )
            
            if result.returncode == 0:
                # Get repository info
                repo_name = "Unknown"
                remote_url = None
                
                try:
                    remote_result = subprocess.run(
                        ['git', 'remote', 'get-url', 'origin'],
                        capture_output=True,
                        text=True,
                        cwd=self.current_dir,
                        check=False,
                        **get_subprocess_creation_flags()
                    )
                    if remote_result.returncode == 0:
                        remote_url = remote_result.stdout.strip()
                        if remote_url:
                            display_url = remote_url[:-4] if remote_url.endswith('.git') else remote_url
                            repo_name = display_url.split('/')[-1]
                except Exception:
                    repo_name = os.path.basename(self.current_dir)
                
                self.git_remote_url = remote_url
                
                # Get branch info
                current_branch = None
                upstream_branch = None
                
                try:
                    br = subprocess.run(
                        ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                        capture_output=True,
                        text=True,
                        cwd=self.current_dir,
                        **get_subprocess_creation_flags()
                    )
                    if br.returncode == 0:
                        current_branch = br.stdout.strip()
                    
                    up = subprocess.run(
                        ['git', 'rev-parse', '--abbrev-ref', '--symbolic-full-name', 'HEAD@{u}'],
                        capture_output=True,
                        text=True,
                        cwd=self.current_dir,
                        check=False,
                        **get_subprocess_creation_flags()
                    )
                    if up.returncode == 0:
                        upstream_branch = up.stdout.strip()
                except Exception:
                    pass
                
                # Build status text
                tracked_part = ""
                if current_branch:
                    tracked_part = f" — Branch: {current_branch}"
                    if upstream_branch:
                        tracked_part += f" (tracked: {upstream_branch})"
                
                if remote_url:
                    self.git_repo_label.setText(f"🔗 Git Repository: {repo_name} ({remote_url}){tracked_part} [copy]")
                else:
                    self.git_repo_label.setText(f"🔗 Git Repository: {repo_name}{tracked_part}")
                self.git_repo_label.show()
                
                # Get last commit
                try:
                    commit_result = subprocess.run(
                        ['git', 'log', '-1', '--format=%cd', '--date=format:%B %d, %Y at %I:%M %p'],
                        capture_output=True,
                        text=True,
                        cwd=self.current_dir,
                        check=False,
                        **get_subprocess_creation_flags()
                    )
                    if commit_result.returncode == 0:
                        last_commit = commit_result.stdout.strip()
                        self.git_commit_label.setText(f"📅 Last Commit: {last_commit}")
                    else:
                        self.git_commit_label.setText("📅 Last Commit: No commits yet")
                    self.git_commit_label.show()
                except Exception:
                    self.git_commit_label.setText("📅 Last Commit: Unable to retrieve")
                    self.git_commit_label.show()
            else:
                self.git_remote_url = None
                self.git_repo_label.hide()
                self.git_commit_label.hide()
        except Exception:
            self.git_remote_url = None
            self.git_repo_label.hide()
            self.git_commit_label.hide()
    
    def _update_shutdown_status(self):
        """Update the shutdown status display"""
        try:
            power_manager = self.app.get_config("power_manager_instance")
            if power_manager:
                status = power_manager.get_shutdown_status()
                
                if status['scheduled'] and status['time_remaining']:
                    time_remaining = status['time_remaining']
                    total_seconds = int(time_remaining.total_seconds())
                    
                    if total_seconds <= 0:
                        self.shutdown_status_label.setText("⚡ Shutdown Timer: Not Scheduled")
                        self.shutdown_status_label.setStyleSheet(f"color: {DarkTheme.TEXT_SUCCESS.name()};")
                        return
                    
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    
                    if hours > 0:
                        time_str = f"{hours}h {minutes}m {seconds}s"
                    elif minutes > 0:
                        time_str = f"{minutes}m {seconds}s"
                    else:
                        time_str = f"{seconds}s"
                    
                    self.shutdown_status_label.setText(f"⚡ {time_str} remaining")
                    self.shutdown_status_label.setStyleSheet(f"color: {DarkTheme.TEXT_ERROR.name()};")
                else:
                    self.shutdown_status_label.setText("⚡ Not Scheduled")
                    self.shutdown_status_label.setStyleSheet(f"color: {DarkTheme.TEXT_SUCCESS.name()};")
            else:
                self.shutdown_status_label.setText("⚡ Not Scheduled")
                self.shutdown_status_label.setStyleSheet(f"color: {DarkTheme.TEXT_SUCCESS.name()};")
        except Exception:
            pass
    
    def _setup_logging(self):
        """Setup logging to file"""
        from datetime import datetime
        
        data_dir = get_data_directory()
        log_dir = data_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_filename = f"termtools_{datetime.now().strftime('%Y%m%d')}.log"
        log_file_path = log_dir / log_filename
        
        try:
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write("\n" + "="*80 + "\n")
                f.write(f"TermTools Session - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Data Directory: {data_dir}\n")
                f.write(f"Working Directory: {os.getcwd()}\n")
                f.write("="*80 + "\n\n")
        except Exception as e:
            print(f"⚠️  Warning: Could not create log file: {e}")
            return None
        
        return str(log_file_path)
    
    def on_status_timer(self):
        """Timer event handler for updating status"""
        self._update_shutdown_status()
        self._update_git_status()
    
    def _on_git_repo_click(self, event):
        """Handle click on git repository label - copy URL to clipboard"""
        if self.git_remote_url:
            try:
                clipboard = QApplication.clipboard()
                clipboard.setText(self.git_remote_url)
                
                QMessageBox.information(
                    self,
                    "URL Copied",
                    f"✅ GitHub URL copied to clipboard!\n\n{self.git_remote_url}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Copy Failed",
                    f"❌ Failed to copy URL to clipboard: {e}"
                )
    
    def on_clear_output(self):
        """Clear the output console"""
        self.output_text.clear()
    
    def on_show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog - Update functionality coming soon!"
        )
    
    def on_show_help(self):
        """Show help dialog"""
        with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
            self.app.show_help()
    
    def on_exit(self):
        """Exit the application"""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit TermTools?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._cleanup_on_exit()
            QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Check if Pomodoro timer is open
        from .modules.pomodoro import PomodoroTimer
        
        if PomodoroTimer._instance is not None and PomodoroTimer._instance.isVisible():
            reply = QMessageBox.question(
                self,
                "Pomodoro Timer Running",
                "Pomodoro timer is still running.\n\n"
                "Do you want to close everything?\n\n"
                "• Click 'Yes' to close everything (including timer)\n"
                "• Click 'No' to hide main window and keep timer running\n"
                "• Click 'Cancel' to return to TermTools",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if PomodoroTimer._instance:
                    PomodoroTimer._instance.close()
                self._cleanup_on_exit()
                event.accept()
                QApplication.quit()
            elif reply == QMessageBox.StandardButton.No:
                print("💡 Main window hidden. Pomodoro timer continues running.")
                print("   (Close the Pomodoro timer to exit the application)")
                self.hide()
                event.ignore()
            else:
                event.ignore()
        else:
            self._cleanup_on_exit()
            event.accept()
            QApplication.quit()
    
    def _cleanup_on_exit(self):
        """Cleanup and log session end"""
        from datetime import datetime
        
        if self.log_file_path:
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write("\n" + "="*80 + "\n")
                    f.write(f"Session ended - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*80 + "\n\n")
            except Exception:
                pass
        
        # Restore stdout/stderr
        if hasattr(self.stdout_redirector, 'original_stdout'):
            sys.stdout = self.stdout_redirector.original_stdout
        if hasattr(self.stderr_redirector, 'original_stderr'):
            sys.stderr = self.stderr_redirector.original_stderr
    
    def event(self, event):
        """Handle custom events"""
        if isinstance(event, UpdateShutdownStatusEvent):
            self._update_shutdown_status()
            return True
        return super().event(event)


class UpdateShutdownStatusEvent(QEvent):
    """Custom event for updating shutdown status"""
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self):
        super().__init__(self.EVENT_TYPE)


def run_qt_app():
    """Entry point for PyQt6 GUI"""
    # Setup logging before starting the app
    setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info("TermTools Application Starting")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("="*80)
    
    app = QApplication(sys.argv)
    app.setApplicationName("TermTools")
    app.setOrganizationName("BasusTools")
    
    logger.debug("Creating main window")
    window = TermToolsMainWindow()
    window.show()
    
    logger.info("Application window displayed, entering event loop")
    exit_code = app.exec()
    
    logger.info(f"Application exiting with code: {exit_code}")
    logger.info("="*80)
    
    sys.exit(exit_code)


def setup_logging():
    """Configure logging to file with detailed format"""
    # Get data directory for logs
    data_dir = get_data_directory()
    log_dir = data_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create log file with date
    log_filename = f"termtools_{datetime.now().strftime('%Y%m%d')}.log"
    log_file_path = log_dir / log_filename
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-25s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            # Optional: Also log to console for development
            # logging.StreamHandler(sys.stderr)
        ]
    )
    
    # Set specific loggers to appropriate levels
    logging.getLogger('PyQt6').setLevel(logging.WARNING)  # Reduce Qt noise
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - writing to: {log_file_path}")
    
    return log_file_path
