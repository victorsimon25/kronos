import streamlit as st


def render_sidebar():

    with st.sidebar:

        st.title("ARIA")
        st.caption("Intelligence Investigation Platform")

        st.divider()

        page = st.radio(
            "Navigation",
            [
                "Investigation Workspace",
                "Investigations",
                "Entities",
                "Analytics"
            ],
            label_visibility="collapsed"
        )

        st.divider()

        if st.session_state.current_case:
            st.caption("CURRENT INVESTIGATION")
            st.write(st.session_state.current_case)
        else:
            st.caption("No investigation selected")

        st.divider()

        st.caption("ARIA Intelligence")

    return page