import streamlit as st
from pathlib import Path
from components.sidebar import render_sidebar


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ARIA Intelligence",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# LOAD CUSTOM CSS
# --------------------------------------------------

css_path = Path(__file__).parent / "assets" / "style.css"

with open(css_path) as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

def initialize_session_state():

    defaults = {
        "current_case": None,
        "selected_node": None,
        "selected_edge": None,
        "selected_event": None,
        "active_filters": {},
        "highlighted_nodes": [],
        "highlighted_edges": [],
        "aria_messages": []
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_session_state()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

page = render_sidebar()

# --------------------------------------------------
# MAIN CONTENT
# --------------------------------------------------

if page == "Investigation Workspace":

    st.title("ARIA INTELLIGENCE")
    st.subheader("Investigation Workspace")

    st.divider()

    investigation = st.selectbox(
        "Select Investigation",
        [
            "Select an investigation",
            "Investigation 001",
            "Investigation 002"
        ]
    )

    if st.button("Open Investigation", type="primary"):

        if investigation == "Select an investigation":
            st.warning("Please select an investigation.")

        else:
            st.session_state.current_case = investigation

            st.success(
                f"{investigation} opened successfully."
            )

            st.write(
                "Current investigation:",
                st.session_state.current_case
            )


elif page == "Investigations":

    st.title("Investigations")
    st.info("Investigation management will be implemented here.")


elif page == "Entities":

    st.title("Entities")
    st.info("Entity search and profiles will be implemented here.")


elif page == "Analytics":

    st.title("Analytics")
    st.info("Investigation analytics will be implemented here.")