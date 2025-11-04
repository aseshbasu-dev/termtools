"""
wxPython GUI Application for TermTools
Built by Asesh Basu

This module provides a modern GUI interface for TermTools using wxPython,
replacing the terminal-based menu with buttons and split buttons.
"""

import wx
import wx.lib.agw.buttonpanel as bp
import sys
import os
import io
import subprocess
import threading
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, List
from .app import TermTools


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
    MAIN_BG = wx.Colour(32, 34, 37)          # Dark charcoal main background
    PANEL_BG = wx.Colour(40, 42, 46)         # Slightly lighter panel background
    HEADER_BG = wx.Colour(45, 47, 51)        # Header background
    SIDEBAR_BG = wx.Colour(36, 38, 41)       # Sidebar/button area background
    
    # Text colors
    TEXT_PRIMARY = wx.Colour(220, 221, 222)   # Primary text (light gray)
    TEXT_SECONDARY = wx.Colour(180, 181, 182) # Secondary text (medium gray)
    TEXT_MUTED = wx.Colour(140, 141, 142)     # Muted text (darker gray)
    TEXT_ACCENT = wx.Colour(88, 166, 255)     # Accent text (blue)
    TEXT_SUCCESS = wx.Colour(46, 204, 113)    # Success text (green)
    TEXT_WARNING = wx.Colour(241, 196, 15)    # Warning text (yellow)
    TEXT_ERROR = wx.Colour(231, 76, 60)       # Error text (red)
    TEXT_DARK = wx.Colour(18, 19, 21)         # Dark text for light backgrounds
    
    # Button colors
    BUTTON_BG = wx.Colour(52, 54, 58)         # Button background
    BUTTON_BG_HOVER = wx.Colour(62, 64, 68)   # Button hover background
    BUTTON_BG_ACTIVE = wx.Colour(72, 74, 78)  # Button active background
    BUTTON_TEXT = wx.Colour(220, 221, 222)    # Button text
    
    # Accent colors (professional blue scheme)
    ACCENT_PRIMARY = wx.Colour(88, 166, 255)  # Primary accent (blue)
    ACCENT_SECONDARY = wx.Colour(74, 144, 226) # Secondary accent (darker blue)
    ACCENT_TERTIARY = wx.Colour(102, 187, 255) # Tertiary accent (lighter blue)
    
    # Output console
    CONSOLE_BG = wx.Colour(24, 26, 27)        # Console background (darker)
    CONSOLE_TEXT = wx.Colour(204, 204, 204)   # Console text
    
    # Borders and separators
    BORDER = wx.Colour(60, 62, 66)            # Border color
    SEPARATOR = wx.Colour(70, 72, 76)         # Separator lines
    
    # Category colors (muted professional palette)
    CATEGORY_GIT = wx.Colour(255, 123, 114)   # Git operations (coral)
    CATEGORY_PYTHON = wx.Colour(52, 168, 83)  # Python env (green)
    CATEGORY_PROJECT = wx.Colour(255, 193, 7) # Project templates (amber)
    CATEGORY_CLEANUP = wx.Colour(156, 39, 176) # Cleanup (purple)
    CATEGORY_POWER = wx.Colour(244, 67, 54)   # Power management (red)
    CATEGORY_HELP = wx.Colour(96, 125, 139)   # Help (blue-gray)


class SplitButton(wx.Panel):
    """
    Custom split button control with main action and dropdown menu.
    Used for menu items with multiple sub-options.
    """
    
    def __init__(self, parent, label, main_handler, sub_items=None):
        """
        Initialize split button
        
        Args:
            parent: Parent window
            label: Button label text
            main_handler: Callback for main button click
            sub_items: List of tuples (label, handler) for dropdown items
        """
        super().__init__(parent)
        
        # Apply dark theme to panel
        self.SetBackgroundColour(DarkTheme.SIDEBAR_BG)
        
        self.main_handler = main_handler
        self.sub_items = sub_items or []
        
        # Create horizontal sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Main button (70% width)
        self.main_button = wx.Button(self, label=label, size=(-1, 35))
        self.main_button.SetBackgroundColour(DarkTheme.BUTTON_BG)
        self.main_button.SetForegroundColour(DarkTheme.BUTTON_TEXT)
        self.main_button.Bind(wx.EVT_BUTTON, self.on_main_click)
        sizer.Add(self.main_button, 7, wx.EXPAND)
        
        if self.sub_items:
            # Dropdown arrow button (30% width)
            self.dropdown_button = wx.Button(self, label="▼", size=(30, 35))
            self.dropdown_button.SetBackgroundColour(DarkTheme.BUTTON_BG_HOVER)
            self.dropdown_button.SetForegroundColour(DarkTheme.BUTTON_TEXT)
            self.dropdown_button.Bind(wx.EVT_BUTTON, self.on_dropdown_click)
            sizer.Add(self.dropdown_button, 0, wx.EXPAND | wx.LEFT, 2)
        
        self.SetSizer(sizer)

        # Buttons adopt theming from parent frame helper
        
    def on_main_click(self, event):
        """Handle main button click"""
        if self.main_handler:
            self.main_handler()
    
    def on_dropdown_click(self, event):
        """Show dropdown menu with sub-options using custom dark-themed menu"""
        if not self.sub_items:
            return
            
        # Create a simple choice dialog with dark theme
        choices = [label for label, handler in self.sub_items]
        
        # Create custom dialog
        dialog = wx.SingleChoiceDialog(
            self, 
            "Select an option:", 
            "Menu Options",
            choices
        )
        
        # Apply dark theme to dialog
        dialog.SetBackgroundColour(DarkTheme.MAIN_BG)
        dialog.SetForegroundColour(DarkTheme.TEXT_PRIMARY)
        
        # Get all children and apply dark theme
        def apply_dark_theme_to_children(parent):
            for child in parent.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetBackgroundColour(DarkTheme.MAIN_BG)
                    child.SetForegroundColour(DarkTheme.TEXT_PRIMARY)
                elif isinstance(child, wx.ListBox):
                    child.SetBackgroundColour(DarkTheme.BUTTON_BG)
                    child.SetForegroundColour(DarkTheme.TEXT_PRIMARY)
                elif isinstance(child, wx.Button):
                    child.SetBackgroundColour(DarkTheme.BUTTON_BG)
                    child.SetForegroundColour(DarkTheme.TEXT_PRIMARY)
                apply_dark_theme_to_children(child)
        
        apply_dark_theme_to_children(dialog)
        dialog.Refresh()
        
        if dialog.ShowModal() == wx.ID_OK:
            selection = dialog.GetSelection()
            if 0 <= selection < len(self.sub_items):
                _, handler = self.sub_items[selection]
                handler()
        
        dialog.Destroy()


