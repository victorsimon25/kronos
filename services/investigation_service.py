"""
Investigation API Service for KRONOS
Consumes case intelligence records and case-specific entity rosters.
"""

import logging
from typing import List, Optional, Dict, Any
from models.investigation import Investigation, InvestigationSummary
from services.api_client import api_client, APIError, NotFoundError, BackendUnavailableError

logger = logging.getLogger("kronos.investigation_service")


class InvestigationService:
    """Service consuming Investigation/Case APIs."""

    def __init__(self, client=api_client):
        self.client = client

    def list_investigations(
        self,
        status: Optional[str] = None,
        risk_level: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[InvestigationSummary]:
        """
        Fetch list of criminal investigations with optional status/risk filtering.
        """
        params: Dict[str, Any] = {}
        if status and status != "All":
            params["status"] = status
        if risk_level and risk_level != "All":
            params["risk_level"] = risk_level
        if query:
            params["q"] = query

        endpoints = ["/investigations", "/api/v1/investigations", "/cases"]
        
        last_error = None
        for endpoint in endpoints:
            try:
                data = self.client.get(endpoint, params=params)
                items = []
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    items = data.get("items") or data.get("cases") or data.get("investigations") or []
                    
                summaries = []
                for item in items:
                    summaries.append(InvestigationSummary(
                        case_id=str(item.get("case_id", item.get("id", "CASE-UNKNOWN"))),
                        title=str(item.get("title", item.get("name", "Untitled Case"))),
                        risk_level=str(item.get("risk_level", item.get("risk", "MEDIUM"))).upper(),
                        status=str(item.get("status", "Active")),
                        entity_count=int(item.get("entity_count", len(item.get("entities", [])))),
                        pattern_count=int(item.get("pattern_count", len(item.get("patterns", [])))),
                        last_updated=item.get("updated_at", item.get("last_updated"))
                    ))
                return summaries
            except BackendUnavailableError:
                raise
            except Exception as e:
                last_error = e
                continue

        if last_error:
            raise last_error
        return []

    def get_investigation_by_id(self, case_id: str) -> Optional[Investigation]:
        """
        Fetch full dossier and linked entities for an investigation.
        """
        endpoints = [
            f"/investigations/{case_id}",
            f"/api/v1/investigations/{case_id}",
            f"/cases/{case_id}"
        ]
        
        for endpoint in endpoints:
            try:
                data = self.client.get(endpoint)
                if isinstance(data, dict):
                    return Investigation(
                        case_id=str(data.get("case_id", data.get("id", case_id))),
                        title=str(data.get("title", data.get("name", f"Case {case_id}"))),
                        description=data.get("description", "No case overview provided."),
                        risk_level=str(data.get("risk_level", data.get("risk", "MEDIUM"))).upper(),
                        status=str(data.get("status", "Active")),
                        lead_analyst=data.get("lead_analyst", "Unassigned"),
                        created_at=data.get("created_at"),
                        updated_at=data.get("updated_at", data.get("last_updated")),
                        entity_count=int(data.get("entity_count", len(data.get("entities", [])))),
                        relationship_count=int(data.get("relationship_count", 0)),
                        pattern_count=int(data.get("pattern_count", len(data.get("patterns", [])))),
                        entity_ids=data.get("entity_ids", data.get("entities", [])),
                        pattern_ids=data.get("pattern_ids", data.get("patterns", [])),
                        tags=data.get("tags", []),
                        key_findings=data.get("key_findings", []),
                        metadata=data.get("metadata", {})
                    )
            except (NotFoundError, BackendUnavailableError):
                raise
            except Exception as e:
                logger.warning(f"Error fetching investigation from {endpoint}: {e}")
                continue
        return None


investigation_service = InvestigationService()
