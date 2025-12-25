"""Tests for parser.py - parsing Claude CLI output."""

from claude_usage.parser import (
    strip_ansi,
    extract_section_percent,
    extract_section_reset,
    extract_email,
    extract_account_tier,
    parse_usage,
)
from claude_usage.models import UsageSnapshot


class TestStripAnsi:
    """Tests for strip_ansi function."""

    def test_removes_color_codes(self):
        text = "\x1b[31mred text\x1b[0m"
        assert strip_ansi(text) == "red text"

    def test_removes_multiple_codes(self):
        text = "\x1b[1m\x1b[32mbold green\x1b[0m normal"
        assert strip_ansi(text) == "bold green normal"

    def test_removes_cursor_codes(self):
        text = "\x1b[?2026l\x1b[?25lhello\x1b[?2026h"
        assert strip_ansi(text) == "hello"

    def test_removes_clear_line_codes(self):
        text = "\x1b[2K\x1b[1A\x1b[2Kcontent"
        assert strip_ansi(text) == "content"

    def test_preserves_plain_text(self):
        text = "plain text without codes"
        assert strip_ansi(text) == "plain text without codes"

    def test_handles_empty_string(self):
        assert strip_ansi("") == ""

    def test_handles_unicode(self):
        text = "█████ 50% used"
        assert strip_ansi(text) == "█████ 50% used"


class TestExtractSectionPercent:
    """Tests for extract_section_percent function."""

    def test_extracts_session_percent(self, sample_clean_text):
        result = extract_section_percent(sample_clean_text, "Current session")
        assert result == 74

    def test_extracts_weekly_percent(self, sample_clean_text):
        result = extract_section_percent(sample_clean_text, "Current week")
        assert result == 15

    def test_returns_none_for_missing_section(self, sample_clean_text):
        result = extract_section_percent(sample_clean_text, "Nonexistent section")
        assert result is None

    def test_extracts_single_digit_percent(self):
        text = "Current session\n█ 5% used"
        result = extract_section_percent(text, "Current session")
        assert result == 5

    def test_extracts_100_percent(self):
        text = "Current session\n██████████████████████████████████████████████████ 100% used"
        result = extract_section_percent(text, "Current session")
        assert result == 100

    def test_handles_remaining_keyword(self):
        text = "Current session\n█████ 30% remaining"
        result = extract_section_percent(text, "Current session")
        assert result == 30


class TestExtractSectionReset:
    """Tests for extract_section_reset function."""

    def test_extracts_session_reset(self, sample_clean_text):
        result = extract_section_reset(sample_clean_text, "Current session")
        assert result == "4pm (Europe/Tallinn)"

    def test_extracts_weekly_reset(self, sample_clean_text):
        result = extract_section_reset(sample_clean_text, "Current week")
        assert result == "Jan 1, 2026, 10:59am (Europe/Tallinn)"

    def test_returns_none_for_missing_section(self, sample_clean_text):
        result = extract_section_reset(sample_clean_text, "Nonexistent section")
        assert result is None

    def test_extracts_simple_date(self):
        text = "Current week\n███ 50% used\nResets Jan 5, 2026"
        result = extract_section_reset(text, "Current week")
        assert result == "Jan 5, 2026"


class TestExtractEmail:
    """Tests for extract_email function."""

    def test_extracts_email(self, sample_clean_text):
        result = extract_email(sample_clean_text)
        assert result == "lars.eckart@googlemail.com"

    def test_returns_none_when_no_email(self):
        text = "Some text without email"
        result = extract_email(text)
        assert result is None

    def test_handles_account_prefix(self):
        text = "Account: user@example.com"
        result = extract_email(text)
        assert result == "user@example.com"


class TestExtractAccountTier:
    """Tests for extract_account_tier function."""

    def test_extracts_pro_tier(self, sample_clean_text):
        result = extract_account_tier(sample_clean_text)
        assert result == "Pro"

    def test_extracts_max_tier(self, sample_raw_output_max):
        result = extract_account_tier(sample_raw_output_max)
        assert result == "Max"

    def test_returns_none_when_not_found(self):
        text = "Some text without tier info"
        result = extract_account_tier(text)
        assert result is None


class TestParseUsage:
    """Tests for parse_usage function - full parsing pipeline."""

    def test_parses_raw_output(self, sample_raw_output):
        result = parse_usage(sample_raw_output)

        assert isinstance(result, UsageSnapshot)
        # Percentages are converted from "used" to "remaining"
        assert result.session_percent == 26  # 100 - 74
        assert result.weekly_percent == 85  # 100 - 15
        assert result.account_tier == "Pro"
        assert result.account_email == "lars.eckart@googlemail.com"
        assert result.session_reset == "4pm (Europe/Tallinn)"
        assert result.error is None

    def test_parses_max_account_with_opus(self, sample_raw_output_max):
        result = parse_usage(sample_raw_output_max)

        assert result.session_percent == 74  # 100 - 26
        assert result.weekly_percent == 6  # 100 - 94
        assert result.opus_percent == 5  # 100 - 95
        assert result.account_tier == "Max"

    def test_handles_empty_input(self):
        result = parse_usage("")

        assert result.session_percent is None
        assert result.weekly_percent is None
        assert result.account_tier is None
        assert result.error is None  # Not an error, just no data

    def test_preserves_raw_text(self, sample_raw_output):
        result = parse_usage(sample_raw_output)
        assert result.raw_text == sample_raw_output

    def test_handles_partial_data(self):
        # Only session info, no weekly
        text = """
        Current session
        █████████████ 50% used
        Resets 4pm
        """
        result = parse_usage(text)

        assert result.session_percent == 50  # 100 - 50
        assert result.weekly_percent is None
