"""
Database models for the LibreNMS plugin.
"""
from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from platform_core.database.postgres import Base

class DeviceHealth(Base):
    """Stores the health status of a device from LibreNMS."""
    __tablename__ = "librenms_device_health"

    device_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(50))
    uptime: Mapped[int] = mapped_column(Integer)
    ping_latency: Mapped[float] = mapped_column(Float)
