"""Tests for the Diagrams Plugin API."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_generate_diagram(client: AsyncClient, auth_headers: dict):
    """Test generating a diagram."""
    diagram_data = {
        "name": "test_diagram",
        "nodes": [
            {"name": "web", "label": "Web Server", "type": "compute", "provider": "aws"},
            {"name": "db", "label": "Database", "type": "database", "provider": "aws"},
        ],
        "edges": [
            {"source": "web", "target": "db", "label": "reads from"},
        ],
    }

    response = await client.post("/api/diagrams/generate", json=diagram_data, headers=auth_headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    # Verify that the response has a non-zero content length
    assert int(response.headers["content-length"]) > 0
