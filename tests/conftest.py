from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient

from platform_core.api.main import app


@pytest_asyncio.fixture(scope="function")  # type: ignore
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
