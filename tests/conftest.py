"""
Test fixtures with proper async lifecycle management.
"""
import pytest
import pytest_asyncio
import asyncio
import os
import logging
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
import uuid
from asgi_lifespan import LifespanManager
import sys
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from platform_core.api.main import create_app
from platform_core.database.postgres import Base
from platform_core.auth.dependencies import get_db


# Setup test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest before tests run."""
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    # Use an in-memory database for tests
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL


# ============================================================================
# CORE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create a session-wide event loop."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db_engine():
    """Create a test database engine that creates and drops tables."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_db_engine):
    """Create a test database session."""
    async_session_maker = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an AsyncClient with a properly managed lifespan.
    This ensures startup/shutdown events are triggered and plugins are loaded.
    """
    mock_manager = MockNeo4jManager()
    app = create_app(neo4j_manager=mock_manager)

    # Attach the mock manager to the app's state for easy access in tests
    app.state.mock_neo4j_manager = mock_manager

    # Override the database dependency to use the test session
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Use LifespanManager to correctly trigger startup/shutdown events
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://test"
        ) as ac:
            ac.app = manager.app  # Attach the app instance to the client
            yield ac

    # Clean up dependency overrides
    app.dependency_overrides.clear()


# ============================================================================
# HELPER FIXTURES
# ============================================================================

@pytest.fixture
def auth_headers() -> dict:
    """Generate auth headers with a new tenant ID for each test."""
    tenant_id = uuid.uuid4()
    return {
        "X-Tenant-ID": str(tenant_id),
        "Content-Type": "application/json"
    }


# ============================================================================
# MOCK FIXTURES
# ============================================================================

class MockNeo4jManager(MagicMock):
    """A mock Neo4jManager that returns predefined data."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.execute_query = AsyncMock(return_value=([], None, None))
