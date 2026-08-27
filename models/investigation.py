"""
Investigation / Case Data Models for KRONOS
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Investigation(BaseModel):
    """Represents an active or historical criminal intelligence investigation / case."""
    case_id: str
    title: str
    description: Optional[str] = "No description provided."
    risk_level: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    status: str = "Active"      # Active, Under Review, Escalated, Closed
    lead_analyst: Optional[str] = "Unassigned"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    # Counts provided by backend/Graph/AI teams
    entity_count: int = 0
    relationship_count: int = 0
    pattern_count: int = 0
    
    # Linked IDs
    entity_ids: List[str] = Field(default_factory=list)
    pattern_ids: List[str] = Field(default_factory=list)
    
    # Key intelligence tags and summary findings
    tags: List[str] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InvestigationSummary(BaseModel):
    """Lightweight summary projection for cards and list views."""
    case_id: str
    title: str
    risk_level: str = "MEDIUM"
    status: str = "Active"
    entity_count: int = 0
    pattern_count: int = 0
    last_updated: Optional[str] = None
