"""
Neo4j database connection manager.
"""
from neo4j import AsyncGraphDatabase, AsyncDriver
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

class Neo4jManager:
    _instance: Optional['Neo4jManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Neo4jManager, cls).__new__(cls)
            cls._instance.driver = None
        return cls._instance

    async def connect(self):
        """Establish connection to the Neo4j database."""
        if self.driver:
            return

        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        logger.info(f"Connecting to Neo4j at {uri}")
        try:
            self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
            await self.driver.verify_connectivity()
            logger.info("✅ Neo4j connection established")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}", exc_info=True)
            self.driver = None
            raise

    async def close(self):
        """Close the Neo4j database connection."""
        if self.driver:
            logger.info("Closing Neo4j driver...")
            await self.driver.close()
            self.driver = None
            logger.info("✅ Neo4j driver closed")

    async def execute_query(self, query: str, params: Optional[dict] = None):
        """Execute a query against the database."""
        if not self.driver:
            raise ConnectionError("Neo4j driver not connected.")

        async with self.driver.session() as session:
            response = await session.run(query, params)
            records = [record async for record in response]
            summary = await response.consume()
            return records, summary, response.keys()

# Global singleton instance
neo4j_manager = Neo4jManager()
