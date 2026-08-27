"""
KRONOS Test Suite
Tests for data models, API services, formatting, and session state using standard unittest.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import unittest
from models.entity import Entity, Relationship, EntitySearchResult
from models.investigation import Investigation, InvestigationSummary
from models.pattern import SuspiciousPattern
from models.analytics import DashboardMetrics
from models.network import NetworkSummary, CentralEntity, CommunityCluster
from utils.formatting import (
    render_risk_badge,
    render_severity_badge,
    render_confidence_badge,
    render_type_badge,
    format_timestamp,
)
from services.api_client import APIClient, BackendUnavailableError, NotFoundError


class TestKronosDashboard(unittest.TestCase):
    def test_entity_model(self):
        rel = Relationship(source_id="PER-01", target_id="PER-02", relation_type="CO_CONSPIRATOR", confidence=0.92)
        ent = Entity(
            id="PER-01",
            name="Marcus Vance",
            type="Person",
            risk_level="HIGH",
            confidence=0.95,
            aliases=["The Ghost", "V-Man"],
            relationships=[rel],
            attributes={"dob": "1984-06-12", "citizenship": "US"}
        )
        self.assertEqual(ent.id, "PER-01")
        self.assertEqual(ent.risk_level, "HIGH")
        self.assertEqual(len(ent.relationships), 1)
        self.assertEqual(ent.relationships[0].relation_type, "CO_CONSPIRATOR")

    def test_investigation_model(self):
        inv = Investigation(
            case_id="CASE-2026-09",
            title="Operation Nightfall",
            risk_level="HIGH",
            status="Active",
            entity_count=12,
            relationship_count=28,
            pattern_count=4,
            entity_ids=["PER-01", "PH-8821"]
        )
        self.assertEqual(inv.case_id, "CASE-2026-09")
        self.assertEqual(inv.entity_count, 12)

    def test_pattern_model(self):
        pat = SuspiciousPattern(
            pattern_id="PAT-901",
            pattern_type="Burner Phone Rotation",
            severity="CRITICAL",
            confidence=0.88,
            description="Multiple IMEI switches in 24 hours."
        )
        self.assertEqual(pat.severity, "CRITICAL")
        self.assertEqual(pat.confidence, 0.88)

    def test_formatting_badges(self):
        self.assertIn("badge-critical", render_risk_badge("CRITICAL"))
        self.assertIn("badge-high", render_risk_badge("HIGH"))
        self.assertIn("badge-medium", render_risk_badge("MEDIUM"))
        self.assertIn("badge-low", render_risk_badge("LOW"))
        self.assertIn("badge-critical", render_severity_badge("CRITICAL"))
        self.assertIn("CONF: 95%", render_confidence_badge(0.95))
        self.assertIn("PERSON", render_type_badge("Person"))

    def test_api_client_error_handling(self):
        # Client pointing to an invalid local port should raise BackendUnavailableError
        client = APIClient(base_url="http://localhost:59999", timeout=1.0)
        is_online, latency, msg = client.check_health()
        self.assertFalse(is_online)
        self.assertTrue("CONNECTION REFUSED" in msg or "ERROR" in msg or "TIMEOUT" in msg)

        with self.assertRaises(BackendUnavailableError):
            client.get("/entities")


if __name__ == "__main__":
    unittest.main()
