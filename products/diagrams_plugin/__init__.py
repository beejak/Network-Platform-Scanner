"""Diagrams plugin for infrastructure visualization."""

from .plugin import DiagramsPlugin

# CRITICAL: Export the Plugin class
Plugin = DiagramsPlugin

__all__ = ['Plugin', 'DiagramsPlugin']
