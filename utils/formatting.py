"""
KRONOS HTML & Intelligence Formatting Utilities
Provides consistent, professional badges, severity indicators, and score formatters.
"""

from typing import Optional


def render_risk_badge(risk_level: Optional[str]) -> str:
    """Render a styled HTML badge for entity/case risk levels."""
    risk = (risk_level or "LOW").upper()
    if risk in ("CRITICAL", "CRIT"):
        return '<span class="badge badge-critical">CRITICAL RISK</span>'
    elif risk in ("HIGH", "HIGH RISK"):
        return '<span class="badge badge-high">HIGH RISK</span>'
    elif risk in ("MEDIUM", "MED", "MODERATE"):
        return '<span class="badge badge-medium">MED RISK</span>'
    elif risk in ("LOW", "LOW RISK"):
        return '<span class="badge badge-low">LOW RISK</span>'
    return f'<span class="badge badge-neutral">{risk}</span>'


def render_severity_badge(severity: Optional[str]) -> str:
    """Render a styled HTML badge for suspicious pattern severity."""
    sev = (severity or "MEDIUM").upper()
    if sev == "CRITICAL":
        return '<span class="badge badge-critical">CRITICAL</span>'
    elif sev == "HIGH":
        return '<span class="badge badge-high">HIGH SEVERITY</span>'
    elif sev == "MEDIUM":
        return '<span class="badge badge-medium">MED SEVERITY</span>'
    elif sev == "LOW":
        return '<span class="badge badge-low">LOW SEVERITY</span>'
    return f'<span class="badge badge-neutral">{sev}</span>'


def render_confidence_badge(confidence: Optional[float]) -> str:
    """Render a formatted confidence percentage pill."""
    if confidence is None:
        return '<span class="badge badge-neutral">CONF: N/A</span>'
    pct = round(confidence * 100) if confidence <= 1.0 else round(confidence)
    if pct >= 85:
        color_class = "badge-low"
    elif pct >= 65:
        color_class = "badge-medium"
    else:
        color_class = "badge-high"
    return f'<span class="badge {color_class}">CONF: {pct}%</span>'


def render_type_badge(entity_type: Optional[str]) -> str:
    """Render an entity type classification tag."""
    etype = (entity_type or "ENTITY").upper()
    return f'<span class="badge badge-cyan">{etype}</span>'


def render_id_pill(item_id: Optional[str]) -> str:
    """Render a monospace item ID pill."""
    cid = item_id or "N/A"
    return f'<span class="id-pill">{cid}</span>'


def format_timestamp(ts: Optional[str]) -> str:
    """Format ISO timestamp or raw string to analyst-readable date."""
    if not ts:
        return "Not Recorded"
    if "T" in ts:
        try:
            date_part, time_part = ts.split("T")
            time_clean = time_part.split(".")[0].split("+")[0].split("Z")[0]
            return f"{date_part} {time_clean} UTC"
        except Exception:
            return ts
    return ts
