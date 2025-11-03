"""
Abstract base class for all product plugins.
Each of the 15 products will inherit from this.
"""
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel


class PluginMetadata(BaseModel):  # type: ignore
    """Plugin metadata model."""

    name: str
    version: str
    description: str
    author: str
    requires: List[str] = []  # Dependencies on other plugins
    capabilities: List[str] = []


class BasePlugin(ABC):
    """Abstract base class that all product plugins inherit."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.metadata = self.get_metadata()
        self.is_initialized = False

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass

    @abstractmethod
    async def initialize(self, **kwargs) -> bool:
        """Initialize plugin resources (DB tables, connections, etc.)."""
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """Cleanup plugin resources."""
        pass

    @abstractmethod
    def get_router(self) -> Optional[APIRouter]:
        """Return FastAPI router for plugin API endpoints."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check plugin health status."""
        pass

    # Tenant-aware methods
    async def on_tenant_created(self, tenant_id: uuid.UUID) -> None:
        """Hook called when new tenant is created."""
        pass

    async def on_tenant_deleted(self, tenant_id: uuid.UUID) -> None:
        """Hook called when tenant is deleted."""
        pass
