# NetBox Plugin

This plugin synchronizes data from a NetBox instance into the platform's database.

## Architecture

The plugin consists of the following components:

- **`client.py`**: An asynchronous `httpx`-based client for the NetBox API.
- **`models.py`**: SQLAlchemy models for the NetBox data.
- **`sync.py`**: A synchronization service that fetches data from NetBox and saves it to the database.
- **`api.py`**: A FastAPI router that exposes the synchronized data through a set of API endpoints.
- **`plugin.py`**: The main plugin class that ties everything together.

## API Endpoints

The following API endpoints are available:

- `GET /api/netbox/sites`: Retrieve all sites.
- `GET /api/netbox/devices`: Retrieve all devices.
- `GET /api/netbox/ip-addresses`: Retrieve all IP addresses.

## Setup

To use this plugin, you need to provide the following environment variables:

- `NETBOX_URL`: The URL of the NetBox instance.
- `NETBOX_TOKEN`: The API token for the NetBox instance.
