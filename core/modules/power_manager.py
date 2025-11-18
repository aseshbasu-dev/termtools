"""
System Power Manager Module for TermTools
Built by Asesh Basu

This module provides system power management functionality including
scheduling shutdown operations with various time options.
State is persisted in JSON format in core/data/shutdown_state.json.
"""

import os
import subprocess
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox, QInputDialog
import json
from datetime import datetime, timedelta
from pathlib import Path
from ..blueprint import Blueprint

# Configure logger
logger = logging.getLogger(__name__)

def _get_subprocess_flags():
    """Get subprocess creation flags to prevent console window flashing on Windows"""
    if os.name == 'nt':
        return {'creationflags': subprocess.CREATE_NO_WINDOW}
    return {}


# Create the blueprint for power management
power_manager_bp = Blueprint("power_manager", "System power management and shutdown scheduling")


class SystemPowerManager:
    """System power management for scheduling shutdown operations"""
    
    def __init__(self):
        self.shutdown_timer = None
        self.shutdown_active = False
        # Use JSON file in core/data directory
        self.state_file = Path("core/data/shutdown_state.json")
    
    def _show_gui_confirmation(self, message, title="Confirm Action"):
        """Show GUI confirmation dialog"""
        logger.debug(f"Showing GUI confirmation dialog: title='{title}', message='{message}'")
        try:
            # Check if we're in a GUI environment
            if QApplication.instance():
                reply = QMessageBox.question(
                    None,  # Use None as parent
                    title,
                    message,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                result = reply == QMessageBox.StandardButton.Yes
                logger.debug(f"User response: {'Yes' if result else 'No'}")
                return result
            else:
                logger.warning("GUI unavailable - TermTools requires GUI mode")
                print(f"❌ GUI unavailable - TermTools requires GUI mode")
                print(f"   Message: {message}")
                return False
        except Exception as e:
            logger.error(f"Error showing GUI confirmation: {e}", exc_info=True)
            print(f"❌ Error showing GUI confirmation: {e}")
            return False
    
    def _show_gui_error(self, message, title="Error"):
        """Show GUI error dialog if available, fallback to terminal"""
        logger.error(f"GUI Error: {title} - {message}")
        try:
            # Check if we're in a GUI environment
            if QApplication.instance():
                QMessageBox.critical(
                    None,
                    title,
                    message
                )
                return
            print(f"❌ {message}")
        except Exception as e:
            logger.error(f"Failed to show GUI error: {e}", exc_info=True)
            print(f"❌ {message}")
    
    def _show_gui_info(self, message, title="Information"):
        """Show GUI info dialog if available, fallback to terminal"""
        logger.info(f"GUI Info: {title} - {message}")
        try:
            # Check if we're in a GUI environment
            if QApplication.instance():
                QMessageBox.information(
                    None,
                    title,
                    message
                )
                return
            print(f"ℹ️  {message}")
        except Exception as e:
            logger.error(f"Failed to show GUI info: {e}", exc_info=True)
            print(f"ℹ️  {message}")
        
    def _save_shutdown_state(self, scheduled=False, scheduled_time=None, description=""):
        """Save shutdown state to JSON file"""
        state = {
            'scheduled': scheduled,
            'scheduled_time': scheduled_time.isoformat() if scheduled_time else None,
            'description': description,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            # Ensure the directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"⚠️  Warning: Could not save shutdown state: {e}")
    
    def _load_shutdown_state(self):
        """Load shutdown state from JSON file"""
        if not self.state_file.exists():
            return {'scheduled': False, 'scheduled_time': None, 'description': '', 'last_updated': None}
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f) or {}
                
            # Convert scheduled_time back to datetime if present
            if state.get('scheduled_time'):
                try:
                    state['scheduled_time'] = datetime.fromisoformat(state['scheduled_time'])
                except:
                    state['scheduled_time'] = None
                    state['scheduled'] = False
                    
            return state
        except Exception as e:
            print(f"⚠️  Warning: Could not load shutdown state: {e}")
            return {'scheduled': False, 'scheduled_time': None, 'description': '', 'last_updated': None}
    
    def get_shutdown_status(self):
        """Get current shutdown status with time remaining"""
        state = self._load_shutdown_state()
        
        if not state.get('scheduled') or not state.get('scheduled_time'):
            return {'scheduled': False, 'time_remaining': None, 'description': ''}
        
        scheduled_time = state['scheduled_time']
        now = datetime.now()
        
        # Check if shutdown time has passed
        if now >= scheduled_time:
            # Clear the state as shutdown should have occurred
            self._save_shutdown_state(scheduled=False)
            return {'scheduled': False, 'time_remaining': None, 'description': ''}
        
        time_remaining = scheduled_time - now
        return {
            'scheduled': True,
            'time_remaining': time_remaining,
            'description': state.get('description', ''),
            'scheduled_time': scheduled_time
        }
        
    def schedule_shutdown(self):
        """Interactive menu for scheduling system shutdown via GUI"""
        print("\n💻 System Power Management")
        print("="*50)
        print("⚠️  WARNING: This will schedule a system shutdown!")
        print("⚠️  Make sure to save all your work before proceeding.")
        print("="*50)
        
        choices = [
            "Shutdown in 1 hour",
            "Shutdown in 2 hours", 
            "Shutdown in 3 hours",
            "Custom time (minutes)",
            "Cancel any scheduled shutdown",
            "Check shutdown status"
        ]
        
        try:
            # Check if we're in a GUI environment
            if QApplication.instance():
                item, ok = QInputDialog.getItem(
                    None,
                    "Power Manager - Shutdown Options",
                    "Select shutdown option:",
                    choices,
                    0,
                    False
                )
                
                if ok and item:
                    choice_index = choices.index(item)
                    logger.debug(f"User selected shutdown option: {choice_index} - {item}")
                    
                    if choice_index == 0:
                        self._schedule_shutdown_minutes(60, "1 hour")
                    elif choice_index == 1:
                        self._schedule_shutdown_minutes(120, "2 hours")
                    elif choice_index == 2:
                        self._schedule_shutdown_minutes(180, "3 hours")
                    elif choice_index == 3:
                        self._custom_shutdown_time()
                    elif choice_index == 4:
                        self._cancel_shutdown()
                    elif choice_index == 5:
                        self._check_shutdown_status()
                else:
                    logger.debug("User cancelled shutdown options dialog")
                    print("⚠️  Operation cancelled.")
            else:
                logger.warning("GUI unavailable for shutdown options")
                print("❌ GUI unavailable - TermTools requires GUI mode")
                
        except Exception as e:
            logger.error(f"Error showing shutdown options: {e}", exc_info=True)
            print(f"❌ Error showing shutdown options: {e}")
    
    def _schedule_shutdown_minutes(self, minutes, description):
        """Schedule shutdown for specified minutes"""
        logger.info(f"Attempting to schedule shutdown: {minutes} minutes ({description})")
        
        # Confirm the action using GUI or terminal
        confirmation_message = f"You are about to schedule a shutdown in {description}.\n\nThe system will shut down in {minutes} minutes."
        
        if not self._show_gui_confirmation(confirmation_message, "Confirm Shutdown"):
            logger.info("User cancelled shutdown scheduling")
            self._show_gui_info("Shutdown cancelled.", "Cancelled")
            return
            
        try:
            scheduled_time = datetime.now() + timedelta(minutes=minutes)
            logger.debug(f"Scheduled shutdown time: {scheduled_time}")
            
            if os.name == 'nt':  # Windows
                # Use Windows shutdown command
                logger.debug(f"Executing Windows shutdown command: shutdown /s /t {minutes * 60}")
                subprocess.run(['shutdown', '/s', '/t', str(minutes * 60)], check=True, **_get_subprocess_flags())
                success_message = f"✅ Shutdown scheduled successfully!\n🕒 System will shutdown in {description}\n💡 Use 'shutdown /a' in command prompt to cancel"
                self._show_gui_info(success_message, "Shutdown Scheduled")
            else:  # Unix-like systems
                logger.debug(f"Executing Unix shutdown command: shutdown -h +{minutes}")
                subprocess.run(['sudo', 'shutdown', '-h', f"+{minutes}"], check=True, **_get_subprocess_flags())
                success_message = f"✅ Shutdown scheduled successfully!\n🕒 System will shutdown in {description}\n💡 Use 'sudo shutdown -c' to cancel"
                self._show_gui_info(success_message, "Shutdown Scheduled")
                
            self.shutdown_active = True
            logger.info(f"Shutdown successfully scheduled for {scheduled_time}")
            
            # Save the shutdown state
            self._save_shutdown_state(
                scheduled=True,
                scheduled_time=scheduled_time,
                description=description
            )
            
        except subprocess.CalledProcessError as e:
            error_message = f"Failed to schedule shutdown: {e}"
            self._show_gui_error(error_message)
        except FileNotFoundError:
            error_message = "Shutdown command not found. This feature may not be available on your system."
            self._show_gui_error(error_message)
    
    def _custom_shutdown_time(self):
        """Schedule shutdown for custom time in minutes via GUI"""
        logger.debug("Opening custom shutdown time dialog")
        try:
            # Check if we're in a GUI environment
            if QApplication.instance():
                minutes, ok = QInputDialog.getInt(
                    None,
                    "Custom Shutdown Time",
                    "Enter minutes until shutdown (1-1440):",
                    60,  # Default value
                    1,   # Minimum
                    1440,  # Maximum (24 hours)
                    1    # Step
                )
                
                if ok:
                    logger.info(f"User entered custom shutdown time: {minutes} minutes")
                    hours = minutes // 60
                    remaining_minutes = minutes % 60
                    
                    if hours > 0:
                        description = f"{hours} hour{'s' if hours > 1 else ''}"
                        if remaining_minutes > 0:
                            description += f" and {remaining_minutes} minute{'s' if remaining_minutes > 1 else ''}"
                    else:
                        description = f"{minutes} minute{'s' if minutes > 1 else ''}"
                    
                    logger.debug(f"Scheduling shutdown with description: {description}")
                    self._schedule_shutdown_minutes(minutes, description)
                else:
                    logger.debug("User cancelled custom shutdown time dialog")
                    print("⚠️  Operation cancelled.")
            else:
                logger.warning("GUI unavailable for custom shutdown time")
                print("❌ GUI unavailable - TermTools requires GUI mode")
                
        except Exception as e:
            logger.error(f"Error getting custom shutdown time: {e}", exc_info=True)
            print(f"❌ Error getting custom shutdown time: {e}")
    
    def _cancel_shutdown(self):
        """Cancel any scheduled shutdown"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['shutdown', '/a'], capture_output=True, text=True, **_get_subprocess_flags())
                if result.returncode == 0:
                    self._show_gui_info("Shutdown cancelled successfully!", "Shutdown Cancelled")
                else:
                    self._show_gui_info("No shutdown was scheduled or shutdown already cancelled.", "No Shutdown Found")
            else:  # Unix-like systems
                result = subprocess.run(['sudo', 'shutdown', '-c'], capture_output=True, text=True, **_get_subprocess_flags())
                if result.returncode == 0:
                    self._show_gui_info("Shutdown cancelled successfully!", "Shutdown Cancelled")
                else:
                    self._show_gui_info("No shutdown was scheduled or shutdown already cancelled.", "No Shutdown Found")
                    
            self.shutdown_active = False
            
            # Clear the shutdown state
            self._save_shutdown_state(scheduled=False)
            
        except Exception as e:
            error_message = f"Error cancelling shutdown: {e}"
            self._show_gui_error(error_message)
    
    def _check_shutdown_status(self):
        """Check if shutdown is scheduled"""
        try:
            if os.name == 'nt':  # Windows
                # Check if shutdown is scheduled by trying to cancel it (won't actually cancel)
                result = subprocess.run(['shutdown', '/a'], capture_output=True, text=True, **_get_subprocess_flags())
                if "No logoff or shutdown in progress" in result.stderr:
                    print("ℹ️  No shutdown is currently scheduled.")
                else:
                    print("⚠️  A shutdown appears to be scheduled.")
                    print("💡 Use option 5 to cancel if needed.")
            else:  # Unix-like systems
                # Check for scheduled shutdown
                result = subprocess.run(['who', '-b'], capture_output=True, text=True, **_get_subprocess_flags())
                print("ℹ️  System shutdown status:")
                print("💡 Use 'sudo shutdown -c' to cancel any scheduled shutdown")
                
        except Exception as e:
            print(f"❌ Error checking shutdown status: {e}")


# Global power manager instance
power_manager = SystemPowerManager()


# Register blueprint routes using decorators
@power_manager_bp.route("9", "Schedule system shutdown", "1hr, 2hr, 3hr, custom", "💻 SYSTEM POWER MANAGEMENT", 1)
def schedule_system_shutdown(app=None):
    """Schedule system shutdown with various time options"""
    power_manager.schedule_shutdown()


# Initialize blueprint on import
@power_manager_bp.on_init
def init_power_manager(app):
    """Initialize the power manager module"""
    app.set_config("power_manager_enabled", True)
    app.set_config("power_manager_instance", power_manager)