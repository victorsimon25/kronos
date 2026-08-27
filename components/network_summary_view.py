"""
KRONOS Network Summary & Topology Analytics Component
Presents graph intelligence and centrality metrics calculated by Graph/Data Analysis team.
"""

from typing import Optional
import streamlit as st
from models.network import NetworkSummary
from utils.formatting import render_risk_badge, render_type_badge, render_id_pill
from utils.state import select_entity
from components.integration_containers import (
    render_network_graph_container,
    render_network_disruption_container
)


def render_network_summary_view(network: Optional[NetworkSummary]) -> None:
    """
    Renders graph metrics, top central entities table, and communities overview.
    Does NOT calculate any graph metrics directly.
    """
    if network is None:
        return

    # Network KPIs
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Graph Nodes</div>
                <div class="metric-value" style="color: #38BDF8;">{network.total_nodes:,}</div>
                <div class="metric-subtext">Entities in graph</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Graph Edges</div>
                <div class="metric-value" style="color: #38BDF8;">{network.total_edges:,}</div>
                <div class="metric-subtext">Relationships indexed</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        density_str = f"{network.network_density:.4f}" if network.network_density is not None else "N/A"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Network Density</div>
                <div class="metric-value" style="color: #F59E0B;">{density_str}</div>
                <div class="metric-subtext">Graph connectivity index</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Communities</div>
                <div class="metric-value" style="color: #06B6D4;">{network.communities_count}</div>
                <div class="metric-subtext">Detected criminal clusters</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">High-Risk Clusters</div>
                <div class="metric-value" style="color: #EF4444;">{network.high_risk_clusters_count}</div>
                <div class="metric-subtext">Severe threat subgroups</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)

    # Main Interactive Graph Integration Container
    render_network_graph_container()

    # Two Columns: Key Central Entities & Detected Communities
    col_central, col_comm = st.columns([1.6, 1.4])

    with col_central:
        with st.container(border=True):
            st.markdown('<div class="intel-card-header">Key Central Entities (Graph Centrality Rankings)</div>', unsafe_allow_html=True)

            if network.central_entities:
                st.markdown(
                    """
                    <table class="intel-table">
                        <thead>
                            <tr>
                                <th>Entity</th>
                                <th>Degree</th>
                                <th>Betweenness</th>
                                <th>PageRank</th>
                                <th>Risk</th>
                            </tr>
                        </thead>
                        <tbody>
                    """,
                    unsafe_allow_html=True
                )
                for c in network.central_entities:
                    btw_str = f"{c.betweenness_centrality:.3f}" if c.betweenness_centrality is not None else "N/A"
                    pr_str = f"{c.pagerank:.3f}" if c.pagerank is not None else "N/A"
                    st.markdown(
                        f"""
                        <tr>
                            <td>
                                <b>{c.name}</b><br/>
                                <span style="font-family: monospace; font-size: 0.7rem; color: #64748B;">{c.entity_id}</span>
                            </td>
                            <td style="font-family: monospace; color: #38BDF8; font-weight: bold;">{c.degree}</td>
                            <td style="font-family: monospace; color: #CBD5E1;">{btw_str}</td>
                            <td style="font-family: monospace; color: #CBD5E1;">{pr_str}</td>
                            <td>{render_risk_badge(c.risk_level)}</td>
                        </tr>
                        """,
                        unsafe_allow_html=True
                    )
                st.markdown("</tbody></table>", unsafe_allow_html=True)
            else:
                st.markdown('<div style="color: #64748B; font-size: 0.8rem; font-style: italic;">No centrality metrics computed yet by Graph team.</div>', unsafe_allow_html=True)

    with col_comm:
        with st.container(border=True):
            st.markdown(f'<div class="intel-card-header">Detected Criminal Communities ({len(network.communities)})</div>', unsafe_allow_html=True)

            if network.communities:
                for com in network.communities:
                    members_str = ", ".join(com.key_members) if com.key_members else "Not listed"
                    st.markdown(
                        f"""
                        <div style="background: #161C28; border: 1px solid #232B3B; border-radius: 4px; padding: 0.75rem; margin-bottom: 0.6rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-weight: 700; color: #FFFFFF; font-size: 0.85rem;">{com.name}</span>
                                {render_risk_badge(com.risk_level)}
                            </div>
                            <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 0.25rem;">
                                Size: <b style="color: #38BDF8;">{com.member_count} entities</b> | Dominant Type: <b>{com.dominant_type}</b>
                            </div>
                            <div style="font-size: 0.72rem; color: #64748B; margin-top: 0.3rem;">
                                Key Nodes: <span style="font-family: monospace; color: #CBD5E1;">{members_str}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<div style="color: #64748B; font-size: 0.8rem; font-style: italic;">No community clusters returned.</div>', unsafe_allow_html=True)

    # Network Disruption Simulation Container
    render_network_disruption_container()
