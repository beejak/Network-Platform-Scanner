#!/usr/bin/env python3
"""
Debug script to test plugin discovery.
Run this to see what's wrong with plugin loading.
"""
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger.info(f"Project root: {project_root}")
logger.info(f"Python path: {sys.path}")

# Try importing products
try:
    import products
    logger.info(f"✅ Products package imported from: {products.__file__}")
    logger.info(f"Products package path: {products.__path__}")
except ImportError as e:
    logger.error(f"❌ Cannot import products: {e}")
    sys.exit(1)

# Try importing plugins
import pkgutil

logger.info("\n" + "="*50)
logger.info("DISCOVERING PLUGINS")
logger.info("="*50)

for importer, modname, ispkg in pkgutil.iter_modules(products.__path__, prefix="products."):
    logger.info(f"\nFound module: {modname} (is_package={ispkg})")

    if ispkg:
        try:
            module = __import__(modname, fromlist=[''])
            logger.info(f"  ✅ Imported successfully")
            logger.info(f"  Module file: {module.__file__}")

            # Check for Plugin class
            if hasattr(module, 'Plugin'):
                logger.info(f"  ✅ Has 'Plugin' class: {module.Plugin}")
            else:
                logger.warning(f"  ⚠️  No 'Plugin' class found")
                logger.info(f"  Available attributes: {dir(module)}")
        except Exception as e:
            logger.error(f"  ❌ Import failed: {e}")

# Now test the registry
logger.info("\n" + "="*50)
logger.info("TESTING PLUGIN REGISTRY")
logger.info("="*50)

from platform_core.plugins.registry import PluginRegistry

registry = PluginRegistry()
registry.discover_plugins()

logger.info(f"\n✅ Discovered {len(registry.plugins)} plugins:")
for name, plugin in registry.plugins.items():
    logger.info(f"  - {name}: {plugin.metadata.description}")

if len(registry.plugins) == 0:
    logger.error("\n❌ NO PLUGINS DISCOVERED!")
    logger.error("Check the error messages above to debug.")
else:
    logger.info("\n🎉 Plugin discovery successful!")
