"""Topology API endpoints using a closure to manage dependencies."""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
import logging
import uuid

from platform_core.database.neo4j_conn import Neo4jManager

logger = logging.getLogger(__name__)

def create_topology_router(neo4j_manager: Neo4jManager) -> APIRouter:
    """
    Factory function to create the topology router.

    This function uses a closure to provide the Neo4jManager to the routes.
    """
    router = APIRouter()

    @router.get("/nodes", response_model=List[Dict[str, Any]])
    async def get_nodes(
        node_type: str = Query(None, description="Filter by node type")
    ) -> List[Dict[str, Any]]:
        """Get all topology nodes."""
        logger.info(f"GET /nodes called with node_type={node_type}")
        if node_type:
            query = f"MATCH (n:{node_type}) RETURN n LIMIT 25"
        else:
            query = "MATCH (n) RETURN n LIMIT 25"

        records, _, _ = await neo4j_manager.execute_query(query)
        return [record["n"] for record in records]

    @router.get("/nodes/{node_id}", response_model=Dict[str, Any])
    async def get_node(node_id: str) -> Dict[str, Any]:
        """Get specific node details."""
        logger.info(f"GET /nodes/{node_id} called")
        query = "MATCH (n {id: $node_id}) RETURN n"
        records, _, _ = await neo4j_manager.execute_query(query, params={"node_id": node_id})
        if not records:
            raise HTTPException(status_code=404, detail="Node not found")
        return records[0]["n"]

    @router.post("/nodes", response_model=Dict[str, Any], status_code=201)
    async def create_node(node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new topology node."""
        logger.info(f"POST /nodes called with data: {node_data}")

        node_id = str(uuid.uuid4())
        props = node_data.copy()
        props['id'] = node_id

        query = "CREATE (n:Node $props) RETURN n"
        records, _, _ = await neo4j_manager.execute_query(query, params={"props": props})

        if not records:
            raise HTTPException(status_code=500, detail="Failed to create node")
        return records[0]["n"]

    @router.get("/edges", response_model=List[Dict[str, Any]])
    async def get_edges() -> List[Dict[str, Any]]:
        """Get all topology edges (connections)."""
        logger.info("GET /edges called")
        query = "MATCH ()-[r]-() RETURN r LIMIT 25"
        records, _, _ = await neo4j_manager.execute_query(query)

        return [
            {
                "id": r.id,
                "type": r.type,
                "start_node_id": r.start_node.id,
                "end_node_id": r.end_node.id,
            }
            for r in (record["r"] for record in records)
        ]

    @router.get("/graph", response_model=Dict[str, Any])
    async def get_full_graph() -> Dict[str, Any]:
        """Get complete topology graph."""
        logger.info("GET /graph called")
        nodes_query = "MATCH (n) RETURN n LIMIT 100"
        edges_query = "MATCH (n)-[r]-(m) RETURN n, r, m LIMIT 100"

        nodes_records, _, _ = await neo4j_manager.execute_query(nodes_query)
        edges_records, _, _ = await neo4j_manager.execute_query(edges_query)

        nodes = [record["n"] for record in nodes_records]
        edges = [
            {
                "source": record["n"]["id"],
                "target": record["m"]["id"],
                "type": record["r"].type,
            }
            for record in edges_records
        ]

        return {"nodes": nodes, "edges": edges}

    return router
