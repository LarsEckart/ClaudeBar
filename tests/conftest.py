"""Pytest configuration and fixtures."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests (may be slow, require Claude CLI)",
    )


# Sample raw output from Claude CLI (captured from real usage)
SAMPLE_RAW_OUTPUT = """
[?2026l[?25l[?2004h[?1004h[?2026h[2K[1A[2K[1A[2K[1A[2K[1A[2K[1A[2K[G
────────────────────────────────────────────────────────────────────────────────
> /usage

────────────────────────────────────────────────────────────────────────────────
  /usage           Show plan usage limits
[?2026l[?2026h[2K[1A[2K[1A[2K[1A[2K[1A[2K[1A[2K[1A[2K[1A[2K[1A[2K[1A[2K[G
> /usage
────────────────────────────────────────────────────────────────────────────────
 Settings:  Status   Config   Usage  (tab to cycle)

 Current session
 ██████████████████████████████████████████████████ 74% used
 Resets 4pm (Europe/Tallinn)

 Current week (all models)
 ███████▌                                           15% used
 Resets Jan 1, 2026, 10:59am (Europe/Tallinn)

 Extra usage
 Extra usage not enabled • /extra-usage to enable

 Esc to cancel
[?2026l
: 2.0.74
 Session ID: b2f8ef7e-a764-42e5-91e6-86ac1bc302db
 cwd: /home/lars/github/claudebar
 Login method: Claude Pro Account
 Organization: lars.eckart@googlemail.com's Organization
 Email: lars.eckart@googlemail.com

 Model: Default Sonnet 4.5 · Best for everyday tasks
 Esc to cancel
[?2026l
"""

SAMPLE_RAW_OUTPUT_MAX = """
> /usage
────────────────────────────────────────────────────────────────────────────────
 Settings:  Status   Config   Usage  (tab to cycle)

 Current session
 █████████████                                      26% used
 Resets 4pm (Europe/Tallinn)

 Current week (all models)
 ██████████████████████████████████████████████▌    94% used
 Resets Jan 5, 2026

 Opus
 ███████████████████████████████████████████████    95% used
 Resets Jan 5, 2026

 Login method: Claude Max Account
 Email: user@example.com
"""

SAMPLE_CLEAN_TEXT = """
> /usage
────────────────────────────────────────────────────────────────────────────────
 Settings:  Status   Config   Usage  (tab to cycle)

 Current session
 ██████████████████████████████████████████████████ 74% used
 Resets 4pm (Europe/Tallinn)

 Current week (all models)
 ███████▌                                           15% used
 Resets Jan 1, 2026, 10:59am (Europe/Tallinn)

 Login method: Claude Pro Account
 Email: lars.eckart@googlemail.com
"""


@pytest.fixture
def sample_raw_output():
    """Real raw output from Claude CLI with ANSI codes."""
    return SAMPLE_RAW_OUTPUT


@pytest.fixture
def sample_raw_output_max():
    """Sample output for Claude Max account with Opus usage."""
    return SAMPLE_RAW_OUTPUT_MAX


@pytest.fixture
def sample_clean_text():
    """Clean text without ANSI codes."""
    return SAMPLE_CLEAN_TEXT
