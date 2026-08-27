"""
KRONOS // AI-Powered Criminal Network Analysis System
Main Streamlit Application Entrypoint (FRONTEND — DASHBOARD)

Run with:
    streamlit run app.py
"""

from pathlib import Path
import streamlit as st

# 1. Page Configuration (Must be first Streamlit call)
st.set_page_config(
    page_title="KRONOS // Criminal Network Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Imports
from utils.state import init_session_state
from components.header import render_header
from components.sidebar import render_sidebar_context
from navigation_registry import ALL_PAGES


def load_css() -> None:
    """Inject custom CSS stylesheet for military/intelligence dark theme."""
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main() -> None:
    """Main application lifecycle with native Streamlit navigation."""
    # Initialize session state defaults
    init_session_state()

    # Apply CSS Theme
    load_css()

    # Setup Native Streamlit Top Sidebar Navigation (No emojis, no bullets)
    pg = st.navigation(ALL_PAGES)

    # Automatically clear global search input when switching pages via sidebar
    current_page_title = getattr(pg, "title", None)
    last_page_title = st.session_state.get("last_nav_page")
    if last_page_title is not None and last_page_title != current_page_title:
        st.session_state.search_nav_counter = st.session_state.get("search_nav_counter", 0) + 1
    st.session_state.last_nav_page = current_page_title

    # Render Header (Classification bar, branding, API status & search)
    render_header()

    # Render Sidebar Context (Active case switcher, active entity pill, diagnostics)
    render_sidebar_context()

    # Run active page
    pg.run()


if __name__ == "__main__":
    main()
