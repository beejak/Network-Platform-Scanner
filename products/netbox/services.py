"""
NetBox Data Synchronization Service
This module provides a service for synchronizing data from NetBox to the local database.
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from products.netbox.client import get_netbox_api
from products.netbox.models import Site, Device, IPAddress, IPPrefix


class NetBoxSyncService:
    """
    Service for synchronizing data from NetBox.
    """

    def __init__(self, db_session: AsyncSession, tenant_id: UUID):
        self.db = db_session
        self.tenant_id = tenant_id
        self.netbox_api = get_netbox_api()

    async def sync_all(self):
        """
        Runs all synchronization methods in the correct order.
        """
        await self.sync_sites()
        await self.sync_devices()
        await self.sync_ip_addresses()
        await self.sync_prefixes()

    async def sync_sites(self):
        """
        Fetches all sites from NetBox and upserts them into the local database.
        """
        netbox_sites = self.netbox_api.dcim.sites.all()
        if not netbox_sites:
            return

        for nb_site in netbox_sites:
            result = await self.db.execute(
                select(Site).where(
                    Site.netbox_id == nb_site.id, Site.tenant_id == self.tenant_id
                )
            )
            site = result.scalars().first()

            if site:
                site.name = nb_site.name
                site.slug = nb_site.slug
                site.description = nb_site.description or ""
            else:
                site = Site(
                    netbox_id=nb_site.id,
                    name=nb_site.name,
                    slug=nb_site.slug,
                    description=nb_site.description or "",
                    tenant_id=self.tenant_id,
                )
                self.db.add(site)
        await self.db.commit()

    async def sync_devices(self):
        """
        Fetches all devices from NetBox and upserts them into the local database.
        """
        netbox_devices = self.netbox_api.dcim.devices.all()
        if not netbox_devices:
            return

        for nb_device in netbox_devices:
            # Find the corresponding local site
            site_id = None
            if nb_device.site:
                result = await self.db.execute(
                    select(Site).where(
                        Site.netbox_id == nb_device.site.id,
                        Site.tenant_id == self.tenant_id,
                    )
                )
                site = result.scalars().first()
                if site:
                    site_id = site.id

            result = await self.db.execute(
                select(Device).where(
                    Device.netbox_id == nb_device.id, Device.tenant_id == self.tenant_id
                )
            )
            device = result.scalars().first()

            if device:
                # Update existing device
                device.name = nb_device.name
                device.device_type = nb_device.device_type.slug
                device.device_role = nb_device.device_role.slug
                device.serial = nb_device.serial or ""
                device.site_id = site_id
                device.status = nb_device.status.value
            else:
                # Create new device
                device = Device(
                    netbox_id=nb_device.id,
                    name=nb_device.name,
                    device_type=nb_device.device_type.slug,
                    device_role=nb_device.device_role.slug,
                    serial=nb_device.serial or "",
                    site_id=site_id,
                    status=nb_device.status.value,
                    tenant_id=self.tenant_id,
                )
                self.db.add(device)
        await self.db.commit()

    async def sync_ip_addresses(self):
        """
        Fetches all IP addresses from NetBox and upserts them into the local database.
        """
        netbox_ips = self.netbox_api.ipam.ip_addresses.all()
        if not netbox_ips:
            return

        for nb_ip in netbox_ips:
            result = await self.db.execute(
                select(IPAddress).where(
                    IPAddress.netbox_id == nb_ip.id,
                    IPAddress.tenant_id == self.tenant_id,
                )
            )
            ip_address = result.scalars().first()

            if ip_address:
                # Update existing IP address
                ip_address.address = str(nb_ip.address)
                ip_address.dns_name = nb_ip.dns_name or ""
                ip_address.description = nb_ip.description or ""
                ip_address.status = nb_ip.status.value
            else:
                # Create new IP address
                ip_address = IPAddress(
                    netbox_id=nb_ip.id,
                    address=str(nb_ip.address),
                    dns_name=nb_ip.dns_name or "",
                    description=nb_ip.description or "",
                    status=nb_ip.status.value,
                    tenant_id=self.tenant_id,
                )
                self.db.add(ip_address)
        await self.db.commit()

    async def sync_prefixes(self):
        """
        Fetches all IP prefixes from NetBox and upserts them into the local database.
        """
        netbox_prefixes = self.netbox_api.ipam.prefixes.all()
        if not netbox_prefixes:
            return

        for nb_prefix in netbox_prefixes:
            result = await self.db.execute(
                select(IPPrefix).where(
                    IPPrefix.netbox_id == nb_prefix.id,
                    IPPrefix.tenant_id == self.tenant_id,
                )
            )
            prefix = result.scalars().first()

            if prefix:
                # Update existing prefix
                prefix.prefix = str(nb_prefix.prefix)
                prefix.description = nb_prefix.description or ""
                prefix.status = nb_prefix.status.value
            else:
                # Create new prefix
                prefix = IPPrefix(
                    netbox_id=nb_prefix.id,
                    prefix=str(nb_prefix.prefix),
                    description=nb_prefix.description or "",
                    status=nb_prefix.status.value,
                    tenant_id=self.tenant_id,
                )
                self.db.add(prefix)
        await self.db.commit()
