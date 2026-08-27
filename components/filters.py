"""
KRONOS Reusable Filter System Component
Modular UI controls for entity types, risk levels, confidence scores, and case filtering.
"""

from typing import Dict, Any, List, Optional
import streamlit as st
from config import ENTITY_TYPES, RISK_LEVELS


def render_entity_filter_bar(key_prefix: str = "entity_filter") -> Dict[str, Any]:
    """
    Renders a compact horizontal filter bar for Entity Search.
    Returns the selected filter dictionary to be passed to backend API.
    """
    col1, col2, col3, col4 = st.columns([2.5, 2.0, 2.5, 1.5])
    
    with col1:
        entity_types = ["All"] + ENTITY_TYPES
        selected_type = st.selectbox(
            "Entity Type",
            options=entity_types,
            index=0,
            key=f"{key_prefix}_type"
        )

    with col2:
        risk_options = ["All"] + RISK_LEVELS
        selected_risk = st.selectbox(
            "Risk Level",
            options=risk_options,
            index=0,
            key=f"{key_prefix}_risk"
        )

    with col3:
        min_conf = st.slider(
            "Min Confidence Score",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
            format="%.2f",
            key=f"{key_prefix}_conf"
        )

    with col4:
        st.write("")  # Spacing
        st.write("")
        apply_btn = st.button("Apply Filters", key=f"{key_prefix}_apply_btn", use_container_width=True)

    return {
        "entity_type": selected_type,
        "risk_level": selected_risk,
        "min_confidence": min_conf,
        "applied": apply_btn
    }


def render_pattern_filter_bar(key_prefix: str = "pattern_filter") -> Dict[str, Any]:
    """
    Renders filter controls for Suspicious Patterns page.
    """
    col1, col2, col3 = st.columns([2.5, 2.5, 3.0])
    
    with col1:
        severity_opts = ["All", "HIGH", "MEDIUM", "LOW", "CRITICAL"]
        selected_severity = st.selectbox(
            "Severity",
            options=severity_opts,
            index=0,
            key=f"{key_prefix}_severity"
        )

    with col2:
        min_conf = st.slider(
            "Min Confidence",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
            format="%.2f",
            key=f"{key_prefix}_conf"
        )

    with col3:
        query = st.text_input(
            "Filter by keyword / pattern type",
            placeholder="e.g., Burner Phone, Shell Org...",
            key=f"{key_prefix}_query"
        )

    return {
        "severity": selected_severity,
        "min_confidence": min_conf,
        "query": query.strip() if query else None
    }
