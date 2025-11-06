"""
Tests for NetBox API endpoints.

CRITICAL: Shows how to properly test with mocked database.
"""
import pytest
import uuid
from httpx import AsyncClient
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# CREATE TESTS (POST)
# ============================================================================

@pytest.mark.asyncio
async def test_create_site(
    client: AsyncClient,
    auth_headers: dict,
    mock_db_session
):
    """Test creating a site."""
    site_data = {
        "netbox_id": 1,
        "name": "New Site",
        "slug": "new-site",
        "description": "A new test site"
    }

    response = await client.post(
        "/api/netbox/sites",
        json=site_data,
        headers=auth_headers
    )

    logger.info(f"Response: {response.status_code} - {response.text}")

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "New Site"
    assert "id" in data

    # Verify commit was called
    assert mock_db_session._commit_called


# ============================================================================
# READ TESTS (GET)
# ============================================================================

@pytest.mark.asyncio
async def test_get_sites(client: AsyncClient, auth_headers: dict):
    """Test getting list of sites."""
    response = await client.get("/api/netbox/sites", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_site_by_id(
    client: AsyncClient,
    auth_headers: dict,
    mock_db_session,
    sample_site_object
):
    """
    Test getting a specific site.

    CRITICAL: Pre-populate mock session with the object!
    """
    # CRITICAL: Add object to mock session BEFORE making request
    mock_db_session.add(sample_site_object)
    await mock_db_session.commit()

    site_id = sample_site_object.id

    response = await client.get(
        f"/api/netbox/sites/{site_id}",
        headers=auth_headers
    )

    logger.info(f"Response: {response.status_code} - {response.text}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(site_id)
    assert data["name"] == sample_site_object.name


# ============================================================================
# UPDATE TESTS (PUT)
# ============================================================================

@pytest.mark.asyncio
async def test_update_site(
    client: AsyncClient,
    auth_headers: dict,
    mock_db_session,
    sample_site_object
):
    """
    Test updating a site.

    CRITICAL: This is where 404s were happening!
    The fix: Pre-populate the mock session with the object.
    """
    # CRITICAL: Add object to session BEFORE update request
    mock_db_session.add(sample_site_object)
    await mock_db_session.commit()

    site_id = sample_site_object.id

    # Update data
    update_data = {
        "name": "Updated Site Name",
        "description": "Updated description"
    }

    response = await client.put(
        f"/api/netbox/sites/{site_id}",
        json=update_data,
        headers=auth_headers
    )

    logger.info(f"Response: {response.status_code} - {response.text}")

    # Should succeed now!
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated Site Name"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_update_nonexistent_site(
    client: AsyncClient,
    auth_headers: dict
):
    """Test updating a site that doesn't exist - should get 404."""
    fake_id = uuid.uuid4()

    update_data = {"name": "Updated Name"}

    response = await client.put(
        f"/api/netbox/sites/{fake_id}",
        json=update_data,
        headers=auth_headers
    )

    # This SHOULD be 404
    assert response.status_code == 404


# ============================================================================
# DELETE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_delete_site(
    client: AsyncClient,
    auth_headers: dict,
    mock_db_session,
    sample_site_object
):
    """
    Test deleting a site.

    CRITICAL: Pre-populate mock session!
    """
    # CRITICAL: Add object to session first
    mock_db_session.add(sample_site_object)
    await mock_db_session.commit()

    site_id = sample_site_object.id

    response = await client.delete(
        f"/api/netbox/sites/{site_id}",
        headers=auth_headers
    )

    logger.info(f"Response: {response.status_code} - {response.text}")

    assert response.status_code == 200

    # Verify object was removed from mock session
    assert (type(sample_site_object), site_id) not in mock_db_session._data_store


@pytest.mark.asyncio
async def test_delete_nonexistent_site(
    client: AsyncClient,
    auth_headers: dict
):
    """Test deleting a site that doesn't exist - should get 404."""
    fake_id = uuid.uuid4()

    response = await client.delete(
        f"/api/netbox/sites/{fake_id}",
        headers=auth_headers
    )

    assert response.status_code == 404
