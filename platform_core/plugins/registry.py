"""
Plugin registry for loading and managing plugins.
"""
from typing import Dict, List, Optional
from .base import BasePlugin, PluginMetadata
import importlib
import pkgutil
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for all plugins."""

    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.load_order: List[str] = []

    def clear(self):
        """Clears the registry of all plugins."""
        self.plugins.clear()
        self.load_order.clear()
        logger.info("Plugin registry cleared.")

    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Register a plugin instance."""
        name = plugin.metadata.name
        if name in self.plugins:
            logger.warning(f"Plugin {name} already registered")
            return False

        self.plugins[name] = plugin
        logger.info(f"Registered plugin: {name} v{plugin.metadata.version}")
        return True

    def discover_plugins(self, plugin_directory: str = "/app/products"):
        """
        Auto-discover plugins in the products directory.

        FIXED VERSION: Handles import path issues properly.
        """
        products_path = Path(plugin_directory).resolve()
        if str(products_path.parent) not in sys.path:
            sys.path.insert(0, str(products_path.parent))

        try:
            # Method 1: Try importing products as a package
            try:
                import products
                logger.info(f"Products package found at: {products.__file__}")
            except ImportError as e:
                logger.error(f"Could not import products package: {e}", exc_info=True)
                return

            # Iterate through submodules
            for importer, modname, ispkg in pkgutil.iter_modules(
                products.__path__,
                prefix="products."
            ):
                if ispkg:
                    logger.info(f"Discovering plugin module: {modname}")
                    try:
                        # Import the module
                        module = importlib.import_module(modname)
                        logger.info(f"Successfully imported module: {modname}")

                        # Look for Plugin class in module
                        if hasattr(module, 'Plugin'):
                            plugin_class = getattr(module, 'Plugin')
                            logger.info(f"Found Plugin class in {modname}")

                            # Instantiate plugin
                            plugin_instance = plugin_class(config={})
                            logger.info(f"Successfully instantiated plugin: {modname}")

                            # Register it
                            if self.register_plugin(plugin_instance):
                                logger.info(f"Successfully registered plugin from {modname}")
                            else:
                                logger.error(f"Failed to register plugin from {modname}")
                        else:
                            logger.warning(f"Module {modname} has no 'Plugin' class")

                    except Exception as e:
                        logger.error(f"Failed to load plugin {modname}: {e}", exc_info=True)

        except ImportError as e:
            logger.error(f"Could not import products package: {e}")
            logger.info("Attempting fallback discovery method...")
            self._discover_plugins_fallback(plugin_directory)

    def _discover_plugins_fallback(self, plugin_directory: str):
        """
        Fallback method: Manually add products directory to path.
        Use this if the normal import fails.
        """
        # Get absolute path to products directory
        current_dir = Path.cwd()
        products_path = current_dir / plugin_directory

        if not products_path.exists():
            logger.error(f"Products directory not found at {products_path}")
            return

        # Add to Python path if not already there
        products_parent = str(products_path.parent)
        if products_parent not in sys.path:
            sys.path.insert(0, products_parent)
            logger.info(f"Added {products_parent} to sys.path")

        # Now try importing again
        try:
            import products

            for item in products_path.iterdir():
                if item.is_dir() and not item.name.startswith('_'):
                    plugin_name = item.name
                    module_name = f"products.{plugin_name}"

                    try:
                        module = importlib.import_module(module_name)

                        if hasattr(module, 'Plugin'):
                            plugin_class = getattr(module, 'Plugin')
                            plugin_instance = plugin_class(config={})
                            self.register_plugin(plugin_instance)
                            logger.info(f"Registered plugin: {plugin_name}")
                    except Exception as e:
                        logger.error(f"Failed to load {plugin_name}: {e}")

        except ImportError as e:
            logger.error(f"Fallback discovery also failed: {e}")

    async def initialize_all(self, **kwargs):
        """Initialize all plugins in dependency order."""
        # Topological sort based on requires
        self.load_order = self._compute_load_order()

        logger.info(f"Initializing plugins in order: {self.load_order}")

        for plugin_name in self.load_order:
            plugin = self.plugins[plugin_name]
            try:
                logger.info(f"Initializing plugin: {plugin_name}")
                success = await plugin.initialize(**kwargs)

                if success:
                    plugin.is_initialized = True
                    logger.info(f"✅ Plugin {plugin_name} initialized successfully")
                else:
                    logger.error(f"❌ Plugin {plugin_name} initialization returned False")

            except Exception as e:
                logger.error(f"❌ Failed to initialize {plugin_name}: {e}", exc_info=True)
                raise

    async def shutdown_all(self):
        """Shutdown all plugins in reverse dependency order."""
        logger.info("Shutting down all plugins...")
        for plugin_name in reversed(self.load_order):
            plugin = self.plugins[plugin_name]
            try:
                logger.info(f"Shutting down plugin: {plugin_name}")
                await plugin.shutdown()
                logger.info(f"✅ Plugin {plugin_name} shut down successfully")
            except Exception as e:
                logger.error(f"❌ Failed to shut down {plugin_name}: {e}", exc_info=True)

    def _compute_load_order(self) -> List[str]:
        """Compute plugin load order based on dependencies."""
        visited = set()
        order = []

        def visit(name: str):
            if name in visited:
                return
            visited.add(name)

            if name not in self.plugins:
                logger.warning(f"Plugin {name} not found but required by another plugin")
                return

            plugin = self.plugins[name]

            # Visit dependencies first
            for dep in plugin.metadata.requires:
                if dep in self.plugins:
                    visit(dep)

            order.append(name)

        # Visit all plugins
        for name in self.plugins:
            visit(name)

        return order

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get plugin by name."""
        return self.plugins.get(name)

    def list_plugins(self) -> List[str]:
        """List all registered plugin names."""
        return list(self.plugins.keys())


# Global registry instance
plugin_registry = PluginRegistry()
