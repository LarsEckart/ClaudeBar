"""Tests for formatters.py - output formatting."""

from claude_usage.formatters import (
    get_css_class,
    format_waybar,
    format_plain,
    format_json,
)
from claude_usage.models import UsageSnapshot


class TestGetCssClass:
    """Tests for get_css_class function."""

    def test_none_returns_unknown(self):
        assert get_css_class(None) == "unknown"

    def test_above_50_returns_good(self):
        assert get_css_class(51) == "good"
        assert get_css_class(75) == "good"
        assert get_css_class(100) == "good"

    def test_20_to_50_returns_warning(self):
        assert get_css_class(20) == "warning"
        assert get_css_class(35) == "warning"
        assert get_css_class(50) == "warning"

    def test_below_20_returns_critical(self):
        assert get_css_class(0) == "critical"
        assert get_css_class(10) == "critical"
        assert get_css_class(19) == "critical"


class TestFormatWaybar:
    """Tests for format_waybar function."""

    def test_normal_snapshot(self):
        snapshot = UsageSnapshot(
            session_percent=45,
            weekly_percent=85,
            session_reset="4pm",
            weekly_reset="Jan 1",
            account_tier="Pro",
        )
        result = format_waybar(snapshot)

        assert result["text"] == "45%"
        assert result["percentage"] == 45
        assert result["class"] == "warning"
        assert "Session: 45%" in result["tooltip"]
        assert "Weekly: 85%" in result["tooltip"]
        assert "Claude Pro" in result["tooltip"]

    def test_error_snapshot(self):
        snapshot = UsageSnapshot(error="Claude CLI not found")
        result = format_waybar(snapshot)

        assert result["text"] == "⚠"
        assert result["class"] == "error"
        assert "Error: Claude CLI not found" in result["tooltip"]
        assert result["percentage"] == 0

    def test_no_data_snapshot(self):
        snapshot = UsageSnapshot()
        result = format_waybar(snapshot)

        assert result["text"] == "?"
        assert result["class"] == "unknown"
        assert "Could not parse" in result["tooltip"]

    def test_session_percent_preferred_over_weekly(self):
        snapshot = UsageSnapshot(session_percent=30, weekly_percent=80)
        result = format_waybar(snapshot)

        assert result["text"] == "30%"
        assert result["percentage"] == 30

    def test_falls_back_to_weekly_if_no_session(self):
        snapshot = UsageSnapshot(weekly_percent=75)
        result = format_waybar(snapshot)

        assert result["text"] == "75%"
        assert result["percentage"] == 75

    def test_includes_reset_times_in_tooltip(self):
        snapshot = UsageSnapshot(
            session_percent=50,
            weekly_percent=80,
            session_reset="4pm (Europe/Tallinn)",
            weekly_reset="Jan 1",
        )
        result = format_waybar(snapshot)

        assert "(resets 4pm (Europe/Tallinn))" in result["tooltip"]
        assert "(resets Jan 1)" in result["tooltip"]

    def test_good_class_for_high_percentage(self):
        snapshot = UsageSnapshot(session_percent=75)
        result = format_waybar(snapshot)
        assert result["class"] == "good"

    def test_critical_class_for_low_percentage(self):
        snapshot = UsageSnapshot(session_percent=10)
        result = format_waybar(snapshot)
        assert result["class"] == "critical"


class TestFormatPlain:
    """Tests for format_plain function."""

    def test_full_snapshot(self):
        snapshot = UsageSnapshot(
            session_percent=53,
            weekly_percent=85,
            opus_percent=90,
            account_tier="Max",
            account_email="user@example.com",
        )
        result = format_plain(snapshot)

        assert "Tier: Claude Max" in result
        assert "Account: user@example.com" in result
        assert "Session: 53%" in result
        assert "Weekly: 85%" in result
        assert "Opus: 90%" in result

    def test_error_snapshot(self):
        snapshot = UsageSnapshot(error="Something went wrong")
        result = format_plain(snapshot)

        assert "Error: Something went wrong" in result

    def test_empty_snapshot(self):
        snapshot = UsageSnapshot()
        result = format_plain(snapshot)

        assert result == "No usage data available"

    def test_partial_snapshot(self):
        snapshot = UsageSnapshot(session_percent=50)
        result = format_plain(snapshot)

        assert "Session: 50%" in result
        assert "Weekly" not in result


class TestFormatJson:
    """Tests for format_json function."""

    def test_full_snapshot(self):
        snapshot = UsageSnapshot(
            session_percent=53,
            weekly_percent=85,
            opus_percent=90,
            session_reset="4pm",
            weekly_reset="Jan 1",
            account_email="user@example.com",
            account_tier="Pro",
        )
        result = format_json(snapshot)

        assert result["session_percent"] == 53
        assert result["weekly_percent"] == 85
        assert result["opus_percent"] == 90
        assert result["session_reset"] == "4pm"
        assert result["weekly_reset"] == "Jan 1"
        assert result["account_email"] == "user@example.com"
        assert result["account_tier"] == "Pro"
        assert result["error"] is None

    def test_error_snapshot(self):
        snapshot = UsageSnapshot(error="Test error")
        result = format_json(snapshot)

        assert result["error"] == "Test error"
        assert result["session_percent"] is None

    def test_empty_snapshot(self):
        snapshot = UsageSnapshot()
        result = format_json(snapshot)

        assert all(
            result[key] is None
            for key in ["session_percent", "weekly_percent", "opus_percent", "error"]
        )
