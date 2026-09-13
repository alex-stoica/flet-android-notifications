"""Keep calendar timezones across the Python-to-Dart scheduling boundary."""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "flet_android_notifications/src"))
from flet_android_notifications import FletAndroidNotifications


def schedule_arguments(scheduled_time, **options):
    with patch.object(FletAndroidNotifications, "_invoke_method", new_callable=AsyncMock, return_value="ok") as invoke:
        asyncio.run(FletAndroidNotifications().schedule_notification(
            8, "Reminder", "Body", scheduled_time, **options,
        ))
    return invoke.call_args.kwargs["arguments"]


@pytest.mark.parametrize("components", [
    "time", "day_of_week_and_time", "day_of_month_and_time", "date_and_time",
])
@pytest.mark.parametrize("local,utc", [
    ("2026-10-24T09:00:00", "2026-10-24T06:00:00"),
    ("2026-10-25T09:00:00", "2026-10-25T07:00:00"),
    ("2027-03-27T09:00:00", "2027-03-27T07:00:00"),
    ("2027-03-28T09:00:00", "2027-03-28T06:00:00"),
])
def test_named_zone_survives_both_dst_transitions(components, local, utc):
    date = datetime.fromisoformat(local).replace(tzinfo=ZoneInfo("Europe/Bucharest"))
    args = schedule_arguments(date, match_date_time_components=components)
    assert args["time_zone"] == "Europe/Bucharest"
    assert args["scheduled_epoch_ms"] == int(datetime.fromisoformat(utc).replace(tzinfo=timezone.utc).timestamp() * 1000)
    assert args["match_date_time_components"] == components


def test_explicit_zone_interprets_naive_datetime_without_host_timezone():
    args = schedule_arguments(datetime(2026, 10, 24, 9), time_zone="Europe/Bucharest", match_date_time_components="time")
    assert args["time_zone"] == "Europe/Bucharest"
    assert args["scheduled_epoch_ms"] == int(datetime(2026, 10, 24, 6, tzinfo=timezone.utc).timestamp() * 1000)


def test_explicit_zone_overrides_recurrence_zone_but_preserves_aware_instant():
    date = datetime(2026, 10, 24, 9, tzinfo=ZoneInfo("Europe/Bucharest"))
    args = schedule_arguments(date, time_zone="America/New_York", match_date_time_components="time")
    assert args["time_zone"] == "America/New_York"
    assert args["scheduled_epoch_ms"] == int(date.timestamp() * 1000)


@pytest.mark.parametrize("tzinfo", [None, timezone.utc, timezone(timedelta(hours=5, minutes=30))])
def test_unnamed_zones_preserve_legacy_behavior(tzinfo):
    date = datetime(2026, 10, 24, 9, tzinfo=tzinfo)
    args = schedule_arguments(date, match_date_time_components="time")
    assert args["time_zone"] == "UTC"
    assert args["scheduled_epoch_ms"] == int(date.timestamp() * 1000)


@pytest.mark.parametrize("fold", [0, 1])
def test_one_off_preserves_both_instants_in_repeated_hour(fold):
    date = datetime(2026, 10, 25, 3, 30, tzinfo=ZoneInfo("Europe/Bucharest"), fold=fold)
    args = schedule_arguments(date)
    assert args["scheduled_epoch_ms"] == int(datetime(2026, 10, 25, fold, 30, tzinfo=timezone.utc).timestamp() * 1000)
    assert args["match_date_time_components"] is None


@pytest.mark.parametrize("zone", ["Not/A_Zone", ""])
def test_invalid_zone_never_reaches_dart(zone):
    with patch.object(FletAndroidNotifications, "_invoke_method", new_callable=AsyncMock) as invoke:
        with pytest.raises((ZoneInfoNotFoundError, ValueError)):
            asyncio.run(FletAndroidNotifications().schedule_notification(
                8, "Reminder", "Body", datetime(2026, 10, 24, 9), time_zone=zone,
            ))
        invoke.assert_not_called()
