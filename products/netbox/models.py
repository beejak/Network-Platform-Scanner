"""
NetBox database models.

These are SQLAlchemy models for NetBox entities.
"""
from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from platform_core.database.postgres import Base


class Site(Base):
    """Data center site model."""
    __tablename__ = "netbox_sites"

    netbox_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    devices: Mapped[list["Device"]] = relationship(back_populates="site")


class Device(Base):
    """Network device model."""
    __tablename__ = "netbox_devices"

    netbox_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_type: Mapped[str] = mapped_column(String(100))
    device_role: Mapped[str] = mapped_column(String(100))
    serial: Mapped[str] = mapped_column(String(100), nullable=True)
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("netbox_sites.id"),
        nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), default="active")

    # Relationships
    site: Mapped["Site"] = relationship(back_populates="devices")


class IPAddress(Base):
    """IP address model."""
    __tablename__ = "netbox_ipaddresses"

    netbox_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    address: Mapped[str] = mapped_column(String(50), nullable=False)
    dns_name: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")


class IPPrefix(Base):
    """IP prefix/subnet model."""
    __tablename__ = "netbox_prefixes"

    netbox_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    prefix: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
