"""
KRONOS Navigation Registry
Defines the official Streamlit st.Page objects for native top navigation.
"""

import streamlit as st
from views.dashboard import render_dashboard_page
from views.entity_search import render_entity_search_page
from views.entity_profile import render_entity_profile_page
from views.investigations import render_investigations_page
from views.suspicious_patterns import render_suspicious_patterns_page
from views.network_summary import render_network_summary_page
from views.aria_copilot import render_aria_copilot_page

PAGE_DASHBOARD_OBJ = st.Page(
    render_dashboard_page,
    title="Dashboard",
    url_path="dashboard",
    default=True
)
PAGE_ENTITY_SEARCH_OBJ = st.Page(
    render_entity_search_page,
    title="Search Entities",
    url_path="search-entities"
)
PAGE_ENTITY_PROFILE_OBJ = st.Page(
    render_entity_profile_page,
    title="Entity Profile",
    url_path="entity-profile"
)
PAGE_INVESTIGATIONS_OBJ = st.Page(
    render_investigations_page,
    title="Investigations",
    url_path="investigations"
)
PAGE_SUSPICIOUS_PATTERNS_OBJ = st.Page(
    render_suspicious_patterns_page,
    title="Suspicious Patterns",
    url_path="suspicious-patterns"
)
PAGE_NETWORK_SUMMARY_OBJ = st.Page(
    render_network_summary_page,
    title="Network Summary",
    url_path="network-summary"
)
PAGE_ARIA_COPILOT_OBJ = st.Page(
    render_aria_copilot_page,
    title="ARIA Copilot",
    url_path="aria-copilot"
)

PAGE_REGISTRY = {
    "Dashboard": PAGE_DASHBOARD_OBJ,
    "Search Entities": PAGE_ENTITY_SEARCH_OBJ,
    "Entity Profile": PAGE_ENTITY_PROFILE_OBJ,
    "Investigations": PAGE_INVESTIGATIONS_OBJ,
    "Suspicious Patterns": PAGE_SUSPICIOUS_PATTERNS_OBJ,
    "Network Summary": PAGE_NETWORK_SUMMARY_OBJ,
    "ARIA Copilot": PAGE_ARIA_COPILOT_OBJ,
}

ALL_PAGES = [
    PAGE_DASHBOARD_OBJ,
    PAGE_ENTITY_SEARCH_OBJ,
    PAGE_ENTITY_PROFILE_OBJ,
    PAGE_INVESTIGATIONS_OBJ,
    PAGE_SUSPICIOUS_PATTERNS_OBJ,
    PAGE_NETWORK_SUMMARY_OBJ,
    PAGE_ARIA_COPILOT_OBJ,
]
