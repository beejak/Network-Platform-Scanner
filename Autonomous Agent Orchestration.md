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
