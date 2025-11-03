"""FastAPI application with plugin support."""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import uuid
from typing import Optional

from platform_core.plugins.registry import plugin_registry
from platform_core.database.neo4j_conn import Neo4jManager, neo4j_manager as global_neo4j_manager

logger = logging.getLogger(__name__)


def lifespan_factory(neo4j_manager: Neo4jManager):
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """
        Application lifespan management.
        """
        logger.info("="*80)
        logger.info("APPLICATION STARTUP")
        logger.info("="*80)

        try:
            # Step 1: Discover plugins
            logger.info("Step 1: Discovering plugins...")
            plugin_registry.discover_plugins()

            plugin_count = len(plugin_registry.plugins)
            logger.info(f"✅ Discovered {plugin_count} plugins: {list(plugin_registry.plugins.keys())}")

            if plugin_count == 0:
                logger.error("❌ NO PLUGINS DISCOVERED! This will cause 404 errors!")
                if os.getenv("TESTING") == "true":
                    raise RuntimeError("No plugins discovered in test mode!")

            # Step 2: Initialize plugins
            logger.info("Step 2: Initializing plugins...")
            await plugin_registry.initialize_all(neo4j_manager=neo4j_manager)
            logger.info("✅ All plugins initialized")

            # Step 3: Mount plugin routers
            logger.info("Step 3: Mounting plugin routers...")

            for plugin_name, plugin in plugin_registry.plugins.items():
                router = plugin.get_router()

                if router:
                    prefix = f"/api/{plugin_name}"
                    app.include_router(router, prefix=prefix, tags=[plugin_name])
                    route_count = len(router.routes)
                    logger.info(f"  ✅ {plugin_name}: mounted {route_count} routes at {prefix}")
                else:
                    logger.warning(f"  ⚠️  {plugin_name}: no router available")

            logger.info("="*80)
            logger.info("✅ APPLICATION STARTUP COMPLETE")
            logger.info("="*80)

        except Exception as e:
            logger.error(f"❌ STARTUP FAILED: {e}", exc_info=True)
            raise

        yield

        logger.info("="*80)
        logger.info("APPLICATION SHUTDOWN")
        logger.info("="*80)

        try:
            await plugin_registry.shutdown_all()
            logger.info("✅ Shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    return lifespan


def create_app(neo4j_manager: Optional[Neo4jManager] = None) -> FastAPI:
    """Create FastAPI application."""
    manager = neo4j_manager if neo4j_manager else global_neo4j_manager

    app = FastAPI(
        title="Network Infrastructure Platform",
        version="1.0.0",
        lifespan=lifespan_factory(manager)
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health endpoint
    @app.get("/health")
    def health():
        return {
            "status": "healthy",
            "plugins": list(plugin_registry.plugins.keys())
        }

    return app
