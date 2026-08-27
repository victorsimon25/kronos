"""
KRONOS Entity Search & Query Page
Dedicated search console allowing analysts to filter across entity types, risk levels, and cases.
"""

from typing import List
import streamlit as st
from utils.navigation import render_breadcrumb
from components.filters import render_entity_filter_bar
from components.entity_table import render_entity_table
from components.empty_states import render_backend_unavailable, render_empty_state, render_error_state
from services.entity_service import entity_service
from services.api_client import BackendUnavailableError, APIError


def render_entity_search_page() -> None:
    """Renders the entity search interface and results table."""
    render_breadcrumb("Search Entities", "Entity Registry")

    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <h2 style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF; margin: 0;">Entity Intelligence Search</h2>
            <p style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.2rem;">
                Search suspects, burner phones, vehicles, shell organizations, and geospatial locations across the intelligence graph.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Search query input bar
    col_input, col_btn = st.columns([4.4, 1.6])
    with col_input:
        current_query = st.session_state.get("entity_search_query", "")
        search_query = st.text_input(
            "Search Query",
            value=current_query,
            placeholder="Search by Person, Phone (+1...), VIN, Location, Alias, or Case ID...",
            label_visibility="collapsed",
            key="ent_search_main_input"
        )
    with col_btn:
        exec_search = st.button("Execute Query", key="ent_search_exec_btn", use_container_width=True)

    # Filter Bar
    filter_data = render_entity_filter_bar(key_prefix="ent_search_page")

    # Determine if we should perform query
    effective_query = search_query.strip()
    active_case = st.session_state.get("selected_case_id")

    results = []
    backend_offline = False
    error_msg = None

    try:
        results = entity_service.search_entities(
            query=effective_query if effective_query else None,
            entity_type=filter_data.get("entity_type"),
            risk_level=filter_data.get("risk_level"),
            min_confidence=filter_data.get("min_confidence"),
            case_id=active_case
        )
    except BackendUnavailableError as e:
        backend_offline = True
        error_msg = str(e)
    except Exception as e:
        error_msg = str(e)

    st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)

    # Display Results or State Indicators
    if backend_offline:
        render_backend_unavailable(error_msg)
    elif error_msg:
        render_error_state("Query Execution Failed", error_msg)
    elif results:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 0.82rem; color: #94A3B8; font-weight: 600; text-transform: uppercase;">
                    Search Results ({len(results)} matching records)
                </span>
                {f'<span style="font-family: monospace; font-size: 0.72rem; color: #38BDF8;">Case Scoped: {active_case}</span>' if active_case else ''}
            </div>
            """,
            unsafe_allow_html=True
        )
        render_entity_table(results, key_prefix="entity_search_page_results")
    else:
        render_empty_state(
            title="No Matching Entities Found",
            description=f"No entity records returned for query '{effective_query or 'All'}' under selected filters."
        )
