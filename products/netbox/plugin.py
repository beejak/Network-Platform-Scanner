"""NetBox plugin implementation."""
from platform_core.plugins.base import BasePlugin, PluginMetadata
from fastapi import APIRouter
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class NetBoxPlugin(BasePlugin):
    """NetBox IPAM/DCIM plugin."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._router = None

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="netbox",
            version="1.0.0",
            description="IP Address Management and Data Center Infrastructure",
            author="Network Platform Team",
            requires=[],
            capabilities=["ipam", "dcim"]
        )

    async def initialize(self, **kwargs) -> bool:
        """Initialize plugin."""
        try:
            logger.info("Initializing NetBox plugin...")

            db_manager = kwargs.get("db_manager")
            if not db_manager:
                raise ValueError("Database manager not provided to NetBox plugin")

            # Create router
            from .api import create_netbox_router
            self._router = create_netbox_router(db_manager)

            logger.info("✅ NetBox plugin initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize NetBox: {e}", exc_info=True)
            return False

    async def shutdown(self) -> bool:
        """Shutdown plugin."""
        logger.info("Shutting down NetBox plugin...")
        return True

    def get_router(self) -> Optional[APIRouter]:
        return self._router

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "plugin": self.metadata.name,
            "initialized": self.is_initialized
        }
