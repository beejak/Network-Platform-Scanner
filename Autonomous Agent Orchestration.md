# 🎯 AUTONOMOUS AGENT ORCHESTRATION: 2-WEEK ENTERPRISE NETWORK INFRASTRUCTURE PLATFORM

## 📋 EXECUTIVE SUMMARY

This document contains chess-grandmaster-level autonomous agent prompts to build 15 enterprise-ready network infrastructure products in Python over 14 days with minimal human intervention. The strategy employs modular architecture, multi-tenancy, RBAC, comprehensive testing, and automated CI/CD error resolution.

**Target Output**: Production-ready network infrastructure platform combining:
- Infrastructure Visualization (Diagrams, Cartography, NetBox)
- Container/K8s Networks (Kubeshark, Otterize, Weave Scope, Kiali)  
- Traditional Network Mapping (LibreNMS, Nmap, Natlas)
- Flow Analytics (Akvorado, PewView)
- Modern Telemetry (gNMIc, Jalapeno)

**Architecture**: Modular Python platform with optional event-driven capabilities, PostgreSQL + Neo4j + ClickHouse backends, multi-tenant isolation, and role-based access control.

---

## 🎓 CHESS GRANDMASTER STRATEGY: 14-DAY ORCHESTRATION PLAN

### Phase 1: Foundation & Architecture (Days 1-2)
**Objective**: Establish core platform infrastructure before any product implementation

**Critical Path Dependencies**:
1. Multi-tenancy database schema (blocks all products)
2. RBAC policy engine (blocks all API development)
3. Core module plugin system (enables parallel product development)
4. Event bus infrastructure (enables async communication)

**Parallel Tracks After Day 2**:
- Track A: Visualization products (3 products)
- Track B: Container networking (4 products)
- Track C: Traditional mapping (3 products)
- Track D: Flow analytics (2 products)
- Track E: Modern telemetry (2 products)

### Phase 2: Core Implementation (Days 3-10)
**Product Development Priority Order** (based on dependencies):

**Week 1 (Days 3-7)**:
- Day 3-4: NetBox (IPAM/DCIM foundation) - HIGHEST PRIORITY
- Day 3-4: Diagrams (code-based visualization) - LOW COMPLEXITY
- Day 5-6: Cartography (Neo4j graph foundation) - MEDIUM COMPLEXITY
- Day 5-6: LibreNMS (SNMP foundation) - CRITICAL FOR TRADITIONAL MAPPING
- Day 7: Nmap (scanning foundation) - ENABLES NATLAS

**Week 2 (Days 8-10)**:
- Day 8: Natlas (depends on Nmap)
- Day 8: PewView (3D visualization - standalone)
- Day 9: Kubeshark (eBPF/K8s foundation)  
- Day 9: gNMIc (gRPC/gNMI foundation) - ENABLES JALAPENO
- Day 10: Kiali, Otterize, Weave Scope (all depend on K8s foundation)
- Day 10: Jalapeno (depends on gNMIc), Akvorado (ClickHouse foundation)

### Phase 3: Testing & Hardening (Days 11-12)
- Unit tests for all modules (pytest + mocks)
- Integration tests (Docker Compose environments)
- Security testing (bandit, RBAC validation)
- Performance testing (load tests for telemetry collectors)

### Phase 4: Error Resolution & Production Readiness (Days 13-14)
- Automated linting pipeline (black, pylint, mypy, isort)
- CI/CD integration (GitHub Actions)
- Documentation generation
- Deployment configurations (Docker + Kubernetes)

---

## 🏗️ MASTER PLATFORM ARCHITECTURE PROMPT

