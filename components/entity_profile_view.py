"""
KRONOS Entity Profile Dossier Component
Dynamic dossier presentation for Person, Phone, Vehicle, Location, Organization, and Event entity types.
"""

from typing import Dict, Any, List
import streamlit as st
from models.entity import Entity, Relationship
from utils.formatting import (
    render_risk_badge,
    render_type_badge,
    render_confidence_badge,
    render_id_pill,
    format_timestamp
)
from utils.state import select_entity, select_case
from components.integration_containers import render_relationship_graph_container


def render_entity_profile_view(entity: Entity) -> None:
    """
    Renders the full entity dossier with dynamic attribute resolution,
    relationship tables, and graph visualization integration hooks.
    """
    # Top Dossier Header Card
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                        <span style="font-size: 1.5rem; font-weight: 700; color: #FFFFFF;">{entity.name}</span>
                        {render_type_badge(entity.type)}
                    </div>
                    <div style="display: flex; gap: 0.75rem; align-items: center; font-size: 0.78rem; color: #94A3B8;">
                        <span>TARGET ID: {render_id_pill(entity.id)}</span>
                        <span>STATUS: <b style="color: #F1F5F9;">{entity.status}</b></span>
                        {f'<span>FIRST OBSERVED: {format_timestamp(entity.first_observed)}</span>' if entity.first_observed else ''}
                    </div>
                </div>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    {render_risk_badge(entity.risk_level)}
                    {render_confidence_badge(entity.confidence)}
                </div>
            </div>
            {f'<div style="margin-top: 0.75rem; font-size: 0.85rem; color: #CBD5E1; line-height: 1.4; border-top: 1px solid #1E293B; padding-top: 0.6rem;">{entity.description}</div>' if entity.description else ''}
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)

    # Secondary Layout: Dynamic Attributes & Case Association
    col_dossier, col_cases = st.columns([2.2, 1.0])

    with col_dossier:
        with st.container(border=True):
            st.markdown(f'<div class="intel-card-header">Target Dossier Attributes ({entity.type.upper()})</div>', unsafe_allow_html=True)

            # Aliases if present
            if entity.aliases:
                st.markdown(
                    f"""
                    <div style="margin-bottom: 0.8rem; font-size: 0.82rem;">
                        <span style="color: #94A3B8; font-weight: 600; text-transform: uppercase; font-size: 0.72rem;">Known Aliases / Monikers:</span><br/>
                        <div style="margin-top: 0.2rem; display: flex; gap: 0.4rem; flex-wrap: wrap;">
                            {' '.join([f'<span class="id-pill" style="color: #FBBF24;">{a}</span>' for a in entity.aliases])}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Dynamic Attributes Table
            if entity.attributes:
                st.markdown(
                    """
                    <table class="intel-table">
                        <thead>
                            <tr>
                                <th style="width: 35%;">Attribute Field</th>
                                <th>Recorded Intelligence Value</th>
                            </tr>
                        </thead>
                        <tbody>
                    """,
                    unsafe_allow_html=True
                )
                for attr_key, attr_val in entity.attributes.items():
                    key_display = attr_key.replace("_", " ").title()
                    val_display = str(attr_val)
                    st.markdown(
                        f"""
                        <tr>
                            <td style="font-weight: 600; color: #94A3B8;">{key_display}</td>
                            <td style="font-family: monospace; color: #E2E8F0;">{val_display}</td>
                        </tr>
                        """,
                        unsafe_allow_html=True
                    )
                st.markdown("</tbody></table>", unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div style="color: #64748B; font-size: 0.8rem; font-style: italic;">No specific structured attributes attached to this entity record.</div>',
                    unsafe_allow_html=True
                )

    with col_cases:
        with st.container(border=True):
            st.markdown('<div class="intel-card-header">Associated Investigations</div>', unsafe_allow_html=True)
            
            if entity.associated_cases:
                for case_id in entity.associated_cases:
                    col_cname, col_cbtn = st.columns([2.5, 1.5])
                    with col_cname:
                        st.markdown(f'<div style="font-family: monospace; font-size: 0.8rem; color: #38BDF8; font-weight: bold; margin-top: 0.3rem;">{case_id}</div>', unsafe_allow_html=True)
                    with col_cbtn:
                        if st.button("Scope Case", key=f"ent_profile_case_{case_id}_{entity.id}", use_container_width=True):
                            select_case(case_id, navigate=True)
                            st.rerun()
            else:
                st.markdown('<div style="color: #64748B; font-size: 0.8rem; font-style: italic;">Not formally linked to an active case.</div>', unsafe_allow_html=True)

    st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)

    # Relationships Section
    with st.container(border=True):
        st.markdown(
            f'<div class="intel-card-header">Relationship & Network Connections ({len(entity.relationships)} direct links)</div>',
            unsafe_allow_html=True
        )

        if entity.relationships:
            st.markdown(
                """
                <div style="display: grid; grid-template-columns: 2.2fr 1.5fr 1.2fr 1.2fr 1.8fr 1.0fr; background: #161C28; padding: 0.5rem 0.8rem; border-radius: 4px 4px 0 0; font-size: 0.72rem; font-weight: 700; color: #94A3B8; text-transform: uppercase;">
                    <div>Target Entity</div>
                    <div>Relation Type</div>
                    <div>Confidence</div>
                    <div>Source Ref</div>
                    <div>Observation Range</div>
                    <div style="text-align: right;">Action</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            for idx, rel in enumerate(entity.relationships):
                r_col, b_col = st.columns([9.0, 1.0])
                obs_range = f"{format_timestamp(rel.first_observed)} - {format_timestamp(rel.last_observed)}" if (rel.first_observed or rel.last_observed) else "Recorded"
                
                with r_col:
                    st.markdown(
                        f"""
                        <div style="display: grid; grid-template-columns: 2.2fr 1.5fr 1.2fr 1.2fr 1.8fr; background: #121721; padding: 0.5rem 0.8rem; border-bottom: 1px solid #1E2636; font-size: 0.78rem; align-items: center;">
                            <div>
                                <span style="font-weight: 600; color: #F1F5F9;">{rel.target_name}</span>
                                <span style="font-size: 0.68rem; color: #64748B; font-family: monospace; display: block;">{rel.target_id}</span>
                            </div>
                            <div><span class="badge badge-neutral">{rel.relation_type}</span></div>
                            <div>{render_confidence_badge(rel.confidence)}</div>
                            <div style="font-family: monospace; font-size: 0.72rem; color: #94A3B8;">{rel.source_ref or 'Graph Ingest'}</div>
                            <div style="font-size: 0.72rem; color: #64748B;">{obs_range}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with b_col:
                    if st.button("Hop", key=f"hop_rel_{entity.id}_{rel.target_id}_{idx}", use_container_width=True):
                        select_entity(rel.target_id, navigate=True)
                        st.rerun()
        else:
            st.markdown('<div style="color: #64748B; font-size: 0.8rem; font-style: italic; padding: 0.5rem 0;">No direct relationships recorded for this entity in the graph.</div>', unsafe_allow_html=True)

    # Designated Visualization Team Container for Ego-Graph
    render_relationship_graph_container(entity_id=entity.id, relationships=entity.relationships)
