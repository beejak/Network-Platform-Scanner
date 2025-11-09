"""NetBox API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import logging

from .models import Site, Device, IPAddress, IPPrefix
from .schemas import SiteResponse, DeviceResponse, IPAddressResponse, IPPrefixResponse
from .services import NetBoxSyncService
from platform_core.api.dependencies import get_db_session
from platform_core.database.postgres import DatabaseManager

logger = logging.getLogger(__name__)


def create_netbox_router(db_manager: DatabaseManager) -> APIRouter:
    router = APIRouter()

    # ============================================================================
    # SYNCHRONIZATION
    # ============================================================================

    @router.post("/sync", status_code=202)
    async def sync_netbox_data(
        request: Request,
        db: AsyncSession = Depends(get_db_session),
    ):
        """Triggers a full data synchronization from NetBox."""
        tenant_id = request.state.tenant_id
        logger.info(f"[{tenant_id}] Starting NetBox data synchronization.")

        sync_service = NetBoxSyncService(db, tenant_id)
        await sync_service.sync_all()

        logger.info(f"[{tenant_id}] NetBox data synchronization complete.")
        return {"message": "NetBox synchronization started."}


    # ============================================================================
    # READ - SITES
    # ============================================================================

    @router.get("/sites", response_model=List[SiteResponse])
    async def get_sites(
        request: Request,
        db: AsyncSession = Depends(get_db_session),
    ):
        """Get all synchronized sites for the tenant."""
        from sqlalchemy import select

        tenant_id = request.state.tenant_id
        result = await db.execute(select(Site).where(Site.tenant_id == tenant_id))
        sites = result.scalars().all()

        return sites

    @router.get("/sites/{site_id}", response_model=SiteResponse)
    async def get_site(
        request: Request,
        site_id: UUID = Path(...),
        db: AsyncSession = Depends(get_db_session)
    ):
        """Get a specific site by its local ID."""
        tenant_id = request.state.tenant_id
        site = await db.get(Site, site_id)

        if not site or site.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Site not found")

        return site

    # ============================================================================
    # READ - DEVICES
    # ============================================================================

    @router.get("/devices", response_model=List[DeviceResponse])
    async def get_devices(
        request: Request,
        db: AsyncSession = Depends(get_db_session),
    ):
        """Get all synchronized devices for the tenant."""
        from sqlalchemy import select

        tenant_id = request.state.tenant_id
        result = await db.execute(select(Device).where(Device.tenant_id == tenant_id))
        devices = result.scalars().all()

        return devices

    # ============================================================================
    # READ - IP ADDRESSES
    # ============================================================================

    @router.get("/ip-addresses", response_model=List[IPAddressResponse])
    async def get_ip_addresses(
        request: Request,
        db: AsyncSession = Depends(get_db_session),
    ):
        """Get all synchronized IP addresses for the tenant."""
        from sqlalchemy import select

        tenant_id = request.state.tenant_id
        result = await db.execute(select(IPAddress).where(IPAddress.tenant_id == tenant_id))
        ips = result.scalars().all()

        return ips

    # ============================================================================
    # READ - IP PREFIXES
    # ============================================================================

    @router.get("/prefixes", response_model=List[IPPrefixResponse])
    async def get_prefixes(
        request: Request,
        db: AsyncSession = Depends(get_db_session),
    ):
        """Get all synchronized IP prefixes for the tenant."""
        from sqlalchemy import select

        tenant_id = request.state.tenant_id
        result = await db.execute(select(IPPrefix).where(IPPrefix.tenant_id == tenant_id))
        prefixes = result.scalars().all()

        return prefixes

    return router
