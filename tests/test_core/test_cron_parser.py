import pytest
from datetime import datetime, timezone, timedelta

from hermes_core.scheduler.cron_parser import CronParser


class TestCronParser:
    def test_parse_standard_expression(self):
        result = CronParser.parse("0 * * * *")
        assert 0 in result["minute"]
        assert len(result["hour"]) == 24

    def test_parse_every_five_minutes(self):
        result = CronParser.parse("*/5 * * * *")
        assert 0 in result["minute"]
        assert 5 in result["minute"]
        assert 55 in result["minute"]

    def test_parse_specific_hour(self):
        result = CronParser.parse("0 9 * * *")
        assert 9 in result["hour"]

    def test_parse_range(self):
        result = CronParser.parse("0 9-17 * * *")
        for h in range(9, 18):
            assert h in result["hour"]

    def test_parse_list(self):
        result = CronParser.parse("0 9,12,18 * * *")
        assert 9 in result["hour"]
        assert 12 in result["hour"]
        assert 18 in result["hour"]

    def test_parse_invalid_field_count(self):
        with pytest.raises(ValueError):
            CronParser.parse("0 * * *")

    def test_parse_invalid_value(self):
        with pytest.raises(ValueError):
            CronParser.parse("60 * * * *")

    def test_next_run_time_basic(self):
        now = datetime.now(timezone.utc)
        next_run = CronParser.next_run_time("*/5 * * * *", after=now)
        assert next_run > now
        assert next_run.minute % 5 == 0

    def test_next_run_time_hourly(self):
        now = datetime.now(timezone.utc)
        next_run = CronParser.next_run_time("0 * * * *", after=now)
        assert next_run > now
        assert next_run.minute == 0

    def test_next_run_time_daily(self):
        now = datetime.now(timezone.utc)
        next_run = CronParser.next_run_time("0 9 * * *", after=now)
        assert next_run > now
        assert next_run.hour == 9
        assert next_run.minute == 0
