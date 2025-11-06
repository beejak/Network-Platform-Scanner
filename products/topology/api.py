"""Topology API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any
import logging
import uuid

from platform_core.database.neo4j_conn import Neo4jManager

logger = logging.getLogger(__name__)

def create_topology_router(neo4j_manager: Neo4jManager) -> APIRouter:
    router = APIRouter()

    async def get_neo4j() -> Neo4jManager:
        return neo4j_manager

    @router.get("/nodes", response_model=List[Dict[str, Any]])
    async def get_nodes(
        node_type: str = Query(None, description="Filter by node type"),
        neo4j: Neo4jManager = Depends(get_neo4j)
    ) -> List[Dict[str, Any]]:
        """Get all topology nodes."""
        logger.info(f"GET /nodes called with node_type={node_type}")
        if node_type:
            query = f"MATCH (n:{node_type}) RETURN n LIMIT 25"
        else:
            query = "MATCH (n) RETURN n LIMIT 25"

        records, _, _ = await neo4j.execute_query(query)
        return [record["n"] for record in records]

    @router.get("/nodes/{node_id}", response_model=Dict[str, Any])
    async def get_node(
        node_id: str,
        neo4j: Neo4jManager = Depends(get_neo4j)
    ) -> Dict[str, Any]:
        """Get specific node details."""
        logger.info(f"GET /nodes/{node_id} called")
        query = "MATCH (n {id: $node_id}) RETURN n"
        records, _, _ = await neo4j.execute_query(query, params={"node_id": node_id})
        if not records:
            raise HTTPException(status_code=404, detail="Node not found")
        return records[0]["n"]

    @router.post("/nodes", response_model=Dict[str, Any], status_code=201)
    async def create_node(
        node_data: Dict[str, Any],
        neo4j: Neo4jManager = Depends(get_neo4j)
    ) -> Dict[str, Any]:
        """Create a new topology node."""
        logger.info(f"POST /nodes called with data: {node_data}")

        node_id = str(uuid.uuid4())
        props = node_data.copy()
        props['id'] = node_id

        query = "CREATE (n:Node $props) RETURN n"
        records, _, _ = await neo4j.execute_query(query, params={"props": props})

        if not records:
            raise HTTPException(status_code=500, detail="Failed to create node")
        return records[0]["n"]

    # ... (other endpoints) ...

    return router
