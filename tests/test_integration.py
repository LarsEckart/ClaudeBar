"""Integration tests - require Claude CLI to be installed."""

import json
import shutil
import subprocess

import pytest

from claude_usage.probe import fetch_usage_raw
from claude_usage.parser import parse_usage
from claude_usage.formatters import format_waybar


# Skip all tests in this module if claude is not installed
pytestmark = pytest.mark.integration


def claude_installed() -> bool:
    """Check if Claude CLI is installed."""
    return shutil.which("claude") is not None


@pytest.fixture(scope="module")
def require_claude():
    """Skip test if Claude CLI is not installed."""
    if not claude_installed():
        pytest.skip("Claude CLI not installed")


class TestProbe:
    """Integration tests for probe.py."""

    def test_fetch_usage_raw_returns_string(self, require_claude):
        """fetch_usage_raw should return a non-empty string."""
        result = fetch_usage_raw(timeout=30)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_fetch_usage_raw_contains_expected_patterns(self, require_claude):
        """Raw output should contain usage-related keywords."""
        result = fetch_usage_raw(timeout=30)

        # Should contain at least some of these patterns
        patterns = ["session", "week", "%", "used", "Resets"]
        found = sum(1 for p in patterns if p.lower() in result.lower())

        assert found >= 2, (
            f"Expected usage patterns not found in output: {result[:500]}"
        )

    def test_fetch_usage_raw_raises_on_missing_binary(self, monkeypatch):
        """Should raise FileNotFoundError if claude binary not found."""
        monkeypatch.setattr(shutil, "which", lambda x: None)

        with pytest.raises(FileNotFoundError, match="Claude CLI not found"):
            fetch_usage_raw()


class TestFullPipeline:
    """End-to-end integration tests."""

    def test_full_pipeline(self, require_claude):
        """Test complete flow: fetch -> parse -> format."""
        # Fetch raw data
        raw = fetch_usage_raw(timeout=30)
        assert raw, "Raw output should not be empty"

        # Parse it
        snapshot = parse_usage(raw)
        assert snapshot.error is None, (
            f"Parsing should not produce error: {snapshot.error}"
        )

        # At least one of these should be present
        assert (
            snapshot.session_percent is not None or snapshot.weekly_percent is not None
        ), "Should have session or weekly percent"

        # Format for waybar
        waybar = format_waybar(snapshot)

        assert "text" in waybar
        assert "tooltip" in waybar
        assert "percentage" in waybar
        assert "class" in waybar
        assert waybar["class"] in ["good", "warning", "critical", "unknown"]

    def test_parsed_percentages_are_valid(self, require_claude):
        """Parsed percentages should be in valid range."""
        raw = fetch_usage_raw(timeout=30)
        snapshot = parse_usage(raw)

        for name, value in [
            ("session", snapshot.session_percent),
            ("weekly", snapshot.weekly_percent),
            ("opus", snapshot.opus_percent),
        ]:
            if value is not None:
                assert 0 <= value <= 100, f"{name} percent {value} out of range"


class TestCliExecution:
    """Test the CLI as a subprocess."""

    def test_cli_waybar_format(self, require_claude):
        """claude-usage should output valid JSON for waybar."""
        result = subprocess.run(
            ["claude-usage"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Should be valid JSON
        output = json.loads(result.stdout)
        assert "text" in output
        assert "tooltip" in output
        assert "class" in output

    def test_cli_plain_format(self, require_claude):
        """claude-usage --format plain should output readable text."""
        result = subprocess.run(
            ["claude-usage", "--format", "plain"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert len(result.stdout) > 0

        # Should contain some usage info or error message
        output = result.stdout.lower()
        assert any(
            word in output
            for word in ["session", "weekly", "tier", "error", "no usage"]
        )

    def test_cli_json_format(self, require_claude):
        """claude-usage --format json should output full JSON data."""
        result = subprocess.run(
            ["claude-usage", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        output = json.loads(result.stdout)
        # Should have all expected keys
        expected_keys = [
            "session_percent",
            "weekly_percent",
            "opus_percent",
            "session_reset",
            "weekly_reset",
            "account_email",
            "account_tier",
            "error",
        ]
        for key in expected_keys:
            assert key in output, f"Missing key: {key}"

    def test_cli_dump_raw(self, require_claude):
        """claude-usage --dump-raw should output raw CLI text."""
        result = subprocess.run(
            ["claude-usage", "--dump-raw"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}"
        assert len(result.stdout) > 0

        # Raw output should contain ANSI codes or usage patterns
        output = result.stdout
        has_ansi = "\x1b[" in output or "\x1b]" in output
        has_usage = "%" in output or "session" in output.lower()
        assert has_ansi or has_usage, "Raw output seems empty or malformed"

    def test_cli_version(self):
        """claude-usage --version should show version."""
        result = subprocess.run(
            ["claude-usage", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "claude-usage" in result.stdout
