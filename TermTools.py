#!/usr/bin/env python3
"""
TermTools - Python Project Manager
Built by Asesh Basu

Main entry point for the modular TermTools application.
GUI interface with wxPython.

Usage:
python TermTools.py

"""

import sys
import os

def main():
    """Entry point of the TermTools application"""
    try:
        # Run in GUI mode
        try:
            from core.wx_app import run_wx_app
            run_wx_app()
        except ImportError as e:
            print(f"❌ Error: wxPython is not installed.")
            print(f"   Please install it using: pip install wxPython")
            print(f"\n   Technical details: {e}")
            sys.exit(1)
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting TermTools: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
