#!/usr/bin/env python3
"""
Diagnostic script to understand what's happening in your test setup.
Run this to see exactly where the problem is.
"""
import sys
import asyncio
import logging
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Run diagnostics."""

    print("="*80)
    print("STEP 1: Import and create app")
    print("="*80)

    from platform_core.api.main import create_app

    app = create_app()
    print(f"✅ App created: {app}")
    print(f"   App lifespan: {app.router.lifespan_context}")

    print("\n" + "="*80)
    print("STEP 2: Check plugin registry")
    print("="*80)

    from platform_core.plugins.registry import plugin_registry

    print(f"Plugins discovered: {len(plugin_registry.plugins)}")
    for name, plugin in plugin_registry.plugins.items():
        print(f"  - {name}: initialized={plugin.is_initialized}")

    print("\n" + "="*80)
    print("STEP 3: Manually trigger lifespan startup")
    print("="*80)

    # Manually execute the lifespan to see what happens
    from contextlib import AsyncExitStack

    async with AsyncExitStack() as stack:
        # This simulates what happens when the app starts
        await stack.enter_async_context(app.router.lifespan_context(app))

        print("\n✅ Lifespan startup complete!")

        print("\n" + "="*80)
        print("STEP 4: Check plugins after startup")
        print("="*80)

        for name, plugin in plugin_registry.plugins.items():
            print(f"  - {name}: initialized={plugin.is_initialized}, router={plugin.get_router()}")

        print("\n" + "="*80)
        print("STEP 5: List all registered routes")
        print("="*80)

        route_count = 0
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(route.methods) if route.methods else 'N/A'
                print(f"  {methods:15s} {route.path}")
                route_count += 1

        print(f"\n✅ Total routes: {route_count}")

        # Check for specific plugin routes
        topology_routes = [r for r in app.routes if hasattr(r, 'path') and '/topology' in r.path]
        diagrams_routes = [r for r in app.routes if hasattr(r, 'path') and '/diagrams' in r.path]

        print(f"\nTopology routes: {len(topology_routes)}")
        print(f"Diagrams routes: {len(diagrams_routes)}")

        if len(topology_routes) == 0 and len(diagrams_routes) == 0:
            print("\n❌ PROBLEM FOUND: No plugin routes registered!")
            print("   This explains the 404 errors.")
        else:
            print("\n✅ Plugin routes are registered correctly.")

        print("\n" + "="*80)
        print("STEP 6: Test a request")
        print("="*80)

        from httpx import AsyncClient, ASGITransport

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Try health check
            response = await client.get("/health")
            print(f"GET /health: {response.status_code}")
            print(f"  Response: {response.json()}")

            # Try plugin endpoint
            import uuid
            headers = {"X-Tenant-ID": str(uuid.uuid4())}

            response = await client.get("/api/topology/nodes", headers=headers)
            print(f"\nGET /api/topology/nodes: {response.status_code}")

            if response.status_code == 404:
                print("  ❌ 404 Error - route not found!")
                print(f"  Response: {response.text}")
            else:
                print(f"  ✅ Success! Response: {response.json()}")

if __name__ == "__main__":
    asyncio.run(main())
