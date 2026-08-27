"""
KRONOS Integration Containers Module
Provides standardized, clean integration hooks for the Frontend Visualization & AI/NLP teams.
"""

from typing import List, Optional, Dict, Any
import streamlit as st


def render_network_graph_container(
    entity_ids: Optional[List[str]] = None,
    case_id: Optional[str] = None,
    height: int = 350,
    container_key: str = "main_network_graph"
) -> None:
    """
    DESIGNATED INTEGRATION CONTAINER: Interactive Network Graph.
    Owned by: FRONTEND — VISUALIZATION TEAM.
    """
    case_str = f"CASE: {case_id}" if case_id else "SCOPE: GLOBAL NETWORK"
    nodes_str = f"({len(entity_ids)} entities targeted)" if entity_ids else ""

    st.markdown(
        f"""
        <div class="hud-corners" style="position: relative;">
            <div class="integration-container-box" style="min-height: {height}px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #06B6D4; margin-bottom: 0.5rem;">
                    [ AWAITING NETWORK DATA ]
                </div>
                <div class="title">Network Intelligence Canvas</div>
                <div class="team-owner">Integration: Visualization Team</div>
                <div class="desc" style="max-width: 500px;">
                    Interactive graph canvas ({case_str} {nodes_str}).<br/>
                    Node selection, community clusters, shortest-path rendering.
                </div>
            </div>
            <span class="hud-corner-bl"></span>
            <span class="hud-corner-br"></span>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_timeline_container(
    case_id: Optional[str] = None,
    entity_id: Optional[str] = None,
    events: Optional[List[Dict[str, Any]]] = None,
    height: int = 320
) -> None:
    """
    DESIGNATED INTEGRATION CONTAINER: Chronological Timeline Visualization.
    Owned by: FRONTEND — VISUALIZATION TEAM.
    """
    st.markdown(
        f"""
        <div class="integration-container-box" style="min-height: {height}px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <div style="font-family: monospace; font-size: 0.72rem; color: #06B6D4; margin-bottom: 0.5rem;">
                [INTEGRATION HOOK: VISUALIZATION TEAM]
            </div>
            <div class="title">Interactive Chronological Timeline</div>
            <div class="team-owner">Owner: Frontend — Visualization Team</div>
            <div class="desc" style="max-width: 500px;">
                Temporal event sequence and communication burst visualization for Case {case_id or 'Global'}.
            </div>
            <div style="margin-top: 0.75rem; font-family: monospace; font-size: 0.72rem; color: #475569; background: #0B0E14; padding: 0.35rem 0.7rem; border-radius: 3px; border: 1px solid #1E293B;">
                Hook: <code>render_timeline_container(case_id='{case_id or ""}', entity_id='{entity_id or ""}')</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_relationship_graph_container(
    entity_id: str,
    relationships: Optional[List[Any]] = None,
    height: int = 360
) -> None:
    """
    DESIGNATED INTEGRATION CONTAINER: Local Ego-Network / Relationship Graph.
    Owned by: FRONTEND — VISUALIZATION TEAM.
    """
    count = len(relationships) if relationships else 0
    st.markdown(
        f"""
        <div class="integration-container-box" style="min-height: {height}px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <div style="font-family: monospace; font-size: 0.72rem; color: #06B6D4; margin-bottom: 0.5rem;">
                [INTEGRATION HOOK: VISUALIZATION TEAM]
            </div>
            <div class="title">Local Relationship Ego-Graph</div>
            <div class="team-owner">Owner: Frontend — Visualization Team</div>
            <div class="desc" style="max-width: 480px;">
                Interactive 1st and 2nd-degree relationship expansion for Target: <b>{entity_id}</b> ({count} direct links).
            </div>
            <div style="margin-top: 0.75rem; font-family: monospace; font-size: 0.72rem; color: #475569; background: #0B0E14; padding: 0.35rem 0.7rem; border-radius: 3px; border: 1px solid #1E293B;">
                Hook: <code>render_relationship_graph_container(entity_id='{entity_id}')</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_evidence_provenance_container(
    evidence_refs: Optional[List[str]] = None,
    case_id: Optional[str] = None
) -> None:
    """
    DESIGNATED INTEGRATION CONTAINER: Evidence & Provenance Viewer.
    Owned by: FRONTEND — VISUALIZATION TEAM & CORE BACKEND (Retrieval).
    """
    refs_count = len(evidence_refs) if evidence_refs else 0
    st.markdown(
        f"""
        <div class="integration-container-box" style="padding: 1.25rem;">
            <div style="font-family: monospace; font-size: 0.72rem; color: #06B6D4; margin-bottom: 0.3rem;">
                [INTEGRATION HOOK: VISUALIZATION & AI/NLP]
            </div>
            <div class="title" style="font-size: 0.85rem;">Evidence & Provenance Inspector</div>
            <div class="team-owner">Owner: Visualization + Backend / AI Retrieval</div>
            <div class="desc" style="font-size: 0.78rem;">
                Source document excerpts, bounding boxes, and forensic verification provenance ({refs_count} citations attached).
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_aria_copilot_container(
    case_id: Optional[str] = None,
    entity_id: Optional[str] = None
) -> None:
    """
    DESIGNATED INTEGRATION CONTAINER: ARIA Copilot Chat & Intelligence Assistant.
    Owned by: FRONTEND — VISUALIZATION TEAM & CORE BACKEND (LLM Orchestration).
    """
    context_str = f"Context: Case {case_id}" if case_id else (f"Context: Entity {entity_id}" if entity_id else "Global Context")
    st.markdown(
        f"""
        <div class="integration-container-box" style="min-height: 420px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <div style="font-family: monospace; font-size: 0.75rem; color: #06B6D4; margin-bottom: 0.5rem;">
                [INTEGRATION HOOK: ARIA COPILOT UI]
            </div>
            <div class="title" style="color: #38BDF8;">ARIA // Autonomous Reasoning Intelligence Assistant</div>
            <div class="team-owner">Owner: Backend / Intelligence (LLM) & Frontend Visualization (Chat UI)</div>
            <div class="desc" style="max-width: 520px; line-height: 1.5; margin-top: 0.75rem;">
                Interactive graph-grounded conversational agent ({context_str}).<br/>
                Answers complex investigative questions, executes multi-hop Cypher queries, and explains anomalous patterns.
            </div>
            <div style="margin-top: 1.25rem; font-family: monospace; font-size: 0.75rem; color: #64748B; background: #0B0E14; padding: 0.5rem 1rem; border-radius: 4px; border: 1px solid #1E293B;">
                Hook: <code>render_aria_copilot_container(case_id='{case_id or ""}', entity_id='{entity_id or ""}')</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_network_disruption_container(
    target_node_ids: Optional[List[str]] = None
) -> None:
    """
    DESIGNATED INTEGRATION CONTAINER: Network Disruption Simulation.
    Owned by: GRAPH / DATA ANALYSIS TEAM (Simulation) & FRONTEND VISUALIZATION (Graph Diff).
    """
    st.markdown(
        f"""
        <div class="integration-container-box" style="min-height: 280px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
            <div style="font-family: monospace; font-size: 0.72rem; color: #06B6D4; margin-bottom: 0.3rem;">
                [INTEGRATION HOOK: GRAPH & VISUALIZATION TEAMS]
            </div>
            <div class="title">Network Disruption & Resilience Simulation</div>
            <div class="team-owner">Owner: Graph Analysis (NetworkX) + Frontend Visualization</div>
            <div class="desc" style="max-width: 480px;">
                Simulate targeted takedowns and key-node removals to evaluate criminal network fragmentation.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
