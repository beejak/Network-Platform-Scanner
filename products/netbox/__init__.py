"""NetBox plugin package."""
from .plugin import NetBoxPlugin

# Export Plugin for discovery
Plugin = NetBoxPlugin

__all__ = ['Plugin', 'NetBoxPlugin']
