"""NetBox API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
import logging

from .models import Site
from .schemas import SiteCreate, SiteResponse, SiteUpdate
from platform_core.api.dependencies import get_db_session
from platform_core.database.postgres import DatabaseManager

logger = logging.getLogger(__name__)


def create_netbox_router(db_manager: DatabaseManager) -> APIRouter:
    router = APIRouter()

    # ============================================================================
    # CREATE
    # ============================================================================

    @router.post("/sites", response_model=SiteResponse)
    async def create_site(
        site_data: SiteCreate,
        db: AsyncSession = Depends(get_db_session)
    ):
        """Create a new site."""
        logger.info(f"Creating site: {site_data.name}")

        # Extract tenant_id from db session context
        # (In real implementation, get from request.state)
        tenant_id = uuid.uuid4()  # For testing

        site = Site(
            **site_data.dict(),
            tenant_id=tenant_id
        )

        db.add(site)
        await db.commit()
        await db.refresh(site)

        # Publish event to RabbitMQ
        from platform_core.rabbitmq import get_rabbitmq_manager
        rabbitmq_manager = get_rabbitmq_manager()
        event_data = SiteResponse.from_orm(site).model_dump_json()
        await rabbitmq_manager.publish_event(
            routing_key="site.created",
            message_body=event_data,
        )

        logger.info(f"Site created: {site.id}")
        return site


    # ============================================================================
    # READ
    # ============================================================================

    @router.get("/sites", response_model=List[SiteResponse])
    async def get_sites(
        db: AsyncSession = Depends(get_db_session)
    ):
        """Get all sites."""
        from sqlalchemy import select

        result = await db.execute(select(Site))
        sites = result.scalars().all()

        return sites


    @router.get("/sites/{site_id}", response_model=SiteResponse)
    async def get_site(
        site_id: uuid.UUID = Path(...),
        db: AsyncSession = Depends(get_db_session)
    ):
        """Get a specific site."""
        logger.info(f"Getting site: {site_id}")

        # CRITICAL: This is what needs to work in tests!
        site = await db.get(Site, site_id)

        if not site:
            logger.warning(f"Site not found: {site_id}")
            raise HTTPException(status_code=404, detail="Site not found")

        return site


    # ============================================================================
    # UPDATE
    # ============================================================================

    @router.put("/sites/{site_id}", response_model=SiteResponse)
    async def update_site(
        site_id: uuid.UUID,
        site_data: SiteUpdate,
        db: AsyncSession = Depends(get_db_session)
    ):
        """Update a site."""
        logger.info(f"Updating site: {site_id}")

        # CRITICAL: This db.get() must return object from mock!
        site = await db.get(Site, site_id)

        if not site:
            logger.warning(f"Site not found: {site_id}")
            raise HTTPException(status_code=404, detail="Site not found")

        # Update fields
        for key, value in site_data.dict(exclude_unset=True).items():
            setattr(site, key, value)

        await db.commit()
        await db.refresh(site)

        logger.info(f"Site updated: {site_id}")
        return site


    # ============================================================================
    # DELETE
    # ============================================================================

    @router.delete("/sites/{site_id}")
    async def delete_site(
        site_id: uuid.UUID,
        db: AsyncSession = Depends(get_db_session)
    ):
        """Delete a site."""
        logger.info(f"Deleting site: {site_id}")

        # CRITICAL: This db.get() must return object from mock!
        site = await db.get(Site, site_id)

        if not site:
            logger.warning(f"Site not found: {site_id}")
            raise HTTPException(status_code=404, detail="Site not found")

        await db.delete(site)
        await db.commit()

        logger.info(f"Site deleted: {site_id}")
        return {"message": "Site deleted successfully"}

    return router
