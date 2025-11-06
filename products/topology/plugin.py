"""Topology plugin with dependency injection support."""
from platform_core.plugins.base import BasePlugin, PluginMetadata
from fastapi import APIRouter
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TopologyPlugin(BasePlugin):
    """Topology plugin using dependency injection."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._router = None

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="topology",
            version="1.0.0",
            description="Network topology visualization",
            author="Network Platform Team",
            requires=[],
            capabilities=["topology_discovery", "graph_visualization"]
        )

    async def initialize(self, **kwargs) -> bool:
        """Initialize plugin with DI."""
        try:
            logger.info("Initializing Topology plugin...")

            neo4j_manager = kwargs.get("neo4j_manager")
            if not neo4j_manager:
                raise ValueError("Neo4j manager not provided to Topology plugin")

            # Create router
            from .api import create_topology_router
            self._router = create_topology_router(neo4j_manager)

            logger.info("✅ Topology plugin initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Topology plugin: {e}", exc_info=True)
            return False

    async def shutdown(self) -> bool:
        """Shutdown plugin."""
        logger.info("Shutting down Topology plugin...")
        return True

    def get_router(self) -> Optional[APIRouter]:
        return self._router

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "plugin": self.metadata.name,
            "initialized": self.is_initialized
        }
