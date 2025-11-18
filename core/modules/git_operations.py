"""
Git Operations Module for TermTools
Built by Asesh Basu

This module provides Git repository management functionality including
quick commit and push operations.
"""

import subprocess
import sys
import os
from ..blueprint import Blueprint


def _get_subprocess_flags():
    """Get subprocess creation flags to prevent console window flashing on Windows"""
    if os.name == 'nt':
        return {'creationflags': subprocess.CREATE_NO_WINDOW}
    return {}

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
        # Check if input was pre-gathered in main thread
        if app:
            user_input = app.get_config('_git_user_input')
            if user_input and 'commit_message' in user_input:
                return user_input['commit_message']
        
        return GitOperations._get_commit_message_gui_threadsafe()
    
    @staticmethod
    def _get_commit_message_gui():
        """Get commit message via GUI dialog"""
        try:
            from PyQt6.QtWidgets import QApplication, QInputDialog
            
            if QApplication.instance():
                text, ok = QInputDialog.getText(
                    None,
                    "Git Commit Message",
                    "Enter commit message:",
                    text="bug fixes"  # Default value
                )
                
                if ok:
                    commit_message = text.strip()
                    return commit_message if commit_message else "bug fixes"
                else:
                    return None  # User cancelled
            else:
                print("❌ GUI unavailable")
                return "bug fixes"
        except Exception as e:
            print(f"❌ Error showing GUI dialog: {e}")
            return "bug fixes"  # Fallback to default message
    
    @staticmethod
    def _get_commit_message_gui_threadsafe():
        """Thread-safe version for GUI operations - PyQt6 handles threading automatically"""
        # PyQt6 handles thread safety automatically, just call the GUI method
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
            from PyQt6.QtWidgets import QApplication, QMessageBox
            
            if QApplication.instance():
                reply = QMessageBox.question(
                    None,
                    title,
                    message,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                return reply == QMessageBox.StandardButton.Yes
            else:
                print("❌ GUI unavailable")
                return False
        except Exception as e:
            print(f"❌ Error showing GUI confirmation: {e}")
            return False  # Default to not confirming if error occurs
    
    @staticmethod
    def _get_confirmation_gui_threadsafe(message, title):
        """Thread-safe version of confirmation dialog - PyQt6 handles threading automatically"""
        # PyQt6 handles thread safety automatically, just call the GUI method
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
            , **_get_subprocess_flags())
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
            , **_get_subprocess_flags())
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
            , **_get_subprocess_flags())
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
            , **_get_subprocess_flags())
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
    def _get_branch_name_input(app=None):
        """
        Get branch name from user via GUI dialog.
        Returns the branch name string or None if cancelled.
        """
        # PyQt6 handles threading automatically
        return GitOperations._get_branch_name_input_gui()

    @staticmethod
    def _get_branch_name_input_gui():
        """Show branch name dialog using PyQt6."""
        try:
            from PyQt6.QtWidgets import QApplication, QInputDialog
            
            if QApplication.instance():
                text, ok = QInputDialog.getText(
                    None,
                    "Create & Switch Branch",
                    "Enter new branch name:",
                    text="feature/your-branch"
                )
                
                if ok:
                    val = text.strip()
                    return val if val else None
                else:
                    return None
            else:
                print("❌ GUI unavailable")
                return None
        except Exception as e:
            print(f"❌ Error showing branch name dialog: {e}")
            return None

    @staticmethod
    def create_branch_and_push(app=None):
        """
        Create a new branch, commit changes and push with upstream tracking.

        Commands displayed and executed:
        git checkout -b <branch>
        git add .
        git commit -m "<commit>"
        git push -u origin <branch>
        """
        print("\n🔧 Create & Switch Branch")
        print("="*60)

        # Ensure git repo
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                check=False
            , **_get_subprocess_flags())
            if result.returncode != 0:
                print("❌ Not a git repository. Please initialize git first.")
                return
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH.")
            return

        # Get branch name
        branch_name = GitOperations._get_branch_name_input(app)
        if branch_name is None:
            print("❌ Operation cancelled (no branch name provided).")
            return

        # Get first commit message
        commit_message = GitOperations._get_commit_message_input(app)
        if commit_message is None:
            print("❌ Operation cancelled.")
            return

        # Show commands that will be executed
        confirmation_message = (
            f"You are about to execute the following Git commands:\n\n"
            f"1. git checkout -b {branch_name}\n"
            f"2. git add .\n"
            f"3. git commit -m \"{commit_message}\"\n"
            f"4. git push -u origin {branch_name}\n\n"
            f"Do you want to proceed?"
        )

        if not GitOperations._get_confirmation(confirmation_message, "Create & Switch Branch Confirmation", app):
            print("❌ Operation cancelled by user.")
            return

        # Step 1: git checkout -b <branch>
        print("\n📦 Step 1/4: Creating and switching to branch...")
        try:
            subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            print(f"✅ Switched to new branch '{branch_name}'")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating/switching branch: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            return

        # Step 2: git add .
        print("\n📦 Step 2/4: Adding all changes...")
        try:
            subprocess.run(
                ['git', 'add', '.'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            print("✅ All changes staged successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error staging changes: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            return

        # Step 3: git commit
        print("\n💾 Step 3/4: Committing changes...")
        try:
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            print(f"✅ Changes committed successfully")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            if "nothing to commit" in (e.stdout or ""):
                print("ℹ️  Nothing to commit (working tree clean)")
                print("   Skipping push operation.")
                return
            else:
                print(f"❌ Error committing changes: {e}")
                if e.stderr:
                    print(f"   {e.stderr.strip()}")
                return

        # Step 4: git push -u origin <branch>
        print("\n🚀 Step 4/4: Pushing to remote and setting upstream...")
        try:
            result = subprocess.run(
                ['git', 'push', '-u', 'origin', branch_name],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            print("✅ Branch pushed and upstream set successfully!")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            if result.stderr:
                print(f"   {result.stderr.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error pushing branch: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            return

        print("\n" + "="*60)
        print(f"🎉 Branch '{branch_name}' created, committed and pushed.")

    @staticmethod
    def _get_repo_url_input(app=None):
        """
        Get repository URL from user via GUI dialog.
        
        Args:
            app: TermTools app instance (used to detect GUI mode)
            
        Returns:
            str: Repository URL or None if cancelled
        """
        # Check if input was pre-gathered in main thread
        if app:
            user_input = app.get_config('_git_user_input')
            if user_input and 'remote_url' in user_input:
                return user_input['remote_url']
            if user_input and 'new_remote_url' in user_input:
                return user_input['new_remote_url']
        
        return GitOperations._get_repo_url_input_gui_threadsafe()
    
    @staticmethod
    def _get_repo_url_input_gui():
        """Get repository URL via GUI dialog"""
        try:
            from PyQt6.QtWidgets import QApplication, QInputDialog
            
            instructions = (
                "Enter your Git repository URL.\n\n"
                "Repository URL formats:\n"
                "• HTTPS: https://github.com/username/repository.git\n"
                "• SSH:   git@github.com:username/repository.git\n\n"
                "Example: https://github.com/aseshbasu-dev/termtools.git"
            )
            
            if QApplication.instance():
                text, ok = QInputDialog.getText(
                    None,
                    "Git Repository URL",
                    instructions,
                    text=""  # Empty default value
                )
                
                if ok:
                    repo_url = text.strip()
                    return repo_url if repo_url else None
                else:
                    return None  # User cancelled
            else:
                print("❌ GUI unavailable")
                return None
        except Exception as e:
            print(f"❌ Error showing GUI dialog: {e}")
            return None
    
    @staticmethod
    def _get_repo_url_input_gui_threadsafe():
        """Thread-safe version - PyQt6 handles threading automatically"""
        # PyQt6 handles thread safety automatically, just call the GUI method
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
        # Check if input was pre-gathered in main thread
        if app:
            user_input = app.get_config('_git_user_input')
            if user_input and 'untrack_path' in user_input:
                return user_input['untrack_path']
        
        return GitOperations._get_untrack_input_gui_threadsafe()
    
    @staticmethod
    def _get_untrack_input_gui():
        """Get files/folders to untrack via GUI dialog"""
        try:
            from PyQt6.QtWidgets import QApplication, QInputDialog
            
            if QApplication.instance():
                text, ok = QInputDialog.getText(
                    None,
                    "Git Untrack Files/Folders",
                    "Enter files/folders to untrack (separate with spaces):\n\nExample: .github .vscode __pycache__ temp.txt",
                    text=""  # Empty default value
                )
                
                if ok:
                    untrack_input = text.strip()
                    return untrack_input if untrack_input else None
                else:
                    return None  # User cancelled
            else:
                print("❌ GUI unavailable")
                return None
        except Exception as e:
            print(f"❌ Error showing GUI dialog: {e}")
            return None
    
    @staticmethod
    def _get_untrack_input_gui_threadsafe():
        """Thread-safe version - PyQt6 handles threading automatically"""
        # PyQt6 handles thread safety automatically, just call the GUI method
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
            , **_get_subprocess_flags())
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
            , **_get_subprocess_flags())
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
            , **_get_subprocess_flags())
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
            , **_get_subprocess_flags())
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
            , **_get_subprocess_flags())
            if result.returncode == 0:
                print("⚠️  This folder is already a Git repository.")
                print(f"   Git directory: {result.stdout.strip()}")
                
                # Check if remote already exists
                result = subprocess.run(
                    ['git', 'remote', 'get-url', 'origin'],
                    capture_output=True,
                    text=True,
                    check=False
                , **_get_subprocess_flags())
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
        print("\n📝 Step 1/6: Getting repository URL...")
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
        print("   git add .")
        print("   git commit -m \"initial upload\"")
        print("   git push -u origin main")
        
        confirmation_message = (
            f"About to initialize Git repository:\n\n"
            f"Repository URL: {repo_url}\n"
            f"Repository name: {repo_name}\n\n"
            f"Commands to execute:\n"
            f"1. git init\n"
            f"2. git remote add origin {repo_url}\n"
            f"3. git add .\n"
            f"4. git commit -m \"initial upload\"\n"
            f"5. git push -u origin main\n\n"
            f"Continue?"
        )
        
        if not GitOperations._get_confirmation(confirmation_message, "Confirm Git Initialization", app):
            print("❌ Operation cancelled by user")
            return
        
        # Step 2: git init
        print("\n🎬 Step 2/5: Initializing Git repository...")
        try:
            result = subprocess.run(
                ['git', 'init'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            print("✅ Git repository initialized successfully")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error initializing repository: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            return
        
        # Step 3: git remote add origin
        print("\n🌐 Step 3/5: Adding remote origin...")
        try:
            # First, check if origin already exists and remove it
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                check=False
            , **_get_subprocess_flags())
            if result.returncode == 0:
                print("   ℹ️  Remote 'origin' already exists, removing...")
                subprocess.run(
                    ['git', 'remote', 'remove', 'origin'],
                    capture_output=True,
                    text=True,
                    check=True
                , **_get_subprocess_flags())
                print("   ✅ Old remote removed")
            
            # Add the new remote
            result = subprocess.run(
                ['git', 'remote', 'add', 'origin', repo_url],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            print("✅ Remote 'origin' added successfully")
            
            # Verify the remote
            result = subprocess.run(
                ['git', 'remote', '-v'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            if result.stdout:
                print("   Remote configuration:")
                for line in result.stdout.strip().split('\n'):
                    print(f"     {line}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error adding remote origin: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            return
        
        # Step 4: git add .
        print("\n📦 Step 4/5: Adding all files...")
        try:
            result = subprocess.run(
                ['git', 'add', '.'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            print("✅ All files staged successfully")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error staging files: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            return
        
        # Step 5: git commit -m "initial upload"
        print("\n💾 Step 5/5: Creating initial commit...")
        try:
            result = subprocess.run(
                ['git', 'commit', '-m', 'initial upload'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            print("✅ Initial commit created successfully")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            if "nothing to commit" in e.stdout:
                print("ℹ️  Nothing to commit (working tree clean)")
            else:
                print(f"❌ Error creating commit: {e}")
                if e.stderr:
                    print(f"   {e.stderr.strip()}")
                return
        
        # Step 6: git push -u origin main
        print("\n🚀 Step 6/6: Pushing to remote repository...")
        try:
            result = subprocess.run(
                ['git', 'push', '-u', 'origin', 'main'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            print("✅ Changes pushed to remote successfully!")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            if result.stderr:  # Git often outputs to stderr even on success
                print(f"   {result.stderr.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error pushing to remote: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            print("\n💡 Tip: Make sure the repository exists on the remote server")
            print("   and you have the necessary permissions to push.")
            return
        
        print("\n" + "="*60)
        print("🎉 Git repository initialized and uploaded successfully!")
        print("📋 Summary:")
        print(f"   • Repository initialized in current folder")
        print(f"   • Remote 'origin' configured: {repo_url}")
        print(f"   • Repository name: {repo_name}")
        print(f"   • All files added, committed, and pushed to remote")
        print(f"   • Branch 'main' is now tracking 'origin/main'")

    @staticmethod
    def show_status(app=None):
        """
        Display the current git status of the repository.
        Shows modified files, staged files, untracked files, and current branch.
        
        Args:
            app: TermTools app instance
        """
        print("\n🔧 Git Status")
        print("="*60)
        
        # Check if git is available
        try:
            subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH.")
            return
        except subprocess.CalledProcessError:
            print("❌ Error checking Git installation.")
            return
        
        # Check if we're in a git repository
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                check=False
            , **_get_subprocess_flags())
            if result.returncode != 0:
                print("❌ Not a git repository.")
                print("   Use 'Initialize Git Repo' to set up git in this folder.")
                return
        except Exception as e:
            print(f"❌ Error checking repository status: {e}")
            return
        
        # Get current branch
        print("\n📌 Current Branch:")
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            current_branch = result.stdout.strip()
            if current_branch:
                print(f"   🌿 {current_branch}")
            else:
                print("   ⚠️  Detached HEAD state")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error getting branch: {e.stderr.strip() if e.stderr else str(e)}")
        
        # Get remote information
        print("\n🌐 Remote Repository:")
        try:
            result = subprocess.run(
                ['git', 'remote', '-v'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            if result.stdout:
                remotes = {}
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        url = parts[1]
                        if name not in remotes:
                            remotes[name] = url
                
                for name, url in remotes.items():
                    print(f"   📡 {name}: {url}")
            else:
                print("   ⚠️  No remote repositories configured")
        except subprocess.CalledProcessError:
            print("   ⚠️  No remote repositories configured")
        
        # Get git status
        print("\n📊 Repository Status:")
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            
            if result.stdout.strip():
                # Parse the status output
                staged_files = []
                modified_files = []
                untracked_files = []
                deleted_files = []
                
                for line in result.stdout.strip().split('\n'):
                    if not line:
                        continue
                    
                    status = line[:2]
                    filename = line[3:].strip()
                    
                    # Check status codes
                    if status[0] in ['A', 'M', 'D', 'R', 'C']:
                        staged_files.append((status[0], filename))
                    if status[1] == 'M':
                        modified_files.append(filename)
                    elif status[1] == 'D':
                        deleted_files.append(filename)
                    if status == '??':
                        untracked_files.append(filename)
                
                # Display categorized files
                if staged_files:
                    print("\n   ✅ Staged files (ready to commit):")
                    for status_code, filename in staged_files:
                        status_symbol = {
                            'A': '➕',  # Added
                            'M': '✏️',  # Modified
                            'D': '🗑️',  # Deleted
                            'R': '📝',  # Renamed
                            'C': '📋'   # Copied
                        }.get(status_code, '•')
                        print(f"      {status_symbol} {filename}")
                
                if modified_files:
                    print("\n   📝 Modified files (not staged):")
                    for filename in modified_files:
                        print(f"      ✏️  {filename}")
                
                if deleted_files:
                    print("\n   🗑️  Deleted files (not staged):")
                    for filename in deleted_files:
                        print(f"      ❌ {filename}")
                
                if untracked_files:
                    print("\n   ❓ Untracked files:")
                    for filename in untracked_files:
                        print(f"      📄 {filename}")
                
                # Summary count
                total_changes = len(staged_files) + len(modified_files) + len(deleted_files) + len(untracked_files)
                print(f"\n   📊 Total: {total_changes} file(s) with changes")
                
            else:
                print("   ✅ Working tree clean - no changes detected")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error getting status: {e}")
            if e.stderr:
                print(f"      {e.stderr.strip()}")
        
        # Get last commit info
        print("\n💾 Last Commit:")
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--oneline'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            if result.stdout.strip():
                print(f"   📌 {result.stdout.strip()}")
            else:
                print("   ⚠️  No commits yet")
        except subprocess.CalledProcessError:
            print("   ⚠️  No commits yet")
        
        # Get ahead/behind info
        print("\n🔄 Sync Status:")
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--left-right', '--count', 'HEAD...@{u}'],
                capture_output=True,
                text=True,
                check=False
            , **_get_subprocess_flags())
            
            if result.returncode == 0 and result.stdout.strip():
                ahead, behind = result.stdout.strip().split()
                ahead, behind = int(ahead), int(behind)
                
                if ahead > 0 and behind > 0:
                    print(f"   ⚠️  Branch diverged: {ahead} commit(s) ahead, {behind} commit(s) behind remote")
                elif ahead > 0:
                    print(f"   ⬆️  {ahead} commit(s) ahead of remote (need to push)")
                elif behind > 0:
                    print(f"   ⬇️  {behind} commit(s) behind remote (need to pull)")
                else:
                    print("   ✅ Up to date with remote")
            else:
                print("   ⚠️  No upstream branch configured")
        except subprocess.CalledProcessError:
            print("   ⚠️  No upstream branch configured")
        except Exception as e:
            print(f"   ⚠️  Could not determine sync status: {e}")
        
        print("\n" + "="*60)
        print("💡 Tip: Use 'Quick Commit & Push' to commit and push changes")

    @staticmethod
    def switch_repo(app=None):
        """
        Switch to a new remote repository URL.
        
        Args:
            app: TermTools app instance
        """
        print("\n🔧 Switch Git Repository")
        print("="*60)
        
        # Check if git is available
        try:
            subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH.")
            return
        except subprocess.CalledProcessError:
            print("❌ Error checking Git installation.")
            return
        
        # Check if we're in a git repository
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                check=False
            , **_get_subprocess_flags())
            if result.returncode != 0:
                print("❌ Not a git repository. Please initialize git first.")
                print("   Use: git init")
                return
        except Exception as e:
            print(f"❌ Error checking repository status: {e}")
            return
        
        # Show current remote configuration
        print("\n📋 Current Remote Configuration:")
        try:
            result = subprocess.run(
                ['git', 'remote', '-v'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    print(f"   {line}")
            else:
                print("   No remotes configured")
        except subprocess.CalledProcessError as e:
            print("   No remotes configured")
        
        # Get new repository URL from user
        print("\n📝 Getting new repository URL...")
        print("\n📋 Repository URL Format Examples:")
        print("   • HTTPS: https://github.com/username/repository.git")
        print("   • SSH:   git@github.com:username/repository.git")
        print("")
        
        new_repo_url = GitOperations._get_repo_url_input(app)
        
        if not new_repo_url:
            print("❌ Operation cancelled - no repository URL specified")
            return
        
        # Extract repository name from URL for display
        repo_name = new_repo_url
        if new_repo_url.endswith('.git'):
            repo_name = new_repo_url.rsplit('/', 1)[-1][:-4]  # Remove .git extension
        elif '/' in new_repo_url:
            repo_name = new_repo_url.rsplit('/', 1)[-1]
        
        print(f"📂 New repository URL: {new_repo_url}")
        print(f"📦 Repository name: {repo_name}")
        
        # Show the exact command that will be executed
        git_command = f"git remote set-url origin {new_repo_url}"
        print("\n🔍 Command that will be executed:")
        print(f"   {git_command}")
        
        # Get confirmation
        confirmation_message = (
            f"About to switch to new repository:\n\n"
            f"New repository URL: {new_repo_url}\n"
            f"Repository name: {repo_name}\n\n"
            f"Command to execute:\n"
            f"{git_command}\n\n"
            f"⚠️  This will change the remote 'origin' URL.\n"
            f"Continue?"
        )
        
        if not GitOperations._get_confirmation(confirmation_message, "Confirm Repository Switch", app):
            print("❌ Operation cancelled by user")
            return
        
        # Execute git remote set-url origin
        print("\n🌐 Switching to new repository...")
        try:
            result = subprocess.run(
                ['git', 'remote', 'set-url', 'origin', new_repo_url],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            print("✅ Remote repository URL updated successfully")
            
            # Verify the new remote configuration
            result = subprocess.run(
                ['git', 'remote', '-v'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            if result.stdout:
                print("\n📋 Updated Remote Configuration:")
                for line in result.stdout.strip().split('\n'):
                    print(f"   {line}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error updating remote URL: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            print("\n💡 Tip: Make sure the remote 'origin' exists.")
            print("   You can add it with: git remote add origin <url>")
            return
        
        # Push to the new remote repository with tracking
        print("\n📤 Pushing to new repository...")
        try:
            result = subprocess.run(
                ['git', 'push', '-u', 'origin', 'main'],
                capture_output=True,
                text=True,
                check=True
            , **_get_subprocess_flags())
            print("✅ Successfully pushed to new repository")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            if result.stderr:
                # Git push outputs to stderr even on success
                print(f"   {result.stderr.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error pushing to new repository: {e}")
            if e.stderr:
                print(f"   {e.stderr.strip()}")
            print("\n💡 Tip: You may need to:")
            print("   • Ensure the remote repository exists and is accessible")
            print("   • Check your authentication credentials")
            print("   • Manually push later with: git push -u origin main")
            # Don't return here - we still want to show the summary
        
        print("\n" + "="*60)
        print("🎉 Repository switched successfully!")
        print("📋 Summary:")
        print(f"   • Remote 'origin' now points to: {new_repo_url}")
        print(f"   • Repository name: {repo_name}")
        print(f"   • Code pushed to new repository with tracking")
        print("\n💡 Next steps:")
        print("   • Verify connection: git fetch origin")
        print("   • Pull latest changes: git pull origin main")


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
    "1.4",
    "Show Git Status",
    "Display current repository status",
    "🔧 GIT OPERATIONS",
    order=4
)
def git_show_status(app=None):
    """Menu handler for showing git status"""
    GitOperations.show_status(app)


@git_operations_bp.route(
    "1.2",
    "Switch Repository",
    "Change remote repository URL",
    "🔧 GIT OPERATIONS",
    order=3
)
def git_switch_repo(app=None):
    """Menu handler for switching repository"""
    GitOperations.switch_repo(app)


@git_operations_bp.route(
    "1.5", 
    "Untrack, Commit & Push",
    "Remove files/folders from Git tracking",
    "🔧 GIT OPERATIONS",
    order=4
)
def git_untrack_commit_push(app=None):
    """Menu handler for untrack, commit and push"""
    GitOperations.untrack_commit_push(app)


@git_operations_bp.route(
    "1.3",
    "Create & Switch Branch",
    "Create a new branch, commit and push (set upstream)",
    "🔧 GIT OPERATIONS",
    order=3
)
def git_create_and_switch_branch(app=None):
    """Menu handler for creating and switching to a new branch"""
    GitOperations.create_branch_and_push(app)


# Initialize the module
@git_operations_bp.on_init
def init_git_module(app):
    """Initialize Git operations module"""
    print("🔧 Git Operations module initialized")
    app.set_config("git_enabled", True)
