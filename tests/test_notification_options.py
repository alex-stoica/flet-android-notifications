import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "flet_android_notifications/src"))
from flet_android_notifications import FletAndroidNotifications, NotificationError


METHODS = [
    ("show_notification", {}),
    ("schedule_notification", {"scheduled_time": datetime(2030, 1, 1, tzinfo=timezone.utc)}),
    ("periodically_show", {"repeat_interval": "daily"}),
    ("periodically_show_with_duration", {"duration_seconds": 60}),
    ("start_foreground_service", {}),
]


@pytest.mark.parametrize("method,extra", METHODS)
def test_common_appearance_mapping(method, extra):
    options = dict(large_icon="avatar", large_icon_type="drawable_resource",
                   color="#464850", colorized=True, visibility="private", category="service")
    with patch.object(FletAndroidNotifications, "_invoke_method", new_callable=AsyncMock, return_value="ok") as invoke:
        asyncio.run(getattr(FletAndroidNotifications(), method)(7, "Title", "Body", **extra, **options))
    arguments = invoke.call_args.kwargs["arguments"]
    assert {key: arguments[key] for key in options} == options


@pytest.mark.parametrize("method,extra", METHODS)
@pytest.mark.parametrize("invalid", [
    {"large_icon": "avatar", "large_icon_type": "invalid"},
    {"color": "red"}, {"visibility": "invalid"}, {"category": "invalid"},
])
def test_invalid_appearance_never_reaches_dart(method, extra, invalid):
    with patch.object(FletAndroidNotifications, "_invoke_method", new_callable=AsyncMock) as invoke:
        with pytest.raises(ValueError):
            asyncio.run(getattr(FletAndroidNotifications(), method)(7, "Title", "Body", **extra, **invalid))
        invoke.assert_not_called()


@pytest.mark.parametrize("method,extra", METHODS)
def test_native_errors_propagate(method, extra):
    with patch.object(FletAndroidNotifications, "_invoke_method", new_callable=AsyncMock, return_value="error:unavailable"):
        with pytest.raises(NotificationError, match="unavailable"):
            asyncio.run(getattr(FletAndroidNotifications(), method)(7, "Title", "Body", **extra))
