# Enterprise Platform Foundation

This repository contains the foundational infrastructure for a multi-tenant, modular enterprise platform. It is designed to serve as the core for up to 15 distinct products, providing common services like authentication, data access, and asynchronous communication.

## Core Architecture

The platform is built on a modern, asynchronous Python stack and features:

*   **Modular Plugin System:** Each product is a self-contained plugin located in the `products/` directory. The platform discovers and loads these plugins at startup.
*   **Multi-Tenant Database:** The PostgreSQL database is designed with a multi-tenant schema in mind, using row-level security (not yet fully implemented) to isolate tenant data.
*   **FastAPI Gateway:** A central FastAPI application serves as the API gateway, routing requests to the appropriate plugins.
*   **Asynchronous Communication:** RabbitMQ is integrated for event-driven communication between services (not yet fully implemented).
*   **Multiple Data Stores:** The architecture supports PostgreSQL for relational data, Neo4j for graph data, and ClickHouse for time-series data.

## Getting Started

### Prerequisites

*   Python 3.10+
*   Docker and Docker Compose
*   `pre-commit` (for development)

### 1. Set Up the Environment

First, clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

Next, create and activate a Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

The project uses `pip` and `setuptools` for dependency management. Install the project in editable mode with all development dependencies:

```bash
pip install -e .[dev]
```

### 3. Start Services

The required backend services (PostgreSQL, RabbitMQ, etc.) are managed via Docker Compose.

```bash
docker-compose up -d
```

### 4. Run Database Migrations

The project uses Alembic to manage database schema migrations. To apply all migrations, run:

```bash
alembic upgrade head
```

### 5. Run the Application

To start the FastAPI application, run:

```bash
uvicorn platform_core.api.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

## Development

### Running Tests

The test suite is built with `pytest`. To run all tests, ensure your Docker services are running and then execute:

```bash
python -m pytest
```

### Code Quality

This project enforces strict code quality standards using `black`, `pylint`, `mypy`, and `isort`. These are managed via `pre-commit` hooks.

To set up the hooks, run:
```bash
pre-commit install
```

To run all checks manually:
```bash
pre-commit run --all-files
```