```markdown
# AUTONOMOUS AGENT TASK: Platform Foundation (Days 1-2)

## OBJECTIVE
Build the core enterprise platform infrastructure that all 15 products will use. This is the FOUNDATION - no product-specific code yet.

## CRITICAL SUCCESS CRITERIA
- Multi-tenant database schema with row-level security
- RBAC policy engine with Casbin
- Plugin system for modular product architecture
- Event bus for async communication (RabbitMQ)
- RESTful API gateway with FastAPI
- All work MUST pass: black, pylint (score >8.0), mypy (strict mode), pytest

## TECHNICAL STACK
- **Web Framework**: FastAPI (async ASGI)
- **Databases**: PostgreSQL (primary), Neo4j (graph), ClickHouse (timeseries/flows)
- **Message Queue**: RabbitMQ (via aio-pika)
- **RBAC**: Casbin (pycasbin)
- **ORM**: SQLAlchemy 2.0 (async)
- **Testing**: pytest, pytest-asyncio, pytest-mock
- **Linting**: black, pylint, mypy, isort
- **Containerization**: Docker + Docker Compose

## DETAILED IMPLEMENTATION PLAN

### Step 1: Project Structure (30 minutes)
Create this EXACT directory structure:
```
network-platform/
├── platform_core/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── postgres.py          # PostgreSQL connection + multi-tenant models
│   │   ├── neo4j_conn.py        # Neo4j connection
│   │   ├── clickhouse_conn.py   # ClickHouse connection
│   │   └── migrations/          # Alembic migrations
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── rbac.py             # Casbin RBAC engine
│   │   ├── models.py            # User, Tenant, Role models
│   │   └── dependencies.py      # FastAPI auth dependencies
│   ├── plugins/
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract base plugin class
│   │   ├── registry.py          # Plugin registry and loader
│   │   └── lifecycle.py         # Plugin lifecycle management
│   ├── events/
│   │   ├── __init__.py
│   │   ├── bus.py               # RabbitMQ event bus
│   │   ├── schemas.py           # Event payload schemas
│   │   └── handlers.py          # Base event handler
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app creation
│   │   ├── middleware.py        # Tenant isolation middleware
│   │   └── routes/              # Core API routes
│   └── config.py                # Pydantic settings
├── products/                     # Plugin directory for 15 products
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .pylintrc
├── mypy.ini
└── README.md
```

### Step 2: Core Database Models with Multi-Tenancy (2 hours)

**File: platform_core/database/postgres.py**
```python
"""
Multi-tenant PostgreSQL database with row-level security.
Every table MUST have tenant_id for isolation.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy import String, DateTime, func, Index
from typing import Optional
import uuid

class Base(DeclarativeBase):
    """Base class with multi-tenancy support."""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # CRITICAL: Every table has these columns
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(index=True)  # MANDATORY for multi-tenancy
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())


class DatabaseManager:
    """Async database connection manager with tenant context."""

    def __init__(self, connection_string: str):
        self.engine = create_async_engine(
            connection_string,
            echo=False,
            pool_size=20,
            max_overflow=40
        )
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self, tenant_id: uuid.UUID) -> AsyncSession:
        """Get session with tenant context injected."""
        session = self.session_factory()
        # Set tenant context - all queries auto-filtered by tenant_id
        await session.execute(f"SET app.current_tenant = '{tenant_id}'")
        return session


# Tenant model
class Tenant(Base):
    __tablename__ = 'tenants'
    name: Mapped[str] = mapped_column(String(255), unique=True)
    # Tenant's own tenant_id is self-referential for compatibility
    tenant_id: Mapped[uuid.UUID] = mapped_column(default=lambda: uuid.uuid4())

# User model with tenant membership
class User(Base):
    __tablename__ = 'users'
    email: Mapped[str] = mapped_column(String(255), index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
```

### Step 3: RBAC with Casbin (2 hours)

**File: platform_core/auth/rbac.py**
```python
"""
Role-Based Access Control using Casbin.
Supports multi-tenancy with per-tenant policies.
"""
import casbin
import casbin_async_sqlalchemy_adapter
from typing import List, Optional
import uuid

class RBACManager:
    """Manages RBAC policies with Casbin."""

    def __init__(self, db_url: str):
        # Casbin model definition
        self.model_conf = """
[request_definition]
r = sub, obj, act, tenant

[policy_definition]
p = sub, obj, act, tenant

