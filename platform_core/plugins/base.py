"""
Base classes for plugins.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class PluginMetadata(BaseModel):
    """
    Metadata for a plugin.
    """
    name: str = Field(..., description="The name of the plugin.")
    version: str = Field(..., description="The version of the plugin.")
    description: str = Field(..., description="A brief description of the plugin.")
    author: str = Field(..., description="The author of the plugin.")
    requires: List[str] = Field([], description="A list of plugins that this plugin depends on.")
    capabilities: List[str] = Field([], description="A list of capabilities that this plugin provides.")

class BasePlugin(ABC):
    """
    Abstract base class for all plugins.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_initialized = False

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Return the metadata for the plugin.
        """
        raise NotImplementedError

    async def initialize(self, **kwargs) -> bool:
        """
        Initialize the plugin.
        """
        self.is_initialized = True
        return True

    async def shutdown(self) -> bool:
        """
        Shutdown the plugin.
        """
        self.is_initialized = False
        return True

    def get_router(self) -> Optional[Any]:
        """
        Return the router for the plugin, if any.
        """
        return None

    async def health_check(self) -> Dict[str, Any]:
        """
        Return the health status of the plugin.
        """
        return {"status": "ok"}
