import pytest
from httpx import AsyncClient

from platform_core.plugins.registry import plugin_registry

pytestmark = pytest.mark.asyncio


async def test_load_netbox_plugin():
    """Test that the NetBox plugin can be loaded."""
    # The plugin registry is a singleton, so we need to clear it before running the test
    plugin_registry.plugins = {}
    plugin_registry.discover_plugins()
    assert "NetBox" in plugin_registry.plugins
