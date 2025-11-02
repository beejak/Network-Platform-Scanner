from typing import Any, Dict, List, Optional

import httpx
from platform_core.config import settings


class NetBoxClient:
    """Asynchronous client for the NetBox API."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.headers = {"Authorization": f"Token {self.token}"}

    async def _request(self, method: str, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                **kwargs,
            )
            await response.raise_for_status()
            return await response.json()

    async def get_sites(self) -> Dict[str, Any]:
        """Fetch all sites from NetBox."""
        response = await self._request("GET", "/api/dcim/sites/")
        return response

    async def get_devices(self, site_id: Optional[int] = None) -> Dict[str, Any]:
        """Fetch all devices from NetBox, optionally filtered by site."""
        params = {}
        if site_id:
            params["site_id"] = site_id
        response = await self._request("GET", "/api/dcim/devices/", params=params)
        return response

    async def get_ip_addresses(
        self, device_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Fetch all IP addresses from NetBox, optionally filtered by device."""
        params = {}
        if device_id:
            params["device_id"] = device_id
        response = await self._request("GET", "/api/ipam/ip-addresses/", params=params)
        return response

    async def get_vlans(self, site_id: Optional[int] = None) -> Dict[str, Any]:
        """Fetch all VLANs from NetBox, optionally filtered by site."""
        params = {}
        if site_id:
            params["site_id"] = site_id
        response = await self._request("GET", "/api/ipam/vlans/", params=params)
        return response
