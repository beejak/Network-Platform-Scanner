import pytest
from httpx import AsyncClient

from platform_core.plugins.registry import plugin_registry

pytestmark = pytest.mark.asyncio


async def test_load_netbox_plugin():
    """Test that the NetBox plugin can be loaded."""
    plugin_registry.discover_plugins()
    assert "NetBox" in plugin_registry.plugins
