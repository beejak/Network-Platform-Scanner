"""Neo4j database connection manager."""
from neo4j import AsyncGraphDatabase
import os

class Neo4jManager:
    """Neo4j database manager."""

    def __init__(self, uri, user, password):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        """Close the database connection."""
        await self.driver.close()

    async def execute_query(self, query, params=None):
        """Execute a query."""
        async with self.driver.session() as session:
            result = await session.run(query, params)
            return await result.data(), await result.summary(), await result.keys()

_neo4j_manager = None

def get_neo4j_manager():
    """Get Neo4j manager singleton."""
    global _neo4j_manager
    if _neo4j_manager is None:
        uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        user = os.environ.get("NEO4J_USER", "neo4j")
        password = os.environ.get("NEO4J_PASSWORD", "password")
        _neo4j_manager = Neo4jManager(uri, user, password)
    return _neo4j_manager
