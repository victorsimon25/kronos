"""
KRONOS Suspicious Patterns Feed & Table Component
Renders AI/NLP detected criminal anomalies, behavioral similarities, and multi-entity links.
"""

from typing import List
import streamlit as st
from models.pattern import SuspiciousPattern
from utils.formatting import (
    render_severity_badge,
    render_confidence_badge,
    render_id_pill,
    format_timestamp
)
from utils.state import select_entity, select_case, select_pattern


def render_pattern_table(patterns: List[SuspiciousPattern], key_prefix: str = "pat_feed") -> None:
    """
    Renders suspicious pattern cards with entity links, severity badges, and case associations.
    """
    if not patterns:
        return

    for idx, pat in enumerate(patterns):
        # Determine card border color based on severity
        sev = pat.severity.upper()
        if sev in ("CRITICAL", "CRIT"):
            border_color = "#EF4444"
        elif sev == "HIGH":
            border_color = "#F97316"
        elif sev == "MEDIUM":
            border_color = "#F59E0B"
        else:
            border_color = "#10B981"

        st.markdown(
            f"""
            <div class="intel-card" style="border-left: 4px solid {border_color}; margin-bottom: 0.85rem;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                            <span style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF;">{pat.pattern_type}</span>
                            {render_id_pill(pat.pattern_id)}
                        </div>
                        <div style="font-size: 0.75rem; color: #94A3B8;">
                            DETECTED: <b>{format_timestamp(pat.detection_date)}</b> | STATUS: <b style="color: #CBD5E1;">{pat.status}</b>
                        </div>
                    </div>
                    <div style="display: flex; gap: 0.4rem; align-items: center;">
                        {render_severity_badge(pat.severity)}
                        {render_confidence_badge(pat.confidence)}
                    </div>
                </div>
                <div style="margin-top: 0.6rem; font-size: 0.82rem; color: #CBD5E1; line-height: 1.4;">
                    {pat.description}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Bottom row: Entities involved & case link buttons
        b_col1, b_col2 = st.columns([3.5, 1.5])
        
        with b_col1:
            if pat.entities_involved:
                ent_links = []
                for e in pat.entities_involved:
                    eid = e.get("id", e.get("entity_id", "Unknown")) if isinstance(e, dict) else str(e)
                    ename = e.get("name", eid) if isinstance(e, dict) else str(e)
                    ent_links.append(f'<span class="id-pill" style="margin-right: 0.3rem;">{ename}</span>')
                st.markdown(
                    f'<div style="font-size: 0.75rem; color: #94A3B8; margin-bottom: 0.5rem;"><b>Entities Involved:</b> {" ".join(ent_links)}</div>',
                    unsafe_allow_html=True
                )

        with b_col2:
            if pat.related_case_id:
                if st.button(f"Scope {pat.related_case_id}", key=f"{key_prefix}_scope_{pat.pattern_id}_{idx}", use_container_width=True):
                    select_case(pat.related_case_id, navigate=True)
                    st.rerun()
                    
        st.markdown('<div style="height: 0.4rem;"></div>', unsafe_allow_html=True)
