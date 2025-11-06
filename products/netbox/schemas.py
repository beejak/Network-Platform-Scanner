"""Pydantic schemas for the NetBox API."""
from pydantic import BaseModel
import uuid

from typing import Optional

class SiteCreate(BaseModel):
    netbox_id: int
    name: str
    slug: str
    description: str

class SiteUpdate(BaseModel):
    netbox_id: Optional[int] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None

class SiteResponse(BaseModel):
    id: uuid.UUID
    netbox_id: int
    name: str
    slug: str
    description: str
    tenant_id: uuid.UUID

    class Config:
        from_attributes = True
