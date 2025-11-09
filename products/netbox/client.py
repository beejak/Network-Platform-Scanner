"""
NetBox API Client
This module provides a client for interacting with the NetBox API.
"""
import pynetbox
from platform_core.config import get_settings

def get_netbox_api():
    """
    Initializes and returns a pynetbox API instance.
    """
    settings = get_settings()
    return pynetbox.api(
        url=settings.NETBOX_URL,
        token=settings.NETBOX_TOKEN
    )
