"""
Test fixtures using a standard, robust FastAPI testing approach.
This version uses both direct injection for the lifespan and dependency
overrides for the API routes, which is the complete and correct solution.
"""
import pytest
import os
import logging
import uuid
from unittest.mock import AsyncMock, MagicMock
from contextlib import asynccontextmanager

from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager

# Import the dependency functions to use as keys for overrides
from platform_core.api.dependencies import get_db_manager, get_neo4j_manager

# Setup logging
logging.basicConfig(
    level=logging.INFO, # Quieter for successful runs
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="function", autouse=True)
def set_test_environment(monkeypatch):
    """Sets the TESTING environment variable for each test function."""
    monkeypatch.setenv("TESTING", "true")

# ============================================================================
# MOCK DATABASE SESSIONS
# ============================================================================

class MockAsyncSession:
    """Stateful mock of SQLAlchemy's AsyncSession."""
    def __init__(self):
        self._data_store = {}
        self._commit_called = False

    def add(self, instance):
        # When adding, we simulate the DB assigning an ID if it's not present.
        if not getattr(instance, 'id', None):
            instance.id = uuid.uuid4()
        key = (type(instance), instance.id)
        self._data_store[key] = instance

    async def commit(self):
        self._commit_called = True

    async def get(self, model_class, object_id):
        key = (model_class, object_id)
        return self._data_store.get(key)

    async def execute(self, statement):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        result.scalars.return_value.all.return_value = []
        return result

    async def refresh(self, instance):
        pass

    async def delete(self, instance):
        key = (type(instance), instance.id)
        if key in self._data_store:
            del self._data_store[key]

    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

@pytest.fixture
def mock_db_session():
    return MockAsyncSession()

@pytest.fixture
def mock_db_manager(mock_db_session):
    manager = AsyncMock()
    @asynccontextmanager
    async def get_session(tenant_id: str):
        yield mock_db_session
    manager.get_session = get_session
    return manager

@pytest.fixture
def mock_neo4j_manager():
    manager = AsyncMock()
    @asynccontextmanager
    async def get_session():
        yield MagicMock() # Simple mock for Neo4j
    manager.get_session = get_session
    return manager

# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_site_data() -> dict:
    """Sample site data for creating objects."""
    return {
        "id": uuid.uuid4(), "netbox_id": 1, "name": "Test Site",
        "slug": "test-site", "description": "Test Description", "tenant_id": uuid.uuid4()
    }

@pytest.fixture
def sample_site_object(sample_site_data):
    from products.netbox.models import Site
    return Site(**sample_site_data)

# ============================================================================
# APPLICATION FIXTURES - THE CORRECT, COMBINED APPROACH
# ============================================================================

@pytest.fixture(scope="function")
async def app(mock_db_manager, mock_neo4j_manager):
    """
    Create a FastAPI app instance with a fully mocked database layer.
    - Injects mock managers into `create_app` for the lifespan.
    - Uses `dependency_overrides` for the API routes.
    """
    from platform_core.api.main import create_app

    app_instance = create_app(
        db_manager_override=mock_db_manager,
        neo4j_manager_override=mock_neo4j_manager
    )

    # Override dependencies for all API routes
    app_instance.dependency_overrides[get_db_manager] = lambda: mock_db_manager
    app_instance.dependency_overrides[get_neo4j_manager] = lambda: mock_neo4j_manager

    # LifespanManager is crucial for running startup/shutdown events
    async with LifespanManager(app_instance) as manager:
        yield manager.app

@pytest.fixture
async def client(app):
    """Provides a fully configured async test client."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_headers() -> dict:
    """Provides standard authentication headers for tests."""
    return {
        "X-Tenant-ID": str(uuid.uuid4()),
        "Content-Type": "application/json"
    }
