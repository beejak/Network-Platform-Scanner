"""
Diagram rendering models.
"""
from typing import List
from pydantic import BaseModel, Field

class Node(BaseModel):
    """
    A node in a diagram.
    """
    name: str = Field(..., description="The name of the node.")
    label: str = Field(..., description="The label of the node.")
    type: str = Field(..., description="The type of the node.")
    provider: str = Field(None, description="The provider of the node.")

class Edge(BaseModel):
    """
    An edge in a diagram.
    """
    source: str = Field(..., description="The source node of the edge.")
    target: str = Field(..., description="The target node of the edge.")
    label: str = Field(None, description="The label of the edge.")

class DiagramRequest(BaseModel):
    """
    A request to generate a diagram.
    """
    name: str = Field(..., description="The name of the diagram.")
    nodes: List[Node] = Field(..., description="The nodes in the diagram.")
    edges: List[Edge] = Field(..., description="The edges in the diagram.")
