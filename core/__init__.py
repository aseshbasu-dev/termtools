"""
TermTools Core - Modular Python Project Manager
Built by Asesh Basu

This package contains the core functionality of TermTools,
organized into modular components similar to Flask's blueprint system.
"""

from .blueprint import Blueprint, TermToolsApp
from .app import TermTools, create_app

__version__ = "1.0.0"
__author__ = "Asesh Basu"

__all__ = ['Blueprint', 'TermToolsApp', 'TermTools', 'create_app']