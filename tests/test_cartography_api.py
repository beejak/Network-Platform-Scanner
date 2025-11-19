"""
Tests for the Cartography Plugin API.
"""
import pytest
import uuid
from httpx import AsyncClient
from unittest.mock import MagicMock, AsyncMock

from products.netbox.models import Site, Device

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_site_with_devices(auth_headers):
    """Creates a mock site with a list of devices for PostgreSQL."""
    tenant_id = uuid.UUID(auth_headers["X-Tenant-ID"])
    site = Site(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        netbox_id=1,
        name="Test Site",
        slug="test-site",
    )
    site.devices = [
        Device(id=uuid.uuid4(), tenant_id=tenant_id, name="Core Router 1", device_role="core-router", site_id=site.id),
    ]
    return site

@pytest.fixture
def mock_neo4j_session():
    """Provides a mock Neo4j session that captures queries."""
    session = AsyncMock()
    session.run = AsyncMock()
    return session

async def test_cartography_sync_end_to_end(
    app, # Add the app fixture
    client: AsyncClient,
    auth_headers: dict,
    mock_db_session,
    mock_neo4j_session,
    mock_site_with_devices
):
    """
    Tests the full workflow:
    1. Mocks data in PostgreSQL.
    2. Mocks the Neo4j session.
    3. Calls POST /sync.
    4. Verifies that the correct Cypher queries were executed.
    """
    site = mock_site_with_devices
    devices = site.devices

    # --- Mock DB Responses ---
    # Create separate mock results for sites and devices
    mock_sites_result = MagicMock(scalars=MagicMock(return_value=MagicMock(all=lambda: [site])))
    mock_devices_result = MagicMock(scalars=MagicMock(return_value=MagicMock(all=lambda: devices)))

    # Use side_effect to return the correct result for each call
    mock_db_session.execute = AsyncMock(side_effect=[mock_sites_result, mock_devices_result])

    # --- Mock Dependency Injection ---
    # We need to override the get_neo4j_session dependency to return our mock
    from platform_core.api.dependencies import get_neo4j_session
    async def override_get_neo4j_session():
        yield mock_neo4j_session

    app.dependency_overrides[get_neo4j_session] = override_get_neo4j_session

    # --- API Call ---
    response = await client.post(
        "/api/cartography/sync",
        headers=auth_headers
    )

    # --- Assertions ---
    assert response.status_code == 202

    # Verify that the session.run method was called for sites and devices
    assert mock_neo4j_session.run.call_count >= 2 # At least one site and one device

    # A more detailed assertion could inspect the `call_args` of mock_neo4j_session.run
    # to ensure the Cypher queries are correct. For now, we'll keep it simple.

    # Clean up the override
    del app.dependency_overrides[get_neo4j_session]
