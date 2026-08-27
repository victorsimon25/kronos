"""
KRONOS Dashboard — Command Center
Hero page: metrics, flagged individuals, activity feed, network canvas.
"""

import streamlit as st
from components.metric_cards import render_metric_cards
from components.integration_containers import render_network_graph_container
from components.empty_states import render_backend_unavailable, render_empty_state
from services.analytics_service import analytics_service
from services.entity_service import entity_service
from services.network_service import network_service
from services.api_client import BackendUnavailableError
from utils.formatting import render_risk_badge, render_type_badge
from utils.state import select_entity


def render_dashboard_page() -> None:
    """Renders the command center dashboard."""
    backend_offline = False
    metrics = None
    flagged_entities = []
    activity_events = []
    network_nodes = None

    # Independent data fetches — partial failure is fine
    try:
        metrics = analytics_service.get_dashboard_metrics()
    except BackendUnavailableError:
        backend_offline = True
    except Exception:
        metrics = None

    if not backend_offline:
        try:
            flagged_entities = entity_service.search_entities(risk_level="HIGH", limit=5)
        except Exception:
            flagged_entities = []

        try:
            activity_events = analytics_service.get_activity_feed(limit=10)
        except Exception:
            activity_events = []

        try:
            network_summary = network_service.get_network_summary()
            if network_summary:
                network_nodes = network_summary.total_nodes
        except Exception:
            network_nodes = None

    if backend_offline:
        render_backend_unavailable("FastAPI backend is offline. Real-time intelligence feeds unavailable.")

    # Metric Cards
    render_metric_cards(metrics, network_nodes=network_nodes)

    st.markdown('<div style="height: 1.25rem;"></div>', unsafe_allow_html=True)

    # Two-Column: Flagged Individuals + Activity Feed
    col_flagged, col_activity = st.columns([1.6, 1.0])

    with col_flagged:
        st.markdown(
            """
            <div class="intel-card-header">
                <span>Flagged Individuals</span>
                <span style="font-size: 0.72rem; color: #EF4444; font-weight: normal;">High-Risk Entities</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        if flagged_entities:
            for i, entity in enumerate(flagged_entities[:5]):
                name = getattr(entity, "name", None) or getattr(entity, "identifier", f"Entity-{i}")
                risk = getattr(entity, "risk_level", "HIGH")
                etype = getattr(entity, "entity_type", "Unknown")
                reason = getattr(entity, "description", None) or "Flagged by risk assessment"
                eid = getattr(entity, "id", None) or getattr(entity, "entity_id", "")

                risk_badge = render_risk_badge(risk)
                type_badge = render_type_badge(etype)

                st.markdown(
                    f"""
                    <div class="flagged-item">
                        <div>{risk_badge} {type_badge}</div>
                        <div class="flagged-item__info">
                            <div class="flagged-item__name">{name}</div>
                            <div class="flagged-item__reason">{reason}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(f"Inspect", key=f"flagged_inspect_{i}", use_container_width=True):
                    select_entity(eid)
                    st.rerun()
        else:
            render_empty_state("No Flagged Individuals", "No high-risk entities detected or backend is offline.")

    with col_activity:
        st.markdown(
            """
            <div class="intel-card-header">
                <span>Activity Feed</span>
                <span style="font-size: 0.72rem; color: #06B6D4; font-weight: normal;">Recent Events</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        if activity_events:
            feed_html = '<div class="activity-feed">'
            for event in activity_events:
                severity = event.get("severity", "info").lower()
                desc = event.get("description", "System event")
                timestamp = event.get("timestamp", "")
                dot_class = f"activity-item__dot--{severity}" if severity in ("critical", "high", "medium", "low") else "activity-item__dot--info"

                feed_html += f"""
                <div class="activity-item">
                    <span class="activity-item__dot {dot_class}"></span>
                    <div class="activity-item__content">
                        <div class="activity-item__desc">{desc}</div>
                        <div class="activity-item__time">{timestamp}</div>
                    </div>
                </div>
                """
            feed_html += '</div>'
            st.markdown(feed_html, unsafe_allow_html=True)
        else:
            render_empty_state("No Recent Activity", "Activity feed unavailable or backend is offline.")

    st.markdown('<div style="height: 1.25rem;"></div>', unsafe_allow_html=True)

    # Network Intelligence Canvas
    st.markdown(
        """
        <div class="intel-card-header">
            <span>Network Intelligence Canvas</span>
        </div>
        """,
        unsafe_allow_html=True
    )
    render_network_graph_container(height=350)
