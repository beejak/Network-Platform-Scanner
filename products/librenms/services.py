"""
Services for the LibreNMS plugin.
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pylibrenms import Librenms
import logging

from platform_core.config import get_settings
from .models import DeviceHealth

logger = logging.getLogger(__name__)

class LibreNMSSyncService:
    """
    Service for synchronizing data from LibreNMS.
    """

    def __init__(self, db_session: AsyncSession, tenant_id: UUID):
        self.db = db_session
        self.tenant_id = tenant_id

        settings = get_settings()
        self.librenms_api = Librenms(
            url=settings.LIBRENMS_URL,
            token=settings.LIBRENMS_TOKEN,
            ssl_verify=False # HACK: for local dev
        )

    async def sync_device_health(self):
        """
        Fetches the health status of all devices from LibreNMS and
        upserts them into the local database.
        """
        try:
            devices = self.librenms_api.list_devices()
            if not devices:
                return

            for device in devices:
                # Fetch detailed health information for each device
                health_info = self.librenms_api.get_device_health(device["device_id"])
                if not health_info:
                    continue

                # Check for ping latency - a key health indicator
                ping_health = next((item for item in health_info if item["type"] == "ping"), None)
                if not ping_health:
                    continue

                result = await self.db.execute(
                    select(DeviceHealth).where(
                        DeviceHealth.device_id == device["device_id"],
                        DeviceHealth.tenant_id == self.tenant_id,
                    )
                )
                device_health = result.scalars().first()

                if device_health:
                    # Update existing health status
                    device_health.status = "up" if device["status"] else "down"
                    device_health.uptime = device["uptime"]
                    device_health.ping_latency = ping_health["value"]
                else:
                    # Create new health status
                    device_health = DeviceHealth(
                        device_id=device["device_id"],
                        status="up" if device["status"] else "down",
                        uptime=device["uptime"],
                        ping_latency=ping_health["value"],
                        tenant_id=self.tenant_id,
                    )
                    self.db.add(device_health)
            await self.db.commit()

        except Exception as e:
            logger.error(f"[{self.tenant_id}] Failed to sync LibreNMS device health: {e}", exc_info=True)
            await self.db.rollback()
