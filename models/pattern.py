"""
Suspicious Pattern Data Models for KRONOS
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SuspiciousPattern(BaseModel):
    """
    Represents an anomalous or suspicious network pattern detected by AI/NLP & Graph teams
    (e.g., Burner Phone Rotation, Rapid Entity Co-occurrence, Funnel Financing, Shell Org Linkage).
    """
    pattern_id: str
    pattern_type: str
    severity: str = "HIGH"  # HIGH, MEDIUM, LOW, CRITICAL
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    detection_date: Optional[str] = None
    description: str = "No pattern description available."
    related_case_id: Optional[str] = None
    status: str = "Unreviewed"  # Unreviewed, Confirmed, False Positive, Escalated
    
    # Involved entity identifiers and metadata provided by backend
    entities_involved: List[Dict[str, Any]] = Field(default_factory=list)
    indicators: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
