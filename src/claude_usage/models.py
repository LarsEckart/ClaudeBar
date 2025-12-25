"""Data models for Claude usage data."""

from dataclasses import dataclass


@dataclass
class UsageSnapshot:
    """Represents a snapshot of Claude CLI usage data."""
    
    session_percent: int | None = None
    weekly_percent: int | None = None
    opus_percent: int | None = None
    session_reset: str | None = None
    weekly_reset: str | None = None
    account_email: str | None = None
    account_tier: str | None = None  # e.g., "Pro", "Max"
    raw_text: str = ""
    error: str | None = None
