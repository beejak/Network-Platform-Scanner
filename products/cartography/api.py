"""
API endpoints for the Cartography plugin.
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from neo4j import AsyncSession as Neo4jAsyncSession
import logging

from platform_core.api.dependencies import get_db_session, get_neo4j_session
from .services import CartographySyncService

logger = logging.getLogger(__name__)

def create_cartography_router() -> APIRouter:
    router = APIRouter()

    @router.post("/sync", status_code=202)
    async def sync_cartography_data(
        request: Request,
        db: AsyncSession = Depends(get_db_session),
        neo4j: Neo4jAsyncSession = Depends(get_neo4j_session),
    ):
        """
        Triggers a full data synchronization from PostgreSQL to Neo4j.
        """
        tenant_id = request.state.tenant_id

        sync_service = CartographySyncService(db, neo4j, tenant_id)
        await sync_service.sync_all()

        return {"message": "Cartography synchronization started."}

    return router
