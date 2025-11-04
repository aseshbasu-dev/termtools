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

    @staticmethod
    def _get_repo_url_input(app=None):
        """
        Get repository URL from user via GUI dialog.
        
        Args:
            app: TermTools app instance (used to detect GUI mode)
            
        Returns:
            str: Repository URL or None if cancelled
        """
        return GitOperations._get_repo_url_input_gui_threadsafe()
    
    @staticmethod
    def _get_repo_url_input_gui():
        """Get repository URL via GUI dialog"""
        try:
            import wx
            
            instructions = (
                "Enter your Git repository URL.\n\n"
                "Repository URL formats:\n"
                "• HTTPS: https://github.com/username/repository.git\n"
                "• SSH:   git@github.com:username/repository.git\n\n"
                "Example: https://github.com/aseshbasu-dev/termtools.git"
            )
            
            # Create dialog for repository URL input
            dlg = wx.TextEntryDialog(
                None,
                instructions,
                "Git Repository URL",
                ""  # Empty default value
            )
            dlg.SetSize(wx.Size(550, 250))  # Make dialog larger for instructions
            
            if dlg.ShowModal() == wx.ID_OK:
                repo_url = dlg.GetValue().strip()
                dlg.Destroy()
                return repo_url if repo_url else None
            else:
                dlg.Destroy()
                return None  # User cancelled
        except Exception as e:
            print(f"❌ Error showing GUI dialog: {e}")
            return None
    
    @staticmethod
    def _get_repo_url_input_gui_threadsafe():
        """Thread-safe version using wx.CallAfter for GUI operations"""
        import wx
        import threading
        
        result_container = {"value": None, "done": False}
        
        def show_dialog():
            try:
                instructions = (
                    "Enter your Git repository URL.\n\n"
                    "Repository URL formats:\n"
                    "• HTTPS: https://github.com/username/repository.git\n"
                    "• SSH:   git@github.com:username/repository.git\n\n"
                    "Example: https://github.com/aseshbasu-dev/termtools.git"
                )
                
                dlg = wx.TextEntryDialog(
                    None,
                    instructions,
                    "Git Repository URL",
                    ""  # Empty default value
                )
                dlg.SetSize(wx.Size(550, 250))
                
                if dlg.ShowModal() == wx.ID_OK:
                    repo_url = dlg.GetValue().strip()
                    result_container["value"] = repo_url if repo_url else None
                else:
                    result_container["value"] = None  # User cancelled
                dlg.Destroy()
            except Exception as e:
                print(f"❌ Error showing GUI dialog: {e}")
                result_container["value"] = None
            finally:
                result_container["done"] = True
        
        # Check if we're on the main thread using threading
        try:
            main_thread = threading.main_thread()
            current_thread = threading.current_thread()
            
            if current_thread == main_thread:
                return GitOperations._get_repo_url_input_gui()
            else:
                # Use CallAfter to execute on main thread
                wx.CallAfter(show_dialog)
                
                # Wait for dialog to complete
                while not result_container["done"]:
                    threading.Event().wait(0.1)
                
                return result_container["value"]
        except:
            # Fallback if wx not available or other issues
            return GitOperations._get_repo_url_input_gui()

    @staticmethod
    def _get_untrack_input(app=None):
        """
        Get files/folders to untrack from user via GUI dialog.
        
        Args:
            app: TermTools app instance (used to detect GUI mode)
            
        Returns:
            str: Space-separated files/folders or None if cancelled
        """
        return GitOperations._get_untrack_input_gui_threadsafe()
    
    @staticmethod
    def _get_untrack_input_gui():
        """Get files/folders to untrack via GUI dialog"""
        try:
            import wx
            
            # Create dialog for files/folders input
            dlg = wx.TextEntryDialog(
                None,
                "Enter files/folders to untrack (separate with spaces):\n\nExample: .github .vscode __pycache__ temp.txt",
                "Git Untrack Files/Folders",
                ""  # Empty default value
            )
            dlg.SetSize(wx.Size(500, 180))  # Make dialog wider for better text entry
            
            if dlg.ShowModal() == wx.ID_OK:
                untrack_input = dlg.GetValue().strip()
                dlg.Destroy()
                return untrack_input if untrack_input else None
            else:
                dlg.Destroy()
                return None  # User cancelled
        except Exception as e:
            print(f"❌ Error showing GUI dialog: {e}")
            return None
    
    @staticmethod
    def _get_untrack_input_gui_threadsafe():
        """Thread-safe version using wx.CallAfter for GUI operations"""
        import wx
        import threading
        
        result_container = {"value": None, "done": False}
        
        def show_dialog():
            try:
                dlg = wx.TextEntryDialog(
                    None,
                    "Enter files/folders to untrack (separate with spaces):\n\nExample: .github .vscode __pycache__ temp.txt",
                    "Git Untrack Files/Folders",
                    ""  # Empty default value
                )
                dlg.SetSize(wx.Size(500, 180))
                
                if dlg.ShowModal() == wx.ID_OK:
                    untrack_input = dlg.GetValue().strip()
                    result_container["value"] = untrack_input if untrack_input else None
                else:
                    result_container["value"] = None  # User cancelled
                dlg.Destroy()
            except Exception as e:
                print(f"❌ Error showing GUI dialog: {e}")
                result_container["value"] = None
            finally:
                result_container["done"] = True
        
        # Check if we're on the main thread using threading
        try:
            main_thread = threading.main_thread()
            current_thread = threading.current_thread()
            
            if current_thread == main_thread:
                return GitOperations._get_untrack_input_gui()
            else:
                # Use CallAfter to execute on main thread
                wx.CallAfter(show_dialog)
                
                # Wait for dialog to complete
                while not result_container["done"]:
                    threading.Event().wait(0.1)
                
                return result_container["value"]
        except:
            # Fallback if wx not available or other issues
            return GitOperations._get_untrack_input_gui()

    @staticmethod
    def untrack_commit_push(app=None):
        """
        Untrack files/folders, commit, and push to remote repository.
        This removes files from Git tracking without deleting them from the filesystem.
        
        Args:
            app: TermTools app instance
        """
        print("🔧 Git Untrack, Commit & Push Operation")
        print("="*60)
        print("💡 This will remove files/folders from Git tracking without deleting them from disk")
        print("   Files will remain on your filesystem but won't be tracked by Git anymore")
        print("")
        
        # Step 1: Get files/folders to untrack
        print("📝 Step 1/4: Getting files/folders to untrack...")
        untrack_input = GitOperations._get_untrack_input(app)
        
        if not untrack_input:
            print("❌ Operation cancelled - no files/folders specified")
            return
        
        # Parse the input into a list of files/folders
        files_to_untrack = untrack_input.split()
        
        if not files_to_untrack:
            print("❌ Operation cancelled - no files/folders specified")
            return
        
        print(f"📂 Files/folders to untrack: {', '.join(files_to_untrack)}")
        
        # Show confirmation with exact commands
        print("\n🔍 Commands that will be executed:")
        git_rm_command = ['git', 'rm', '-r', '--cached'] + files_to_untrack
        print(f"   {' '.join(git_rm_command)}")
        commit_message = f"Remove {' '.join(files_to_untrack)} from tracking"
        print(f"   git commit -m \"{commit_message}\"")
        print(f"   git push origin main")
        
        # Get confirmation
        confirmation_message = (
            f"⚠️  About to untrack: {', '.join(files_to_untrack)}\n\n"
            f"Commands to execute:\n"
            f"• {' '.join(git_rm_command)}\n"
            f"• git commit -m \"{commit_message}\"\n"
            f"• git push origin main\n\n"
            f"Files will remain on disk but won't be tracked by Git.\n"
            f"Continue?"
        )
        
        if not GitOperations._get_confirmation(confirmation_message, "Confirm Git Untrack Operation", app):
            print("❌ Operation cancelled by user")
            return
        
        # Step 2: git rm --cached
        print("\n🗑️  Step 2/4: Removing files from Git tracking...")
        try:
            result = subprocess.run(
                git_rm_command,
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Files removed from Git tracking successfully")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error removing files from tracking: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            print("💡 Tip: Make sure the files exist and are currently tracked by Git")
            return
        
        # Step 3: git commit
        print("\n💾 Step 3/4: Committing changes...")
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
        
        # Step 4: git push
        print("\n🚀 Step 4/4: Pushing to remote...")
        try:
            result = subprocess.run(
                ['git', 'push', 'origin', 'main'],
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
        print("🎉 All untrack operations completed successfully!")
        print("📋 Summary:")
        print(f"   • Removed from Git tracking: {', '.join(files_to_untrack)}")
        print(f"   • Files remain on disk but are no longer tracked by Git")
        print(f"   • Changes committed and pushed to remote repository")

    @staticmethod
    def initialize_repo(app=None):
        """
        Initialize a Git repository and add a remote origin.
        
        Args:
            app: TermTools app instance
        """
        print("\n🔧 Initialize Git Repository")
        print("="*60)
        
        # Check if git is available
        try:
            subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                check=True
            )
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH.")
            return
        except subprocess.CalledProcessError:
            print("❌ Error checking Git installation.")
            return
        
        # Check if already a git repository
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print("⚠️  This folder is already a Git repository.")
                print(f"   Git directory: {result.stdout.strip()}")
                
                # Check if remote already exists
                result = subprocess.run(
                    ['git', 'remote', 'get-url', 'origin'],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    print(f"   Remote 'origin' already configured: {result.stdout.strip()}")
                
                if not GitOperations._get_confirmation(
                    "Git repository already initialized. Do you want to continue and update the remote?",
                    "Git Already Initialized",
                    app
                ):
                    print("❌ Operation cancelled.")
                    return
        except Exception as e:
            print(f"⚠️  Could not check repository status: {e}")
        
        # Get repository URL from user
        print("\n📝 Step 1/3: Getting repository URL...")
        print("\n📋 Repository URL Format Examples:")
        print("   • HTTPS: https://github.com/username/repository.git")
        print("   • SSH:   git@github.com:username/repository.git")
        print("")
        
        repo_url = GitOperations._get_repo_url_input(app)
        
        if not repo_url:
            print("❌ Operation cancelled - no repository URL specified")
            return
        
        # Extract repository name from URL for display
        repo_name = repo_url
        if repo_url.endswith('.git'):
            repo_name = repo_url.rsplit('/', 1)[-1][:-4]  # Remove .git extension
        elif '/' in repo_url:
            repo_name = repo_url.rsplit('/', 1)[-1]
        
        print(f"📂 Repository URL: {repo_url}")
        print(f"📦 Repository name: {repo_name}")
        
        # Show confirmation with exact commands
        print("\n🔍 Commands that will be executed:")
        print("   git init")
        print(f"   git remote add origin {repo_url}")
        
        confirmation_message = (
            f"About to initialize Git repository:\n\n"
            f"Repository URL: {repo_url}\n"
            f"Repository name: {repo_name}\n\n"
            f"Commands to execute:\n"
            f"1. git init\n"
            f"2. git remote add origin {repo_url}\n\n"
            f"Continue?"
        )
        
        if not GitOperations._get_confirmation(confirmation_message, "Confirm Git Initialization", app):
            print("❌ Operation cancelled by user")
            return
        
        # Step 2: git init
        print("\n🎬 Step 2/3: Initializing Git repository...")
        try:
            result = subprocess.run(
                ['git', 'init'],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Git repository initialized successfully")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error initializing repository: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            return
        
        # Step 3: git remote add origin
        print("\n🌐 Step 3/3: Adding remote origin...")
        try:
            # First, check if origin already exists and remove it
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                print("   ℹ️  Remote 'origin' already exists, removing...")
                subprocess.run(
                    ['git', 'remote', 'remove', 'origin'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("   ✅ Old remote removed")
            
            # Add the new remote
            result = subprocess.run(
                ['git', 'remote', 'add', 'origin', repo_url],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Remote 'origin' added successfully")
            
            # Verify the remote
            result = subprocess.run(
                ['git', 'remote', '-v'],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                print("   Remote configuration:")
                for line in result.stdout.strip().split('\n'):
                    print(f"     {line}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error adding remote origin: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            return
        
        print("\n" + "="*60)
        print("🎉 Git repository initialized successfully!")
        print("📋 Summary:")
        print(f"   • Repository initialized in current folder")
        print(f"   • Remote 'origin' configured: {repo_url}")
        print(f"   • Repository name: {repo_name}")
        print("\n💡 Next steps:")
        print("   • Add files: git add .")
        print("   • Create first commit: git commit -m \"Initial commit\"")
        print("   • Push to remote: git push -u origin main")


# Register menu items using the blueprint route decorator
@git_operations_bp.route(
    "1",
    "Initialize Git Repo",
    "Initialize repository and add remote origin",
    "🔧 GIT OPERATIONS",
    order=1
)
def git_initialize_repo(app=None):
    """Menu handler for initializing git repository"""
    GitOperations.initialize_repo(app)


@git_operations_bp.route(
    "1.1",
    "Quick Commit & Push",
    "Add, commit, and push changes",
    "🔧 GIT OPERATIONS",
    order=2
)
def git_quick_commit_push(app=None):
    """Menu handler for quick commit and push"""
    GitOperations.quick_commit_push(app)


@git_operations_bp.route(
    "1.5", 
    "Untrack, Commit & Push",
    "Remove files/folders from Git tracking",
    "🔧 GIT OPERATIONS",
    order=3
)
def git_untrack_commit_push(app=None):
    """Menu handler for untrack, commit and push"""
    GitOperations.untrack_commit_push(app)


# Initialize the module
@git_operations_bp.on_init
def init_git_module(app):
    """Initialize Git operations module"""
    print("🔧 Git Operations module initialized")
    app.set_config("git_enabled", True)
