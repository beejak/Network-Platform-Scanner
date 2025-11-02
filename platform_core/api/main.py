"""
FastAPI application with tenant isolation middleware.
"""
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from platform_core.auth.rbac import RBACManager
from platform_core.config import settings
from platform_core.database.postgres import DatabaseManager
from platform_core.events.bus import event_bus
from platform_core.plugins.registry import plugin_registry

logger = logging.getLogger(__name__)


from typing import AsyncGenerator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown."""
    # Startup
    logger.info("Starting Network Platform...")

    app.state.db_manager = DatabaseManager(settings.DATABASE_URL)

    # Connect event bus
    await event_bus.connect()

    # Discover and initialize plugins
    plugin_registry.discover_plugins()
    await plugin_registry.initialize_all()

    # Mount plugin routers
    for plugin_name, plugin in plugin_registry.plugins.items():
        router = plugin.get_router()
        if router:
            app.include_router(router, prefix=f"/api/{plugin_name}", tags=[plugin_name])

    logger.info("Platform started successfully")
    yield

    # Shutdown
    logger.info("Shutting down platform...")
    for plugin in plugin_registry.plugins.values():
        await plugin.shutdown()
    await app.state.db_manager.engine.dispose()


def create_app() -> FastAPI:
    """Factory function to create FastAPI app."""
    app = FastAPI(
        title="Network Infrastructure Platform", version="1.0.0", lifespan=lifespan
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from platform_core.api.middleware import TenantIsolationMiddleware

    app.add_middleware(TenantIsolationMiddleware)

    @app.get("/health")  # type: ignore
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
