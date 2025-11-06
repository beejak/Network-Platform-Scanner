"""Dependency injection for database sessions."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, Depends
import logging

# Import the actual implementations to avoid circular dependencies
from platform_core.database.postgres import get_database_manager as get_postgres_manager
from platform_core.database.neo4j_conn import get_neo4j_manager as get_neo4j_db_manager

logger = logging.getLogger(__name__)

# Define wrappers that will be used as dependencies throughout the app.
# This provides a single, consistent point for overrides in tests.
def get_db_manager():
    """Provides the PostgreSQL database manager."""
    return get_postgres_manager()

def get_neo4j_manager():
    """Provides the Neo4j database manager."""
    return get_neo4j_db_manager()


async def get_db_session(
    request: Request, db_manager=Depends(get_db_manager)
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session with tenant context using standard FastAPI DI.
    """
    tenant_id = request.state.tenant_id

    async with db_manager.get_session(tenant_id) as session:
        yield session

async def get_neo4j_session(
    request: Request, neo4j_manager=Depends(get_neo4j_manager)
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get neo4j session with tenant context using standard FastAPI DI.
    """
    async with neo4j_manager.get_session() as session:
        yield session
