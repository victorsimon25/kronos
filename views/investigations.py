"""
KRONOS Investigations & Case Management Page
Provides case dossiers, linked suspect rosters, and timeline/evidence integration hooks.
"""

from typing import List, Optional
import streamlit as st
from utils.navigation import render_breadcrumb
from components.investigation_card import (
    render_investigation_summary_table,
    render_investigation_dossier
)
from components.empty_states import (
    render_backend_unavailable,
    render_empty_state,
    render_error_state
)
from services.investigation_service import investigation_service
from services.api_client import BackendUnavailableError, NotFoundError, APIError
from utils.state import select_case


def render_investigations_page() -> None:
    """Renders the case management and detailed investigation workspace."""
    active_case_id = st.session_state.get("selected_case_id")
    
    render_breadcrumb("Investigations", active_case_id)

    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <h2 style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF; margin: 0;">Case Intelligence Management</h2>
            <p style="font-size: 0.8rem; color: #94A3B8; margin-top: 0.2rem;">
                Track ongoing operations, multi-target syndicate cases, and forensic evidence links.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Top Case Filter & Selector Bar
    col_filter, col_status, col_btn = st.columns([3, 2, 1.5])
    with col_filter:
        case_search = st.text_input(
            "Search Cases",
            placeholder="Search by Case ID, Title, Lead Analyst...",
            label_visibility="collapsed",
            key="case_search_input"
        )
    with col_status:
        status_filter = st.selectbox(
            "Status Filter",
            options=["All", "Active", "Under Review", "Escalated", "Closed"],
            label_visibility="collapsed",
            key="case_status_filter"
        )
    with col_btn:
        if active_case_id:
            if st.button("View All Cases", key="case_view_all_btn", use_container_width=True):
                select_case(None, navigate=False)
                st.rerun()

    # If a specific case is selected, render its full dossier
    if active_case_id:
        backend_offline = False
        case_dossier = None
        error_msg = None
        
        try:
            case_dossier = investigation_service.get_investigation_by_id(active_case_id)
        except BackendUnavailableError as e:
            backend_offline = True
            error_msg = str(e)
        except Exception as e:
            error_msg = str(e)

        if backend_offline:
            render_backend_unavailable(error_msg)
        elif error_msg:
            render_error_state("Failed to Load Case Dossier", error_msg)
        elif case_dossier:
            render_investigation_dossier(case_dossier)
        else:
            render_empty_state(
                title=f"Case '{active_case_id}' Not Found",
                description="The selected investigation could not be retrieved from the backend."
            )
        return

    # Otherwise render the list of all cases
    cases = []
    backend_offline = False
    error_msg = None

    try:
        cases = investigation_service.list_investigations(
            status=status_filter if status_filter != "All" else None,
            query=case_search.strip() if case_search.strip() else None
        )
    except BackendUnavailableError as e:
        backend_offline = True
        error_msg = str(e)
    except Exception as e:
        error_msg = str(e)

    if backend_offline:
        render_backend_unavailable(error_msg)
    elif error_msg:
        render_error_state("Failed to List Investigations", error_msg)
    elif cases:
        st.markdown(
            f"""
            <div style="font-size: 0.82rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;">
                Active Investigations Roster ({len(cases)} cases)
            </div>
            """,
            unsafe_allow_html=True
        )
        render_investigation_summary_table(cases, key_prefix="investigations_page_table")
    else:
        render_empty_state(
            title="No Investigations Found",
            description="No active or archived case files match your search criteria."
        )
