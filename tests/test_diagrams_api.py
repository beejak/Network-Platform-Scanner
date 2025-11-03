import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_generate_diagram(client: AsyncClient):
    """Test the /generate endpoint."""
    request_data = {
        "name": "My Diagram",
        "nodes": [
            {"name": "web", "label": "Web Server", "provider": "aws", "type": "compute", "name": "ec2"},
            {"name": "db", "label": "Database", "provider": "aws", "type": "database", "name": "rds"},
        ],
        "edges": [{"source": "web", "target": "db"}],
    }
    headers = {"X-Tenant-ID": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"}
    response = await client.post(
        "/api/diagrams/generate", json=request_data, headers=headers
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
