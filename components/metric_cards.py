"""
KRONOS Metric Cards Component
Renders 5 operational KPI metric cards for the command center dashboard.
"""

from typing import Optional
import streamlit as st
from models.analytics import DashboardMetrics


def render_metric_cards(metrics: Optional[DashboardMetrics], network_nodes: Optional[int] = None) -> None:
    """Renders 5 KPI metric cards: Total Entities, Active Cases, Flagged Suspects, Patterns Detected, Network Nodes."""
    col1, col2, col3, col4, col5 = st.columns(5)

    def _card(col, label: str, value: str, subtext: str, accent: str):
        with col:
            st.markdown(
                f"""
                <div class="metric-card" style="border-top: 2px solid {accent};">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-subtext">{subtext}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    if metrics is None:
        _card(col1, "Total Entities", "--", "Entities in system", "#06B6D4")
        _card(col2, "Active Cases", "--", "Open investigations", "#F59E0B")
        _card(col3, "Flagged Suspects", "--", "High-risk entities", "#EF4444")
        _card(col4, "Patterns Detected", "--", "AI detections", "#F97316")
        _card(col5, "Network Nodes", "--", "Graph nodes", "#3B82F6")
        return

    nodes_val = f"{network_nodes:,}" if network_nodes is not None else f"{metrics.network_nodes:,}" if metrics.network_nodes else "--"

    _card(col1, "Total Entities", f"{metrics.total_entities:,}", "Entities in system", "#06B6D4")
    _card(col2, "Active Cases", f"{metrics.active_investigations:,}", "Open investigations", "#F59E0B")
    _card(col3, "Flagged Suspects", f"{metrics.high_risk_entities:,}", "High-risk entities", "#EF4444")
    _card(col4, "Patterns Detected", f"{metrics.suspicious_patterns_detected:,}", "AI detections", "#F97316")
    _card(col5, "Network Nodes", nodes_val, "Graph nodes", "#3B82F6")
