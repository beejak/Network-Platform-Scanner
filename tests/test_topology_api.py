"""Tests for the Topology Plugin API using service-layer mocking."""
import pytest
import uuid
from unittest.mock import AsyncMock

from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

# ============================================================================
# Test Data
# ============================================================================

NODE_A_ID = str(uuid.uuid4())
NODE_B_ID = str(uuid.uuid4())

@pytest.fixture
def mock_topology_data():
    """Provides sample graph data for mocking."""
    nodes = [
        {"id": NODE_A_ID, "name": "Router 1", "type": "device"},
        {"id": NODE_B_ID, "name": "Switch 1", "type": "device"},
    ]
    return nodes

# ============================================================================
# API Tests with Mocked Neo4j Manager
# ============================================================================

async def test_get_nodes(client: AsyncClient, mock_neo4j_manager: AsyncMock, mock_topology_data, auth_headers: dict):
    """Test fetching all topology nodes."""
    # Configure the mock manager to return our sample nodes
    mock_neo4j_manager.execute_query.return_value = ([{"n": node} for node in mock_topology_data], None, None)

    response = await client.get("/api/topology/nodes", headers=auth_headers)

    assert response.status_code == 200

    response_data = response.json()
    assert len(response_data) == 2
    assert response_data[0]["name"] == "Router 1"

    # Verify the correct query was executed
    mock_neo4j_manager.execute_query.assert_called_with("MATCH (n) RETURN n LIMIT 25")

async def test_get_node_by_id(client: AsyncClient, mock_neo4j_manager: AsyncMock, mock_topology_data, auth_headers: dict):
    """Test fetching a single node by its ID."""
    target_node = mock_topology_data[0]

    # Configure mock to return just the one node
    mock_neo4j_manager.execute_query.return_value = ([{"n": target_node}], None, None)

    response = await client.get(f"/api/topology/nodes/{NODE_A_ID}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Router 1"

    # Verify the correct query was executed with parameters
    mock_neo4j_manager.execute_query.assert_called_with(
        "MATCH (n {id: $node_id}) RETURN n", params={"node_id": NODE_A_ID}
    )

async def test_get_node_not_found(client: AsyncClient, mock_neo4j_manager: AsyncMock, auth_headers: dict):
    """Test response when a node is not found."""
    non_existent_id = str(uuid.uuid4())

    # Configure mock to return no records
    mock_neo4j_manager.execute_query.return_value = ([], None, None)

    response = await client.get(f"/api/topology/nodes/{non_existent_id}", headers=auth_headers)

    assert response.status_code == 404

async def test_create_node(client: AsyncClient, mock_neo4j_manager: AsyncMock, auth_headers: dict):
    """Test creating a new node."""
    new_node_data = {"name": "Firewall", "type": "security"}

    # Mock the return value from the create query
    created_node = new_node_data.copy()
    created_node["id"] = str(uuid.uuid4())
    mock_neo4j_manager.execute_query.return_value = ([{"n": created_node}], None, None)

    response = await client.post("/api/topology/nodes", json=new_node_data, headers=auth_headers)

    assert response.status_code == 201

    response_data = response.json()
    assert response_data["name"] == "Firewall"
    assert "id" in response_data

    # Verify the create query was called
    # We can check the query string contains 'CREATE' as a basic check
    call_args, call_kwargs = mock_neo4j_manager.execute_query.call_args
    assert "CREATE" in call_args[0]
