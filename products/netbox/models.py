import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from platform_core.database.postgres import Base


class Site(Base):
    """Represents a physical location."""
    netbox_id: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255), default="")


class Device(Base):
    """Represents a network device."""
    netbox_id: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String(255))
    device_type: Mapped[str] = mapped_column(String(255))
    device_role: Mapped[str] = mapped_column(String(255))
    site_id: Mapped[int] = mapped_column(Integer)


class IPAddress(Base):
    """Represents an IP address."""
    netbox_id: Mapped[int] = mapped_column(Integer, unique=True)
    address: Mapped[str] = mapped_column(String(255))
    dns_name: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(255), default="active")
