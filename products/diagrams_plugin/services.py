"""
Service for generating diagrams from NetBox data.
"""
import os
import tempfile
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from diagrams import Diagram, Cluster
from diagrams.aws.network import SiteToSiteVpn
from products.netbox.models import Site, Device

# Safe import for Router with fallback
try:
    from diagrams.cisco.network import Router
except (ImportError, AttributeError):
    from diagrams.generic.network import Router

# Safe import for Switch with fallback
try:
    from diagrams.cisco.network import Switch as L3Switch
except (ImportError, AttributeError):
    from diagrams.generic.network import Switch as L3Switch


class DiagramsService:
    """Service for generating diagrams."""

    def __init__(self, db_session: AsyncSession, tenant_id: UUID):
        self.db = db_session
        self.tenant_id = tenant_id

    async def generate_site_diagram(self, site_slug: str) -> str:
        """
        Generates a diagram for a specific site and returns the file path.
        """
        # 1. Fetch the site and its devices from the database
        result = await self.db.execute(
            select(Site)
            .where(Site.slug == site_slug, Site.tenant_id == self.tenant_id)
            .options(selectinload(Site.devices))
        )
        site = result.scalars().first()

        if not site:
            raise ValueError("Site not found")

        # 2. Generate the diagram using the 'diagrams' library
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpf:
            output_filename_base = tmpf.name.rsplit(".", 1)[0]

        with Diagram(site.name, show=False, filename=output_filename_base, outformat="png"):
            with Cluster(site.name):
                # Map device roles to diagram nodes
                device_nodes = {}
                for device in site.devices:
                    node_class = L3Switch
                    if "router" in device.device_role:
                        node_class = Router
                    elif "vpn" in device.device_role:
                        node_class = SiteToSiteVpn

                    device_nodes[device.id] = node_class(label=device.name)

        return f"{output_filename_base}.png"
