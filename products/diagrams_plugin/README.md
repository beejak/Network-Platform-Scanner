# Diagrams Plugin

This plugin provides the capability to generate diagrams programmatically using the `diagrams` library. It exposes an API endpoint that accepts a declarative definition of a diagram and returns a PNG image.

## API

### `POST /api/diagrams/generate`

This endpoint generates a diagram from a JSON payload.

**Request Body:**

The request body should be a JSON object with the following structure:

```json
{
  "name": "My Diagram",
  "nodes": [
    {
      "name": "web",
      "label": "Web Server",
      "provider": "aws",
      "type": "compute"
    },
    {
      "name": "db",
      "label": "Database",
      "provider": "aws",
      "type": "database"
    }
  ],
  "edges": [
    {
      "source": "web",
      "target": "db",
      "label": "connects to"
    }
  ]
}
```

- **`name`**: The name of the diagram.
- **`nodes`**: A list of nodes to include in the diagram.
  - **`name`**: A unique identifier for the node.
  - **`label`**: The display label for the node.
  - **`provider`**: The cloud provider (e.g., `aws`).
  - **`type`**: The type of resource (e.g., `compute`, `database`).
- **`edges`**: A list of edges to connect the nodes.
  - **`source`**: The `name` of the source node.
  - **`target`**: The `name` of the target node.
  - **`label`**: An optional label for the edge.

**Response:**

- **`200 OK`**: The response will be a PNG image of the generated diagram.
- **`422 Unprocessable Entity`**: The request body is invalid.

**Example `curl` Request:**

```bash
curl -X POST http://localhost:8000/api/diagrams/generate \\
-H "Content-Type: application/json" \\
-H "X-Tenant-ID: a1b2c3d4-e5f6-7890-1234-567890abcdef" \\
-d '{
  "name": "My Diagram",
  "nodes": [
    {
      "name": "web",
      "label": "Web Server",
      "provider": "aws",
      "type": "compute"
    },
    {
      "name": "db",
      "label": "Database",
      "provider": "aws",
      "type": "database"
    }
  ],
  "edges": [
    {
      "source": "web",
      "target": "db",
      "label": "connects to"
    }
  ]
}' \\
--output my-diagram.png
```
