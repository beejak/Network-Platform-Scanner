"""Diagrams plugin package."""
from .plugin import DiagramsPlugin

# Export Plugin for discovery
Plugin = DiagramsPlugin

__all__ = ['Plugin', 'DiagramsPlugin']
