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
    def quick_commit_push():
        """
        Execute git add, commit, and push in sequence.
        Equivalent to: git add . ; git commit -m "bug fixes" ; git push
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
                return
        except FileNotFoundError:
            print("❌ Git is not installed or not in PATH.")
            return
        
        # Get commit message from user
        print("\n📝 Enter commit message (or press Enter for 'bug fixes'):")
        commit_message = input("   > ").strip()
        if not commit_message:
            commit_message = "bug fixes"
        
        print(f"\n🎯 Commit message: '{commit_message}'")
        print("\nProceed with the following operations?")
        print("   1. git add .")
        print(f"   2. git commit -m \"{commit_message}\"")
        print("   3. git push")
        
        response = input("\nContinue? (Y/n): ").strip().lower()
        if response not in ['y', 'yes', '']:
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
    GitOperations.quick_commit_push()


# Initialize the module
@git_operations_bp.on_init
def init_git_module(app):
    """Initialize Git operations module"""
    print("🔧 Git Operations module initialized")
    app.set_config("git_enabled", True)
