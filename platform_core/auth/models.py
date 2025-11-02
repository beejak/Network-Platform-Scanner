import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from platform_core.database.postgres import Base


# Tenant model
class Tenant(Base):
    name: Mapped[str] = mapped_column(String(255), unique=True)
    # Tenant's own tenant_id is self-referential for compatibility
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        default=lambda: uuid.uuid4(), primary_key=True
    )


# User model with tenant membership
class User(Base):
    email: Mapped[str] = mapped_column(String(255), index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
