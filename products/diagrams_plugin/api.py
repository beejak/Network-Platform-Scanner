"""
API endpoints for the Diagrams plugin.
"""
import os
from fastapi import APIRouter, Depends, HTTPException, Request, Path
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTask
import logging

from platform_core.api.dependencies import get_db_session
from .services import DiagramsService

logger = logging.getLogger(__name__)

def create_diagrams_router() -> APIRouter:
    router = APIRouter()

    @router.post("/generate/{site_slug}")
    async def generate_site_diagram(
        request: Request,
        site_slug: str = Path(..., description="The slug of the site to generate a diagram for."),
        db: AsyncSession = Depends(get_db_session),
    ):
        """
        Generates a network diagram for a specific site.
        """
        tenant_id = request.state.tenant_id
        logger.info(f"[{tenant_id}] Generating diagram for site: {site_slug}")

        service = DiagramsService(db, tenant_id)

        try:
            diagram_path = await service.generate_site_diagram(site_slug)

            # Use a background task to clean up the temporary file after the response is sent
            cleanup_task = BackgroundTask(os.remove, diagram_path)

            return FileResponse(
                diagram_path,
                media_type="image/png",
                background=cleanup_task,
            )
        except ValueError as e:
            logger.warning(f"[{tenant_id}] Site not found for diagram generation: {site_slug}")
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(f"[{tenant_id}] Failed to generate diagram for site {site_slug}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to generate diagram.")

    return router
