"""
KRONOS Sidebar Context Component
Renders case context switcher, active entity indicators, and system diagnostics in the sidebar.
Navigation is handled natively by Streamlit st.navigation at the top of the sidebar.
"""

from typing import Optional
import streamlit as st
from config import BACKEND_URL


def render_sidebar_context() -> None:
    """Renders contextual panels in the sidebar below the native top navigation."""
    with st.sidebar:
        st.markdown('<hr style="border: 0; border-top: 1px solid #1E293B; margin: 1rem 0;" />', unsafe_allow_html=True)

        st.markdown(
            """
            <div style="padding-bottom: 0.5rem; margin-bottom: 0.75rem;">
                <div style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC; letter-spacing: 0.06em;">
                    KRONOS <span style="font-size: 0.72rem; color: #38BDF8;">// OPS</span>
                </div>
                <div style="font-size: 0.7rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.04em;">
                    Criminal Intelligence Console
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Active Case Context Panel
        active_case = st.session_state.get("selected_case_id")
        st.markdown(
            """
            <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #94A3B8; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
                CASE CONTEXT
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if active_case:
            st.markdown(
                f"""
                <div style="background: #121721; border: 1px solid #232B3B; border-radius: 4px; padding: 0.6rem 0.8rem; margin-bottom: 0.5rem;">
                    <div style="font-family: monospace; font-size: 0.78rem; color: #38BDF8; font-weight: bold;">
                        {active_case}
                    </div>
                    <div style="font-size: 0.7rem; color: #94A3B8; margin-top: 0.2rem;">
                        Scoped Intelligence Active
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button("Clear Case Context", key="sidebar_clear_case_btn", use_container_width=True):
                st.session_state.selected_case_id = None
                st.rerun()
        else:
            st.markdown(
                """
                <div style="font-size: 0.75rem; color: #64748B; font-style: italic; margin-bottom: 0.5rem;">
                    Global Intelligence Scope
                </div>
                """,
                unsafe_allow_html=True
            )

        # Active Entity Quick-Access
        selected_entity = st.session_state.get("selected_entity_id")
        if selected_entity:
            st.markdown('<hr style="border: 0; border-top: 1px solid #1E293B; margin: 0.75rem 0;" />', unsafe_allow_html=True)
            st.markdown(
                """
                <div style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #94A3B8; letter-spacing: 0.05em; margin-bottom: 0.4rem;">
                    ACTIVE ENTITY
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown(
                f"""
                <div style="background: #121721; border: 1px solid #232B3B; border-radius: 4px; padding: 0.5rem 0.8rem; margin-bottom: 0.5rem;">
                    <div style="font-family: monospace; font-size: 0.75rem; color: #22D3EE;">
                        {selected_entity}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # System Diagnostics Footer
        st.markdown(
            f"""
            <div style="font-size: 0.68rem; color: #475569; margin-top: 1.5rem; font-family: monospace; line-height: 1.4;">
                SYSTEM: KRONOS INTELLIGENCE<br/>
                TARGET API: {BACKEND_URL}
            </div>
            """,
            unsafe_allow_html=True
        )


# Backward compatibility alias
render_sidebar = render_sidebar_context
