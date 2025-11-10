"""
Tests for the Diagrams Plugin API, focusing on NetBox data integration.
"""
import pytest
import uuid
from httpx import AsyncClient
from unittest.mock import MagicMock, AsyncMock

from products.netbox.models import Site, Device

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_site_with_devices(auth_headers):
    """Creates a mock site with a list of devices."""
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
        Device(id=uuid.uuid4(), tenant_id=tenant_id, name="Access Switch 1", device_role="access-switch", site_id=site.id),
    ]
    return site

async def test_generate_site_diagram_success(
    client: AsyncClient,
    auth_headers: dict,
    mock_db_session,
    mock_site_with_devices
):
    """Test successfully generating a site diagram."""
    site = mock_site_with_devices

    # --- Mock DB Response ---
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.first.return_value = site
    mock_db_session.execute = AsyncMock(return_value=mock_execute_result)

    # --- API Call ---
    response = await client.post(
        f"/api/diagrams/generate/{site.slug}",
        headers=auth_headers
    )

    # --- Assertions ---
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert int(response.headers["content-length"]) > 100 # Should be a reasonably sized image

async def test_generate_diagram_for_nonexistent_site(
    client: AsyncClient,
    auth_headers: dict,
    mock_db_session
):
    """Test that a 404 is returned for a site that doesn't exist."""
    # --- Mock DB Response ---
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.first.return_value = None # Site not found
    mock_db_session.execute = AsyncMock(return_value=mock_execute_result)

    # --- API Call ---
    response = await client.post(
        "/api/diagrams/generate/nonexistent-site",
        headers=auth_headers
    )

    # --- Assertions ---
    assert response.status_code == 404
    assert response.json() == {"detail": "Site not found"}
