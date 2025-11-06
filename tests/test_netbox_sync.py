"""Tests for NetBox data synchronization using the refined hybrid mock."""
import pytest
import uuid
from unittest.mock import patch, MagicMock, AsyncMock

from products.netbox.sync import NetBoxSyncService
from products.netbox.models import Site

pytestmark = pytest.mark.asyncio

# ============================================================================
# Synchronization Logic Tests
# ============================================================================

@patch("products.netbox.sync.NetBoxClient")
async def test_sync_sites_creates_new_sites(mock_netbox_client: MagicMock):
    """Test that new sites from NetBox are correctly added to the DB."""
    # --- Setup Mocks ---
    session = MagicMock()
    session.commit = AsyncMock()

    execute_result = MagicMock()
    execute_result.scalars.return_value.first.return_value = None
    session.execute = AsyncMock(return_value=execute_result)

    client_instance = mock_netbox_client.return_value
    client_instance.get_sites = AsyncMock(return_value=[
        {"id": 1, "name": "Site A", "slug": "site-a"},
    ])

    # --- Run Sync ---
    sync_service = NetBoxSyncService(session, uuid.uuid4())
    await sync_service._sync_sites(client_instance)

    # --- Assertions ---
    session.add.assert_called_once()
    client_instance.get_sites.assert_awaited_once()

@patch("products.netbox.sync.NetBoxClient")
async def test_sync_devices_creates_new_devices(mock_netbox_client: MagicMock):
    """Test that new devices are added when their corresponding site exists."""
    # --- Setup Mocks ---
    session = MagicMock()
    session.commit = AsyncMock()

    client_instance = mock_netbox_client.return_value
    client_instance.get_devices = AsyncMock(return_value=[
        {"id": 100, "name": "Device 1", "site_id": 1, "device_type": "Router", "device_role": "Core", "serial": "XYZ"},
    ])

    # CORRECT ORDER: First execute finds the device (returns None), second finds the site.
    device_lookup = MagicMock()
    device_lookup.scalars.return_value.first.return_value = None

    site_lookup = MagicMock()
    site_lookup.scalars.return_value.first.return_value = Site(id=uuid.uuid4(), netbox_id=1)

    session.execute = AsyncMock(side_effect=[device_lookup, site_lookup])

    # --- Run Sync ---
    sync_service = NetBoxSyncService(session, uuid.uuid4())
    await sync_service._sync_devices(client_instance)

    # --- Assertions ---
    session.add.assert_called_once()
    client_instance.get_devices.assert_awaited_once()
