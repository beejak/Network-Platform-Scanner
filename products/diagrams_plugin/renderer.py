from typing import List, Optional

from pydantic import BaseModel


class Node(BaseModel):
    name: str
    label: str
    provider: Optional[str] = None
    type: str


class Edge(BaseModel):
    source: str
    target: str
    label: Optional[str] = None


class DiagramRequest(BaseModel):
    name: str
    nodes: List[Node]
    edges: List[Edge]
