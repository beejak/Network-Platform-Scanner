import os
import tempfile
from typing import Any, Dict

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from fastapi import APIRouter
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from .renderer import DiagramRequest

router = APIRouter()


@router.post("/generate")
async def generate_diagram(request: DiagramRequest):
    """Generate a diagram from a definition."""
    with tempfile.NamedTemporaryFile(delete=True) as tmpf:
        filename_base = tmpf.name

    output_filename = f"{filename_base}.png"

    try:
        with Diagram(
            request.name, show=False, filename=filename_base, outformat="png"
        ):
            nodes: Dict[str, Any] = {}
            # Simplified node lookup
            provider_map = {
                "aws": {
                    "compute": EC2,
                    "database": RDS,
                    "network": ELB,
                }
            }
            for node_data in request.nodes:
                provider = (node_data.provider or "").lower()
                node_type = node_data.type.lower()
                node_cls = provider_map.get(provider, {}).get(node_type, EC2)
                nodes[node_data.name] = node_cls(label=node_data.label)

            for edge_data in request.edges:
                source = nodes.get(edge_data.source)
                target = nodes.get(edge_data.target)
                if source and target:
                    Edge(source, target, label=edge_data.label)
        return FileResponse(
            output_filename,
            media_type="image/png",
            background=BackgroundTask(os.remove, output_filename),
        )
    except Exception as e:
        if os.path.exists(output_filename):
            os.remove(output_filename)
        raise e
