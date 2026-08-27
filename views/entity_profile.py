"""
KRONOS Entity Profile & Intelligence Dossier Page
Renders detailed target profile, attributes, relationship links, and ego-network visualization hook.
"""

from typing import Optional
import streamlit as st
from utils.navigation import render_breadcrumb
from components.entity_profile_view import render_entity_profile_view
from components.empty_states import (
    render_backend_unavailable,
    render_empty_state,
    render_error_state
)
from services.entity_service import entity_service
from services.api_client import BackendUnavailableError, NotFoundError, APIError
from utils.state import select_entity


def render_entity_profile_page() -> None:
    """Renders the detailed entity intelligence profile."""
    selected_id = st.session_state.get("selected_entity_id")
    
    render_breadcrumb("Entity Profile", selected_id)

    # Top lookup bar to switch active entity
    col_sel, col_btn = st.columns([4, 1])
    with col_sel:
        target_id_input = st.text_input(
            "Enter Entity Identifier",
            value=selected_id or "",
            placeholder="e.g., ENT-9821, PER-0042, +15550192...",
            label_visibility="collapsed",
            key="profile_target_id_input"
        )
    with col_btn:
        if st.button("Load Dossier", key="profile_load_btn", use_container_width=True):
            if target_id_input.strip():
                select_entity(target_id_input.strip(), navigate=False)
                st.rerun()

    if not selected_id and not target_id_input.strip():
        render_empty_state(
            title="No Target Entity Selected",
            description="Select an entity from Search Entities or enter an Entity ID above to inspect its intelligence dossier."
        )
        return

    target_id = selected_id or target_id_input.strip()

    # Retrieve Entity Dossier from Backend
    entity = None
    backend_offline = False
    not_found = False
    error_msg = None

    try:
        entity = entity_service.get_entity_by_id(target_id)
        if not entity:
            not_found = True
    except NotFoundError:
        not_found = True
    except BackendUnavailableError as e:
        backend_offline = True
        error_msg = str(e)
    except Exception as e:
        error_msg = str(e)

    # Render Result
    if backend_offline:
        render_backend_unavailable(error_msg)
    elif not_found:
        render_empty_state(
            title=f"Entity '{target_id}' Not Found",
            description="The requested entity identifier does not exist in the intelligence corpus."
        )
    elif error_msg:
        render_error_state("Failed Loading Dossier", error_msg)
    elif entity:
        render_entity_profile_view(entity)
