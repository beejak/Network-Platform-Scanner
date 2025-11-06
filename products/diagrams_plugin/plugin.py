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
        self._router = None

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="diagrams",
            version="1.0.0",
            description="Infrastructure diagram generation",
            author="Network Platform Team",
            requires=[],
            capabilities=["diagram_rendering"]
        )

    async def initialize(self, **kwargs) -> bool:
        """Initialize plugin."""
        try:
            logger.info("Initializing Diagrams plugin...")

            # Create router
            from .api import create_diagrams_router
            self._router = create_diagrams_router()

            logger.info("✅ Diagrams plugin initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Diagrams: {e}", exc_info=True)
            return False

    async def shutdown(self) -> bool:
        """Shutdown plugin."""
        logger.info("Shutting down Diagrams plugin...")
        return True

    def get_router(self) -> Optional[APIRouter]:
        return self._router

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "plugin": self.metadata.name,
            "initialized": self.is_initialized
        }
