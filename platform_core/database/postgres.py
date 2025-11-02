"""
Multi-tenant PostgreSQL database with row-level security.
Every table MUST have tenant_id for isolation.
"""
import uuid

from sqlalchemy import DateTime, String, func
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import (DeclarativeBase, Mapped, declared_attr,
                            mapped_column)


class Base(DeclarativeBase):  # type: ignore
    """Base class with multi-tenancy support."""

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return str(cls.__name__.lower())

    # CRITICAL: Every table has these columns
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        index=True
    )  # MANDATORY for multi-tenancy
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )


class DatabaseManager:
    """Async database connection manager with tenant context."""

    def __init__(self, connection_string: str) -> None:
        self.engine = create_async_engine(
            connection_string, echo=False, pool_size=20, max_overflow=40
        )
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self, tenant_id: uuid.UUID) -> AsyncSession:
        """Get session with tenant context injected."""
        session = self.session_factory()
        # Set tenant context - all queries auto-filtered by tenant_id
        await session.execute(f"SET app.current_tenant = '{tenant_id}'")
        return session
