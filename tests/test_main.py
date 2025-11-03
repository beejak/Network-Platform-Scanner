"""
Tests for the main FastAPI application.
"""
import pytest
from httpx import AsyncClient

# All fixtures are now managed in conftest.py

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """
    Test the /health endpoint.
    This now implicitly tests that plugins are being loaded via the app lifespan.
    """
    response = await client.get("/health")
    assert response.status_code == 200

    json_response = response.json()
    assert json_response["status"] == "healthy"
    assert "plugins" in json_response

    # Check that all expected plugins are loaded
    loaded_plugins = json_response["plugins"]
    assert "diagrams" in loaded_plugins
    assert "NetBox" in loaded_plugins
    assert "topology" in loaded_plugins
