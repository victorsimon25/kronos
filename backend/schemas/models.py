from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Entity(BaseModel):
    id: str
    type: str
    name: Optional[str] = None
    value: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseModel):
    source_id: str
    target_id: str
    type: str
    confidence: Optional[float] = None
    evidence_id: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class Event(BaseModel):
    id: str
    type: str
    timestamp: Optional[str] = None
    location: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    evidence_id: Optional[str] = None


class Evidence(BaseModel):
    id: str
    source_type: str
    source_name: str
    excerpt: str
    timestamp: Optional[str] = None
    confidence: Optional[float] = None


class ExtractionResult(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    events: List[Event] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)