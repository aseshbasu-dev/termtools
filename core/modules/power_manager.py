"""
System Power Manager Module for TermTools
Built by Asesh Basu

This module provides system power management functionality including
scheduling shutdown operations with various time options.
"""

import os
import subprocess
from ..blueprint import Blueprint

# Create the blueprint for power management
power_manager_bp = Blueprint("power_manager", "System power management and shutdown scheduling")


class SystemPowerManager:
    """System power management for scheduling shutdown operations"""
    
    def __init__(self):
        self.shutdown_timer = None
        self.shutdown_active = False
        
    def schedule_shutdown(self):
        """Interactive menu for scheduling system shutdown"""
        print("\n💻 System Power Management")
        print("="*50)
        print("⚠️  WARNING: This will schedule a system shutdown!")
        print("⚠️  Make sure to save all your work before proceeding.")
        print("="*50)
        
        print("\nShutdown options:")
        print("1️⃣  Shutdown in 1 hour")
        print("2️⃣  Shutdown in 2 hours") 
        print("3️⃣  Shutdown in 3 hours")
        print("4️⃣  Custom time (minutes)")
        print("5️⃣  Cancel any scheduled shutdown")
        print("6️⃣  Check shutdown status")
        print("0️⃣  Return to main menu")
        
        try:
            choice = input("\nEnter your choice (0-6): ").strip()
            
            if choice == "1":
                self._schedule_shutdown_minutes(60, "1 hour")
            elif choice == "2":
                self._schedule_shutdown_minutes(120, "2 hours")
            elif choice == "3":
                self._schedule_shutdown_minutes(180, "3 hours")
            elif choice == "4":
                self._custom_shutdown_time()
            elif choice == "5":
                self._cancel_shutdown()
            elif choice == "6":
                self._check_shutdown_status()
            elif choice == "0":
                return
            else:
                print("❌ Invalid choice. Please enter 0-6.")
                
        except KeyboardInterrupt:
            print("\n⚠️  Operation cancelled.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _schedule_shutdown_minutes(self, minutes, description):
        """Schedule shutdown for specified minutes"""
        # Confirm the action
        print(f"\n⚠️  You are about to schedule a shutdown in {description}")
        print(f"💻 The system will shut down in {minutes} minutes")
        confirm = input("Are you sure? Type 'YES' to confirm or ENTER to cancel: ").strip()
        
        if confirm.casefold() != "yes":
            print("❌ Shutdown cancelled.")
            return
            
        try:
            if os.name == 'nt':  # Windows
                # Use Windows shutdown command
                subprocess.run(['shutdown', '/s', '/t', str(minutes * 60)], check=True)
                print(f"✅ Shutdown scheduled successfully!")
                print(f"🕒 System will shutdown in {description}")
                print(f"💡 Use 'shutdown /a' in command prompt to cancel")
            else:  # Unix-like systems
                subprocess.run(['sudo', 'shutdown', '-h', f"+{minutes}"], check=True)
                print(f"✅ Shutdown scheduled successfully!")
                print(f"🕒 System will shutdown in {description}")
                print(f"💡 Use 'sudo shutdown -c' to cancel")
                
            self.shutdown_active = True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to schedule shutdown: {e}")
        except FileNotFoundError:
            print("❌ Shutdown command not found. This feature may not be available on your system.")
    
    def _custom_shutdown_time(self):
        """Schedule shutdown for custom time in minutes"""
        try:
            minutes = input("Enter minutes until shutdown (1-1440): ").strip()
            minutes = int(minutes)
            
            if minutes < 1 or minutes > 1440:  # Max 24 hours
                print("❌ Invalid time. Please enter 1-1440 minutes.")
                return
                
            hours = minutes // 60
            remaining_minutes = minutes % 60
            
            if hours > 0:
                description = f"{hours} hour{'s' if hours > 1 else ''}"
                if remaining_minutes > 0:
                    description += f" and {remaining_minutes} minute{'s' if remaining_minutes > 1 else ''}"
            else:
                description = f"{minutes} minute{'s' if minutes > 1 else ''}"
                
            self._schedule_shutdown_minutes(minutes, description)
            
        except ValueError:
            print("❌ Invalid input. Please enter a valid number.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _cancel_shutdown(self):
        """Cancel any scheduled shutdown"""
        try:
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
                    
            self.shutdown_active = False
            
        except Exception as e:
            print(f"❌ Error cancelling shutdown: {e}")
    
    def _check_shutdown_status(self):
        """Check if shutdown is scheduled"""
        try:
            if os.name == 'nt':  # Windows
                # Check if shutdown is scheduled by trying to cancel it (won't actually cancel)
                result = subprocess.run(['shutdown', '/a'], capture_output=True, text=True)
                if "No logoff or shutdown in progress" in result.stderr:
                    print("ℹ️  No shutdown is currently scheduled.")
                else:
                    print("⚠️  A shutdown appears to be scheduled.")
                    print("💡 Use option 5 to cancel if needed.")
            else:  # Unix-like systems
                # Check for scheduled shutdown
                result = subprocess.run(['who', '-b'], capture_output=True, text=True)
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