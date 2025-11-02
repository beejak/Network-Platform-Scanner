from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from platform_core.auth.dependencies import get_db
from products.netbox.models import Device, IPAddress, Site
from pydantic import BaseModel, UUID4
import uuid

router = APIRouter()

class SiteRead(BaseModel):
    id: UUID4
    name: str
    slug: str
    tenant_id: UUID4

    model_config = {"from_attributes": True}

class DeviceRead(BaseModel):
    id: UUID4
    name: str
    site_id: UUID4
    device_type: str
    serial: str
    tenant_id: UUID4

    model_config = {"from_attributes": True}

class IPAddressRead(BaseModel):
    id: UUID4
    address: str
    device_id: UUID4
    tenant_id: UUID4

    model_config = {"from_attributes": True}



@router.get("/sites", response_model=List[SiteRead])
async def read_sites(
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all sites."""
    result = await db.execute(select(Site))
    return result.scalars().all()


@router.get("/devices", response_model=List[DeviceRead])
async def read_devices(
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all devices."""
    result = await db.execute(select(Device))
    return result.scalars().all()


@router.get("/ip-addresses", response_model=List[IPAddressRead])
async def read_ip_addresses(
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all IP addresses."""
    result = await db.execute(select(IPAddress))
    return result.scalars().all()
