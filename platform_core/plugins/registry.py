"""
Plugin registry for the platform.
"""
import importlib
import pkgutil
from typing import Dict, Any, List

from platform_core.plugins.base import BasePlugin

class PluginRegistry:
    """
    Manages the discovery, loading, and lifecycle of plugins.
    """
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.load_order: List[str] = []

    def discover_plugins(self, package="products"):
        """
        Discover plugins in the specified package.
        """
        import products
        for _, name, _ in pkgutil.iter_modules(products.__path__):
            try:
                module = importlib.import_module(f"{package}.{name}")
                plugin_class = getattr(module, "Plugin", None)
                if plugin_class and issubclass(plugin_class, BasePlugin):
                    plugin_instance = plugin_class({})
                    self.register_plugin(plugin_instance)
            except Exception as e:
                print(f"Failed to load plugin {name}: {e}")

    def register_plugin(self, plugin: BasePlugin):
        """
        Register a plugin instance.
        """
        self.plugins[plugin.get_metadata().name] = plugin
        self.load_order.append(plugin.get_metadata().name)

    async def initialize_all(self, **kwargs):
        """
        Initialize all registered plugins.
        """
        for name in self.load_order:
            await self.plugins[name].initialize(**kwargs)

    async def shutdown_all(self):
        """
        Shutdown all registered plugins.
        """
        for name in reversed(self.load_order):
            await self.plugins[name].shutdown()

    async def health_check_all(self) -> List[Dict[str, Any]]:
        """
        Run a health check on all registered plugins.
        """
        health_checks = []
        for name in self.load_order:
            health = await self.plugins[name].health_check()
            health_checks.append(health)
        return health_checks

plugin_registry = PluginRegistry()