[role_definition]
g = _, _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub, r.tenant) && r.obj == p.obj && r.act == p.act && r.tenant == p.tenant
"""
        # Initialize adapter (async SQLAlchemy)
        self.adapter = casbin_async_sqlalchemy_adapter.Adapter(db_url)
        self.enforcer = casbin.AsyncEnforcer(self.model_conf, self.adapter)

    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: str
    ) -> bool:
        """Check if user has permission for action on resource in tenant."""
        return await self.enforcer.enforce(user_id, resource, action, tenant_id)

    async def add_role_for_user(
        self,
        user_id: str,
        role: str,
        tenant_id: str
    ) -> bool:
        """Assign role to user within a tenant."""
        return await self.enforcer.add_role_for_user(user_id, role, tenant_id)

    async def add_policy(
        self,
        role: str,
        resource: str,
        action: str,
        tenant_id: str
    ) -> bool:
        """Add permission policy for a role in a tenant."""
        return await self.enforcer.add_policy(role, resource, action, tenant_id)

# Default roles and permissions
DEFAULT_ROLES = {
    "admin": ["*", "*", "all"],  # Full access
    "operator": ["devices", "networks", "flows"],
    "viewer": ["read"],
}
```

### Step 4: Plugin System (3 hours)

**File: platform_core/plugins/base.py**
```python
"""
Abstract base class for all product plugins.
Each of the 15 products will inherit from this.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from fastapi import APIRouter
from pydantic import BaseModel
import uuid

class PluginMetadata(BaseModel):
    """Plugin metadata model."""
    name: str
    version: str
    description: str
    author: str
    requires: List[str] = []  # Dependencies on other plugins
    capabilities: List[str] = []

class BasePlugin(ABC):
    """Abstract base class that all product plugins inherit."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metadata = self.get_metadata()
        self.is_initialized = False

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize plugin resources (DB tables, connections, etc.)."""
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """Cleanup plugin resources."""
        pass

    @abstractmethod
    def get_router(self) -> Optional[APIRouter]:
        """Return FastAPI router for plugin API endpoints."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check plugin health status."""
        pass

    # Tenant-aware methods
    async def on_tenant_created(self, tenant_id: uuid.UUID):
        """Hook called when new tenant is created."""
        pass

    async def on_tenant_deleted(self, tenant_id: uuid.UUID):
        """Hook called when tenant is deleted."""
        pass
```

**File: platform_core/plugins/registry.py**
```python
"""
Plugin registry for loading and managing plugins.
"""
from typing import Dict, List, Optional
from .base import BasePlugin, PluginMetadata
import importlib
import pkgutil
import logging

logger = logging.getLogger(__name__)

class PluginRegistry:
    """Central registry for all plugins."""

    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.load_order: List[str] = []

    def register_plugin(self, plugin: BasePlugin) -> bool:
        """Register a plugin instance."""
        name = plugin.metadata.name
        if name in self.plugins:
            logger.warning(f"Plugin {name} already registered")
            return False

        self.plugins[name] = plugin
        logger.info(f"Registered plugin: {name} v{plugin.metadata.version}")
        return True

    def discover_plugins(self, plugin_directory: str = "products"):
        """Auto-discover plugins in the products directory."""
        import products  # The products package

        for importer, modname, ispkg in pkgutil.iter_modules(products.__path__):
            if ispkg:
                try:
                    module = importlib.import_module(f"products.{modname}")
                    # Look for Plugin class in module
                    if hasattr(module, 'Plugin'):
                        plugin_class = getattr(module, 'Plugin')
                        plugin_instance = plugin_class(config={})
                        self.register_plugin(plugin_instance)
                except Exception as e:
                    logger.error(f"Failed to load plugin {modname}: {e}")

    async def initialize_all(self):
        """Initialize all plugins in dependency order."""
        # Topological sort based on requires
        self.load_order = self._compute_load_order()

        for plugin_name in self.load_order:
            plugin = self.plugins[plugin_name]
            try:
                await plugin.initialize()
                plugin.is_initialized = True
                logger.info(f"Initialized plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Failed to initialize {plugin_name}: {e}")
                raise

    def _compute_load_order(self) -> List[str]:
        """Compute plugin load order based on dependencies."""
        # Simple topological sort
        visited = set()
        order = []

        def visit(name: str):
            if name in visited:
                return
            visited.add(name)
            plugin = self.plugins[name]
            for dep in plugin.metadata.requires:
                if dep in self.plugins:
                    visit(dep)
            order.append(name)

        for name in self.plugins:
            visit(name)

        return order

