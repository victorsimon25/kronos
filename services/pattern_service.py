"""
Suspicious Pattern API Service for KRONOS
Consumes anomaly, behavioral similarity, and suspicious network pattern detections from AI/NLP team.
"""

import logging
from typing import List, Optional, Dict, Any
from models.pattern import SuspiciousPattern
from services.api_client import api_client, APIError, NotFoundError, BackendUnavailableError

logger = logging.getLogger("kronos.pattern_service")


class PatternService:
    """Service consuming AI/NLP Suspicious Pattern APIs."""

    def __init__(self, client=api_client):
        self.client = client

    def list_suspicious_patterns(
        self,
        severity: Optional[str] = None,
        min_confidence: Optional[float] = None,
        case_id: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[SuspiciousPattern]:
        """
        Fetch suspicious patterns detected across the intelligence corpus.
        Filters are transmitted to the backend.
        """
        params: Dict[str, Any] = {}
        if severity and severity != "All":
            params["severity"] = severity
        if min_confidence is not None and min_confidence > 0.0:
            params["min_confidence"] = min_confidence
        if case_id and case_id != "All":
            params["case_id"] = case_id
        if query:
            params["q"] = query

        endpoints = ["/patterns", "/api/v1/patterns", "/suspicious-patterns"]
        
        last_error = None
        for endpoint in endpoints:
            try:
                data = self.client.get(endpoint, params=params)
                items = []
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    items = data.get("items") or data.get("patterns") or data.get("results") or []
                    
                patterns = []
                for item in items:
                    patterns.append(SuspiciousPattern(
                        pattern_id=str(item.get("pattern_id", item.get("id", "PAT-UNKNOWN"))),
                        pattern_type=str(item.get("pattern_type", item.get("type", "Suspicious Activity"))),
                        severity=str(item.get("severity", "HIGH")).upper(),
                        confidence=float(item.get("confidence", 0.85)),
                        detection_date=item.get("detection_date", item.get("created_at")),
                        description=str(item.get("description", "No description provided.")),
                        related_case_id=item.get("related_case_id", item.get("case_id")),
                        status=str(item.get("status", "Unreviewed")),
                        entities_involved=item.get("entities_involved", item.get("entities", [])),
                        indicators=item.get("indicators", []),
                        metadata=item.get("metadata", {})
                    ))
                return patterns
            except BackendUnavailableError:
                raise
            except Exception as e:
                last_error = e
                continue

        if last_error:
            raise last_error
        return []

    def get_pattern_by_id(self, pattern_id: str) -> Optional[SuspiciousPattern]:
        """
        Fetch single suspicious pattern record by ID.
        """
        endpoints = [f"/patterns/{pattern_id}", f"/api/v1/patterns/{pattern_id}"]
        for endpoint in endpoints:
            try:
                data = self.client.get(endpoint)
                if isinstance(data, dict):
                    return SuspiciousPattern(
                        pattern_id=str(data.get("pattern_id", data.get("id", pattern_id))),
                        pattern_type=str(data.get("pattern_type", data.get("type", "Suspicious Activity"))),
                        severity=str(data.get("severity", "HIGH")).upper(),
                        confidence=float(data.get("confidence", 0.85)),
                        detection_date=data.get("detection_date", data.get("created_at")),
                        description=str(data.get("description", "No description provided.")),
                        related_case_id=data.get("related_case_id", data.get("case_id")),
                        status=str(data.get("status", "Unreviewed")),
                        entities_involved=data.get("entities_involved", data.get("entities", [])),
                        indicators=data.get("indicators", []),
                        metadata=data.get("metadata", {})
                    )
            except (NotFoundError, BackendUnavailableError):
                raise
            except Exception as e:
                logger.warning(f"Error fetching pattern {pattern_id}: {e}")
                continue
        return None


pattern_service = PatternService()
