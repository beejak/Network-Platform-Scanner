"""
Service for synchronizing data from a NetBox instance.
"""
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any, List

from .models import Site, Device, IPAddress
from .client import NetBoxClient

logger = logging.getLogger(__name__)

class NetBoxSyncService:
    """
    Service to synchronize data from a NetBox instance to the local database.
    """
    def __init__(self, db: AsyncSession, tenant_id: uuid.UUID):
        self.db = db
        self.tenant_id = str(tenant_id)

    async def sync_data(self):
        """
        Fetch data from NetBox and synchronize it with the local database.
        """
        # In a real app, you'd get these from config
        client = NetBoxClient(api_url="http://netbox:8080", token="test-token")

        await self._sync_sites(client)
        await self._sync_devices(client)
        await self.db.commit()

    async def _sync_sites(self, client: NetBoxClient):
        sites_data = await client.get_sites()
        for site_data in sites_data:
            site = await self.db.execute(
                select(Site).where(Site.netbox_id == site_data["id"], Site.tenant_id == self.tenant_id)
            )
            site = site.scalars().first()

            if site:
                site.name = site_data["name"]
                site.slug = site_data["slug"]
            else:
                site = Site(
                    netbox_id=site_data["id"],
                    name=site_data["name"],
                    slug=site_data["slug"],
                    tenant_id=self.tenant_id
                )
            self.db.add(site)

    async def _sync_devices(self, client: NetBoxClient):
        devices_data = await client.get_devices()
        logger.info(f"Syncing {len(devices_data)} devices...")
        for device_data in devices_data:
            device_result = await self.db.execute(
                select(Device).where(Device.netbox_id == device_data["id"], Device.tenant_id == self.tenant_id)
            )
            device = device_result.scalars().first()
            logger.info(f"Found existing device: {device}")

            site_result = await self.db.execute(
                select(Site).where(Site.netbox_id == device_data["site_id"], Site.tenant_id == self.tenant_id)
            )
            site = site_result.scalars().first()
            logger.info(f"Found site for device: {site}")

            if not site:
                logger.warning(f"Skipping device {device_data['name']} because site {device_data['site_id']} was not found.")
                continue

            if device:
                logger.info(f"Updating device {device.name}")
                device.name = device_data["name"]
                device.device_type = device_data["device_type"]
                device.device_role = device_data["device_role"]
                device.serial = device_data["serial"]
                device.site_id = site.id
            else:
                logger.info(f"Creating new device {device_data['name']}")
                device = Device(
                    netbox_id=device_data["id"],
                    name=device_data["name"],
                    device_type=device_data["device_type"],
                    device_role=device_data["device_role"],
                    serial=device_data["serial"],
                    site_id=site.id,
                    tenant_id=self.tenant_id
                )
            self.db.add(device)
            logger.info("Device added to session.")
