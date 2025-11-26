"""
Tests for the LibreNMS Plugin API.
"""
import pytest
import uuid
from httpx import AsyncClient
from unittest.mock import MagicMock, patch, AsyncMock

from products.librenms.models import DeviceHealth

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_librenms_api():
    """Mocks the pylibrenms.Librenms."""
    with patch("products.librenms.services.Librenms") as mock:
        instance = mock.return_value
        instance.list_devices.return_value = [
            {"device_id": 1, "status": True, "uptime": 12345},
        ]
        instance.get_device_health.return_value = [
            {"type": "ping", "value": 10.5},
        ]
        yield instance

async def test_librenms_sync_and_get(
    client: AsyncClient,
    auth_headers: dict,
    mock_db_session,
    mock_librenms_api
):
    """
    Tests the full workflow:
    1. Mocks the LibreNMS API.
    2. Calls POST /sync.
    3. Calls GET /health to verify the data.
    """
    tenant_id = uuid.UUID(auth_headers["X-Tenant-ID"])

    # --- Call POST /sync ---
    sync_response = await client.post("/api/librenms/sync", headers=auth_headers)
    assert sync_response.status_code == 202

    # --- Verify data with GET /health ---
    # To make this work, we need to populate our mock session with the data
    # that the sync service *would* have added.
    synced_health = DeviceHealth(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        device_id=1,
        status="up",
        uptime=12345,
        ping_latency=10.5,
    )
    mock_db_session.add(synced_health)

    # Mock the execute method to return the data we just added
    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value.all.return_value = [synced_health]
    mock_db_session.execute = AsyncMock(return_value=mock_execute_result)

    get_health_response = await client.get("/api/librenms/health", headers=auth_headers)
    assert get_health_response.status_code == 200
    health_data = get_health_response.json()

    assert len(health_data) == 1
    assert health_data[0]["device_id"] == 1
    assert health_data[0]["status"] == "up"
    assert health_data[0]["ping_latency"] == 10.5
