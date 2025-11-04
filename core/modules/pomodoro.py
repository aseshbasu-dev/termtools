"""
Pomodoro Timer Module for TermTools
Built by Asesh Basu

This module provides a comprehensive Pomodoro timer with work/break sessions,
customizable time intervals, and statistics tracking. The timer runs in a
separate window and automatically loops through work and break periods.
"""

import wx
import json
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
from ..blueprint import Blueprint

# Create the blueprint for pomodoro timer
pomodoro_bp = Blueprint("pomodoro", "Pomodoro timer for productivity management")


class PomodoroStats:
    """Manage Pomodoro statistics and persistence"""
    
    def __init__(self):
        self.stats_file = Path("core/data/pomodoro_stats.json")
        self._ensure_stats_file()
    
    def _ensure_stats_file(self):
        """Ensure stats file exists with default structure"""
        if not self.stats_file.exists():
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            default_stats = {
                "total_work_sessions": 0,
                "total_work_minutes": 0,
                "total_break_minutes": 0,
                "sessions_by_date": {},
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self._save_stats(default_stats)
    
    def _load_stats(self):
        """Load statistics from file"""
        try:
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading stats: {e}")
            return {}
    
    def _save_stats(self, stats):
        """Save statistics to file"""
        try:
            stats["last_updated"] = datetime.now().isoformat()
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving stats: {e}")
    
    def record_work_session(self, minutes):
        """Record a completed work session"""
        stats = self._load_stats()
        stats["total_work_sessions"] = stats.get("total_work_sessions", 0) + 1
        stats["total_work_minutes"] = stats.get("total_work_minutes", 0) + minutes
        
        # Track by date
        today = datetime.now().strftime("%Y-%m-%d")
        if "sessions_by_date" not in stats:
            stats["sessions_by_date"] = {}
        
        if today not in stats["sessions_by_date"]:
            stats["sessions_by_date"][today] = {
                "work_sessions": 0,
                "work_minutes": 0,
                "break_minutes": 0
            }
        
        stats["sessions_by_date"][today]["work_sessions"] += 1
        stats["sessions_by_date"][today]["work_minutes"] += minutes
        
        self._save_stats(stats)
    
    def record_break_session(self, minutes):
        """Record a completed break session"""
        stats = self._load_stats()
        stats["total_break_minutes"] = stats.get("total_break_minutes", 0) + minutes
        
        # Track by date
        today = datetime.now().strftime("%Y-%m-%d")
        if "sessions_by_date" not in stats:
            stats["sessions_by_date"] = {}
        
        if today not in stats["sessions_by_date"]:
            stats["sessions_by_date"][today] = {
                "work_sessions": 0,
                "work_minutes": 0,
                "break_minutes": 0
            }
        
        stats["sessions_by_date"][today]["break_minutes"] += minutes
        
        self._save_stats(stats)
    
    def get_stats(self):
        """Get current statistics"""
        return self._load_stats()
    
    def get_today_stats(self):
        """Get today's statistics"""
        stats = self._load_stats()
        today = datetime.now().strftime("%Y-%m-%d")
        
        if "sessions_by_date" in stats and today in stats["sessions_by_date"]:
            return stats["sessions_by_date"][today]
        
        return {
            "work_sessions": 0,
            "work_minutes": 0,
            "break_minutes": 0
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        default_stats = {
            "total_work_sessions": 0,
            "total_work_minutes": 0,
            "total_break_minutes": 0,
            "sessions_by_date": {},
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        self._save_stats(default_stats)


class PomodoroTimer(wx.Frame):
    """Pomodoro timer window with work/break sessions"""
    
    # Class variable to track if an instance is already open
    _instance = None
    
    def __init__(self, parent=None):
        # Prevent multiple instances
        if PomodoroTimer._instance is not None:
            # Bring existing window to front
            if PomodoroTimer._instance.IsShown():
                PomodoroTimer._instance.Raise()
                PomodoroTimer._instance.RequestUserAttention()
                return
        
        super().__init__(
            parent,
            title="🍅 Pomodoro Timer",
            size=(500, 700),
            style=wx.DEFAULT_FRAME_STYLE
        )
        
        # Set this instance as the active one
        PomodoroTimer._instance = self
        
        self.stats_manager = PomodoroStats()
        
        # Timer state
        self.is_running = False
        self.is_paused = False
        self.current_phase = "work"  # "work" or "break"
        self.work_minutes = 25
        self.break_minutes = 5
        self.time_remaining = 0
        self.session_count = 0
        
        # Timer thread
        self.timer_thread = None
        self.stop_event = threading.Event()
        
        # Apply dark theme
        from ..wx_app import DarkTheme
        self.theme = DarkTheme
        self.SetBackgroundColour(self.theme.MAIN_BG)
        
        self._create_ui()
        self.Centre()
        
        # Bind close event to stop timer thread and clean up
        self.Bind(wx.EVT_CLOSE, self.on_close)
    
    def _create_ui(self):
        """Create the user interface"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title section
        title_panel = wx.Panel(self)
        title_panel.SetBackgroundColour(self.theme.HEADER_BG)
        title_sizer = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticText(title_panel, label="🍅 POMODORO TIMER")
        title_font = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        title_label.SetFont(title_font)
        title_label.SetForegroundColour(self.theme.TEXT_PRIMARY)
        title_label.SetBackgroundColour(self.theme.HEADER_BG)
        title_sizer.Add(title_label, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        subtitle_label = wx.StaticText(title_panel, label="Focus • Work • Achieve")
        subtitle_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL)
        subtitle_label.SetFont(subtitle_font)
        subtitle_label.SetForegroundColour(self.theme.TEXT_ACCENT)
        subtitle_label.SetBackgroundColour(self.theme.HEADER_BG)
        title_sizer.Add(subtitle_label, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        
        title_panel.SetSizer(title_sizer)
        main_sizer.Add(title_panel, 0, wx.EXPAND)
        
        # Configuration section
        config_panel = wx.Panel(self)
        config_panel.SetBackgroundColour(self.theme.PANEL_BG)
        config_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Section title
        config_title = wx.StaticText(config_panel, label="⚙️ Session Configuration")
        config_title_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        config_title.SetFont(config_title_font)
        config_title.SetForegroundColour(self.theme.TEXT_PRIMARY)
        config_title.SetBackgroundColour(self.theme.PANEL_BG)
        config_sizer.Add(config_title, 0, wx.ALL, 10)
        
        # Work time selection
        work_box = wx.BoxSizer(wx.HORIZONTAL)
        work_label = wx.StaticText(config_panel, label="Work Time:")
        work_label.SetForegroundColour(self.theme.TEXT_PRIMARY)
        work_label.SetBackgroundColour(self.theme.PANEL_BG)
        work_box.Add(work_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        work_choices = ["5 min", "10 min", "15 min", "20 min", "25 min", "30 min", "35 min", "40 min", "45 min", "Custom"]
        self.work_choice = wx.Choice(config_panel, choices=work_choices)
        self.work_choice.SetSelection(4)  # Default 25 min
        self.work_choice.SetBackgroundColour(self.theme.BUTTON_BG)
        self.work_choice.SetForegroundColour(self.theme.TEXT_PRIMARY)
        self.work_choice.Bind(wx.EVT_CHOICE, self.on_work_choice)
        work_box.Add(self.work_choice, 1, wx.EXPAND)
        
        config_sizer.Add(work_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # Break time selection
        break_box = wx.BoxSizer(wx.HORIZONTAL)
        break_label = wx.StaticText(config_panel, label="Break Time:")
        break_label.SetForegroundColour(self.theme.TEXT_PRIMARY)
        break_label.SetBackgroundColour(self.theme.PANEL_BG)
        break_box.Add(break_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        break_choices = ["5 min", "10 min", "15 min", "20 min", "25 min", "30 min", "35 min", "40 min", "45 min", "Custom"]
        self.break_choice = wx.Choice(config_panel, choices=break_choices)
        self.break_choice.SetSelection(0)  # Default 5 min
        self.break_choice.SetBackgroundColour(self.theme.BUTTON_BG)
        self.break_choice.SetForegroundColour(self.theme.TEXT_PRIMARY)
        self.break_choice.Bind(wx.EVT_CHOICE, self.on_break_choice)
        break_box.Add(self.break_choice, 1, wx.EXPAND)
        
        config_sizer.Add(break_box, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        config_panel.SetSizer(config_sizer)
        main_sizer.Add(config_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        # Timer display section
        timer_panel = wx.Panel(self)
        timer_panel.SetBackgroundColour(self.theme.CONSOLE_BG)
        timer_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Current phase label
        self.phase_label = wx.StaticText(timer_panel, label="Ready to Start")
        phase_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.phase_label.SetFont(phase_font)
        self.phase_label.SetForegroundColour(self.theme.TEXT_ACCENT)
        self.phase_label.SetBackgroundColour(self.theme.CONSOLE_BG)
        timer_sizer.Add(self.phase_label, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        
        # Time display
        self.time_label = wx.StaticText(timer_panel, label="25:00")
        time_font = wx.Font(48, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.time_label.SetFont(time_font)
        self.time_label.SetForegroundColour(self.theme.TEXT_PRIMARY)
        self.time_label.SetBackgroundColour(self.theme.CONSOLE_BG)
        timer_sizer.Add(self.time_label, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 30)
        
        # Session counter
        self.session_label = wx.StaticText(timer_panel, label="Sessions Completed: 0")
        session_font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.session_label.SetFont(session_font)
        self.session_label.SetForegroundColour(self.theme.TEXT_SECONDARY)
        self.session_label.SetBackgroundColour(self.theme.CONSOLE_BG)
        timer_sizer.Add(self.session_label, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)
        
        timer_panel.SetSizer(timer_sizer)
        main_sizer.Add(timer_panel, 1, wx.EXPAND | wx.ALL, 5)
        
        # Control buttons
        button_panel = wx.Panel(self)
        button_panel.SetBackgroundColour(self.theme.PANEL_BG)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.start_button = wx.Button(button_panel, label="▶ Start", size=(100, 35))
        self._style_button(self.start_button, self.theme.ACCENT_PRIMARY)
        self.start_button.Bind(wx.EVT_BUTTON, self.on_start)
        button_sizer.Add(self.start_button, 0, wx.ALL, 5)
        
        self.pause_button = wx.Button(button_panel, label="⏸ Pause", size=(100, 35))
        self._style_button(self.pause_button)
        self.pause_button.Enable(False)
        self.pause_button.Bind(wx.EVT_BUTTON, self.on_pause)
        button_sizer.Add(self.pause_button, 0, wx.ALL, 5)
        
        self.stop_button = wx.Button(button_panel, label="⏹ Stop", size=(100, 35))
        self._style_button(self.stop_button)
        self.stop_button.Enable(False)
        self.stop_button.Bind(wx.EVT_BUTTON, self.on_stop)
        button_sizer.Add(self.stop_button, 0, wx.ALL, 5)
        
        self.reset_button = wx.Button(button_panel, label="🔄 Reset", size=(100, 35))
        self._style_button(self.reset_button)
        self.reset_button.Bind(wx.EVT_BUTTON, self.on_reset)
        button_sizer.Add(self.reset_button, 0, wx.ALL, 5)
        
        button_panel.SetSizer(button_sizer)
        main_sizer.Add(button_panel, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Statistics section
        stats_panel = wx.Panel(self)
        stats_panel.SetBackgroundColour(self.theme.SIDEBAR_BG)
        stats_sizer = wx.BoxSizer(wx.VERTICAL)
        
        stats_title = wx.StaticText(stats_panel, label="📊 Statistics")
        stats_title_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        stats_title.SetFont(stats_title_font)
        stats_title.SetForegroundColour(self.theme.TEXT_PRIMARY)
        stats_title.SetBackgroundColour(self.theme.SIDEBAR_BG)
        stats_sizer.Add(stats_title, 0, wx.ALL, 10)
        
        # Stats display
        self.stats_text = wx.TextCtrl(
            stats_panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
            size=(-1, 120)
        )
        self.stats_text.SetBackgroundColour(self.theme.CONSOLE_BG)
        self.stats_text.SetForegroundColour(self.theme.CONSOLE_TEXT)
        self.stats_text.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        stats_sizer.Add(self.stats_text, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # Stats buttons
        stats_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        view_stats_button = wx.Button(stats_panel, label="📈 View All Stats", size=(150, 30))
        self._style_button(view_stats_button)
        view_stats_button.Bind(wx.EVT_BUTTON, self.on_view_stats)
        stats_button_sizer.Add(view_stats_button, 0, wx.ALL, 5)
        
        reset_stats_button = wx.Button(stats_panel, label="🗑️ Reset Stats", size=(150, 30))
        self._style_button(reset_stats_button, self.theme.TEXT_ERROR)
        reset_stats_button.Bind(wx.EVT_BUTTON, self.on_reset_stats)
        stats_button_sizer.Add(reset_stats_button, 0, wx.ALL, 5)
        
        stats_sizer.Add(stats_button_sizer, 0, wx.ALIGN_CENTER)
        
        stats_panel.SetSizer(stats_sizer)
        main_sizer.Add(stats_panel, 0, wx.EXPAND | wx.ALL, 5)
        
        # Add a button to show main window if hidden
        show_main_panel = wx.Panel(self)
        show_main_panel.SetBackgroundColour(self.theme.MAIN_BG)
        show_main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.show_main_button = wx.Button(show_main_panel, label="🏠 Show TermTools Main Window", size=(-1, 35))
        self._style_button(self.show_main_button, self.theme.ACCENT_SECONDARY)
        self.show_main_button.Bind(wx.EVT_BUTTON, self.on_show_main_window)
        show_main_sizer.Add(self.show_main_button, 1, wx.EXPAND | wx.ALL, 5)
        
        show_main_panel.SetSizer(show_main_sizer)
        main_sizer.Add(show_main_panel, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        
        # Update displays
        self._update_stats_display()
        self._update_time_display()
        
        self.SetSizer(main_sizer)
        self.Layout()  # Force layout update
    
    def _style_button(self, button, color=None):
        """Apply styling to a button"""
        if color is None:
            color = self.theme.BUTTON_BG
        
        button.SetBackgroundColour(color)
        button.SetForegroundColour(self.theme.BUTTON_TEXT)
        
        # Add hover effects
        default_bg = color
        hover_bg = self.theme.ACCENT_TERTIARY
        hover_fg = self.theme.TEXT_DARK
        
        def on_enter(event):
            button.SetBackgroundColour(hover_bg)
            button.SetForegroundColour(hover_fg)
            button.Refresh()
            event.Skip()
        
        def on_leave(event):
            button.SetBackgroundColour(default_bg)
            button.SetForegroundColour(self.theme.BUTTON_TEXT)
            button.Refresh()
            event.Skip()
        
        button.Bind(wx.EVT_ENTER_WINDOW, on_enter)
        button.Bind(wx.EVT_LEAVE_WINDOW, on_leave)
    
    def on_work_choice(self, event):
        """Handle work time selection"""
        selection = self.work_choice.GetStringSelection()
        
        if selection == "Custom":
            dlg = wx.TextEntryDialog(
                self,
                "Enter custom work time (minutes):",
                "Custom Work Time",
                "25"
            )
            
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    minutes = int(dlg.GetValue())
                    if 1 <= minutes <= 180:
                        self.work_minutes = minutes
                        if not self.is_running:
                            self._update_time_display()
                    else:
                        wx.MessageBox(
                            "Please enter a value between 1 and 180 minutes.",
                            "Invalid Input",
                            wx.OK | wx.ICON_ERROR
                        )
                        self.work_choice.SetSelection(4)  # Reset to 25 min
                except ValueError:
                    wx.MessageBox(
                        "Please enter a valid number.",
                        "Invalid Input",
                        wx.OK | wx.ICON_ERROR
                    )
                    self.work_choice.SetSelection(4)  # Reset to 25 min
            else:
                self.work_choice.SetSelection(4)  # Reset to 25 min
            
            dlg.Destroy()
        else:
            self.work_minutes = int(selection.split()[0])
            if not self.is_running:
                self._update_time_display()
    
    def on_break_choice(self, event):
        """Handle break time selection"""
        selection = self.break_choice.GetStringSelection()
        
        if selection == "Custom":
            dlg = wx.TextEntryDialog(
                self,
                "Enter custom break time (minutes):",
                "Custom Break Time",
                "5"
            )
            
            if dlg.ShowModal() == wx.ID_OK:
                try:
                    minutes = int(dlg.GetValue())
                    if 1 <= minutes <= 60:
                        self.break_minutes = minutes
                    else:
                        wx.MessageBox(
                            "Please enter a value between 1 and 60 minutes.",
                            "Invalid Input",
                            wx.OK | wx.ICON_ERROR
                        )
                        self.break_choice.SetSelection(0)  # Reset to 5 min
                except ValueError:
                    wx.MessageBox(
                        "Please enter a valid number.",
                        "Invalid Input",
                        wx.OK | wx.ICON_ERROR
                    )
                    self.break_choice.SetSelection(0)  # Reset to 5 min
            else:
                self.break_choice.SetSelection(0)  # Reset to 5 min
            
            dlg.Destroy()
        else:
            self.break_minutes = int(selection.split()[0])
    
    def on_start(self, event):
        """Start the Pomodoro timer"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            
            # Set initial time if first start
            if self.time_remaining == 0:
                self.current_phase = "work"
                self.time_remaining = self.work_minutes * 60
                self._update_phase_label()
            
            # Update button states
            self.start_button.Enable(False)
            self.pause_button.Enable(True)
            self.stop_button.Enable(True)
            self.work_choice.Enable(False)
            self.break_choice.Enable(False)
            
            # Start timer thread
            self.stop_event.clear()
            self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
            self.timer_thread.start()
    
    def on_pause(self, event):
        """Pause/resume the timer"""
        if self.is_paused:
            # Resume
            self.is_paused = False
            self.pause_button.SetLabel("⏸ Pause")
        else:
            # Pause
            self.is_paused = True
            self.pause_button.SetLabel("▶ Resume")
    
    def on_stop(self, event):
        """Stop the timer"""
        self.stop_event.set()
        self.is_running = False
        self.is_paused = False
        self.time_remaining = 0
        
        # Update UI
        self.start_button.Enable(True)
        self.pause_button.Enable(False)
        self.stop_button.Enable(False)
        self.work_choice.Enable(True)
        self.break_choice.Enable(True)
        self.pause_button.SetLabel("⏸ Pause")
        
        self.phase_label.SetLabel("Ready to Start")
        self.phase_label.SetForegroundColour(self.theme.TEXT_ACCENT)
        self._update_time_display()
    
    def on_close(self, event):
        """Handle window close event - stop timer thread and clean up singleton"""
        # Stop the timer thread if running
        if self.is_running:
            self.stop_event.set()
            self.is_running = False
            
            # Wait for thread to finish (with timeout)
            if self.timer_thread and self.timer_thread.is_alive():
                self.timer_thread.join(timeout=1.0)
        
        # Clear the singleton instance
        PomodoroTimer._instance = None
        
        # Check if main window is hidden - if so, exit the app
        try:
            wx_app = wx.GetApp()
            if wx_app and hasattr(wx_app, 'frame'):
                main_frame = wx_app.frame
                if main_frame and not main_frame.IsShown():
                    # Main window is hidden, exit the application
                    print("✅ Pomodoro timer closed. Exiting TermTools.")
                    wx.CallAfter(wx_app.ExitMainLoop)
        except Exception:
            pass  # Silently fail if there are issues checking main window
        
        # Destroy the window
        self.Destroy()
    
    def on_reset(self, event):
        """Reset the timer and session count"""
        if self.is_running:
            dlg = wx.MessageDialog(
                self,
                "Timer is running. Stop it first?",
                "Timer Running",
                wx.YES_NO | wx.ICON_QUESTION
            )
            
            if dlg.ShowModal() == wx.ID_YES:
                self.on_stop(None)
            else:
                dlg.Destroy()
                return
            
            dlg.Destroy()
        
        self.session_count = 0
        self.current_phase = "work"
        self.time_remaining = 0
        
        self.session_label.SetLabel("Sessions Completed: 0")
        self.phase_label.SetLabel("Ready to Start")
        self.phase_label.SetForegroundColour(self.theme.TEXT_ACCENT)
        self._update_time_display()
    
    def on_view_stats(self, event):
        """View all statistics"""
        stats = self.stats_manager.get_stats()
        
        # Format stats for display
        stats_text = "="*40 + "\n"
        stats_text += "       📊 POMODORO STATISTICS\n"
        stats_text += "="*40 + "\n\n"
        
        stats_text += f"🎯 Total Work Sessions: {stats.get('total_work_sessions', 0)}\n"
        stats_text += f"⏱️ Total Work Time: {stats.get('total_work_minutes', 0)} minutes\n"
        stats_text += f"☕ Total Break Time: {stats.get('total_break_minutes', 0)} minutes\n\n"
        
        # Recent sessions by date
        sessions_by_date = stats.get('sessions_by_date', {})
        if sessions_by_date:
            stats_text += "📅 Recent Sessions by Date:\n"
            stats_text += "-"*40 + "\n"
            
            # Get last 7 days
            sorted_dates = sorted(sessions_by_date.keys(), reverse=True)[:7]
            for date in sorted_dates:
                day_stats = sessions_by_date[date]
                stats_text += f"\n{date}:\n"
                stats_text += f"  • Sessions: {day_stats.get('work_sessions', 0)}\n"
                stats_text += f"  • Work: {day_stats.get('work_minutes', 0)} min\n"
                stats_text += f"  • Break: {day_stats.get('break_minutes', 0)} min\n"
        
        # Show in dialog
        dlg = wx.MessageDialog(
            self,
            stats_text,
            "Pomodoro Statistics",
            wx.OK | wx.ICON_INFORMATION
        )
        dlg.ShowModal()
        dlg.Destroy()
    
    def on_show_main_window(self, event):
        """Show/restore the main TermTools window"""
        try:
            wx_app = wx.GetApp()
            if wx_app and hasattr(wx_app, 'frame'):
                main_frame = wx_app.frame
                if main_frame:
                    if not main_frame.IsShown():
                        main_frame.Show()
                        print("✅ Main window restored")
                    main_frame.Raise()
                    main_frame.RequestUserAttention()
        except Exception as e:
            wx.MessageBox(
                f"Could not show main window: {e}",
                "Error",
                wx.OK | wx.ICON_ERROR
            )
    
    def on_reset_stats(self, event):
        """Reset all statistics"""
        dlg = wx.MessageDialog(
            self,
            "Are you sure you want to reset all statistics?\nThis cannot be undone.",
            "Confirm Reset Statistics",
            wx.YES_NO | wx.ICON_WARNING | wx.NO_DEFAULT
        )
        
        if dlg.ShowModal() == wx.ID_YES:
            self.stats_manager.reset_stats()
            self._update_stats_display()
            wx.MessageBox(
                "Statistics have been reset successfully.",
                "Statistics Reset",
                wx.OK | wx.ICON_INFORMATION
            )
        
        dlg.Destroy()
    
    def _timer_loop(self):
        """Main timer loop running in separate thread"""
        while self.is_running and not self.stop_event.is_set():
            if not self.is_paused:
                if self.time_remaining > 0:
                    self.time_remaining -= 1
                    wx.CallAfter(self._update_time_display)
                    time.sleep(1)
                else:
                    # Session complete
                    wx.CallAfter(self._on_session_complete)
                    
                    # Auto-switch to next phase
                    if self.current_phase == "work":
                        self.current_phase = "break"
                        self.time_remaining = self.break_minutes * 60
                    else:
                        self.current_phase = "work"
                        self.time_remaining = self.work_minutes * 60
                    
                    wx.CallAfter(self._update_phase_label)
                    wx.CallAfter(self._update_time_display)
            else:
                time.sleep(0.1)  # Short sleep when paused
    
    def _on_session_complete(self):
        """Handle session completion"""
        if self.current_phase == "work":
            self.session_count += 1
            self.session_label.SetLabel(f"Sessions Completed: {self.session_count}")
            
            # Record work session in stats
            self.stats_manager.record_work_session(self.work_minutes)
            
            # Play notification
            wx.Bell()
            
            # Show notification
            wx.MessageBox(
                f"✅ Work session complete!\n\nTime for a {self.break_minutes} minute break.",
                "Pomodoro Complete",
                wx.OK | wx.ICON_INFORMATION
            )
        else:
            # Record break session in stats
            self.stats_manager.record_break_session(self.break_minutes)
            
            # Play notification
            wx.Bell()
            
            # Show notification
            wx.MessageBox(
                f"☕ Break complete!\n\nReady for the next {self.work_minutes} minute work session?",
                "Break Complete",
                wx.OK | wx.ICON_INFORMATION
            )
        
        # Update stats display
        self._update_stats_display()
    
    def _update_time_display(self):
        """Update the time display label"""
        # Check if widget still exists
        if not self.time_label or not self.time_label.IsShown():
            return
        
        try:
            if self.time_remaining == 0:
                # Show default time based on current phase
                if self.current_phase == "work":
                    minutes = self.work_minutes
                else:
                    minutes = self.break_minutes
                self.time_label.SetLabel(f"{minutes:02d}:00")
            else:
                minutes = self.time_remaining // 60
                seconds = self.time_remaining % 60
                self.time_label.SetLabel(f"{minutes:02d}:{seconds:02d}")
        except RuntimeError:
            # Widget has been deleted, stop trying to update
            pass
    
    def _update_phase_label(self):
        """Update the phase label"""
        # Check if widget still exists
        if not self.phase_label or not self.phase_label.IsShown():
            return
        
        try:
            if self.current_phase == "work":
                self.phase_label.SetLabel("🎯 WORK SESSION")
                self.phase_label.SetForegroundColour(self.theme.TEXT_SUCCESS)
            else:
                self.phase_label.SetLabel("☕ BREAK TIME")
                self.phase_label.SetForegroundColour(self.theme.ACCENT_PRIMARY)
        except RuntimeError:
            # Widget has been deleted, stop trying to update
            pass
    
    def _update_stats_display(self):
        """Update the stats text display"""
        # Check if widget still exists
        if not self.stats_text or not self.stats_text.IsShown():
            return
        
        try:
            today_stats = self.stats_manager.get_today_stats()
            all_stats = self.stats_manager.get_stats()
            
            stats_text = f"Today's Progress:\n"
            stats_text += f"  🎯 Work Sessions: {today_stats.get('work_sessions', 0)}\n"
            stats_text += f"  ⏱️  Work Time: {today_stats.get('work_minutes', 0)} min\n"
            stats_text += f"  ☕ Break Time: {today_stats.get('break_minutes', 0)} min\n\n"
            stats_text += f"All Time:\n"
            stats_text += f"  🎯 Total Sessions: {all_stats.get('total_work_sessions', 0)}\n"
            stats_text += f"  ⏱️  Total Work: {all_stats.get('total_work_minutes', 0)} min\n"
            
            self.stats_text.SetValue(stats_text)
        except RuntimeError:
            # Widget has been deleted, stop trying to update
            pass


@pomodoro_bp.route("13", "🍅 Pomodoro Timer", "Focus timer with work/break sessions", "🎯 PRODUCTIVITY", order=1)
def show_pomodoro_timer(app=None):
    """Show the Pomodoro timer window"""
    def show_frame():
        """Function to run on main thread"""
        try:
            # Check if an instance already exists
            if PomodoroTimer._instance is not None and PomodoroTimer._instance.IsShown():
                # Bring existing window to front
                PomodoroTimer._instance.Raise()
                PomodoroTimer._instance.RequestUserAttention()
                print("💡 Pomodoro timer is already open - bringing window to front")
                return
            
            # Create and show the Pomodoro timer as an independent window
            timer_frame = PomodoroTimer()
            timer_frame.Show()
            
            print("✅ Pomodoro timer window opened")
            
        except Exception as e:
            print(f"❌ Error showing Pomodoro timer: {e}")
            import traceback
            traceback.print_exc()
    
    # Use wx.CallAfter to ensure GUI operations happen on main thread
    wx.CallAfter(show_frame)
