"""
KRONOS Investigation Card & Dossier Component
Renders investigation summary cards and detailed case intelligence dossiers.
"""

from typing import List
import streamlit as st
from models.investigation import Investigation, InvestigationSummary
from utils.formatting import (
    render_risk_badge,
    render_id_pill,
    format_timestamp
)
from utils.state import select_case, select_entity
from components.integration_containers import (
    render_network_graph_container,
    render_timeline_container,
    render_evidence_provenance_container
)


def render_investigation_summary_table(
    cases: List[InvestigationSummary],
    key_prefix: str = "case_summary"
) -> None:
    """
    Renders a table/roster of active investigations with quick drill-down buttons.
    """
    if not cases:
        return

    st.markdown(
        """
        <div style="display: grid; grid-template-columns: 1.8fr 3fr 1.2fr 1.2fr 1fr 1fr 1.8fr 1.2fr; background: #161C28; padding: 0.6rem 0.8rem; border-radius: 4px 4px 0 0; border-bottom: 1px solid #232B3B; font-size: 0.72rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">
            <div>Case ID</div>
            <div>Title</div>
            <div>Risk</div>
            <div>Status</div>
            <div>Entities</div>
            <div>Patterns</div>
            <div>Last Updated</div>
            <div style="text-align: right;">Action</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    for idx, c in enumerate(cases):
        row_col, btn_col = st.columns([8.8, 1.2])
        
        status_color = "#10B981" if c.status == "Active" else "#94A3B8"
        
        with row_col:
            st.markdown(
                f"""
                <div style="display: grid; grid-template-columns: 1.8fr 3fr 1.2fr 1.2fr 1fr 1fr 1.8fr; background: #121721; padding: 0.55rem 0.8rem; border-bottom: 1px solid #1E2636; font-size: 0.8rem; align-items: center;">
                    <div>{render_id_pill(c.case_id)}</div>
                    <div style="font-weight: 600; color: #F1F5F9;">{c.title}</div>
                    <div>{render_risk_badge(c.risk_level)}</div>
                    <div><span style="color: {status_color}; font-weight: 600; font-size: 0.75rem;">● {c.status}</span></div>
                    <div style="font-family: monospace; color: #38BDF8;">{c.entity_count}</div>
                    <div style="font-family: monospace; color: #F97316;">{c.pattern_count}</div>
                    <div style="font-size: 0.72rem; color: #64748B;">{format_timestamp(c.last_updated)}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with btn_col:
            if st.button("Open Case", key=f"{key_prefix}_open_{c.case_id}_{idx}", use_container_width=True):
                select_case(c.case_id, navigate=True)
                st.rerun()


def render_investigation_dossier(case: Investigation) -> None:
    """
    Renders the complete detailed investigation dossier with linked entities,
    findings, timeline hook, and network graph hook.
    """
    # Top Case Banner
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="font-size: 1.4rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.3rem;">
                        {case.title}
                    </div>
                    <div style="display: flex; gap: 0.75rem; align-items: center; font-size: 0.78rem; color: #94A3B8;">
                        <span>CASE IDENTIFIER: {render_id_pill(case.case_id)}</span>
                        <span>LEAD ANALYST: <b style="color: #CBD5E1;">{case.lead_analyst}</b></span>
                        <span>STATUS: <b style="color: #10B981;">{case.status}</b></span>
                    </div>
                </div>
                <div>
                    {render_risk_badge(case.risk_level)}
                </div>
            </div>
            <div style="margin-top: 0.75rem; font-size: 0.85rem; color: #CBD5E1; line-height: 1.5; border-top: 1px solid #1E293B; padding-top: 0.6rem;">
                {case.description}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)

    # Metrics Summary Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Target Entities</div>
                <div class="metric-value" style="color: #38BDF8;">{case.entity_count}</div>
                <div class="metric-subtext">Linked suspects & nodes</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Relationships</div>
                <div class="metric-value" style="color: #38BDF8;">{case.relationship_count}</div>
                <div class="metric-subtext">Graph connections</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Suspicious Patterns</div>
                <div class="metric-value" style="color: #F97316;">{case.pattern_count}</div>
                <div class="metric-subtext">Anomalies identified</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Last Updated</div>
                <div class="metric-value" style="font-size: 1.1rem; color: #94A3B8; margin-top: 0.5rem;">{format_timestamp(case.updated_at)}</div>
                <div class="metric-subtext">Created: {format_timestamp(case.created_at)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)

    # Key Findings & Linked Entities
    col_findings, col_entities = st.columns([1.5, 1.5])

    with col_findings:
        with st.container(border=True):
            st.markdown('<div class="intel-card-header">Key Investigative Findings</div>', unsafe_allow_html=True)
            if case.key_findings:
                for finding in case.key_findings:
                    st.markdown(f'<li style="color: #CBD5E1; font-size: 0.82rem; margin-bottom: 0.4rem;">{finding}</li>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color: #64748B; font-size: 0.8rem; font-style: italic;">No key findings recorded yet for this case.</div>', unsafe_allow_html=True)

    with col_entities:
        with st.container(border=True):
            st.markdown(f'<div class="intel-card-header">Linked Entity Roster ({len(case.entity_ids)})</div>', unsafe_allow_html=True)
            if case.entity_ids:
                for ent_id in case.entity_ids:
                    ecol_name, ecol_btn = st.columns([3, 1])
                    with ecol_name:
                        st.markdown(f'<div style="font-family: monospace; font-size: 0.8rem; color: #F1F5F9; margin-top: 0.25rem;">● {ent_id}</div>', unsafe_allow_html=True)
                    with ecol_btn:
                        if st.button("Inspect", key=f"case_ent_inspect_{case.case_id}_{ent_id}", use_container_width=True):
                            select_entity(ent_id, navigate=True)
                            st.rerun()
            else:
                st.markdown('<div style="color: #64748B; font-size: 0.8rem; font-style: italic;">No entities associated yet.</div>', unsafe_allow_html=True)

    # Designated Visualization Containers for Case Timeline, Graph & Evidence
    render_timeline_container(case_id=case.case_id)
    render_network_graph_container(case_id=case.case_id, entity_ids=case.entity_ids)
    render_evidence_provenance_container(case_id=case.case_id)
