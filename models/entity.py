"""
Entity Data Models for KRONOS
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class Relationship(BaseModel):
    """Represents a directional or associative relationship between two entities."""
    id: Optional[str] = None
    source_id: str
    target_id: str
    target_name: Optional[str] = "Unknown Target"
    target_type: Optional[str] = "Entity"
    relation_type: str = "ASSOCIATED_WITH"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_ref: Optional[str] = None
    first_observed: Optional[str] = None
    last_observed: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Entity(BaseModel):
    """
    Core Entity model representing people, phones, vehicles, locations,
    organizations, and events identified within the intelligence corpus.
    """
    id: str
    name: str
    type: str  # Person, Phone, Vehicle, Location, Organization, Event
    risk_level: str = "LOW"  # HIGH, MEDIUM, LOW
    risk_score: Optional[float] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    status: str = "Active"
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    associated_cases: List[str] = Field(default_factory=list)
    
    # Dynamic key-value attributes (e.g., IMEI, License Plate, Address, DOB)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    
    # Connected Relationships summary
    relationships: List[Relationship] = Field(default_factory=list)
    
    # Temporal metadata
    first_observed: Optional[str] = None
    last_observed: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class EntitySearchResult(BaseModel):
    """Search projection for entity list and table views."""
    id: str
    name: str
    type: str
    risk_level: str = "LOW"
    confidence: float = 1.0
    relationship_count: int = 0
    associated_cases: List[str] = Field(default_factory=list)
    last_observed: Optional[str] = None
