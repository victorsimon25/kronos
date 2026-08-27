"""
KRONOS Session State Management Module
Maintains active navigation, selected entity/case, search queries, and filters across reruns.
"""

from typing import Optional, Dict, Any
import streamlit as st
from config import PAGE_DASHBOARD


def init_session_state() -> None:
    """Initialize default keys in streamlit session state if not already set."""
    defaults: Dict[str, Any] = {
        "current_page": PAGE_DASHBOARD,
        "selected_entity_id": None,
        "selected_case_id": None,
        "selected_pattern_id": None,
        "global_search_query": "",
        "entity_search_query": "",
        "filter_entity_type": "All",
        "filter_risk_level": "All",
        "filter_min_confidence": 0.0,
        "filter_case_id": "All",
        "backend_online": False,
        "backend_latency_ms": 0.0,
        "backend_status_msg": "CHECKING...",
    }
    
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def set_page(page_name: str) -> None:
    """Navigate to a specific page using modern Streamlit page switching."""
    st.session_state.current_page = page_name
    try:
        from navigation_registry import PAGE_REGISTRY
        if page_name in PAGE_REGISTRY:
            st.switch_page(PAGE_REGISTRY[page_name])
    except Exception:
        pass


def select_entity(entity_id: str, navigate: bool = True) -> None:
    """Select an entity and optionally route to the Entity Profile page."""
    st.session_state.selected_entity_id = entity_id
    if navigate:
        set_page("Entity Profile")


def select_case(case_id: str, navigate: bool = True) -> None:
    """Select an active case/investigation context and optionally route to Investigations page."""
    st.session_state.selected_case_id = case_id
    if navigate:
        set_page("Investigations")


def select_pattern(pattern_id: str, navigate: bool = True) -> None:
    """Select a suspicious pattern and optionally route to Suspicious Patterns page."""
    st.session_state.selected_pattern_id = pattern_id
    if navigate:
        set_page("Suspicious Patterns")
