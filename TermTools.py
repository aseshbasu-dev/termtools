#!/usr/bin/env python3
"""
TermTools - Python Project Manager
Built by Asesh Basu

Main entry point for the modular TermTools application.
"""

from core import create_app

def main():
    """Entry point of the TermTools application"""
    try:
        app = create_app()
        app.run()
    except ImportError as e:
        print(f"Error importing modules: {e}")
    except Exception as e:
        print(f"Error starting TermTools: {e}")

if __name__ == "__main__":
    main()
