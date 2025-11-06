"""
Main FastAPI application for the platform.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from platform_core.database.postgres import get_database_manager
from platform_core.database.neo4j_conn import get_neo4j_manager


from platform_core.plugins.registry import plugin_registry

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    """
    logger.info("=" * 80)
    logger.info("APPLICATION STARTUP")
    logger.info("=" * 80)

    # Discover and initialize plugins
    logger.info("Step 1: Discovering plugins...")
    plugin_registry.discover_plugins()
    logger.info(f"✅ Discovered {len(plugin_registry.plugins)} plugins: {list(plugin_registry.plugins.keys())}")

    # Initialize database managers, using overrides if available
    db_manager = getattr(app.state, "db_manager_override", get_database_manager())
    neo4j_manager = getattr(app.state, "neo4j_manager_override", get_neo4j_manager())

    logger.info("Step 2: Initializing plugins...")
    await plugin_registry.initialize_all(db_manager=db_manager, neo4j_manager=neo4j_manager)
    logger.info("✅ All plugins initialized")

    # Mount plugin routers
    logger.info("Step 3: Mounting plugin routers...")
    for plugin_name, plugin in plugin_registry.plugins.items():
        router = plugin.get_router()
        if router:
            app.include_router(router, prefix=f"/api/{plugin_name}", tags=[plugin_name])
            logger.info(f"  ✅ {plugin_name}: mounted {len(router.routes)} routes at /api/{plugin_name}")
        else:
            logger.warning(f"  ⚠️  {plugin_name}: no router available")

    logger.info("=" * 80)
    logger.info("✅ APPLICATION STARTUP COMPLETE")
    logger.info("=" * 80)

    yield

    logger.info("=" * 80)
    logger.info("APPLICATION SHUTDOWN")
    logger.info("=" * 80)
    await plugin_registry.shutdown_all()
    logger.info("✅ Shutdown complete")


def create_app(db_manager_override=None, neo4j_manager_override=None) -> FastAPI:
    """
    Create and configure the FastAPI application.
    Allows for dependency overrides for testing.
    """
    app = FastAPI(
        title="Network Enterprise Platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Store overrides in the app's state to be used by the lifespan context
    if db_manager_override:
        app.state.db_manager_override = db_manager_override
    if neo4j_manager_override:
        app.state.neo4j_manager_override = neo4j_manager_override

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_tenant_id(request: Request, call_next):
        tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            # In a real app, you'd probably return a 400 Bad Request
            # For now, we'll use a default for testing
            tenant_id = "default-tenant"
        request.state.tenant_id = tenant_id
        response = await call_next(request)
        return response

    @app.get("/health")
    async def health_check():
        plugin_health = await plugin_registry.health_check_all()
        return {"status": "healthy", "plugins": plugin_health}

    return app

app = create_app()
