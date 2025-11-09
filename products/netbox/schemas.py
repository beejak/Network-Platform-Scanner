"""Pydantic schemas for the NetBox API."""
from pydantic import BaseModel
import uuid
from typing import Optional

# ============================================================================
# Site Schemas
# ============================================================================
class SiteBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    netbox_id: int

class SiteCreate(SiteBase):
    pass

class SiteUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None

class SiteResponse(SiteBase):
    id: uuid.UUID
    tenant_id: uuid.UUID

    class Config:
        from_attributes = True

# ============================================================================
# Device Schemas
# ============================================================================
class DeviceBase(BaseModel):
    name: str
    device_type: str
    device_role: str
    serial: Optional[str] = None
    status: str
    netbox_id: int

class DeviceResponse(DeviceBase):
    id: uuid.UUID
    site_id: Optional[uuid.UUID] = None
    tenant_id: uuid.UUID

    class Config:
        from_attributes = True

# ============================================================================
# IP Address Schemas
# ============================================================================
class IPAddressBase(BaseModel):
    address: str
    dns_name: Optional[str] = None
    description: Optional[str] = None
    status: str
    netbox_id: int

class IPAddressResponse(IPAddressBase):
    id: uuid.UUID
    tenant_id: uuid.UUID

    class Config:
        from_attributes = True

# ============================================================================
# IP Prefix Schemas
# ============================================================================
class IPPrefixBase(BaseModel):
    prefix: str
    description: Optional[str] = None
    status: str
    netbox_id: int

class IPPrefixResponse(IPPrefixBase):
    id: uuid.UUID
    tenant_id: uuid.UUID

    class Config:
        from_attributes = True
