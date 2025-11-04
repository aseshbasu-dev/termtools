"""
Git Operations Module for TermTools
Built by Asesh Basu

This module provides Git repository management functionality including
quick commit and push operations.
"""

import subprocess
import sys
from ..blueprint import Blueprint

# Create the blueprint for Git operations
git_operations_bp = Blueprint("git_operations", "Git repository management")


class GitOperations:
    """Git repository management operations"""
    
    @staticmethod
    def _get_commit_message_input(app=None):
        """
        Get commit message from user via GUI dialog.
        
        Args:
            app: TermTools app instance (used to detect GUI mode)
            
        Returns:
            str: Commit message or None if cancelled
        """
        return GitOperations._get_commit_message_gui_threadsafe()
    
    @staticmethod
    def _get_commit_message_gui():
        """Get commit message via GUI dialog"""
        try:
            import wx
            
            # Create dialog for commit message input
            dlg = wx.TextEntryDialog(
                None,
                "Enter commit message:",
                "Git Commit Message",
                "bug fixes"  # Default value
            )
            dlg.SetSize(wx.Size(400, 150))  # Make dialog wider for better text entry
            
            if dlg.ShowModal() == wx.ID_OK:
                commit_message = dlg.GetValue().strip()
                dlg.Destroy()
                return commit_message if commit_message else "bug fixes"
            else:
                dlg.Destroy()
                return None  # User cancelled
        except Exception as e:
            print(f"❌ Error showing GUI dialog: {e}")
            return "bug fixes"  # Fallback to default message
    
    @staticmethod
    def _get_commit_message_gui_threadsafe():
        """Thread-safe version using wx.CallAfter for GUI operations"""
        import wx
        import threading
        
        result_container = {"value": None, "done": False}
        
        def show_dialog():
            try:
                dlg = wx.TextEntryDialog(
                    None,
                    "Enter commit message:",
                    "Git Commit Message",
                    "bug fixes"  # Default value
                )
                dlg.SetSize(wx.Size(400, 150))
                
                if dlg.ShowModal() == wx.ID_OK:
                    commit_message = dlg.GetValue().strip()
                    result_container["value"] = commit_message if commit_message else "bug fixes"
                else:
                    result_container["value"] = None  # User cancelled
                dlg.Destroy()
            except Exception as e:
                print(f"❌ Error showing GUI dialog: {e}")
                result_container["value"] = "bug fixes"  # Fallback
            finally:
                result_container["done"] = True
        
        # Check if we're on the main thread using threading
        try:
            main_thread = threading.main_thread()
            current_thread = threading.current_thread()
            
            if current_thread == main_thread:
                return GitOperations._get_commit_message_gui()
            else:
                # Use CallAfter to execute on main thread
                wx.CallAfter(show_dialog)
                
                # Wait for dialog to complete
                while not result_container["done"]:
                    threading.Event().wait(0.1)
                
                return result_container["value"]
        except:
            # Fallback if wx not available or other issues
            return GitOperations._get_commit_message_gui()
    
    @staticmethod
    def _get_confirmation(message, title="Confirmation", app=None):
        """
        Get confirmation from user via GUI dialog.
        
        Args:
            message: Confirmation message to display
            title: Dialog title (for GUI mode)
            app: TermTools app instance
            
        Returns:
            bool: True if user confirmed, False if cancelled
        """
        return GitOperations._get_confirmation_gui_threadsafe(message, title)
    
    @staticmethod
    def _get_confirmation_gui(message, title):
        """Get confirmation via GUI dialog"""
        try:
            import wx
            
            dlg = wx.MessageDialog(
                None,
                message,
                title,
                wx.YES_NO | wx.ICON_QUESTION
            )
            
            result = dlg.ShowModal()
            dlg.Destroy()
            return result == wx.ID_YES
        except Exception as e:
            print(f"❌ Error showing GUI confirmation: {e}")
            return False  # Default to not confirming if error occurs
    
    @staticmethod
    def _get_confirmation_gui_threadsafe(message, title):
        """Thread-safe version of confirmation dialog"""
        import wx
        import threading
        
        result_container = {"value": False, "done": False}
        
        def show_dialog():
            try:
                dlg = wx.MessageDialog(
                    None,
                    message,
                    title,
                    wx.YES_NO | wx.ICON_QUESTION
                )
                
                result = dlg.ShowModal()
                result_container["value"] = result == wx.ID_YES
                dlg.Destroy()
            except Exception as e:
                print(f"❌ Error showing GUI confirmation: {e}")
                result_container["value"] = False  # Default to not confirming
            finally:
                result_container["done"] = True
        
        # Check if we're on the main thread
        try:
            main_thread = threading.main_thread()
            current_thread = threading.current_thread()
            
            if current_thread == main_thread:
                return GitOperations._get_confirmation_gui(message, title)
            else:
                # Use CallAfter to execute on main thread
                wx.CallAfter(show_dialog)
                
                # Wait for dialog to complete
                while not result_container["done"]:
                    threading.Event().wait(0.1)
                
                return result_container["value"]
        except:
            # Fallback
            return GitOperations._get_confirmation_gui(message, title)

    @staticmethod
    def quick_commit_push(app=None):
        """
        Execute git add, commit, and push in sequence.
        Equivalent to: git add . ; git commit -m "bug fixes" ; git push
        
        Args:
            app: TermTools app instance (used to detect GUI mode)
        """
        print("\n🔧 Git Quick Commit & Push")
        print("="*60)
        
        # Check if we're in a git repository
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print("❌ Not a git repository. Please initialize git first.")
                print("   Use: git init")
                print("   Then, add a remote repository with:")
                print("   git remote add origin <remote_repository_url>")
                print("   Then run this command again")
                return
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH.")
            return
        
        # Get commit message from user
        commit_message = GitOperations._get_commit_message_input(app)
        if commit_message is None:  # User cancelled
            print("❌ Operation cancelled.")
            return
        
        print(f"\n🎯 Commit message: '{commit_message}'")
        
        # Get confirmation from user with actual Git commands
        confirmation_message = (
            f"You are about to execute the following Git commands:\n\n"
            f"1. git add .\n"
            f"2. git commit -m \"{commit_message}\"\n"
            f"3. git push\n\n"
            f"Do you want to proceed?"
        )
        if not GitOperations._get_confirmation(confirmation_message, "Git Quick Commit & Push Confirmation", app):
            print("❌ Operation cancelled.")
            return
        
        # Step 1: git add .
        print("\n📦 Step 1/3: Adding all changes...")
        try:
            result = subprocess.run(
                ['git', 'add', '.'],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ All changes staged successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error staging changes: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            return
        
        # Step 2: git commit
        print("\n💾 Step 2/3: Committing changes...")
        try:
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Changes committed successfully")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            if "nothing to commit" in e.stdout:
                print("ℹ️  Nothing to commit (working tree clean)")
                print("   Skipping push operation.")
                return
            else:
                print(f"❌ Error committing changes: {e}")
                if e.stderr:
                    print(f"   {e.stderr.strip()}")
                return
        
        # Step 3: git push
        print("\n🚀 Step 3/3: Pushing to remote...")
        try:
            result = subprocess.run(
                ['git', 'push'],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Changes pushed successfully!")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            if result.stderr:  # Git often outputs to stderr even on success
                print(f"   {result.stderr.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error pushing changes: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            print("\n💡 Tip: You may need to set up a remote or pull first.")
            return
        
        print("\n" + "="*60)
        print("🎉 All operations completed successfully!")


# Register menu items using the blueprint route decorator
@git_operations_bp.route(
    "1",
    "Quick Commit & Push",
    "Add, commit, and push changes",
    "🔧 GIT OPERATIONS",
    order=1
)
def git_quick_commit_push(app=None):
    """Menu handler for quick commit and push"""
    GitOperations.quick_commit_push(app)


# Initialize the module
@git_operations_bp.on_init
def init_git_module(app):
    """Initialize Git operations module"""
    print("🔧 Git Operations module initialized")
    app.set_config("git_enabled", True)
