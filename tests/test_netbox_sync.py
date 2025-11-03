import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid
from contextlib import asynccontextmanager

from products.netbox.sync import NetBoxSyncService

@pytest.fixture
def mock_netbox_client():
    """Mock NetBox client with proper async returns."""
    client = AsyncMock()

    # Mock get_sites() - returns full API response structure
    client.get_sites.return_value = {
        'count': 2,
        'next': None,
        'previous': None,
        'results': [
            {
                'id': 1,
                'name': 'Site 1',
                'slug': 'site-1',
                'description': 'Test Site 1'
            },
            {
                'id': 2,
                'name': 'Site 2',
                'slug': 'site-2',
                'description': 'Test Site 2'
            }
        ]
    }

    # Mock get_devices()
    client.get_devices.return_value = {
        'count': 1,
        'results': [
            {
                'id': 1,
                'name': 'device-01',
                'device_type': {'display': 'Cisco 2960'},
                'device_role': {'display': 'Access Switch'},
                'site': {'id': 1}
            }
        ]
    }

    # Mock get_ip_addresses()
    client.get_ip_addresses.return_value = {
        'count': 1,
        'results': [
            {
                'id': 1,
                'address': '192.168.1.1/24',
                'dns_name': 'router.example.com',
                'description': 'Management IP',
                'status': {'value': 'active', 'label': 'Active'}
            }
        ]
    }

    return client


@pytest.fixture
def mock_db_manager():
    """Mock database manager."""
    manager = MagicMock()

    # Mock session context manager
    mock_session = AsyncMock()

    # Mock execute() to return empty results (no existing records)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    # Mock commit()
    mock_session.commit = AsyncMock()
    mock_session.add = AsyncMock()

    # Make get_session return async context manager
    @asynccontextmanager
    async def get_session_mock(*args, **kwargs):
        yield mock_session

    manager.get_session = get_session_mock

    return manager


@pytest.mark.asyncio
async def test_sync_sites(mock_netbox_client, mock_db_manager):
    """Test syncing sites from NetBox."""
    tenant_id = uuid.uuid4()

    service = NetBoxSyncService(mock_netbox_client, mock_db_manager)

    # Execute sync
    count = await service.sync_sites(tenant_id)

    # Assertions
    assert count == 2  # Should have synced 2 sites

    # Verify client was called
    mock_netbox_client.get_sites.assert_called_once()

    # Since get_session is a real function now, we can't assert it was called.
    # Instead, we'll check that commit was called.
    async with mock_db_manager.get_session() as session:
        session.commit.assert_called_once()
        session.add.assert_called()


@pytest.mark.asyncio
async def test_sync_devices(mock_netbox_client, mock_db_manager):
    """Test syncing devices from NetBox."""
    tenant_id = uuid.uuid4()

    service = NetBoxSyncService(mock_netbox_client, mock_db_manager)

    count = await service.sync_devices(tenant_id)

    assert count == 1
    mock_netbox_client.get_devices.assert_called_once()


@pytest.mark.asyncio
async def test_sync_ip_addresses(mock_netbox_client, mock_db_manager):
    """Test syncing IP addresses from NetBox."""
    tenant_id = uuid.uuid4()

    service = NetBoxSyncService(mock_netbox_client, mock_db_manager)

    count = await service.sync_ip_addresses(tenant_id)

    assert count == 1
    mock_netbox_client.get_ip_addresses.assert_called_once()


@pytest.mark.asyncio
async def test_sync_sites_with_existing_data(mock_netbox_client, mock_db_manager):
    """Test syncing when site already exists (update scenario)."""
    tenant_id = uuid.uuid4()

    # Create mock existing site
    existing_site = MagicMock()
    existing_site.netbox_id = 1
    existing_site.name = 'Old Name'

    # Configure mock to return existing site for the first call, and None for the second
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.side_effect = [existing_site, None]

    async with mock_db_manager.get_session() as session:
        session.execute.return_value = mock_result

        service = NetBoxSyncService(mock_netbox_client, mock_db_manager)

        count = await service.sync_sites(tenant_id)

        # Should still count as synced
        assert count == 2

        # Should have updated existing site
        assert existing_site.name == 'Site 1'  # Updated from 'Old Name'
