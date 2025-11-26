"""LibreNMS plugin implementation."""
from platform_core.plugins.base import BasePlugin, PluginMetadata
from fastapi import APIRouter
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LibreNMSPlugin(BasePlugin):
    """Plugin for LibreNMS integration."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._router = None

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="librenms",
            version="1.0.0",
            description="LibreNMS integration for SNMP-based monitoring",
            author="Network Platform Team",
            requires=[],
            capabilities=["snmp_monitoring"]
        )

    async def initialize(self, **kwargs) -> bool:
        """Initialize plugin."""
        try:
            logger.info("Initializing LibreNMS plugin...")

            # Create router
            from .api import create_librenms_router
            self._router = create_librenms_router()

            logger.info("✅ LibreNMS plugin initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize LibreNMS: {e}", exc_info=True)
            return False

    async def shutdown(self) -> bool:
        """Shutdown plugin."""
        logger.info("Shutting down LibreNMS plugin...")
        return True

    def get_router(self) -> Optional[APIRouter]:
        return self._router

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "plugin": self.metadata.name,
            "initialized": self.is_initialized
        }
