"""
KRONOS Polished State Renderers
Handles Loading, Empty, Offline, and Error states cleanly without exposing raw stack traces.
"""

import streamlit as st
from config import BACKEND_URL


def render_loading_state(message: str = "Querying intelligence core...") -> None:
    """Renders a restrained, professional intelligence loading state."""
    st.markdown(
        f"""
        <div style="background: #121721; border: 1px solid #1E293B; border-radius: 4px; padding: 1.25rem; text-align: center; margin: 0.75rem 0;">
            <div style="font-family: monospace; color: #38BDF8; font-size: 0.85rem; letter-spacing: 0.08em;">
                [STATUS: RETRIEVING DATA]
            </div>
            <div style="color: #94A3B8; font-size: 0.82rem; margin-top: 0.4rem;">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_empty_state(
    title: str = "No Intelligence Records Found",
    description: str = "No data returned matching the current filters or query criteria.",
    action_label: str = None,
    action_key: str = None
) -> bool:
    """Renders a clean empty data indicator."""
    st.markdown(
        f"""
        <div style="background: #121721; border: 1px solid #1E2636; border-radius: 4px; padding: 1.25rem 1rem; text-align: center; margin: 0.5rem 0 1rem 0;">
            <div style="color: #94A3B8; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em;">
                {title}
            </div>
            <div style="color: #64748B; font-size: 0.78rem; margin-top: 0.35rem; max-width: 450px; margin-left: auto; margin-right: auto;">
                {description}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if action_label and action_key:
        cols = st.columns([1, 2, 1])
        with cols[1]:
            return st.button(action_label, key=action_key, use_container_width=True)
    return False


def render_backend_unavailable(details: str = None) -> None:
    """
    Renders an informative offline diagnostic banner when Core Backend is unreachable.
    Does NOT fabricate data.
    """
    st.markdown(
        f"""
        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 4px; padding: 1.25rem; margin: 0.75rem 0 1rem 0;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span class="badge badge-critical" style="margin-right: 0.5rem;">BACKEND OFFLINE</span>
                    <span style="font-weight: 700; color: #F87171; font-size: 0.9rem;">Core Backend API Unavailable</span>
                </div>
                <div style="font-family: monospace; font-size: 0.75rem; color: #94A3B8;">
                    TARGET: {BACKEND_URL}
                </div>
            </div>
            <div style="color: #CBD5E1; font-size: 0.82rem; margin-top: 0.75rem; line-height: 1.5;">
                Unable to establish connection with the Core Backend API service. 
                Intelligence retrieval, entity lookups, and graph summaries are paused.
            </div>
            <div style="background: #0B0E14; border: 1px solid #1E293B; border-radius: 3px; padding: 0.6rem 0.8rem; margin-top: 0.75rem; font-family: monospace; font-size: 0.75rem; color: #A0AEC0;">
                Troubleshooting:<br/>
                1. Ensure FastAPI backend is running on <code>{BACKEND_URL}</code><br/>
                2. Set the <code>BACKEND_URL</code> environment variable if using a different port or host.<br/>
                {f'<span style="color: #F87171;">Diagnostic: {details}</span>' if details else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_error_state(title: str, message: str) -> None:
    """Renders a user-facing error panel without raw Python stack traces."""
    st.markdown(
        f"""
        <div style="background: rgba(249, 115, 22, 0.08); border: 1px solid rgba(249, 115, 22, 0.35); border-radius: 4px; padding: 1.25rem; margin: 0.75rem 0 1rem 0;">
            <div style="font-weight: 700; color: #FB923C; font-size: 0.9rem; margin-bottom: 0.4rem;">
                [ERROR] {title}
            </div>
            <div style="color: #CBD5E1; font-size: 0.82rem; line-height: 1.4;">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
