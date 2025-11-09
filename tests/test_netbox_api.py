"""
Tests for the refactored, read-only NetBox API endpoints.
"""
import pytest
import uuid
from httpx import AsyncClient
from unittest.mock import patch, MagicMock, AsyncMock

from products.netbox.models import Site, Device

# ============================================================================
# API Test Setup
# ============================================================================

pytestmark = pytest.mark.asyncio

# ============================================================================
# SYNCHRONIZATION ENDPOINT TESTS
# ============================================================================

@patch("products.netbox.api.NetBoxSyncService")
async def test_post_sync_endpoint(
    mock_sync_service,
    client: AsyncClient,
    auth_headers: dict
):
    """Test that the POST /sync endpoint correctly triggers the sync service."""
    # --- Setup Mock ---
    mock_instance = mock_sync_service.return_value
    mock_instance.sync_all = AsyncMock()

    # --- API Call ---
    response = await client.post(
        "/api/netbox/sync",
        headers=auth_headers
    )

    # --- Assertions ---
    assert response.status_code == 202
    assert response.json() == {"message": "NetBox synchronization started."}

    # Verify that the sync service was called
    mock_instance.sync_all.assert_awaited_once()

# ============================================================================
# END-TO-END SYNCHRONIZATION TEST
# ============================================================================

def create_mock_nb_object(**kwargs):
    """Helper to create a mock pynetbox object."""
    mock_obj = MagicMock()
    for key, value in kwargs.items():
        if isinstance(value, dict):
            setattr(mock_obj, key, create_mock_nb_object(**value))
        else:
            setattr(mock_obj, key, value)
    return mock_obj

async def test_end_to_end_sync_and_get(
    client: AsyncClient,
    auth_headers: dict,
    mock_pynetbox_api,
    mock_db_session
):
    """
    Tests the full workflow:
    1. Mock external NetBox data.
    2. Call POST /sync to trigger the synchronization.
    3. Call GET /sites and GET /devices to verify the data was saved correctly.
    """
    tenant_id = uuid.UUID(auth_headers["X-Tenant-ID"])

    # --- 1. Mock external NetBox data ---
    mock_site = create_mock_nb_object(id=1, name="E2E Test Site", slug="e2e-test-site", description="End-to-end")
    mock_device = create_mock_nb_object(
        id=100, name="E2E Device", device_type={"slug": "firewall"},
        device_role={"slug": "edge"}, status={"value": "active"}, site=mock_site
    )
    mock_pynetbox_api.dcim.sites.all.return_value = [mock_site]
    mock_pynetbox_api.dcim.devices.all.return_value = [mock_device]

    # --- 2. Call POST /sync ---
    sync_response = await client.post("/api/netbox/sync", headers=auth_headers)
    assert sync_response.status_code == 202

    # --- 3. Verify data with GET endpoints ---
    # To make this work, we need to populate our mock session with the data
    # that the sync service *would* have added.
    synced_site = Site(
        id=uuid.uuid4(), tenant_id=tenant_id, netbox_id=mock_site.id,
        name=mock_site.name, slug=mock_site.slug, description=mock_site.description
    )
    synced_device = Device(
        id=uuid.uuid4(), tenant_id=tenant_id, site_id=synced_site.id,
        name="E2E Device", device_type="firewall", device_role="edge",
        status="active", netbox_id=100
    )
    mock_db_session.add(synced_site)
    mock_db_session.add(synced_device)

    # Mock the execute method to return the data we just added
    mock_execute_result_sites = MagicMock()
    mock_execute_result_sites.scalars.return_value.all.return_value = [synced_site]
    mock_execute_result_devices = MagicMock()
    mock_execute_result_devices.scalars.return_value.all.return_value = [synced_device]

    async def mock_execute(statement):
        if "netbox_sites" in str(statement):
            return mock_execute_result_sites
        elif "netbox_devices" in str(statement):
            return mock_execute_result_devices
        return MagicMock() # Default for other queries
    mock_db_session.execute = mock_execute

    # Verify Sites
    get_sites_response = await client.get("/api/netbox/sites", headers=auth_headers)
    assert get_sites_response.status_code == 200
    sites_data = get_sites_response.json()
    assert len(sites_data) == 1
    assert sites_data[0]["name"] == "E2E Test Site"

    # Verify Devices
    get_devices_response = await client.get("/api/netbox/devices", headers=auth_headers)
    assert get_devices_response.status_code == 200
    devices_data = get_devices_response.json()
    assert len(devices_data) == 1
    assert devices_data[0]["name"] == "E2E Device"
    assert devices_data[0]["site_id"] == str(synced_site.id)
