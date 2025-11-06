"""PostgreSQL database with Base model."""
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Base(DeclarativeBase):
    """Base model for all tables."""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        index=True
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class DatabaseManager:
    """Database manager."""

    def __init__(self, connection_string: str):
        self.engine = create_async_engine(connection_string)
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    @asynccontextmanager
    async def get_session(self, tenant_id: uuid.UUID):
        """Get session with tenant context."""
        async with self.session_factory() as session:
            # In a real app, you would set the tenant context here
            # For example: await session.execute(f"SET app.tenant_id = '{tenant_id}'")
            yield session


_db_manager = None

def get_database_manager():
    """Get DB manager singleton."""
    global _db_manager
    if _db_manager is None:
        # In a real app, you'd get this from config
        _db_manager = DatabaseManager("postgresql+asyncpg://localhost/test")
    return _db_manager