class OutputRedirector:
    """Redirects stdout/stderr to both wx.TextCtrl and log file"""
    
    def __init__(self, text_ctrl, log_file_path=None):
        self.text_ctrl = text_ctrl
        self.buffer = io.StringIO()
        self.log_file_path = log_file_path
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
    def write(self, text):
        """Write text to both text control and log file"""
        # Write to GUI
        wx.CallAfter(self._append_text, text)
        
        # Write to log file
        if self.log_file_path:
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    # Strip ANSI color codes for file
                    import re
                    clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
                    f.write(clean_text)
                    f.flush()
            except Exception as e:
                # Silently fail if logging fails to avoid infinite loops
                pass
        
    def _append_text(self, text):
        """Append text to the control (called in main thread)"""
        if self.text_ctrl:
            # Strip ANSI color codes
            import re
            text = re.sub(r'\033\[[0-9;]*m', '', text)
            self.text_ctrl.AppendText(text)
            
    def flush(self):
        """Flush the buffer"""
        pass


class TermToolsFrame(wx.Frame):
    """Main application window for TermTools GUI"""
    
    def __init__(self):
        super().__init__(
            None, 
            title="TermTools - Python Project Manager v2.10 GUI",
            size=(1000, 700)
        )
        
        # Apply dark theme to main frame
        self.SetBackgroundColour(DarkTheme.MAIN_BG)
        
        # Initialize TermTools backend
        self.app = TermTools()
        self.current_dir = os.getcwd()
        
        # Set icon if available
        self.SetIcon(wx.Icon(wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE)))
        
        # Create UI
        self._create_ui()
        
        # Bind close event
        self.Bind(wx.EVT_CLOSE, self.on_window_close)
        
        # Center on screen
        self.Centre()
        
    def _create_ui(self):
        """Create the user interface"""
        # Create main panel
        main_panel = wx.Panel(self)
        main_panel.SetBackgroundColour(DarkTheme.MAIN_BG)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header section
        header_panel = self._create_header(main_panel)
        main_sizer.Add(header_panel, 0, wx.EXPAND | wx.ALL, 10)
        
        # Create splitter for buttons and output
        splitter = wx.SplitterWindow(main_panel)
        splitter.SetBackgroundColour(DarkTheme.MAIN_BG)
        
        # Left panel - Menu buttons
        left_panel = wx.ScrolledWindow(splitter)
        left_panel.SetBackgroundColour(DarkTheme.SIDEBAR_BG)
        left_panel.SetScrollRate(20, 20)
        self.button_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Create menu buttons organized by category
        self._create_menu_buttons(left_panel)
        
        left_panel.SetSizer(self.button_sizer)
        
        # Right panel - Output console
        right_panel = wx.Panel(splitter)
        right_panel.SetBackgroundColour(DarkTheme.PANEL_BG)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Output label
        output_label = wx.StaticText(right_panel, label="Output Console:")
        output_label.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        output_label.SetForegroundColour(DarkTheme.TEXT_PRIMARY)
        output_label.SetBackgroundColour(DarkTheme.PANEL_BG)
        right_sizer.Add(output_label, 0, wx.ALL, 5)
        
        # Output text control
        self.output_text = wx.TextCtrl(
            right_panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP | wx.HSCROLL
        )
        self.output_text.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.output_text.SetBackgroundColour(DarkTheme.CONSOLE_BG)
        self.output_text.SetForegroundColour(DarkTheme.CONSOLE_TEXT)
        right_sizer.Add(self.output_text, 1, wx.EXPAND | wx.ALL, 5)
        
        # Clear button
        clear_button = wx.Button(right_panel, label="Clear Output")
        self._style_button(clear_button)
        clear_button.Bind(wx.EVT_BUTTON, self.on_clear_output)
        right_sizer.Add(clear_button, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        
        right_panel.SetSizer(right_sizer)
        
        # Split the window (40% buttons, 60% output)
        splitter.SplitVertically(left_panel, right_panel)
        splitter.SetSashPosition(400)
        splitter.SetMinimumPaneSize(300)
        
        main_sizer.Add(splitter, 1, wx.EXPAND | wx.ALL, 5)
        
        # Create custom status bar at bottom
        status_panel = wx.Panel(main_panel)
        status_panel.SetBackgroundColour(DarkTheme.PANEL_BG)
        status_panel.SetMinSize((-1, 25))
        
        status_sizer = wx.BoxSizer(wx.HORIZONTAL)
        status_sizer.Add(wx.Size(10, -1), 0, 0)  # Left padding
        
        self.status_text_ctrl = wx.StaticText(status_panel, label="", style=wx.ST_NO_AUTORESIZE)
        self.status_text_ctrl.SetBackgroundColour(DarkTheme.PANEL_BG)
        self.status_text_ctrl.SetForegroundColour(wx.Colour(255, 255, 255))  # Pure white
        self.status_text_ctrl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        
        status_sizer.Add(self.status_text_ctrl, 1, wx.ALIGN_CENTER_VERTICAL)
        status_sizer.Add(wx.Size(10, -1), 0, 0)  # Right padding
        
        status_panel.SetSizer(status_sizer)
        
        # Add to main sizer
        main_sizer.Add(status_panel, 0, wx.EXPAND)
        
        # Store reference for SetStatusText method
        self.status_bar = status_panel

        main_panel.SetSizer(main_sizer)
        
        # Setup logging
        self.log_file_path = self._setup_logging()
        
        # Setup output redirection with logging
        self.stdout_redirector = OutputRedirector(self.output_text, self.log_file_path)
        self.stderr_redirector = OutputRedirector(self.output_text, self.log_file_path)
        
        # Redirect sys.stdout and sys.stderr
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stderr_redirector
        
        # Status bar
        self.SetStatusText(f"Ready - Current directory: {self.current_dir}")

        # Setup timer for periodic shutdown status updates
        self.status_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_status_timer, self.status_timer)
        self.status_timer.Start(1000)  # Update every second
        
    def _create_header(self, parent):
        """Create the header section with title and info"""
        panel = wx.Panel(parent)
        panel.SetBackgroundColour(DarkTheme.HEADER_BG)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(panel, label="🔧 TERMTOOLS")
        title_font = wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        title.SetForegroundColour(DarkTheme.TEXT_PRIMARY)
        title.SetBackgroundColour(DarkTheme.HEADER_BG)
        sizer.Add(title, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        
        # Subtitle
        subtitle = wx.StaticText(panel, label="Python Project Manager")
        subtitle_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        subtitle.SetFont(subtitle_font)
        subtitle.SetForegroundColour(DarkTheme.TEXT_ACCENT)
        subtitle.SetBackgroundColour(DarkTheme.HEADER_BG)
        sizer.Add(subtitle, 0, wx.ALIGN_CENTER | wx.TOP, 2)
        
        # Author
        author = wx.StaticText(panel, label=f"Built by {self.app.author}")
        author_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        author.SetFont(author_font)
        author.SetForegroundColour(DarkTheme.TEXT_SECONDARY)
        author.SetBackgroundColour(DarkTheme.HEADER_BG)
        sizer.Add(author, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 5)
        
        # Separator line
        separator = wx.StaticLine(panel, style=wx.LI_HORIZONTAL)
        separator.SetBackgroundColour(DarkTheme.SEPARATOR)
        sizer.Add(separator, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)
        
        # Status section panel with darker background
        status_panel = wx.Panel(panel)
        status_panel.SetBackgroundColour(DarkTheme.PANEL_BG)
        status_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Status section title with date/time
        from datetime import datetime
        current_datetime = datetime.now().strftime("%B %d, %Y %I:%M:%S %p")
        self.status_title_label = wx.StaticText(status_panel, label=f"STATUS ON {current_datetime}")
        status_title_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.status_title_label.SetFont(status_title_font)
        self.status_title_label.SetForegroundColour(DarkTheme.TEXT_ACCENT)
        self.status_title_label.SetBackgroundColour(DarkTheme.PANEL_BG)
        status_sizer.Add(self.status_title_label, 0, wx.ALIGN_CENTER | wx.TOP, 8)
        
        # Current directory status
        dir_label = wx.StaticText(status_panel, label=f"📁 Current Folder: {self.current_dir}")
        dir_label.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        dir_label.SetForegroundColour(DarkTheme.TEXT_PRIMARY)
        dir_label.SetBackgroundColour(DarkTheme.PANEL_BG)
        status_sizer.Add(dir_label, 0, wx.ALIGN_CENTER | wx.TOP, 5)
        
        # Git repository status (dynamic, clickable)
        self.git_repo_label = wx.StaticText(status_panel, label="")
        git_repo_font = wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.git_repo_label.SetFont(git_repo_font)
        self.git_repo_label.SetForegroundColour(DarkTheme.CATEGORY_GIT)
        self.git_repo_label.SetBackgroundColour(DarkTheme.PANEL_BG)
        self.git_repo_label.SetCursor(wx.Cursor(wx.CURSOR_HAND))  # Show hand cursor
        self.git_repo_label.Bind(wx.EVT_LEFT_UP, self._on_git_repo_click)
        status_sizer.Add(self.git_repo_label, 0, wx.ALIGN_CENTER | wx.TOP, 3)
        
        # Store the remote URL for copying
        self.git_remote_url = None
        
        # Git last commit status (dynamic)
        self.git_commit_label = wx.StaticText(status_panel, label="")
        git_commit_font = wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.git_commit_label.SetFont(git_commit_font)
        self.git_commit_label.SetForegroundColour(DarkTheme.TEXT_SECONDARY)
        self.git_commit_label.SetBackgroundColour(DarkTheme.PANEL_BG)
        status_sizer.Add(self.git_commit_label, 0, wx.ALIGN_CENTER | wx.TOP, 2)
        
        # Shutdown timer status (dynamic)
        self.shutdown_status_label = wx.StaticText(status_panel, label="⚡ Shutdown Timer: Not Scheduled")
        shutdown_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.shutdown_status_label.SetFont(shutdown_font)
        self.shutdown_status_label.SetForegroundColour(DarkTheme.TEXT_SUCCESS)
        self.shutdown_status_label.SetBackgroundColour(DarkTheme.PANEL_BG)
        status_sizer.Add(self.shutdown_status_label, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 5)
        
        status_panel.SetSizer(status_sizer)
        sizer.Add(status_panel, 0, wx.EXPAND | wx.TOP, 5)
        
        # Bottom separator line
        separator2 = wx.StaticLine(panel, style=wx.LI_HORIZONTAL)
        separator2.SetBackgroundColour(DarkTheme.SEPARATOR)
        sizer.Add(separator2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)
        
        # Update shutdown status and git status on initial load
        self._update_shutdown_status()
        self._update_git_status()
        
        panel.SetSizer(sizer)
        return panel
        
    def _create_menu_buttons(self, parent):
        """Create buttons for all menu items organized by category"""
        categories = self.app.get_menu_items_by_category()
        
        # Define category colors
        category_colors = {
            "🔧 GIT OPERATIONS": DarkTheme.CATEGORY_GIT,
            "🐍 PYTHON ENVIRONMENT": DarkTheme.CATEGORY_PYTHON,
            "📁 PROJECT TEMPLATES": DarkTheme.CATEGORY_PROJECT,
            "🧹 CLEANUP": DarkTheme.CATEGORY_CLEANUP,
            "🎯 PRODUCTIVITY": wx.Colour(255, 179, 71),  # Orange for productivity
            "⚡ POWER MANAGEMENT": DarkTheme.CATEGORY_POWER,
        }
        
        for category, items in categories.items():
            # Category header
            category_text = wx.StaticText(parent, label=category)
            category_font = wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
            category_text.SetFont(category_font)
            
            # Apply category-specific color or default
            category_color = category_colors.get(category, DarkTheme.TEXT_ACCENT)
            category_text.SetForegroundColour(category_color)
            category_text.SetBackgroundColour(DarkTheme.SIDEBAR_BG)
            self.button_sizer.Add(category_text, 0, wx.ALL, 10)
            
            # Add items in this category
            for item in items:
                # Determine if this item needs a split button
                sub_options = self._get_sub_options(item)
                
                if sub_options:
                    # Create split button with custom main handler for power management
                    if "shutdown" in item.title.lower():
                        # For shutdown button, main action is custom time dialog
                        main_handler = lambda: self.execute_power_custom()
                    else:
                        # For other split buttons, use original handler
                        main_handler = lambda h=item.handler: self.execute_handler(h)
                    
                    split_btn = SplitButton(
                        parent,
                        f"{item.title}",
                        main_handler,
                        sub_options
                    )
                    self._style_split_button(split_btn)
                    self.button_sizer.Add(split_btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
                else:
                    # Create regular button
                    button = wx.Button(parent, label=f"{item.title}", size=(-1, 35))
                    self._style_button(button)
                    button.SetToolTip(item.description)
                    button.Bind(wx.EVT_BUTTON, lambda evt, h=item.handler: self.execute_handler(h))
                    self.button_sizer.Add(button, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        # Add separator
        separator = wx.StaticLine(parent)
        separator.SetBackgroundColour(DarkTheme.SEPARATOR)
        self.button_sizer.Add(separator, 0, wx.EXPAND | wx.ALL, 10)
        
        # Settings button
        settings_button = wx.Button(parent, label="⚙️ Settings", size=wx.Size(-1, 35))
        self._style_button(settings_button, text_colour=DarkTheme.TEXT_ACCENT)
        settings_button.Bind(wx.EVT_BUTTON, self.on_show_settings)
        self.button_sizer.Add(settings_button, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        # Help button
        help_button = wx.Button(parent, label="❓ Show Help", size=wx.Size(-1, 35))
        self._style_button(help_button, text_colour=DarkTheme.CATEGORY_HELP)
        help_button.Bind(wx.EVT_BUTTON, self.on_show_help)
        self.button_sizer.Add(help_button, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        # Exit button
        exit_button = wx.Button(parent, label="❌ Exit", size=wx.Size(-1, 35))
        self._style_button(exit_button, text_colour=DarkTheme.TEXT_ERROR)
        exit_button.Bind(wx.EVT_BUTTON, self.on_exit)
        self.button_sizer.Add(exit_button, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
    
    def _style_button(self, button, *, background=None, text_colour=None, hover_background=None, hover_text=None):
        """Apply dark theme styling with consistent hover/focus behavior"""
        default_bg = background or DarkTheme.BUTTON_BG
        default_fg = text_colour or DarkTheme.BUTTON_TEXT
        hover_bg = hover_background if hover_background is not None else DarkTheme.ACCENT_TERTIARY
        hover_fg = hover_text if hover_text is not None else DarkTheme.TEXT_DARK

        if hasattr(button, "SetThemeEnabled"):
            button.SetThemeEnabled(False)

        button.SetBackgroundColour(default_bg)
        button.SetOwnBackgroundColour(default_bg)
        button.SetForegroundColour(default_fg)
        button.SetOwnForegroundColour(default_fg)

        def apply_colors(bg, fg):
            button.SetBackgroundColour(bg)
            button.SetOwnBackgroundColour(bg)
            button.SetForegroundColour(fg)
            button.SetOwnForegroundColour(fg)
            button.Refresh()

        def on_enter(event):
            apply_colors(hover_bg, hover_fg)
            event.Skip()

        def on_leave(event):
            apply_colors(default_bg, default_fg)
            event.Skip()

        button.Bind(wx.EVT_ENTER_WINDOW, on_enter)
        button.Bind(wx.EVT_LEAVE_WINDOW, on_leave)
        button.Bind(wx.EVT_SET_FOCUS, on_enter)
        button.Bind(wx.EVT_KILL_FOCUS, on_leave)

    def _style_split_button(self, split_button):
        """Style both parts of a split button"""
        self._style_button(split_button.main_button)
        if hasattr(split_button, "dropdown_button"):
            self._style_button(
                split_button.dropdown_button,
                background=DarkTheme.BUTTON_BG,
                hover_background=DarkTheme.ACCENT_SECONDARY,
                hover_text=DarkTheme.TEXT_DARK
            )

    def SetStatusText(self, text, field=0):
        """Override SetStatusText to update our custom status bar"""
        if hasattr(self, 'status_text_ctrl') and self.status_text_ctrl:
            self.status_text_ctrl.SetLabel(text)
            # Ensure white color is maintained
            self.status_text_ctrl.SetForegroundColour(wx.Colour(255, 255, 255))
            self.status_text_ctrl.Refresh()

    def _get_sub_options(self, menu_item):
        """
        Determine if a menu item has sub-options and return them.
        For power manager: 1hr, 2hr, 3hr, cancel shutdown options
        For other modules: Check if handler has sub-menu structure
        """
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
        def run():
            # Redirect output
            with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                try:
                    # Check if handler expects app parameter
                    import inspect
                    sig = inspect.signature(handler)
                    if len(sig.parameters) > 0:
                        handler(self.app)
                    else:
                        handler()
                    print("\n✅ Operation completed.\n")
                except Exception as e:
                    print(f"\n❌ Error: {e}\n")
                    import traceback
                    traceback.print_exc()
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def execute_power_option(self, minutes, description):
        """Execute power management shutdown option with GUI confirmation"""
        # Show confirmation dialog first, before threading
        power_manager = self.app.get_config("power_manager_instance")
        if not power_manager:
            wx.MessageBox(
                "Power manager not initialized",
                "Error",
                wx.OK | wx.ICON_ERROR
            )
            return
        
        # Use the power manager's GUI confirmation method
        confirmation_message = f"You are about to schedule a shutdown in {description}.\n\nThe system will shut down in {minutes} minutes."
        
        if not power_manager._show_gui_confirmation(confirmation_message, "Confirm Shutdown"):
            return  # User cancelled
        
        # Now proceed with the shutdown scheduling in a thread
        def run():
            with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                try:
                    from datetime import datetime, timedelta
                    import subprocess
                    import os
                    
                    scheduled_time = datetime.now() + timedelta(minutes=minutes)
                    
                    if os.name == 'nt':  # Windows
                        subprocess.run(['shutdown', '/s', '/t', str(minutes * 60)], check=True, **get_subprocess_creation_flags())
                        print(f"✅ Shutdown scheduled successfully!")
                        print(f"🕒 System will shutdown in {description}")
                        print(f"💡 Use 'shutdown /a' in command prompt to cancel")
                    else:  # Unix-like systems
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
                    
                    # Update status display after scheduling
                    wx.CallAfter(self._update_shutdown_status)
                    
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to schedule shutdown: {e}")
                except FileNotFoundError:
                    print("❌ Shutdown command not found. This feature may not be available on your system.")
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def execute_power_custom(self):
        """Execute custom shutdown time dialog"""
        dlg = wx.TextEntryDialog(
            self,
            "Enter minutes until shutdown (1-1440):",
            "Custom Shutdown Time"
        )
        
        if dlg.ShowModal() == wx.ID_OK:
            try:
                minutes = int(dlg.GetValue())
                if 1 <= minutes <= 1440:
                    hours = minutes // 60
                    remaining = minutes % 60
                    if hours > 0:
                        desc = f"{hours} hour{'s' if hours > 1 else ''}"
                        if remaining > 0:
                            desc += f" and {remaining} minute{'s' if remaining > 1 else ''}"
                    else:
                        desc = f"{minutes} minute{'s' if minutes > 1 else ''}"
                    
                    self.execute_power_option(minutes, desc)
                else:
                    wx.MessageBox(
                        "Please enter a value between 1 and 1440 minutes.",
                        "Invalid Input",
                        wx.OK | wx.ICON_ERROR
                    )
            except ValueError:
                wx.MessageBox(
                    "Please enter a valid number.",
                    "Invalid Input",
                    wx.OK | wx.ICON_ERROR
                )
        
        dlg.Destroy()
    
    def execute_power_cancel(self):
        """Cancel scheduled shutdown with GUI confirmation"""
        power_manager = self.app.get_config("power_manager_instance")
        if not power_manager:
            wx.MessageBox(
                "Power manager not initialized",
                "Error",
                wx.OK | wx.ICON_ERROR
            )
            return
        
        # Check if there's actually a shutdown scheduled
        status = power_manager.get_shutdown_status()
        if not status.get('scheduled'):
            wx.MessageBox(
                "No shutdown is currently scheduled.",
                "No Shutdown Found",
                wx.OK | wx.ICON_INFORMATION
            )
            return
        
        # Confirm cancellation
        if not power_manager._show_gui_confirmation(
            "Are you sure you want to cancel the scheduled shutdown?",
            "Confirm Cancel Shutdown"
        ):
            return  # User cancelled
        
        # Proceed with cancellation in a thread
        def run():
            with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
                try:
                    import subprocess
                    import os
                    
                    if os.name == 'nt':  # Windows
                        result = subprocess.run(['shutdown', '/a'], capture_output=True, text=True, **get_subprocess_creation_flags())
                        if result.returncode == 0:
                            print("✅ Shutdown cancelled successfully!")
                        else:
                            print("ℹ️  No shutdown was scheduled or shutdown already cancelled.")
                    else:  # Unix-like systems
                        result = subprocess.run(['sudo', 'shutdown', '-c'], capture_output=True, text=True, **get_subprocess_creation_flags())
                        if result.returncode == 0:
                            print("✅ Shutdown cancelled successfully!")
                        else:
                            print("ℹ️  No shutdown was scheduled or shutdown already cancelled.")
                    
                    power_manager.shutdown_active = False
                    power_manager._save_shutdown_state(scheduled=False)
                    
                    # Update status display after cancelling
                    wx.CallAfter(self._update_shutdown_status)
                    
                except Exception as e:
                    print(f"❌ Error cancelling shutdown: {e}")
        
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
            # Check if we're in a git repository
            result = subprocess.run(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                capture_output=True,
                text=True,
                cwd=self.current_dir,
                **get_subprocess_creation_flags()
            )
            
            if result.returncode == 0:
                # Get repository name and URL from remote
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
                        # Extract repo name from URL (e.g., https://github.com/user/repo.git -> repo)
                        if remote_url:
                            # Remove .git extension for display name
                            display_url = remote_url[:-4] if remote_url.endswith('.git') else remote_url
                            # Extract last part of path as repo name
                            repo_name = display_url.split('/')[-1]
                except Exception:
                    # If remote doesn't exist, try to get from directory name
                    repo_name = os.path.basename(self.current_dir)
                
                # Store remote URL for copy functionality
                self.git_remote_url = remote_url
                
                # Display repo name with full URL (with click hint)
                if remote_url:
                    self.git_repo_label.SetLabel(f"🔗 Git Repository: {repo_name} ({remote_url}) [copy]")
                else:
                    self.git_repo_label.SetLabel(f"🔗 Git Repository: {repo_name}")
                self.git_repo_label.Show()
                
                # Get last commit date and time
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
                        self.git_commit_label.SetLabel(f"📅 Last Commit: {last_commit}")
                        self.git_commit_label.Show()
                    else:
                        self.git_commit_label.SetLabel("📅 Last Commit: No commits yet")
                        self.git_commit_label.Show()
                except Exception:
                    self.git_commit_label.SetLabel("📅 Last Commit: Unable to retrieve")
                    self.git_commit_label.Show()
            else:
                # Not a git repository
                self.git_remote_url = None
                self.git_repo_label.Hide()
                self.git_commit_label.Hide()
        except Exception as e:
            # Hide git status if git is not available or any error occurs
            self.git_remote_url = None
            self.git_repo_label.Hide()
            self.git_commit_label.Hide()
    
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
                        # Time has passed, set to not scheduled
                        self.shutdown_status_label.SetLabel("⚡ Shutdown Timer: Not Scheduled")
                        self.shutdown_status_label.SetForegroundColour(DarkTheme.TEXT_SUCCESS)
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
                    
                    self.shutdown_status_label.SetLabel(f"⚡ Shutdown Timer: {time_str} remaining")
                    self.shutdown_status_label.SetForegroundColour(DarkTheme.TEXT_ERROR)
                else:
                    self.shutdown_status_label.SetLabel("⚡ Shutdown Timer: Not Scheduled")
                    self.shutdown_status_label.SetForegroundColour(DarkTheme.TEXT_SUCCESS)
            else:
                self.shutdown_status_label.SetLabel("⚡ Shutdown Timer: Not Scheduled")
                self.shutdown_status_label.SetForegroundColour(DarkTheme.TEXT_SUCCESS)
        except Exception as e:
            # Silently handle errors to avoid disrupting the UI
            pass
    
    def _setup_logging(self):
        """Setup logging to file"""
        from datetime import datetime
        from pathlib import Path
        
        # Create logs directory if it doesn't exist
        log_dir = Path("core/data/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with date
        log_filename = f"termtools_{datetime.now().strftime('%Y%m%d')}.log"
        log_file_path = log_dir / log_filename
        
        # Write session header
        try:
            with open(log_file_path, 'a', encoding='utf-8') as f:
                f.write("\n")
                f.write("="*80 + "\n")
                f.write(f"TermTools Session - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n")
                f.write("\n")
        except Exception as e:
            print(f"⚠️  Warning: Could not create log file: {e}")
            return None
        
        return str(log_file_path)
    
    def on_status_timer(self, event):
        """Timer event handler for updating shutdown status, git status, and time"""
        # Update shutdown status
        self._update_shutdown_status()
        
        # Update git status (check every timer tick in case user changes directories or makes commits)
        self._update_git_status()
        
        # Update current date/time
        from datetime import datetime
        current_datetime = datetime.now().strftime("%B %d, %Y %I:%M:%S %p")
        if hasattr(self, 'status_title_label'):
            self.status_title_label.SetLabel(f"STATUS ON {current_datetime}")
    
    def _on_git_repo_click(self, event):
        """Handle click on git repository label - copy URL to clipboard"""
        if hasattr(self, 'git_remote_url') and self.git_remote_url:
            try:
                # Copy to clipboard
                if wx.TheClipboard.Open():
                    wx.TheClipboard.SetData(wx.TextDataObject(self.git_remote_url))
                    wx.TheClipboard.Close()
                    
                    # Show a temporary notification
                    wx.MessageBox(
                        f"✅ GitHub URL copied to clipboard!\n\n{self.git_remote_url}",
                        "URL Copied",
                        wx.OK | wx.ICON_INFORMATION
                    )
            except Exception as e:
                wx.MessageBox(
                    f"❌ Failed to copy URL to clipboard: {e}",
                    "Copy Failed",
                    wx.OK | wx.ICON_ERROR
                )
    
    def on_clear_output(self, event):
        """Clear the output console"""
        self.output_text.Clear()
    
    def on_show_settings(self, event):
        """Show settings dialog"""
        # Create custom settings dialog
        dlg = wx.Dialog(
            self,
            title="⚙️ TermTools Settings",
            size=wx.Size(400, 400),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        
        # Apply dark theme
        dlg.SetBackgroundColour(DarkTheme.MAIN_BG)
        
        # Create main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title = wx.StaticText(dlg, label="Application Settings")
        title_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title.SetFont(title_font)
        title.SetForegroundColour(DarkTheme.TEXT_PRIMARY)
        title.SetBackgroundColour(DarkTheme.MAIN_BG)
        sizer.Add(title, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 15)
        
        # Update section
        update_panel = wx.Panel(dlg)
        update_panel.SetBackgroundColour(DarkTheme.PANEL_BG)
        update_sizer = wx.BoxSizer(wx.VERTICAL)
        
        update_label = wx.StaticText(update_panel, label="🔄 Update TermTools")
        update_label.SetForegroundColour(DarkTheme.TEXT_ACCENT)
        update_label.SetBackgroundColour(DarkTheme.PANEL_BG)
        update_sizer.Add(update_label, 0, wx.ALL, 10)
        
        update_desc = wx.StaticText(
            update_panel, 
            label="Download and install the latest version of TermTools.\nThis will require administrator privileges."
        )
        update_desc.SetForegroundColour(DarkTheme.TEXT_SECONDARY)
        update_desc.SetBackgroundColour(DarkTheme.PANEL_BG)
        update_sizer.Add(update_desc, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # Check for updates button
        check_update_button = wx.Button(update_panel, label="🔍 Check for Updates", size=wx.Size(-1, 35))
        self._style_button(check_update_button, text_colour=DarkTheme.TEXT_ACCENT)
        check_update_button.Bind(wx.EVT_BUTTON, lambda evt: self._on_check_for_updates(update_panel))
        update_sizer.Add(check_update_button, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # Update status label (initially hidden)
        self.update_status_label = wx.StaticText(update_panel, label="")
        self.update_status_label.SetForegroundColour(DarkTheme.TEXT_SECONDARY)
        self.update_status_label.SetBackgroundColour(DarkTheme.PANEL_BG)
        update_sizer.Add(self.update_status_label, 0, wx.LEFT | wx.RIGHT, 10)
        
        # Update button
        update_button = wx.Button(update_panel, label="🚀 Update Now", size=wx.Size(-1, 35))
        self._style_button(update_button, text_colour=DarkTheme.TEXT_SUCCESS)
        update_button.Bind(wx.EVT_BUTTON, lambda evt: self._on_update_termtools(dlg))
        update_sizer.Add(update_button, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        update_panel.SetSizer(update_sizer)
        sizer.Add(update_panel, 1, wx.EXPAND | wx.ALL, 10)
        
        # Close button
        close_button = wx.Button(dlg, label="Close", size=wx.Size(-1, 35))
        self._style_button(close_button)
        close_button.Bind(wx.EVT_BUTTON, lambda evt: dlg.EndModal(wx.ID_CANCEL))
        sizer.Add(close_button, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        dlg.SetSizer(sizer)
        
        # Apply dark theme to all children
        def apply_dark_theme_to_children(parent):
            for child in parent.GetChildren():
                if isinstance(child, wx.StaticText):
                    child.SetBackgroundColour(DarkTheme.MAIN_BG)
                    child.SetForegroundColour(DarkTheme.TEXT_PRIMARY)
                elif isinstance(child, wx.Button):
                    child.SetBackgroundColour(DarkTheme.BUTTON_BG)
                    child.SetForegroundColour(DarkTheme.TEXT_PRIMARY)
                elif isinstance(child, wx.Panel):
                    child.SetBackgroundColour(DarkTheme.PANEL_BG)
                apply_dark_theme_to_children(child)
        
        apply_dark_theme_to_children(dlg)
        dlg.Refresh()
        
        dlg.ShowModal()
        dlg.Destroy()
    
    def _on_update_termtools(self, parent_dialog):
        """Handle the update TermTools button click"""
        # Close the settings dialog first
        parent_dialog.EndModal(wx.ID_CANCEL)
        
        # Show confirmation dialog
        confirm_dlg = wx.MessageDialog(
            self,
            "This will download and install the latest version of TermTools.\n\n"
            "• Administrator privileges will be requested\n"
            "• The application may restart automatically\n"
            "• Your current session will be preserved\n\n"
            "Continue with the update?",
            "Confirm Update",
            wx.YES_NO | wx.ICON_QUESTION
        )
        
        if confirm_dlg.ShowModal() == wx.ID_YES:
            confirm_dlg.Destroy()
            
            # Run the update in a separate thread to avoid blocking the GUI
            import threading
            update_thread = threading.Thread(target=self._perform_update)
            update_thread.daemon = True
            update_thread.start()
        else:
            confirm_dlg.Destroy()
    
    def _perform_update(self):
        """Perform the actual update operation"""
        try:
            # Import here to avoid circular imports
            import subprocess
            
            # The PowerShell command for updating
            command = (
                "$u='https://raw.githubusercontent.com/aseshbasu-dev/termtools/refs/heads/main/install_start.ps1'; "
                "$f=Join-Path $env:TEMP 'bootstrap_and_run.ps1'; "
                "Invoke-WebRequest -Uri $u -OutFile $f -UseBasicParsing; "
                "Start-Process -FilePath 'powershell' -Verb RunAs -ArgumentList \"-NoProfile -ExecutionPolicy Bypass -File `\"$f`\"\""
            )
            
            # Show progress in output
            wx.CallAfter(self._append_output, "🔄 Starting TermTools update...\n")
            wx.CallAfter(self._append_output, "📥 Downloading latest installer...\n")
            
            # Run the PowerShell command
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                check=True,
                **get_subprocess_creation_flags()
            )
            
            wx.CallAfter(self._append_output, "✅ Update process initiated successfully!\n")
            wx.CallAfter(self._append_output, "💡 The installer will run with administrator privileges.\n")
            wx.CallAfter(self._append_output, "🔄 Please restart TermTools to complete the update process.\n")
            
            # Show any output from the command
            if result.stdout:
                wx.CallAfter(self._append_output, f"Output: {result.stdout.strip()}\n")
            if result.stderr:
                wx.CallAfter(self._append_output, f"Warnings: {result.stderr.strip()}\n")
                
        except subprocess.CalledProcessError as e:
            wx.CallAfter(self._append_output, f"❌ Update failed to initiate: {e}\n")
            if e.stderr:
                wx.CallAfter(self._append_output, f"   Error details: {e.stderr.strip()}\n")
            wx.CallAfter(self._append_output, "💡 Make sure you have internet connection and administrator privileges.\n")
        except FileNotFoundError:
            wx.CallAfter(self._append_output, "❌ PowerShell not found. This feature requires Windows PowerShell.\n")
        except Exception as e:
            wx.CallAfter(self._append_output, f"❌ Unexpected error during update: {e}\n")
    
    def _on_check_for_updates(self, update_panel):
        """Handle the check for updates button click"""
        # Update status to show checking
        wx.CallAfter(self._update_status_label, "🔍 Checking for updates...", DarkTheme.TEXT_ACCENT)
        
        # Run the update check in a separate thread to avoid blocking the GUI
        import threading
        check_thread = threading.Thread(target=self._perform_update_check)
        check_thread.daemon = True
        check_thread.start()
    
    def _perform_update_check(self):
        """Perform the actual update check operation"""
        try:
            local_hash = self._get_local_installation_hash()
            remote_hash = self._get_remote_repository_hash()
            
            if not remote_hash:
                wx.CallAfter(self._update_status_label, 
                           "❌ Unable to check for updates (network error)", 
                           DarkTheme.TEXT_ERROR)
                return
            
            if not local_hash:
                wx.CallAfter(self._update_status_label, 
                           "⚠️ No local installation info found", 
                           DarkTheme.TEXT_WARNING)
                wx.CallAfter(self._append_output, 
                           "💡 This appears to be a development installation.\n")
                return
            
            # Compare hashes (first 8 characters for display)
            local_short = local_hash[:8] if local_hash else "unknown"
            remote_short = remote_hash[:8] if remote_hash else "unknown"
            
            if local_hash == remote_hash:
                wx.CallAfter(self._update_status_label, 
                           f"✅ Up to date (version: {local_short})", 
                           DarkTheme.TEXT_SUCCESS)
                wx.CallAfter(self._append_output, 
                           f"✅ TermTools is up to date! Local: {local_short}, Remote: {remote_short}\n")
            else:
                wx.CallAfter(self._update_status_label, 
                           f"🔄 Update available! Local: {local_short} → Remote: {remote_short}", 
                           DarkTheme.TEXT_WARNING)
                wx.CallAfter(self._append_output, 
                           f"🔄 Update available!\n"
                           f"   Current version: {local_short}\n"
                           f"   Latest version:  {remote_short}\n"
                           f"💡 Click 'Update Now' to install the latest version.\n")
                
        except Exception as e:
            wx.CallAfter(self._update_status_label, 
                       f"❌ Error checking for updates: {str(e)}", 
                       DarkTheme.TEXT_ERROR)
            wx.CallAfter(self._append_output, f"❌ Error checking for updates: {e}\n")
    
    def _get_local_installation_hash(self):
        """Get the local installation commit hash from installation_info.json"""
        try:
            import json
            import os
            
            # Check the installed location from Program Files ONLY
            # This ensures we always check the actual installed version
            installed_path = r"C:\Program Files\BasusTools\TermTools\core\data\installation_info.json"
            
            if not os.path.exists(installed_path):
                print(f"❌ Installation info not found at: {installed_path}")
                print("💡 TermTools must be installed via the installer to use update checks.")
                return None
            
            with open(installed_path, 'r') as f:
                metadata = json.load(f)
                commit_hash = metadata.get("remote_commit_hash")
                if not commit_hash:
                    print("⚠️ Installation info exists but contains no commit hash.")
                return commit_hash
                
        except Exception as e:
            print(f"❌ Error reading local installation info: {e}")
            return None
    
    def _get_remote_repository_hash(self):
        """Get the latest commit hash from GitHub API"""
        try:
            import urllib.request
            import json
            
            # GitHub API URL for latest commit
            url = "https://api.github.com/repos/aseshbasu-dev/termtools/commits/main"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data["sha"]
                
        except Exception as e:
            print(f"Warning: Could not fetch remote commit hash: {e}")
            return None
    
    def _update_status_label(self, text, color):
        """Update the status label text and color"""
        if hasattr(self, 'update_status_label'):
            self.update_status_label.SetLabel(text)
            self.update_status_label.SetForegroundColour(color)
            self.update_status_label.GetParent().Layout()  # Refresh layout
    
    def _append_output(self, text):
        """Append text to the output console"""
        current_text = self.output_text.GetValue()
        self.output_text.SetValue(current_text + text)
        # Auto-scroll to bottom
        self.output_text.ShowPosition(self.output_text.GetLastPosition())

    def on_show_help(self, event):
        """Show help dialog"""
        with redirect_stdout(self.stdout_redirector), redirect_stderr(self.stderr_redirector):
            self.app.show_help()
    
    def on_exit(self, event):
        """Exit the application"""
        dlg = wx.MessageDialog(
            self,
            "Are you sure you want to exit TermTools?",
            "Confirm Exit",
            wx.YES_NO | wx.ICON_QUESTION
        )
        
        if dlg.ShowModal() == wx.ID_YES:
            self._cleanup_on_exit()
            self.Close()
        
        dlg.Destroy()
    
    def on_window_close(self, event):
        """Handle window close event (X button)"""
        # Check if Pomodoro timer is open
        from .modules.pomodoro import PomodoroTimer
        
        if PomodoroTimer._instance is not None and PomodoroTimer._instance.IsShown():
            # Ask user what to do
            dlg = wx.MessageDialog(
                self,
                "Pomodoro timer is still running.\n\n"
                "Do you want to close everything?\n\n"
                "• Click 'Yes' to close everything (including timer)\n"
                "• Click 'No' to hide main window and keep timer running\n"
                "• Click 'Cancel' to return to TermTools",
                "Pomodoro Timer Running",
                wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION | wx.NO_DEFAULT
            )
            
            result = dlg.ShowModal()
            dlg.Destroy()
            
            if result == wx.ID_YES:
                # Close everything and exit app
                if PomodoroTimer._instance:
                    PomodoroTimer._instance.Close()
                self._cleanup_on_exit()
                self.Destroy()
                # Exit the application
                wx.GetApp().ExitMainLoop()
            elif result == wx.ID_NO:
                # Hide main window, keep timer running
                print("💡 Main window hidden. Pomodoro timer continues running.")
                print("   (Close the Pomodoro timer to exit the application)")
                self.Hide()
                # Veto the close event to keep the frame alive but hidden
                event.Veto()
            else:
                # Cancel - veto the close
                event.Veto()
        else:
            # No timer running, close everything and exit
            self._cleanup_on_exit()
            self.Destroy()
            wx.GetApp().ExitMainLoop()
    
    def _cleanup_on_exit(self):
        """Cleanup and log session end"""
        from datetime import datetime
        
        # Write session end to log
        if hasattr(self, 'log_file_path') and self.log_file_path:
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write("\n")
                    f.write("="*80 + "\n")
                    f.write(f"Session ended - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*80 + "\n")
                    f.write("\n")
            except Exception:
                pass  # Silently fail
        
        # Restore original stdout/stderr
        if hasattr(self, 'stdout_redirector') and hasattr(self.stdout_redirector, 'original_stdout'):
            sys.stdout = self.stdout_redirector.original_stdout
        if hasattr(self, 'stderr_redirector') and hasattr(self.stderr_redirector, 'original_stderr'):
            sys.stderr = self.stderr_redirector.original_stderr


class TermToolsWxApp(wx.App):

    """wxPython application class for TermTools"""
    
    def OnInit(self):
        """Initialize the application"""
        # Don't exit when last window closes - we manage this manually
        self.SetExitOnFrameDelete(False)
        
        self.frame = TermToolsFrame()
        self.frame.Show()
        return True
    
    def OnExit(self):
        """Called when application is about to exit"""
        return 0


def run_wx_app():
    """Entry point for wxPython GUI"""
    app = TermToolsWxApp(redirect=False)
    app.MainLoop()
