"""
KRONOS Header Component
Renders the top security classification banner, application branding, live connection pill,
and global entity search bar.
"""

import streamlit as st
from config import APP_NAME, APP_SUBTITLE, APP_VERSION, SECURITY_CLASSIFICATION, BACKEND_URL
from utils.state import set_page
from services.api_client import api_client


def render_header() -> None:
    """Renders the top application header and status bar."""
    # Top Security Classification Banner
    st.markdown(
        f'<div class="classification-bar">{SECURITY_CLASSIFICATION}</div>',
        unsafe_allow_html=True
    )
    
    # Check backend health
    is_online, latency_ms, status_msg = api_client.check_health()
    st.session_state.backend_online = is_online
    st.session_state.backend_latency_ms = latency_ms
    st.session_state.backend_status_msg = status_msg
    
    status_dot_class = "status-dot status-dot-live" if is_online else "status-dot status-dot-offline"
    status_label = f"LIVE ({latency_ms}ms)" if is_online else f"OFFLINE ({status_msg})"

    # Header Row
    col_brand, col_search, col_status = st.columns([2.8, 4.4, 2.8])
    
    with col_brand:
        active_case = st.session_state.get("selected_case_id")
        case_tag = f'<span class="badge badge-high" style="margin-left: 0.5rem;">CASE: {active_case}</span>' if active_case else ''
        st.markdown(
            f"""
            <div style="display: flex; align-items: baseline; gap: 0.5rem; margin-top: 0.2rem;">
                <span class="kronos-title">{APP_NAME}</span>
                <span style="font-size: 0.72rem; color: #38BDF8; font-family: monospace;">{APP_VERSION}</span>
                {case_tag}
            </div>
            <div class="kronos-subtitle">{APP_SUBTITLE}</div>
            """,
            unsafe_allow_html=True
        )

    with col_search:
        # Dynamic search key to allow instant clickability and automatic reset across page switches
        counter = st.session_state.get("search_nav_counter", 0)
        search_key = f"global_search_input_{counter}"

        def on_search_trigger():
            query_val = st.session_state.get(search_key, "")
            if query_val and query_val.strip():
                st.session_state.entity_search_query = query_val.strip()
                st.session_state.search_nav_counter = counter + 1
                set_page("Search Entities")

        search_col, btn_col = st.columns([3.3, 1.2])
        with search_col:
            global_q = st.text_input(
                "Global Search",
                placeholder="Lookup Entity / Phone / VIN / Alias...",
                label_visibility="collapsed",
                key=search_key,
                on_change=on_search_trigger
            )
        with btn_col:
            if st.button("Search", key=f"global_search_btn_{counter}", use_container_width=True):
                on_search_trigger()
                st.rerun()

    with col_status:
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-end; align-items: center; gap: 0.75rem; margin-top: 0.35rem;">
                <div class="status-pill">
                    <span class="{status_dot_class}"></span>
                    <span>API: {status_label}</span>
                </div>
                <div style="font-family: monospace; font-size: 0.72rem; color: #64748B;">
                    <code>{BACKEND_URL.replace('http://', '').replace('https://', '')}</code>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('<hr style="border: 0; border-top: 1px solid #1E293B; margin: 0.75rem 0 1.25rem 0;" />', unsafe_allow_html=True)
