"""Tests for Topology API."""
import pytest
from httpx import AsyncClient
import logging
from unittest.mock import AsyncMock

logger = logging.getLogger(__name__)


# ============================================================================
# API Tests
# ============================================================================

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Verify app is running and plugins loaded."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "topology" in data["plugins"]


@pytest.mark.asyncio
async def test_get_nodes(client: AsyncClient, auth_headers: dict):
    """Test GET /api/topology/nodes with mock data."""
    mock_manager = client.app.state.mock_neo4j_manager
    mock_manager.execute_query.return_value = ([{"n": {"id": "test-node-1"}}, {"n": {"id": "test-node-2"}}], None, None)

    response = await client.get("/api/topology/nodes", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "test-node-1"
    mock_manager.execute_query.assert_called_once()


@pytest.mark.asyncio
async def test_get_node_by_id(client: AsyncClient, auth_headers: dict):
    """Test GET /api/topology/nodes/{id} with mock data."""
    node_id = "test-123"
    mock_manager = client.app.state.mock_neo4j_manager
    mock_manager.execute_query.return_value = ([{"n": {"id": node_id}}], None, None)

    response = await client.get(f"/api/topology/nodes/{node_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == node_id
    mock_manager.execute_query.assert_called_once_with(
        "MATCH (n {id: $node_id}) RETURN n", params={"node_id": node_id}
    )


@pytest.mark.asyncio
async def test_create_node(client: AsyncClient, auth_headers: dict):
    """Test POST /api/topology/nodes with mock data."""
    mock_manager = client.app.state.mock_neo4j_manager
    mock_manager.execute_query.return_value = ([{"n": {"id": "new-mock-node"}}], None, None)

    node_data = {"type": "router", "name": "Test Router"}
    response = await client.post(
        "/api/topology/nodes",
        json=node_data,
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "new-mock-node"
    assert mock_manager.execute_query.call_count == 1
