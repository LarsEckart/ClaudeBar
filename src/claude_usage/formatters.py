"""Format UsageSnapshot for various outputs."""

import re

from .models import UsageSnapshot


def _strip_timezone(reset_time: str) -> str:
    """Strip timezone info like '(Europe/Tallinn)' from reset time."""
    return re.sub(r"\s*\([^)]+\)\s*$", "", reset_time).strip()


def _convert_to_24h(time_str: str) -> str:
    """Convert 12h time format to 24h format (e.g., '4pm' -> '16:00')."""
    # Match patterns like "4pm", "11:30am", "4:59pm"
    pattern = r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b"

    def replace_time(match: re.Match) -> str:
        hour = int(match.group(1))
        minutes = match.group(2) or "00"
        period = match.group(3).lower()

        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0

        return f"{hour:02d}:{minutes}"

    return re.sub(pattern, replace_time, time_str, flags=re.IGNORECASE)


def get_css_class(percent: int | None) -> str:
    """
    Get CSS class based on usage percentage.

    Args:
        percent: Usage percentage (higher = more remaining)

    Returns:
        CSS class name: "good", "warning", "critical", or "unknown"
    """
    if percent is None:
        return "unknown"
    if percent > 50:
        return "good"
    if percent >= 20:
        return "warning"
    return "critical"


# Colors for Pango markup in tooltip
_COLORS = {
    "good": "#a6e3a1",      # green
    "warning": "#f9e2af",   # yellow
    "critical": "#f38ba8",  # red
    "unknown": "#6c7086",   # gray
}


def _colored_percent(percent: int) -> str:
    """Return percentage with Pango color markup based on level."""
    css_class = get_css_class(percent)
    color = _COLORS.get(css_class, _COLORS["unknown"])
    return f'<span foreground="{color}">{percent:3d}%</span>'


def format_waybar(snapshot: UsageSnapshot) -> dict:
    """
    Format snapshot for Waybar custom module.

    Returns:
        Dict with keys: text, tooltip, percentage, class
    """
    if snapshot.error:
        return {
            "text": "⚠",
            "tooltip": f"Error: {snapshot.error}",
            "percentage": 0,
            "class": "error",
        }

    # Use session percent as primary display, fall back to weekly
    primary_percent = (
        snapshot.session_percent
        if snapshot.session_percent is not None
        else snapshot.weekly_percent
    )

    if primary_percent is None:
        return {
            "text": "?",
            "tooltip": "Could not parse usage data",
            "percentage": 0,
            "class": "unknown",
        }

    # Build tooltip showing account tier, session and weekly
    tooltip_parts = []
    if snapshot.account_tier:
        tooltip_parts.append(f"Claude {snapshot.account_tier}")
    if snapshot.session_percent is not None:
        reset_info = (
            f" (resets {_convert_to_24h(_strip_timezone(snapshot.session_reset))})"
            if snapshot.session_reset
            else ""
        )
        tooltip_parts.append(f"Session: {_colored_percent(snapshot.session_percent)}{reset_info}")
    if snapshot.weekly_percent is not None:
        reset_info = (
            f" (resets {_convert_to_24h(_strip_timezone(snapshot.weekly_reset))})"
            if snapshot.weekly_reset
            else ""
        )
        tooltip_parts.append(f"Weekly:  {_colored_percent(snapshot.weekly_percent)}{reset_info}")

    tooltip = "\n".join(tooltip_parts) if tooltip_parts else "Claude Usage"

    return {
        "text": f"{primary_percent}%",
        "tooltip": tooltip,
        "percentage": primary_percent,
        "class": get_css_class(primary_percent),
    }


def format_plain(snapshot: UsageSnapshot) -> str:
    """Format snapshot as plain text."""
    if snapshot.error:
        return f"Error: {snapshot.error}"

    lines = []
    if snapshot.account_tier:
        lines.append(f"Tier: Claude {snapshot.account_tier}")
    if snapshot.account_email:
        lines.append(f"Account: {snapshot.account_email}")
    if snapshot.weekly_percent is not None:
        lines.append(f"Weekly: {snapshot.weekly_percent}%")
    if snapshot.session_percent is not None:
        lines.append(f"Session: {snapshot.session_percent}%")
    if snapshot.opus_percent is not None:
        lines.append(f"Opus: {snapshot.opus_percent}%")

    return "\n".join(lines) if lines else "No usage data available"


def format_json(snapshot: UsageSnapshot) -> dict:
    """Format snapshot as full JSON data."""
    return {
        "session_percent": snapshot.session_percent,
        "weekly_percent": snapshot.weekly_percent,
        "opus_percent": snapshot.opus_percent,
        "session_reset": snapshot.session_reset,
        "weekly_reset": snapshot.weekly_reset,
        "account_email": snapshot.account_email,
        "account_tier": snapshot.account_tier,
        "error": snapshot.error,
    }
