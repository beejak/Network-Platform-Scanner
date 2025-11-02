"""
Plugin registry for loading and managing plugins.
"""
import importlib
import logging
import pkgutil
from typing import Dict, List, Optional

from .base import BasePlugin, PluginMetadata

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for all plugins."""

    def __init__(self) -> None:
        self.plugins: Dict[str, BasePlugin] = {}
        self.load_order: List[str] = []

    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Register a plugin instance."""
        name = plugin.metadata.name
        if name in self.plugins:
            logger.warning(f"Plugin {name} already registered")
            return False

        self.plugins[name] = plugin
        logger.info(f"Registered plugin: {name} v{plugin.metadata.version}")
        return True

    def discover_plugins(self, plugin_directory: str = "products") -> None:
        """Auto-discover plugins in the products directory."""
        import products  # The products package

        for importer, modname, ispkg in pkgutil.iter_modules(products.__path__):
            if ispkg:
                try:
                    module = importlib.import_module(f"products.{modname}")
                    # Look for Plugin class in module
                    if hasattr(module, "Plugin"):
                        plugin_class = getattr(module, "Plugin")
                        plugin_instance = plugin_class(config={})
                        self.register_plugin(plugin_instance)
                except Exception as e:
                    logger.error(f"Failed to load plugin {modname}: {e}")

    async def initialize_all(self) -> None:
        """Initialize all plugins in dependency order."""
        # Topological sort based on requires
        self.load_order = self._compute_load_order()

        for plugin_name in self.load_order:
            plugin = self.plugins[plugin_name]
            try:
                await plugin.initialize()
                plugin.is_initialized = True
                logger.info(f"Initialized plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Failed to initialize {plugin_name}: {e}")
                raise

    def _compute_load_order(self) -> List[str]:
        """Compute plugin load order based on dependencies."""
        # Simple topological sort
        visited: set[str] = set()
        order: List[str] = []

        def visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)
            plugin = self.plugins[name]
            for dep in plugin.metadata.requires:
                if dep in self.plugins:
                    visit(dep)
            order.append(name)

        for name in self.plugins:
            visit(name)

        return order


# Global registry instance
plugin_registry = PluginRegistry()
