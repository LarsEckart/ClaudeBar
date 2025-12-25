"""Parse raw Claude CLI output into structured data."""

import re
from .models import UsageSnapshot


# ANSI escape sequence pattern - matches various escape sequences
ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\].*?\x07|\x1b\[\?[0-9]+[hl]')

# Pattern to match email addresses
EMAIL_PATTERN = re.compile(r'(?:Account|Email|Logged in as)[:\s]+(\S+@\S+)', re.IGNORECASE)

# Pattern to match account tier from "Login method: Claude Pro Account" or "Claude Max Account"
TIER_PATTERN = re.compile(r'Login method:\s*Claude\s+(\w+)\s+Account', re.IGNORECASE)


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    return ANSI_PATTERN.sub('', text)


def extract_section_percent(text: str, section_header: str) -> int | None:
    """
    Extract a percentage value from a section.
    
    Claude CLI format:
      Current session
      █████████████                                      26% used
      
    Args:
        text: Text to search
        section_header: Section header (e.g., "Current session", "Current week")
        
    Returns:
        Percentage as integer, or None if not found
    """
    # Find the section and extract the percentage on following lines
    pattern = re.compile(
        rf'{section_header}[^\n]*\n[^%]*?(\d{{1,3}})\s*%\s*(?:used|remaining|left)?',
        re.IGNORECASE | re.MULTILINE
    )
    match = pattern.search(text)
    if match:
        return int(match.group(1))
    return None


def extract_section_reset(text: str, section_header: str) -> str | None:
    """
    Extract reset time from a section.
    
    Claude CLI format:
      Current session
      █████████████                                      26% used
      Resets 4pm (Europe/Tallinn)
      
    Args:
        text: Text to search  
        section_header: Section header (e.g., "Current session", "Current week")
        
    Returns:
        Reset time string, or None if not found
    """
    # Find section, then look for "Resets" line within next few lines
    pattern = re.compile(
        rf'{section_header}[^\n]*\n(?:[^\n]*\n){{0,3}}[^\n]*Resets?\s+([^\n]+)',
        re.IGNORECASE | re.MULTILINE
    )
    match = pattern.search(text)
    if match:
        reset_time = match.group(1).strip()
        # Clean up any trailing parentheses timezone info if desired
        return reset_time
    return None


def extract_email(text: str) -> str | None:
    """Extract email address from usage text."""
    match = EMAIL_PATTERN.search(text)
    if match:
        return match.group(1)
    return None


def extract_account_tier(text: str) -> str | None:
    """Extract account tier (Pro, Max, etc.) from status text."""
    match = TIER_PATTERN.search(text)
    if match:
        return match.group(1)
    return None


def parse_usage(raw_text: str) -> UsageSnapshot:
    """
    Parse raw CLI output into a UsageSnapshot.
    
    Args:
        raw_text: Raw output from Claude CLI
        
    Returns:
        Parsed UsageSnapshot
    """
    # Strip ANSI codes for easier parsing
    clean_text = strip_ansi(raw_text)
    
    # Extract session data (labeled "Current session")
    session_percent = extract_section_percent(clean_text, "Current session")
    session_reset = extract_section_reset(clean_text, "Current session")
    
    # Extract weekly data (labeled "Current week")
    weekly_percent = extract_section_percent(clean_text, "Current week")
    weekly_reset = extract_section_reset(clean_text, "Current week")
    
    # Extract Opus data if present
    opus_percent = extract_section_percent(clean_text, "Opus")
    
    # Convert "used" to "remaining" - the usage shows X% used, we want remaining
    if session_percent is not None:
        session_percent = 100 - session_percent
    if weekly_percent is not None:
        weekly_percent = 100 - weekly_percent
    if opus_percent is not None:
        opus_percent = 100 - opus_percent
    
    return UsageSnapshot(
        session_percent=session_percent,
        weekly_percent=weekly_percent,
        opus_percent=opus_percent,
        session_reset=session_reset,
        weekly_reset=weekly_reset,
        account_email=extract_email(clean_text),
        account_tier=extract_account_tier(clean_text),
        raw_text=raw_text,
    )
