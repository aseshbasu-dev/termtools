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
import threading
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, List
from .app import TermTools


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
    """Redirects stdout/stderr to a wx.TextCtrl"""
    
    def __init__(self, text_ctrl):
        self.text_ctrl = text_ctrl
        self.buffer = io.StringIO()
        
    def write(self, text):
        """Write text to the text control"""
        wx.CallAfter(self._append_text, text)
        
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
            title="TermTools - Python Project Manager",
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

        main_panel.SetSizer(main_sizer)        # Setup output redirection
        self.stdout_redirector = OutputRedirector(self.output_text)
        self.stderr_redirector = OutputRedirector(self.output_text)
        
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
        
        # Current directory
        dir_label = wx.StaticText(panel, label=f"📁 {self.current_dir}")
        dir_label.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        dir_label.SetForegroundColour(DarkTheme.TEXT_MUTED)
        dir_label.SetBackgroundColour(DarkTheme.HEADER_BG)
        sizer.Add(dir_label, 0, wx.ALIGN_CENTER | wx.BOTTOM, 5)
        
        # Shutdown status indicator
        self.shutdown_status_label = wx.StaticText(panel, label="")
        shutdown_font = wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.shutdown_status_label.SetFont(shutdown_font)
        self.shutdown_status_label.SetForegroundColour(DarkTheme.TEXT_ERROR)
        self.shutdown_status_label.SetBackgroundColour(DarkTheme.HEADER_BG)
        sizer.Add(self.shutdown_status_label, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        # Update shutdown status on initial load
        self._update_shutdown_status()
        
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
        
        # Help button
        help_button = wx.Button(parent, label="❓ Show Help", size=(-1, 35))
        self._style_button(help_button, text_colour=DarkTheme.CATEGORY_HELP)
        help_button.Bind(wx.EVT_BUTTON, self.on_show_help)
        self.button_sizer.Add(help_button, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        # Exit button
        exit_button = wx.Button(parent, label="❌ Exit", size=(-1, 35))
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
                        subprocess.run(['shutdown', '/s', '/t', str(minutes * 60)], check=True)
                        print(f"✅ Shutdown scheduled successfully!")
                        print(f"🕒 System will shutdown in {description}")
                        print(f"💡 Use 'shutdown /a' in command prompt to cancel")
                    else:  # Unix-like systems
                        subprocess.run(['sudo', 'shutdown', '-h', f"+{minutes}"], check=True)
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
                        result = subprocess.run(['shutdown', '/a'], capture_output=True, text=True)
                        if result.returncode == 0:
                            print("✅ Shutdown cancelled successfully!")
                        else:
                            print("ℹ️  No shutdown was scheduled or shutdown already cancelled.")
                    else:  # Unix-like systems
                        result = subprocess.run(['sudo', 'shutdown', '-c'], capture_output=True, text=True)
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
                        # Time has passed, clear status
                        self.shutdown_status_label.SetLabel("")
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
                    
                    self.shutdown_status_label.SetLabel(f"⚠️ SHUTDOWN SCHEDULED FOR {time_str}")
                else:
                    self.shutdown_status_label.SetLabel("")
            else:
                self.shutdown_status_label.SetLabel("")
        except Exception as e:
            # Silently handle errors to avoid disrupting the UI
            pass
    
    def on_status_timer(self, event):
        """Timer event handler for updating shutdown status"""
        self._update_shutdown_status()
    
    def on_clear_output(self, event):
        """Clear the output console"""
        self.output_text.Clear()
    
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
            self.Close()
        
        dlg.Destroy()


class TermToolsWxApp(wx.App):
    """wxPython application class for TermTools"""
    
    def OnInit(self):
        """Initialize the application"""
        self.frame = TermToolsFrame()
        self.frame.Show()
        return True


def run_wx_app():
    """Entry point for wxPython GUI"""
    app = TermToolsWxApp(redirect=False)
    app.MainLoop()
