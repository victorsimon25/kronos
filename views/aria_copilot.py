"""
KRONOS ARIA Copilot Integration Page
Provides designated workspace and container hooks for ARIA (owned by Backend/Intelligence and Visualization teams).
"""

import streamlit as st
from utils.navigation import render_breadcrumb
from components.integration_containers import render_aria_copilot_container


def render_aria_copilot_page() -> None:
    """Renders the ARIA Copilot workspace entrypoint."""
    active_case = st.session_state.get("selected_case_id")
    active_entity = st.session_state.get("selected_entity_id")

    render_breadcrumb("ARIA Copilot", active_case or active_entity)

    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <h2 style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF; margin: 0;">ARIA // Intelligence Copilot</h2>
            <p style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.2rem;">
                Autonomous Reasoning & Graph Intelligence Copilot for natural language investigation queries.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Designated Container hook for Visualization & Backend teams
    render_aria_copilot_container(case_id=active_case, entity_id=active_entity)
