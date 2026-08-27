"""
Analytics API Service for KRONOS
Consumes system summary metrics from Core Backend.
"""

import logging
from typing import Optional, Dict, Any, List
from models.analytics import DashboardMetrics
from services.api_client import api_client, APIError, BackendUnavailableError

logger = logging.getLogger("kronos.analytics_service")


class AnalyticsService:
    """Consumes operational intelligence metrics and KPI endpoints."""

    def __init__(self, client=api_client):
        self.client = client

    def get_dashboard_metrics(self) -> DashboardMetrics:
        """
        Fetch summary KPI metrics for the main investigator dashboard.
        Tries standard endpoints: /analytics/summary, /api/v1/analytics/summary, /analytics
        """
        endpoints = [
            "/analytics/summary",
            "/api/v1/analytics/summary",
            "/analytics"
        ]
        
        last_error = None
        for endpoint in endpoints:
            try:
                data = self.client.get(endpoint)
                if isinstance(data, dict):
                    # Adapt backend payload to DashboardMetrics
                    return DashboardMetrics(
                        total_entities=data.get("total_entities", data.get("entities_count", 0)),
                        total_relationships=data.get("total_relationships", data.get("relationships_count", 0)),
                        active_investigations=data.get("active_investigations", data.get("cases_count", 0)),
                        high_risk_entities=data.get("high_risk_entities", 0),
                        suspicious_patterns_detected=data.get("suspicious_patterns_detected", data.get("patterns_count", 0)),
                        avg_confidence_score=float(data.get("avg_confidence_score", data.get("average_confidence", 0.0))),
                        entity_type_distribution=data.get("entity_type_distribution", {}),
                        risk_distribution=data.get("risk_distribution", {}),
                        last_sync_time=data.get("last_sync_time", data.get("timestamp")),
                        system_status=data.get("status", "ONLINE")
                    )
            except BackendUnavailableError:
                # Re-raise backend unavailable error immediately
                raise
            except Exception as e:
                last_error = e
                continue
                
        if last_error:
            raise last_error
        raise APIError("No analytics endpoint responded successfully.")


    def get_activity_feed(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch recent system activity events for the dashboard feed."""
        endpoints = [
            "/analytics/activity",
            "/api/v1/events/recent",
            "/events",
        ]

        for endpoint in endpoints:
            try:
                data = self.client.get(endpoint, params={"limit": limit})
                if isinstance(data, list):
                    return data[:limit]
                if isinstance(data, dict) and "events" in data:
                    return data["events"][:limit]
            except Exception:
                continue

        return []


analytics_service = AnalyticsService()
