"""
KRONOS Entity Table & Results Component
Renders search results, entity rosters, and table views with quick drill-down navigation.
"""

from typing import List
import streamlit as st
from models.entity import EntitySearchResult
from utils.formatting import (
    render_risk_badge,
    render_type_badge,
    render_confidence_badge,
    render_id_pill,
    format_timestamp
)
from utils.state import select_entity


def render_entity_table(entities: List[EntitySearchResult], key_prefix: str = "ent_table") -> None:
    """
    Renders an interactive entity table with direct links to Entity Profile dossiers.
    """
    if not entities:
        return

    # Header Row
    st.markdown(
        """
        <div style="display: grid; grid-template-columns: 2.5fr 1.2fr 1.2fr 1.2fr 1fr 1.5fr 1.2fr; background: #161C28; padding: 0.6rem 0.8rem; border-radius: 4px 4px 0 0; border-bottom: 1px solid #232B3B; font-size: 0.72rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">
            <div>Identifier / Name</div>
            <div>Type</div>
            <div>Risk Level</div>
            <div>Confidence</div>
            <div>Links</div>
            <div>Associated Cases</div>
            <div style="text-align: right;">Action</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    for idx, ent in enumerate(entities):
        cases_str = ", ".join(ent.associated_cases) if ent.associated_cases else "None"
        if len(cases_str) > 25:
            cases_str = cases_str[:22] + "..."
            
        row_col, btn_col = st.columns([8.8, 1.2])
        
        with row_col:
            st.markdown(
                f"""
                <div style="display: grid; grid-template-columns: 2.5fr 1.2fr 1.2fr 1.2fr 1fr 1.5fr; background: #121721; padding: 0.55rem 0.8rem; border-bottom: 1px solid #1E2636; font-size: 0.8rem; align-items: center;">
                    <div>
                        <span style="font-weight: 600; color: #F1F5F9;">{ent.name}</span>
                        <div style="font-size: 0.7rem; color: #64748B; font-family: monospace;">ID: {ent.id}</div>
                    </div>
                    <div>{render_type_badge(ent.type)}</div>
                    <div>{render_risk_badge(ent.risk_level)}</div>
                    <div>{render_confidence_badge(ent.confidence)}</div>
                    <div style="font-family: monospace; color: #38BDF8; font-weight: 600;">{ent.relationship_count}</div>
                    <div style="font-size: 0.75rem; color: #94A3B8;">{cases_str}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        with btn_col:
            if st.button("Inspect", key=f"{key_prefix}_view_{ent.id}_{idx}", use_container_width=True):
                select_entity(ent.id, navigate=True)
                st.rerun()
