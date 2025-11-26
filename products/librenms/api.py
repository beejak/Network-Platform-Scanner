"""
API endpoints for the LibreNMS plugin.
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from platform_core.api.dependencies import get_db_session
from .services import LibreNMSSyncService
from .schemas import DeviceHealthResponse
from .models import DeviceHealth

logger = logging.getLogger(__name__)

def create_librenms_router() -> APIRouter:
    router = APIRouter()

    @router.post("/sync", status_code=202)
    async def sync_librenms_data(
        request: Request,
        db: AsyncSession = Depends(get_db_session),
    ):
        """
        Triggers a data synchronization from LibreNMS.
        """
        tenant_id = request.state.tenant_id

        sync_service = LibreNMSSyncService(db, tenant_id)
        await sync_service.sync_device_health()

        return {"message": "LibreNMS synchronization started."}

    @router.get("/health", response_model=List[DeviceHealthResponse])
    async def get_device_health(
        request: Request,
        db: AsyncSession = Depends(get_db_session),
    ):
        """
        Get the health status of all synchronized devices.
        """
        from sqlalchemy import select

        tenant_id = request.state.tenant_id
        result = await db.execute(select(DeviceHealth).where(DeviceHealth.tenant_id == tenant_id))
        health_data = result.scalars().all()

        return health_data

    return router
