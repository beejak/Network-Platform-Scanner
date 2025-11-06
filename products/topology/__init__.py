"""Topology plugin package."""
from .plugin import TopologyPlugin

# Export Plugin for discovery
Plugin = TopologyPlugin

__all__ = ['Plugin', 'TopologyPlugin']
