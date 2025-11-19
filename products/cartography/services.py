"""
Services for the Cartography plugin.
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from neo4j import AsyncSession as Neo4jAsyncSession
import logging

from products.netbox.models import Site, Device

logger = logging.getLogger(__name__)

class CartographySyncService:
    """
    Service for synchronizing data from PostgreSQL to Neo4j.
    """

    def __init__(
        self,
        db_session: AsyncSession,
        neo4j_session: Neo4jAsyncSession,
        tenant_id: UUID,
    ):
        self.db = db_session
        self.neo4j = neo4j_session
        self.tenant_id = tenant_id

    async def sync_all(self):
        """
        Runs all synchronization methods in the correct order.
        """
        logger.info(f"[{self.tenant_id}] Starting Cartography synchronization.")
        await self.sync_sites()
        await self.sync_devices()
        logger.info(f"[{self.tenant_id}] Cartography synchronization complete.")

    async def sync_sites(self):
        """
        Fetches all sites from PostgreSQL and creates corresponding nodes in Neo4j.
        """
        result = await self.db.execute(
            select(Site).where(Site.tenant_id == self.tenant_id)
        )
        sites = result.scalars().all()

        for site in sites:
            await self.neo4j.run(
                """
                MERGE (s:Site {id: $id})
                ON CREATE SET s.name = $name, s.slug = $slug, s.tenant_id = $tenant_id
                ON MATCH SET s.name = $name, s.slug = $slug
                """,
                id=str(site.id),
                name=site.name,
                slug=site.slug,
                tenant_id=str(self.tenant_id),
            )

    async def sync_devices(self):
        """
        Fetches all devices from PostgreSQL and creates corresponding nodes
        and relationships in Neo4j.
        """
        result = await self.db.execute(
            select(Device)
            .where(Device.tenant_id == self.tenant_id)
            .options(selectinload(Device.site))
        )
        devices = result.scalars().all()

        for device in devices:
            await self.neo4j.run(
                """
                MERGE (d:Device {id: $id})
                ON CREATE SET d.name = $name, d.device_type = $device_type,
                              d.device_role = $device_role, d.tenant_id = $tenant_id
                ON MATCH SET d.name = $name, d.device_type = $device_type,
                             d.device_role = $device_role
                """,
                id=str(device.id),
                name=device.name,
                device_type=device.device_type,
                device_role=device.device_role,
                tenant_id=str(self.tenant_id),
            )

            if device.site_id:
                await self.neo4j.run(
                    """
                    MATCH (d:Device {id: $device_id})
                    MATCH (s:Site {id: $site_id})
                    MERGE (d)-[:LOCATED_IN]->(s)
                    """,
                    device_id=str(device.id),
                    site_id=str(device.site_id),
                )
