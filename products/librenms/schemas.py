"""Pydantic schemas for the LibreNMS API."""
from pydantic import BaseModel
import uuid

class DeviceHealthResponse(BaseModel):
    id: uuid.UUID
    device_id: int
    status: str
    uptime: int
    ping_latency: float
    tenant_id: uuid.UUID

    class Config:
        from_attributes = True
