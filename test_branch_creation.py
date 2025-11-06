#!/usr/bin/env python3
"""
Test script for the new branch creation functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.modules.git_operations import GitOperations

def test_branch_creation():
    """Test the create_new_branch method with simulated inputs"""

    # Mock the input methods to return test values
    original_get_branch_name = GitOperations._get_branch_name_input
    original_get_commit_message = GitOperations._get_commit_message_input
    original_get_confirmation = GitOperations._get_confirmation

    def mock_branch_input(app=None):
        print("Mock: Branch name input - returning 'test-feature'")
        return "test-feature"

    def mock_commit_input(app=None):
        print("Mock: Commit message input - returning 'Initial commit for test feature'")
        return "Initial commit for test feature"

    def mock_confirmation(message, title="Confirmation", app=None):
        print(f"Mock: Confirmation dialog - message: {message[:100]}...")
        print("Mock: Returning True (confirmed)")
        return True

    # Replace the methods
    GitOperations._get_branch_name_input = mock_branch_input
    GitOperations._get_commit_message_input = mock_commit_input
    GitOperations._get_confirmation = mock_confirmation

    try:
        # Run the create_new_branch method
        print("Testing create_new_branch method...")
        GitOperations.create_new_branch()

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Restore original methods
        GitOperations._get_branch_name_input = original_get_branch_name
        GitOperations._get_commit_message_input = original_get_commit_message
        GitOperations._get_confirmation = original_get_confirmation

if __name__ == "__main__":
    test_branch_creation()