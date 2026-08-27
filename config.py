"""
KRONOS // Criminal Network Intelligence Platform
Frontend Dashboard Configuration Module
"""

import os
from typing import Dict, Any

# Application Metadata
APP_NAME = "KRONOS"
APP_SUBTITLE = "AI-Powered Criminal Network Analysis System"
APP_VERSION = "v1.0.0-PROD"
SECURITY_CLASSIFICATION = "LAW ENFORCEMENT SENSITIVE // REL TO LE ONLY"

# API & Backend Configuration
# Default to localhost:8000, customizable via BACKEND_URL environment variable
DEFAULT_BACKEND_URL = "http://localhost:8000"
BACKEND_URL = os.getenv("BACKEND_URL", DEFAULT_BACKEND_URL).rstrip("/")
API_TIMEOUT_SECONDS = float(os.getenv("API_TIMEOUT_SECONDS", "8.0"))
API_RETRY_COUNT = int(os.getenv("API_RETRY_COUNT", "2"))

# Color Palette — matches design.md tokens exactly
PALETTE: Dict[str, str] = {
    "bg_main": "#0A0D12",
    "bg_surface": "#111827",
    "bg_surface_elevated": "#1A2130",
    "border_subtle": "#1F2937",
    "border_active": "#06B6D4",
    "text_primary": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",

    "risk_critical": "#EF4444",
    "risk_high": "#F97316",
    "risk_medium": "#F59E0B",
    "risk_low": "#10B981",

    "accent_cyan": "#06B6D4",
    "accent_blue": "#3B82F6",
}

# Standard Navigation Pages
PAGE_DASHBOARD = "Dashboard"
PAGE_ENTITY_SEARCH = "Search Entities"
PAGE_ENTITY_PROFILE = "Entity Profile"
PAGE_INVESTIGATIONS = "Investigations"
PAGE_SUSPICIOUS_PATTERNS = "Suspicious Patterns"
PAGE_NETWORK_SUMMARY = "Network Summary"
PAGE_ARIA_COPILOT = "ARIA Copilot"

NAV_PAGES = [
    PAGE_DASHBOARD,
    PAGE_ENTITY_SEARCH,
    PAGE_ENTITY_PROFILE,
    PAGE_INVESTIGATIONS,
    PAGE_SUSPICIOUS_PATTERNS,
    PAGE_NETWORK_SUMMARY,
    PAGE_ARIA_COPILOT,
]

# Entity Types
ENTITY_TYPES = [
    "Person",
    "Phone",
    "Vehicle",
    "Location",
    "Organization",
    "Event",
]

# Risk Levels
RISK_LEVELS = ["HIGH", "MEDIUM", "LOW"]
SEVERITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
