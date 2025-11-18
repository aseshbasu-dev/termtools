"""
Pomodoro Timer Module for TermTools
Built by Asesh Basu

This module provides a comprehensive Pomodoro timer with work/break sessions,
customizable time intervals, and statistics tracking. The timer runs in a
separate window and automatically loops through work and break periods.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QComboBox, QTextEdit, QMessageBox, QInputDialog, QApplication
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
import json
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
import os
from ..blueprint import Blueprint

# Import platform-specific sound module
if os.name == 'nt':  # Windows
    import winsound
else:  # Unix/Linux/Mac
    try:
        import subprocess
    except ImportError:
        pass

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


class SoundNotifier:
    """Handle sound notifications for timer events"""
    
    @staticmethod
    def play_completion_sound(session_type="work"):
        """Play a completion sound notification"""
        try:
            if os.name == 'nt':  # Windows
                if session_type == "work":
                    frequencies = [523, 659, 784, 988, 1175]
                    for freq in frequencies:
                        winsound.Beep(freq, 250)
                        time.sleep(0.05)
                    winsound.Beep(1319, 500)
                else:
                    frequencies = [880, 698, 523]
                    for freq in frequencies:
                        winsound.Beep(freq, 350)
                        time.sleep(0.1)
            else:
                # Unix/Linux/Mac: Use system bell
                bell_count = 5 if session_type == "work" else 3
                for _ in range(bell_count):
                    QApplication.beep()
                    time.sleep(0.2)
                    
        except Exception as e:
            print(f"⚠️ Sound notification failed: {e}")
            QApplication.beep()


class PomodoroTimer(QMainWindow):
    """Pomodoro timer window with work/break sessions"""
    
    # Class variable to track if an instance is already open
    _instance = None
    
    def __init__(self, parent=None):
        # Prevent multiple instances
        if PomodoroTimer._instance is not None:
            if PomodoroTimer._instance.isVisible():
                PomodoroTimer._instance.raise_()
                PomodoroTimer._instance.activateWindow()
                return
        
        super().__init__(parent)
        
        # Set this instance as the active one
        PomodoroTimer._instance = self
        
        self.setWindowTitle("🍅 Pomodoro Timer")
        self.resize(500, 700)
        
        self.stats_manager = PomodoroStats()
        
        # Timer state
        self.is_running = False
        self.is_paused = False
        self.current_phase = "work"
        self.work_minutes = 25
        self.break_minutes = 5
        self.time_remaining = 0
        self.session_count = 0
        
        # Timer thread
        self.timer_thread = None
        self.stop_event = threading.Event()
        
        # Apply dark theme
        from ..qt_app import DarkTheme
        self.theme = DarkTheme
        self.apply_dark_theme()
        
        self._create_ui()
        
    def apply_dark_theme(self):
        """Apply dark theme colors"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, self.theme.MAIN_BG)
        palette.setColor(QPalette.ColorRole.WindowText, self.theme.TEXT_PRIMARY)
        palette.setColor(QPalette.ColorRole.Base, self.theme.CONSOLE_BG)
        palette.setColor(QPalette.ColorRole.Text, self.theme.TEXT_PRIMARY)
        palette.setColor(QPalette.ColorRole.Button, self.theme.BUTTON_BG)
        palette.setColor(QPalette.ColorRole.ButtonText, self.theme.BUTTON_TEXT)
        self.setPalette(palette)
    
    def _create_ui(self):
        """Create the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Title section
        title_widget = self._create_title_section()
        main_layout.addWidget(title_widget)
        
        # Configuration section
        config_widget = self._create_config_section()
        main_layout.addWidget(config_widget)
        
        # Timer display
        timer_widget = self._create_timer_section()
        main_layout.addWidget(timer_widget, 1)
        
        # Control buttons
        button_widget = self._create_button_section()
        main_layout.addWidget(button_widget)
        
        # Statistics
        stats_widget = self._create_stats_section()
        main_layout.addWidget(stats_widget)
        
        # Show main window button
        show_main_btn = QPushButton("🏠 Show TermTools Main Window")
        show_main_btn.setMinimumHeight(35)
        show_main_btn.clicked.connect(self.on_show_main_window)
        self._style_button(show_main_btn, self.theme.ACCENT_SECONDARY)
        main_layout.addWidget(show_main_btn)
        
        # Update displays
        self._update_stats_display()
        self._update_time_display()
        
    def _create_title_section(self):
        """Create title section"""
        widget = QWidget()
        widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setColor(QPalette.ColorRole.Window, self.theme.HEADER_BG)
        widget.setPalette(palette)
        
        layout = QVBoxLayout(widget)
        
        title = QLabel("🍅 POMODORO TIMER")
        title.setFont(QFont("", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {self.theme.TEXT_PRIMARY.name()};")
        layout.addWidget(title)
        
        subtitle = QLabel("Focus • Work • Achieve")
        subtitle.setFont(QFont("", 10))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {self.theme.TEXT_ACCENT.name()}; font-style: italic;")
        layout.addWidget(subtitle)
        
        return widget
    
    def _create_config_section(self):
        """Create configuration section"""
        widget = QWidget()
        widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setColor(QPalette.ColorRole.Window, self.theme.PANEL_BG)
        widget.setPalette(palette)
        
        layout = QVBoxLayout(widget)
        
        title = QLabel("⚙️ Session Configuration")
        title.setFont(QFont("", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {self.theme.TEXT_PRIMARY.name()};")
        layout.addWidget(title)
        
        # Work time selection
        work_layout = QHBoxLayout()
        work_label = QLabel("Work Time:")
        work_label.setStyleSheet(f"color: {self.theme.TEXT_PRIMARY.name()};")
        work_layout.addWidget(work_label)
        
        self.work_choice = QComboBox()
        work_choices = ["5 min", "10 min", "15 min", "20 min", "25 min", "30 min", "35 min", "40 min", "45 min", "Custom"]
        self.work_choice.addItems(work_choices)
        self.work_choice.setCurrentIndex(4)  # Default 25 min
        self.work_choice.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme.BUTTON_BG.name()};
                color: {self.theme.TEXT_PRIMARY.name()};
                padding: 5px;
                border: 1px solid {self.theme.BORDER.name()};
            }}
        """)
        self.work_choice.currentTextChanged.connect(self.on_work_choice)
        work_layout.addWidget(self.work_choice)
        
        layout.addLayout(work_layout)
        
        # Break time selection
        break_layout = QHBoxLayout()
        break_label = QLabel("Break Time:")
        break_label.setStyleSheet(f"color: {self.theme.TEXT_PRIMARY.name()};")
        break_layout.addWidget(break_label)
        
        self.break_choice = QComboBox()
        break_choices = ["5 min", "10 min", "15 min", "20 min", "25 min", "30 min", "Custom"]
        self.break_choice.addItems(break_choices)
        self.break_choice.setCurrentIndex(0)  # Default 5 min
        self.break_choice.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.theme.BUTTON_BG.name()};
                color: {self.theme.TEXT_PRIMARY.name()};
                padding: 5px;
                border: 1px solid {self.theme.BORDER.name()};
            }}
        """)
        self.break_choice.currentTextChanged.connect(self.on_break_choice)
        break_layout.addWidget(self.break_choice)
        
        layout.addLayout(break_layout)
        
        return widget
    
    def _create_timer_section(self):
        """Create timer display section"""
        widget = QWidget()
        widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setColor(QPalette.ColorRole.Window, self.theme.CONSOLE_BG)
        widget.setPalette(palette)
        
        layout = QVBoxLayout(widget)
        
        self.phase_label = QLabel("Ready to Start")
        self.phase_label.setFont(QFont("", 14, QFont.Weight.Bold))
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.phase_label.setStyleSheet(f"color: {self.theme.TEXT_ACCENT.name()};")
        layout.addWidget(self.phase_label)
        
        self.time_label = QLabel("25:00")
        self.time_label.setFont(QFont("Consolas", 48, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(f"color: {self.theme.TEXT_PRIMARY.name()};")
        layout.addWidget(self.time_label)
        
        self.session_label = QLabel("Sessions Completed: 0")
        self.session_label.setFont(QFont("", 10))
        self.session_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.session_label.setStyleSheet(f"color: {self.theme.TEXT_SECONDARY.name()};")
        layout.addWidget(self.session_label)
        
        return widget
    
    def _create_button_section(self):
        """Create control buttons"""
        widget = QWidget()
        widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setColor(QPalette.ColorRole.Window, self.theme.PANEL_BG)
        widget.setPalette(palette)
        
        layout = QHBoxLayout(widget)
        
        self.start_button = QPushButton("▶ Start")
        self.start_button.setMinimumHeight(35)
        self.start_button.clicked.connect(self.on_start)
        self._style_button(self.start_button, self.theme.ACCENT_PRIMARY)
        layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("⏸ Pause")
        self.pause_button.setMinimumHeight(35)
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.on_pause)
        self._style_button(self.pause_button)
        layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.setMinimumHeight(35)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.on_stop)
        self._style_button(self.stop_button)
        layout.addWidget(self.stop_button)
        
        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.setMinimumHeight(35)
        self.reset_button.clicked.connect(self.on_reset)
        self._style_button(self.reset_button)
        layout.addWidget(self.reset_button)
        
        return widget
    
    def _create_stats_section(self):
        """Create statistics section"""
        widget = QWidget()
        widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setColor(QPalette.ColorRole.Window, self.theme.SIDEBAR_BG)
        widget.setPalette(palette)
        
        layout = QVBoxLayout(widget)
        
        title = QLabel("📊 Statistics")
        title.setFont(QFont("", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {self.theme.TEXT_PRIMARY.name()};")
        layout.addWidget(title)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(120)
        self.stats_text.setFont(QFont("Consolas", 9))
        self.stats_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme.CONSOLE_BG.name()};
                color: {self.theme.CONSOLE_TEXT.name()};
                border: 1px solid {self.theme.BORDER.name()};
            }}
        """)
        layout.addWidget(self.stats_text)
        
        # Stats buttons
        button_layout = QHBoxLayout()
        
        view_stats_btn = QPushButton("📈 View All Stats")
        view_stats_btn.setMinimumHeight(30)
        view_stats_btn.clicked.connect(self.on_view_stats)
        self._style_button(view_stats_btn)
        button_layout.addWidget(view_stats_btn)
        
        reset_stats_btn = QPushButton("🗑️ Reset Stats")
        reset_stats_btn.setMinimumHeight(30)
        reset_stats_btn.clicked.connect(self.on_reset_stats)
        self._style_button(reset_stats_btn, self.theme.TEXT_ERROR)
        button_layout.addWidget(reset_stats_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def _style_button(self, button, bg_color=None):
        """Apply styling to button"""
        bg = bg_color or self.theme.BUTTON_BG
        
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg.name()};
                color: {self.theme.BUTTON_TEXT.name()};
                border: none;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.ACCENT_TERTIARY.name()};
                color: {self.theme.TEXT_DARK.name()};
            }}
            QPushButton:pressed {{
                background-color: {self.theme.BUTTON_BG_ACTIVE.name()};
            }}
            QPushButton:disabled {{
                background-color: {self.theme.BUTTON_BG.name()};
                color: {self.theme.TEXT_MUTED.name()};
            }}
        """)
    
    def on_work_choice(self, text):
        """Handle work time selection"""
        if text == "Custom":
            minutes, ok = QInputDialog.getInt(
                self,
                "Custom Work Time",
                "Enter custom work time (minutes):",
                25, 1, 180, 1
            )
            
            if ok:
                self.work_minutes = minutes
                if not self.is_running:
                    self._update_time_display()
            else:
                self.work_choice.setCurrentIndex(4)  # Reset to 25 min
        else:
            self.work_minutes = int(text.split()[0])
            if not self.is_running:
                self._update_time_display()
    
    def on_break_choice(self, text):
        """Handle break time selection"""
        if text == "Custom":
            minutes, ok = QInputDialog.getInt(
                self,
                "Custom Break Time",
                "Enter custom break time (minutes):",
                5, 1, 60, 1
            )
            
            if ok:
                self.break_minutes = minutes
            else:
                self.break_choice.setCurrentIndex(0)  # Reset to 5 min
        else:
            self.break_minutes = int(text.split()[0])
    
    def on_start(self):
        """Start the timer"""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            
            if self.time_remaining == 0:
                self.current_phase = "work"
                self.time_remaining = self.work_minutes * 60
                self._update_phase_label()
            
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.work_choice.setEnabled(False)
            self.break_choice.setEnabled(False)
            
            self.stop_event.clear()
            self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
            self.timer_thread.start()
    
    def on_pause(self):
        """Pause/resume the timer"""
        if self.is_paused:
            self.is_paused = False
            self.pause_button.setText("⏸ Pause")
        else:
            self.is_paused = True
            self.pause_button.setText("▶ Resume")
    
    def on_stop(self):
        """Stop the timer"""
        self.stop_event.set()
        self.is_running = False
        self.is_paused = False
        self.time_remaining = 0
        
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.work_choice.setEnabled(True)
        self.break_choice.setEnabled(True)
        self.pause_button.setText("⏸ Pause")
        
        self.phase_label.setText("Ready to Start")
        self.phase_label.setStyleSheet(f"color: {self.theme.TEXT_ACCENT.name()};")
        self._update_time_display()
    
    def on_reset(self):
        """Reset the timer and session count"""
        if self.is_running:
            reply = QMessageBox.question(
                self,
                "Timer Running",
                "Timer is running. Stop it first?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.on_stop()
            else:
                return
        
        self.session_count = 0
        self.current_phase = "work"
        self.time_remaining = 0
        
        self.session_label.setText("Sessions Completed: 0")
        self.phase_label.setText("Ready to Start")
        self.phase_label.setStyleSheet(f"color: {self.theme.TEXT_ACCENT.name()};")
        self._update_time_display()
    
    def on_view_stats(self):
        """View all statistics"""
        stats = self.stats_manager.get_stats()
        
        stats_text = "="*40 + "\n"
        stats_text += "       📊 POMODORO STATISTICS\n"
        stats_text += "="*40 + "\n\n"
        
        stats_text += f"🎯 Total Work Sessions: {stats.get('total_work_sessions', 0)}\n"
        stats_text += f"⏱️ Total Work Time: {stats.get('total_work_minutes', 0)} minutes\n"
        stats_text += f"☕ Total Break Time: {stats.get('total_break_minutes', 0)} minutes\n\n"
        
        sessions_by_date = stats.get('sessions_by_date', {})
        if sessions_by_date:
            stats_text += "📅 Recent Sessions by Date:\n"
            stats_text += "-"*40 + "\n"
            
            sorted_dates = sorted(sessions_by_date.keys(), reverse=True)[:7]
            for date in sorted_dates:
                day_stats = sessions_by_date[date]
                stats_text += f"\n{date}:\n"
                stats_text += f"  • Sessions: {day_stats.get('work_sessions', 0)}\n"
                stats_text += f"  • Work: {day_stats.get('work_minutes', 0)} min\n"
                stats_text += f"  • Break: {day_stats.get('break_minutes', 0)} min\n"
        
        QMessageBox.information(self, "Pomodoro Statistics", stats_text)
    
    def on_show_main_window(self):
        """Show/restore the main TermTools window"""
        try:
            app = QApplication.instance()
            for widget in app.topLevelWidgets():
                if isinstance(widget, QMainWindow) and widget != self:
                    if not widget.isVisible():
                        widget.show()
                        print("✅ Main window restored")
                    widget.raise_()
                    widget.activateWindow()
                    break
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not show main window: {e}")
    
    def on_reset_stats(self):
        """Reset all statistics"""
        reply = QMessageBox.question(
            self,
            "Confirm Reset Statistics",
            "Are you sure you want to reset all statistics?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.stats_manager.reset_stats()
            self._update_stats_display()
            QMessageBox.information(self, "Statistics Reset", "Statistics have been reset successfully.")
    
    def _timer_loop(self):
        """Main timer loop running in separate thread"""
        while self.is_running and not self.stop_event.is_set():
            if not self.is_paused:
                if self.time_remaining > 0:
                    self.time_remaining -= 1
                    QApplication.instance().postEvent(self, UpdateTimeEvent())
                    time.sleep(1)
                else:
                    QApplication.instance().postEvent(self, SessionCompleteEvent())
                    
                    if self.current_phase == "work":
                        self.current_phase = "break"
                        self.time_remaining = self.break_minutes * 60
                    else:
                        self.current_phase = "work"
                        self.time_remaining = self.work_minutes * 60
                    
                    QApplication.instance().postEvent(self, UpdatePhaseEvent())
                    QApplication.instance().postEvent(self, UpdateTimeEvent())
            else:
                time.sleep(0.1)
    
    def _on_session_complete(self):
        """Handle session completion"""
        if self.current_phase == "work":
            self.session_count += 1
            self.session_label.setText(f"Sessions Completed: {self.session_count}")
            
            self.stats_manager.record_work_session(self.work_minutes)
            
            threading.Thread(
                target=SoundNotifier.play_completion_sound,
                args=("work",),
                daemon=True
            ).start()
            
            QMessageBox.information(
                self,
                "Pomodoro Complete",
                f"✅ Work session complete!\n\nTime for a {self.break_minutes} minute break."
            )
        else:
            self.stats_manager.record_break_session(self.break_minutes)
            
            threading.Thread(
                target=SoundNotifier.play_completion_sound,
                args=("break",),
                daemon=True
            ).start()
            
            QMessageBox.information(
                self,
                "Break Complete",
                f"☕ Break complete!\n\nReady for the next {self.work_minutes} minute work session?"
            )
        
        self._update_stats_display()
    
    def _update_time_display(self):
        """Update the time display label"""
        try:
            if self.time_remaining == 0:
                if self.current_phase == "work":
                    minutes = self.work_minutes
                else:
                    minutes = self.break_minutes
                self.time_label.setText(f"{minutes:02d}:00")
            else:
                minutes = self.time_remaining // 60
                seconds = self.time_remaining % 60
                self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        except RuntimeError:
            pass
    
    def _update_phase_label(self):
        """Update the phase label"""
        try:
            if self.current_phase == "work":
                self.phase_label.setText("🎯 WORK SESSION")
                self.phase_label.setStyleSheet(f"color: {self.theme.TEXT_SUCCESS.name()};")
            else:
                self.phase_label.setText("☕ BREAK TIME")
                self.phase_label.setStyleSheet(f"color: {self.theme.ACCENT_PRIMARY.name()};")
        except RuntimeError:
            pass
    
    def _update_stats_display(self):
        """Update the stats text display"""
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
            
            self.stats_text.setPlainText(stats_text)
        except RuntimeError:
            pass
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_running:
            self.stop_event.set()
            self.is_running = False
            
            if self.timer_thread and self.timer_thread.is_alive():
                self.timer_thread.join(timeout=1.0)
        
        PomodoroTimer._instance = None
        
        try:
            app = QApplication.instance()
            for widget in app.topLevelWidgets():
                if isinstance(widget, QMainWindow) and widget != self and not widget.isVisible():
                    print("✅ Pomodoro timer closed. Exiting TermTools.")
                    QApplication.quit()
                    break
        except Exception:
            pass
        
        event.accept()
    
    def event(self, event):
        """Handle custom events"""
        if isinstance(event, UpdateTimeEvent):
            self._update_time_display()
            return True
        elif isinstance(event, UpdatePhaseEvent):
            self._update_phase_label()
            return True
        elif isinstance(event, SessionCompleteEvent):
            self._on_session_complete()
            return True
        return super().event(event)


# Custom event classes
from PyQt6.QtCore import QEvent

class UpdateTimeEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self):
        super().__init__(self.EVENT_TYPE)

class UpdatePhaseEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self):
        super().__init__(self.EVENT_TYPE)

class SessionCompleteEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self):
        super().__init__(self.EVENT_TYPE)


@pomodoro_bp.route("13", "🍅 Pomodoro Timer", "Focus timer with work/break sessions", "🎯 PRODUCTIVITY", order=1)
def show_pomodoro_timer(app=None):
    """Show the Pomodoro timer window"""
    try:
        if PomodoroTimer._instance is not None and PomodoroTimer._instance.isVisible():
            PomodoroTimer._instance.raise_()
            PomodoroTimer._instance.activateWindow()
            print("💡 Pomodoro timer is already open - bringing window to front")
            return
        
        timer_frame = PomodoroTimer()
        timer_frame.show()
        
        print("✅ Pomodoro timer window opened")
        
    except Exception as e:
        print(f"❌ Error showing Pomodoro timer: {e}")
        import traceback
        traceback.print_exc()
