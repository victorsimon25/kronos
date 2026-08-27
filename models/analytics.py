"""
Analytics and Metric Data Models for KRONOS
"""

from typing import Dict, Optional, Any
from pydantic import BaseModel, Field


class DashboardMetrics(BaseModel):
    """
    High-level operational intelligence metrics provided by the backend.
    """
    total_entities: int = 0
    total_relationships: int = 0
    active_investigations: int = 0
    high_risk_entities: int = 0
    suspicious_patterns_detected: int = 0
    avg_confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    network_nodes: int = 0

    entity_type_distribution: Dict[str, int] = Field(default_factory=dict)
    risk_distribution: Dict[str, int] = Field(default_factory=dict)

    last_sync_time: Optional[str] = None
    system_status: str = "ONLINE"
    metadata: Dict[str, Any] = Field(default_factory=dict)
