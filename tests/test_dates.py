"""Tests for date handling logic."""

import pytest

from shiftswap.dates import (
    add_days,
    date_range,
    days_in_month,
    diff_days,
    is_valid_date,
    normalize_date,
    parse_date,
    period_dates,
    week_bounds,
)


class TestParseDate:
    def test_valid_iso_date(self):
        assert parse_date("2026-01-01").isoformat() == "2026-01-01"

    def test_leap_year(self):
        assert parse_date("2024-02-29").isoformat() == "2024-02-29"

    def test_invalid_month(self):
        with pytest.raises(ValueError):
            parse_date("2026-13-01")

    def test_invalid_day(self):
        with pytest.raises(ValueError):
            parse_date("2026-02-30")

    def test_non_string(self):
        with pytest.raises(ValueError):
            parse_date(20260101)


class TestNormalizeDate:
    def test_canonical_form(self):
        assert normalize_date("2026-11-05") == "2026-11-05"

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            normalize_date("not-a-date")


class TestIsValidDate:
    def test_true_for_valid(self):
        assert is_valid_date("2026-10-31") is True

    def test_false_for_invalid(self):
        assert is_valid_date("2026-02-30") is False
        assert is_valid_date("garbage") is False


class TestDaysInMonth:
    def test_january(self):
        assert days_in_month(2026, 1) == 31

    def test_february_leap(self):
        assert days_in_month(2024, 2) == 29

    def test_february_non_leap(self):
        assert days_in_month(2026, 2) == 28

    def test_april(self):
        assert days_in_month(2026, 4) == 30


class TestAddDays:
    def test_forward(self):
        assert add_days("2026-01-01", 1) == "2026-01-02"

    def test_backward(self):
        assert add_days("2026-01-05", -2) == "2026-01-03"

    def test_month_rollover(self):
        assert add_days("2026-01-31", 1) == "2026-02-01"


class TestDiffDays:
    def test_simple(self):
        assert diff_days("2026-01-01", "2026-01-10") == 9

    def test_negative(self):
        assert diff_days("2026-01-10", "2026-01-01") == -9


class TestWeekBounds:
    def test_monday_reference(self):
        mon, sun = week_bounds("2026-01-05")  # Monday
        assert mon == "2026-01-05"
        assert sun == "2026-01-11"

    def test_wednesday_reference(self):
        mon, sun = week_bounds("2026-01-07")  # Wednesday
        assert mon == "2026-01-05"
        assert sun == "2026-01-11"


class TestDateRange:
    def test_inclusive(self):
        dates = list(date_range("2026-01-01", "2026-01-03"))
        assert dates == ["2026-01-01", "2026-01-02", "2026-01-03"]

    def test_start_after_end_raises(self):
        with pytest.raises(ValueError):
            list(date_range("2026-01-10", "2026-01-01"))


class TestPeriodDates:
    def test_day(self):
        assert period_dates("day", "2026-01-01") == ["2026-01-01"]

    def test_week(self):
        dates = period_dates("week", "2026-01-07")
        assert len(dates) == 7
        assert dates[0] == "2026-01-05"

    def test_month(self):
        dates = period_dates("month", "2026-02-15")
        assert len(dates) == 28
        assert dates[0] == "2026-02-01"
        assert dates[-1] == "2026-02-28"

    def test_unknown_period(self):
        with pytest.raises(ValueError):
            period_dates("year", "2026-01-01")