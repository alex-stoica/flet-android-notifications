"""Check timer units/defaults at the Python-to-Dart boundary."""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "flet_android_notifications" / "src"))
from flet_android_notifications import FletAndroidNotifications


def test_foreground_timer_uses_epoch_milliseconds():
    when = datetime(2026, 9, 12, 12, 0, tzinfo=timezone.utc)
    with patch.object(FletAndroidNotifications, "_invoke_method", new_callable=AsyncMock, return_value="ok") as invoke:
        asyncio.run(FletAndroidNotifications().start_foreground_service(
            7, "Wew", "Currently Hosting", when=when,
            uses_chronometer=True, chronometer_count_down=True, show_when=False,
        ))
    args = invoke.call_args.kwargs["arguments"]
    assert args["when"] == 1789214400000
    assert args["uses_chronometer"] is True
    assert args["chronometer_count_down"] is True
    assert args["show_when"] is False


def test_foreground_timer_defaults_preserve_timestamp_behavior():
    with patch.object(FletAndroidNotifications, "_invoke_method", new_callable=AsyncMock, return_value="ok") as invoke:
        asyncio.run(FletAndroidNotifications().start_foreground_service(7, "Wew", "Currently Hosting"))
    args = invoke.call_args.kwargs["arguments"]
    assert args["when"] is None
    assert args["show_when"] is True
    assert args["uses_chronometer"] is False
    assert args["chronometer_count_down"] is False
