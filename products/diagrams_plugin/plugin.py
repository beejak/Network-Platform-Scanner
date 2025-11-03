"""Diagrams plugin implementation."""
from platform_core.plugins.base import BasePlugin, PluginMetadata
from fastapi import APIRouter
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DiagramsPlugin(BasePlugin):
    """Plugin for infrastructure diagram generation."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.router = None

    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="diagrams",
            version="1.0.0",
            description="Infrastructure diagram generation from code",
            author="Network Platform Team",
            requires=[],  # No dependencies
            capabilities=["diagram_rendering", "template_management"]
        )

    async def initialize(self, **kwargs) -> bool:
        """Initialize plugin resources."""
        try:
            logger.info("Initializing Diagrams plugin...")

            # Import routes (do this here to avoid circular imports)
            from .api import router as diagrams_router
            self.router = diagrams_router

            logger.info("✅ Diagrams plugin initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Diagrams plugin: {e}")
            return False

    async def shutdown(self) -> bool:
        """Cleanup plugin resources."""
        logger.info("Shutting down Diagrams plugin...")
        return True

    def get_router(self) -> Optional[APIRouter]:
        """Return FastAPI router for plugin API endpoints."""
        return self.router

    async def health_check(self) -> Dict[str, Any]:
        """Check plugin health status."""
        return {
            "status": "healthy",
            "plugin": self.metadata.name,
            "version": self.metadata.version,
            "initialized": self.is_initialized
        }
