"""
Network Analysis Data Models for KRONOS
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class CentralEntity(BaseModel):
    """Represents a high-centrality node computed by Graph/Data Analysis team."""
    entity_id: str
    name: str
    type: str = "Person"
    degree: int = 0
    betweenness_centrality: Optional[float] = None
    degree_centrality: Optional[float] = None
    pagerank: Optional[float] = None
    community_id: Optional[int] = None
    risk_level: str = "HIGH"


class CommunityCluster(BaseModel):
    """Represents a detected criminal subgroup/cluster in the network."""
    community_id: int
    name: str = "Cluster"
    member_count: int = 0
    dominant_type: str = "Person"
    risk_level: str = "MEDIUM"
    key_members: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class NetworkSummary(BaseModel):
    """
    Graph analytical metrics provided by Graph/Data Analysis team via API.
    The frontend NEVER calculates these metrics directly.
    """
    total_nodes: int = 0
    total_edges: int = 0
    network_density: Optional[float] = None
    communities_count: int = 0
    most_connected_entity: Optional[str] = None
    high_risk_clusters_count: int = 0
    
    # Top central entities and clusters
    central_entities: List[CentralEntity] = Field(default_factory=list)
    communities: List[CommunityCluster] = Field(default_factory=list)
    
    # Breakdown statistics
    relationship_types: Dict[str, int] = Field(default_factory=dict)
    temporal_activity: Dict[str, int] = Field(default_factory=dict)
    
    metadata: Dict[str, Any] = Field(default_factory=dict)
