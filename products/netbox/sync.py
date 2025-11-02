import uuid
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from platform_core.database.postgres import DatabaseManager
from products.netbox.client import NetBoxClient
from products.netbox.models import Device, IPAddress, Site


class NetBoxSyncService:
    """Service for syncing NetBox data to local database."""

    def __init__(self, client: NetBoxClient, db_manager: DatabaseManager):
        self.client = client
        self.db_manager = db_manager

    async def sync_sites(self, tenant_id: uuid.UUID) -> int:
        """Sync sites from NetBox to local database."""
        # 1. Get data from NetBox API (full response with 'results' key)
        response = await self.client.get_sites()
        sites_data = response.get("results", [])  # ← Extract results list

        # 2. Get database session with tenant context
        async with self.db_manager.get_session(tenant_id) as session:
            synced_count = 0

            # 3. Process each item
            for site_data in sites_data:
                # Check if exists
                result = await session.execute(
                    select(Site).where(
                        Site.netbox_id == site_data["id"],
                        Site.tenant_id == tenant_id,
                    )
                )
                existing_site = result.scalar_one_or_none()

                if existing_site:
                    # Update existing
                    existing_site.name = site_data["name"]
                    existing_site.slug = site_data["slug"]
                    existing_site.description = site_data.get("description", "")
                else:
                    # Create new
                    new_site = Site(
                        netbox_id=site_data["id"],
                        name=site_data["name"],
                        slug=site_data["slug"],
                        description=site_data.get("description", ""),
                        tenant_id=tenant_id,
                    )
                    await session.add(new_site)

                synced_count += 1

            # 4. Commit transaction
            await session.commit()

        return synced_count

    async def sync_devices(self, tenant_id: uuid.UUID) -> int:
        """Sync devices from NetBox."""
        response = await self.client.get_devices()
        devices_data = response.get("results", [])

        async with self.db_manager.get_session(tenant_id) as session:
            synced_count = 0

            for device_data in devices_data:
                result = await session.execute(
                    select(Device).where(
                        Device.netbox_id == device_data["id"],
                        Device.tenant_id == tenant_id,
                    )
                )
                existing_device = result.scalar_one_or_none()

                if existing_device:
                    existing_device.name = device_data["name"]
                    existing_device.device_type = device_data.get(
                        "device_type", {}
                    ).get("display", "")
                    existing_device.device_role = device_data.get(
                        "device_role", {}
                    ).get("display", "")
                    existing_device.site_id = device_data.get("site", {}).get("id")
                else:
                    new_device = Device(
                        netbox_id=device_data["id"],
                        name=device_data["name"],
                        device_type=device_data.get("device_type", {}).get(
                            "display", ""
                        ),
                        device_role=device_data.get("device_role", {}).get(
                            "display", ""
                        ),
                        site_id=device_data.get("site", {}).get("id"),
                        tenant_id=tenant_id,
                    )
                    await session.add(new_device)

                synced_count += 1

            await session.commit()

        return synced_count

    async def sync_ip_addresses(self, tenant_id: uuid.UUID) -> int:
        """Sync IP addresses from NetBox."""
        response = await self.client.get_ip_addresses()
        ip_data_list = response.get("results", [])

        async with self.db_manager.get_session(tenant_id) as session:
            synced_count = 0

            for ip_data in ip_data_list:
                result = await session.execute(
                    select(IPAddress).where(
                        IPAddress.netbox_id == ip_data["id"],
                        IPAddress.tenant_id == tenant_id,
                    )
                )
                existing_ip = result.scalar_one_or_none()

                if existing_ip:
                    existing_ip.address = ip_data["address"]
                    existing_ip.dns_name = ip_data.get("dns_name", "")
                    existing_ip.description = ip_data.get("description", "")
                    existing_ip.status = ip_data.get("status", {}).get("value", "active")
                else:
                    new_ip = IPAddress(
                        netbox_id=ip_data["id"],
                        address=ip_data["address"],
                        dns_name=ip_data.get("dns_name", ""),
                        description=ip_data.get("description", ""),
                        status=ip_data.get("status", {}).get("value", "active"),
                        tenant_id=tenant_id,
                    )
                    await session.add(new_ip)

                synced_count += 1

            await session.commit()

        return synced_count
