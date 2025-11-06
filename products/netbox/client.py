"""
Minimalistic client for interacting with the NetBox API.
"""
import httpx

class NetBoxClient:
    """A client for fetching data from the NetBox API."""
    def __init__(self, api_url: str, token: str):
        self.api_url = api_url.rstrip("/")
        self.headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def get_sites(self):
        """Asynchronously get sites from NetBox."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/api/dcim/sites/", headers=self.headers)
            response.raise_for_status()
            return response.json()["results"]

    async def get_devices(self):
        """Asynchronously get devices from NetBox."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/api/dcim/devices/", headers=self.headers)
            response.raise_for_status()
            return response.json()["results"]
