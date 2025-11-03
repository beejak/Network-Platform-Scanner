import pytest
from httpx import AsyncClient
from platform_core.api.main import create_app

app = create_app()

@pytest.mark.asyncio
async def test_generate_diagram():
    """
    Test case for generating a diagram.
    """
    diagram_payload = {
        "name": "My Test Diagram",
        "nodes": [
            {
                "name": "ec2",
                "label": "My EC2 Instance",
                "provider": "aws",
                "type": "compute",
            }
        ],
        "edges": [],
    }

    async with app.router.lifespan_context(app):
        headers = {"X-Tenant-ID": "a1b2c3d4-e5f6-7890-1234-567890abcdef"}
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/diagrams/generate",
                headers=headers,
                json=diagram_payload,
            )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content is not None
