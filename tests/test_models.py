"""Tests for models.py - data models."""

from claude_usage.models import UsageSnapshot


class TestUsageSnapshot:
    """Tests for UsageSnapshot dataclass."""

    def test_default_values(self):
        snapshot = UsageSnapshot()

        assert snapshot.session_percent is None
        assert snapshot.weekly_percent is None
        assert snapshot.opus_percent is None
        assert snapshot.session_reset is None
        assert snapshot.weekly_reset is None
        assert snapshot.account_email is None
        assert snapshot.account_tier is None
        assert snapshot.raw_text == ""
        assert snapshot.error is None

    def test_can_set_all_fields(self):
        snapshot = UsageSnapshot(
            session_percent=50,
            weekly_percent=80,
            opus_percent=90,
            session_reset="4pm",
            weekly_reset="Jan 1",
            account_email="user@example.com",
            account_tier="Pro",
            raw_text="raw data here",
            error=None,
        )

        assert snapshot.session_percent == 50
        assert snapshot.weekly_percent == 80
        assert snapshot.opus_percent == 90
        assert snapshot.session_reset == "4pm"
        assert snapshot.weekly_reset == "Jan 1"
        assert snapshot.account_email == "user@example.com"
        assert snapshot.account_tier == "Pro"
        assert snapshot.raw_text == "raw data here"
        assert snapshot.error is None

    def test_error_snapshot(self):
        snapshot = UsageSnapshot(error="Something went wrong")

        assert snapshot.error == "Something went wrong"
        assert snapshot.session_percent is None

    def test_is_dataclass(self):
        """Verify it behaves like a dataclass."""
        from dataclasses import is_dataclass

        assert is_dataclass(UsageSnapshot)

    def test_equality(self):
        snapshot1 = UsageSnapshot(session_percent=50)
        snapshot2 = UsageSnapshot(session_percent=50)
        snapshot3 = UsageSnapshot(session_percent=60)

        assert snapshot1 == snapshot2
        assert snapshot1 != snapshot3