# Global registry instance
plugin_registry = PluginRegistry()
```

### Step 5: Event Bus (RabbitMQ) (2 hours)

**File: platform_core/events/bus.py**
```python
"""
Async event bus using RabbitMQ for inter-plugin communication.
"""
import aio_pika
from aio_pika import connect_robust, Message, ExchangeType
from typing import Callable, Dict, Any, Optional
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class EventBus:
    """RabbitMQ-based event bus for asynchronous communication."""

    def __init__(self, rabbitmq_url: str):
        self.url = rabbitmq_url
        self.connection: Optional[aio_pika.RobustConnection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self.subscribers: Dict[str, Callable] = {}

    async def connect(self):
        """Establish RabbitMQ connection."""
        self.connection = await connect_robust(self.url)
        self.channel = await self.connection.channel()

        # Create topic exchange for event routing
        self.exchange = await self.channel.declare_exchange(
            'network_platform_events',
            ExchangeType.TOPIC,
            durable=True
        )
        logger.info("Event bus connected to RabbitMQ")

    async def publish(self, event_type: str, payload: Dict[str, Any], tenant_id: str):
        """Publish event to the bus."""
        if not self.exchange:
            raise RuntimeError("Event bus not connected")

        routing_key = f"{tenant_id}.{event_type}"
        message_body = json.dumps({
            "event_type": event_type,
            "payload": payload,
            "tenant_id": tenant_id
        })

        await self.exchange.publish(
            Message(body=message_body.encode()),
            routing_key=routing_key
        )
        logger.debug(f"Published event: {routing_key}")

    async def subscribe(
        self,
        event_pattern: str,
        handler: Callable,
        queue_name: Optional[str] = None
    ):
        """Subscribe to events matching pattern (e.g., '*.device.added')."""
        if not self.channel:
            raise RuntimeError("Event bus not connected")

        queue = await self.channel.declare_queue(
            queue_name or f"queue_{event_pattern}",
            durable=True
        )
        await queue.bind(self.exchange, routing_key=event_pattern)

        async def process_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    event_data = json.loads(message.body.decode())
                    await handler(event_data)
                except Exception as e:
                    logger.error(f"Error processing event: {e}")

        await queue.consume(process_message)
        logger.info(f"Subscribed to events: {event_pattern}")

# Global event bus instance
event_bus = EventBus("amqp://guest:guest@rabbitmq:5672/")
```

### Step 6: FastAPI Application with Middleware (2 hours)

**File: platform_core/api/main.py**
```python
"""
FastAPI application with tenant isolation middleware.
"""
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uuid
import logging

from ..database.postgres import DatabaseManager
from ..auth.rbac import RBACManager
from ..plugins.registry import plugin_registry
from ..events.bus import event_bus

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    logger.info("Starting Network Platform...")

    # Connect to databases
    await app.state.db_manager.engine.begin()

    # Connect event bus
    await event_bus.connect()

    # Discover and initialize plugins
    plugin_registry.discover_plugins()
    await plugin_registry.initialize_all()

    # Mount plugin routers
    for plugin_name, plugin in plugin_registry.plugins.items():
        router = plugin.get_router()
        if router:
            app.include_router(router, prefix=f"/api/{plugin_name}", tags=[plugin_name])

    logger.info("Platform started successfully")
    yield

    # Shutdown
    logger.info("Shutting down platform...")
    for plugin in plugin_registry.plugins.values():
        await plugin.shutdown()

def create_app() -> FastAPI:
    """Factory function to create FastAPI app."""
    app = FastAPI(
        title="Network Infrastructure Platform",
        version="1.0.0",
        lifespan=lifespan
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Tenant isolation middleware
    @app.middleware("http")
    async def tenant_isolation_middleware(request: Request, call_next):
        """Extract and validate tenant from JWT token."""
        # Extract tenant_id from JWT or header
        tenant_id = request.headers.get("X-Tenant-ID")

        if not tenant_id and request.url.path.startswith("/api/"):
            raise HTTPException(status_code=401, detail="Tenant ID required")

        if tenant_id:
            try:
                r
