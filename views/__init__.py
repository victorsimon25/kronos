"""
KRONOS Pages Package
"""

from .dashboard import render_dashboard_page
from .entity_search import render_entity_search_page
from .entity_profile import render_entity_profile_page
from .investigations import render_investigations_page
from .suspicious_patterns import render_suspicious_patterns_page
from .network_summary import render_network_summary_page
from .aria_copilot import render_aria_copilot_page

__all__ = [
    "render_dashboard_page",
    "render_entity_search_page",
    "render_entity_profile_page",
    "render_investigations_page",
    "render_suspicious_patterns_page",
    "render_network_summary_page",
    "render_aria_copilot_page",
]
