"""
Entity API Service for KRONOS
Handles entity search, detailed dossier retrieval, and relationship querying.
"""

import logging
from typing import List, Optional, Dict, Any
from models.entity import Entity, Relationship, EntitySearchResult
from services.api_client import api_client, APIError, NotFoundError, BackendUnavailableError

logger = logging.getLogger("kronos.entity_service")


class EntityService:
    """Service consuming Entity and Relationship APIs."""

    def __init__(self, client=api_client):
        self.client = client

    def search_entities(
        self,
        query: Optional[str] = None,
        entity_type: Optional[str] = None,
        risk_level: Optional[str] = None,
        min_confidence: Optional[float] = None,
        case_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[EntitySearchResult]:
        """
        Query backend for entities matching search and filter criteria.
        Passes all filter parameters to backend API.
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset
        }
        if query:
            params["q"] = query
        if entity_type and entity_type != "All":
            params["type"] = entity_type
        if risk_level and risk_level != "All":
            params["risk_level"] = risk_level
        if min_confidence is not None and min_confidence > 0.0:
            params["min_confidence"] = min_confidence
        if case_id and case_id != "All":
            params["case_id"] = case_id

        endpoints = ["/entities", "/api/v1/entities", "/entities/search"]
        
        last_error = None
        for endpoint in endpoints:
            try:
                data = self.client.get(endpoint, params=params)
                
                # Handle direct list response or wrapper dict {"items": [...]} or {"entities": [...]}
                items = []
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    items = data.get("items") or data.get("entities") or data.get("results") or []
                    
                results = []
                for item in items:
                    results.append(EntitySearchResult(
                        id=str(item.get("id", item.get("entity_id", "UNKNOWN"))),
                        name=str(item.get("name", item.get("label", item.get("id", "Unknown")))),
                        type=str(item.get("type", item.get("entity_type", "Person"))),
                        risk_level=str(item.get("risk_level", item.get("risk", "LOW"))).upper(),
                        confidence=float(item.get("confidence", item.get("confidence_score", 1.0))),
                        relationship_count=int(item.get("relationship_count", item.get("degrees", len(item.get("relationships", []))))),
                        associated_cases=item.get("associated_cases", item.get("cases", [])),
                        last_observed=item.get("last_observed", item.get("updated_at"))
                    ))
                return results
            except BackendUnavailableError:
                raise
            except Exception as e:
                last_error = e
                continue

        if last_error:
            raise last_error
        return []

    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """
        Fetch full entity dossier by unique ID.
        """
        endpoints = [f"/entities/{entity_id}", f"/api/v1/entities/{entity_id}"]
        
        for endpoint in endpoints:
            try:
                data = self.client.get(endpoint)
                if isinstance(data, dict):
                    # Parse relationships if embedded
                    raw_rels = data.get("relationships", [])
                    rels = []
                    for r in raw_rels:
                        rels.append(Relationship(
                            id=r.get("id"),
                            source_id=str(r.get("source_id", entity_id)),
                            target_id=str(r.get("target_id", r.get("target", "UNKNOWN"))),
                            target_name=r.get("target_name", r.get("target_label", "Unknown Target")),
                            target_type=r.get("target_type", "Entity"),
                            relation_type=r.get("relation_type", r.get("type", "ASSOCIATED_WITH")),
                            confidence=float(r.get("confidence", 1.0)),
                            source_ref=r.get("source_ref", r.get("evidence_ref")),
                            first_observed=r.get("first_observed"),
                            last_observed=r.get("last_observed"),
                            metadata=r.get("metadata", {})
                        ))
                    
                    return Entity(
                        id=str(data.get("id", data.get("entity_id", entity_id))),
                        name=str(data.get("name", data.get("label", entity_id))),
                        type=str(data.get("type", data.get("entity_type", "Person"))),
                        risk_level=str(data.get("risk_level", data.get("risk", "LOW"))).upper(),
                        risk_score=data.get("risk_score"),
                        confidence=float(data.get("confidence", 1.0)),
                        status=data.get("status", "Active"),
                        description=data.get("description"),
                        aliases=data.get("aliases", []),
                        associated_cases=data.get("associated_cases", data.get("cases", [])),
                        attributes=data.get("attributes", data.get("properties", {})),
                        relationships=rels,
                        first_observed=data.get("first_observed"),
                        last_observed=data.get("last_observed"),
                        created_at=data.get("created_at"),
                        updated_at=data.get("updated_at")
                    )
            except (NotFoundError, BackendUnavailableError):
                raise
            except Exception as e:
                logger.warning(f"Failed fetching entity from {endpoint}: {e}")
                continue
        return None

    def get_entity_relationships(self, entity_id: str) -> List[Relationship]:
        """
        Fetch relationship graph neighbors for an entity if served on a dedicated sub-resource.
        """
        endpoints = [
            f"/entities/{entity_id}/relationships",
            f"/api/v1/entities/{entity_id}/relationships"
        ]
        for endpoint in endpoints:
            try:
                data = self.client.get(endpoint)
                items = data if isinstance(data, list) else data.get("relationships", [])
                rels = []
                for r in items:
                    rels.append(Relationship(
                        id=r.get("id"),
                        source_id=str(r.get("source_id", entity_id)),
                        target_id=str(r.get("target_id", r.get("target", "UNKNOWN"))),
                        target_name=r.get("target_name", r.get("target_label", "Unknown Target")),
                        target_type=r.get("target_type", "Entity"),
                        relation_type=r.get("relation_type", r.get("type", "ASSOCIATED_WITH")),
                        confidence=float(r.get("confidence", 1.0)),
                        source_ref=r.get("source_ref"),
                        first_observed=r.get("first_observed"),
                        last_observed=r.get("last_observed")
                    ))
                return rels
            except Exception:
                continue
        return []


entity_service = EntityService()
