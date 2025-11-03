"""
Topology Plugin
"""
from platform_core.plugins.base import BasePlugin, PluginMetadata
from fastapi import APIRouter
from typing import Optional
import logging

from .api import create_topology_router
from platform_core.database.neo4j_conn import Neo4jManager

logger = logging.getLogger(__name__)

class Plugin(BasePlugin):
    """
    Provides topology visualization and management capabilities using Neo4j.
    """

    _router: Optional[APIRouter] = None
    _neo4j_manager: Optional[Neo4jManager] = None

    def get_metadata(self) -> PluginMetadata:
        """
        Get plugin metadata.
        """
        return PluginMetadata(
            name="topology",
            version="1.0.0",
            description="Graph-based topology visualization and management.",
            author="Your Name",
            requires=[]
        )

    async def initialize(self, neo4j_manager: Neo4jManager, **kwargs) -> bool:
        """
        Initialize the plugin.
        """
        logger.info("Initializing Topology plugin...")
        try:
            self._neo4j_manager = neo4j_manager
            self._router = create_topology_router(self._neo4j_manager)
            logger.info("✅ Topology plugin initialized")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize Topology plugin: {e}", exc_info=True)
            return False

    async def shutdown(self):
        """
        Shutdown the plugin.
        """
        logger.info("Shutting down Topology plugin...")

    async def health_check(self) -> bool:
        """
        Check the health of the plugin.
        """
        if not self._neo4j_manager:
            return False
        try:
            await self._neo4j_manager.execute_query("RETURN 1")
            return True
        except Exception:
            return False

    def get_router(self) -> Optional[APIRouter]:
        """
        Get the plugin's API router.
        """
        return self._router
