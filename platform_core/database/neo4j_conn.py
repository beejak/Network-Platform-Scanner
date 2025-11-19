"""Neo4j database connection manager."""
from neo4j import AsyncGraphDatabase
import os
from contextlib import asynccontextmanager

class Neo4jManager:
    """Neo4j database manager."""

    def __init__(self, uri, user, password):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        """Close the database connection."""
        await self.driver.close()

    @asynccontextmanager
    async def get_session(self):
        """Provides a Neo4j session as an async context manager."""
        session = self.driver.session()
        try:
            yield session
        finally:
            await session.close()

from platform_core.config import get_settings

_neo4j_manager = None

def get_neo4j_manager():
    """Get Neo4j manager singleton, configured via application settings."""
    global _neo4j_manager
    if _neo4j_manager is None:
        settings = get_settings()
        _neo4j_manager = Neo4jManager(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD
        )
    return _neo4j_manager
