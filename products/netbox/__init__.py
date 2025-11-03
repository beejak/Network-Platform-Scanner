"""NetBox plugin for IPAM/DCIM management."""

from .plugin import NetBoxPlugin

# CRITICAL: Export the Plugin class so registry can find it
Plugin = NetBoxPlugin

__all__ = ['Plugin', 'NetBoxPlugin']
