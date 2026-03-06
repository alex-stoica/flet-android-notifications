# flet-android-notifications

Native Android notifications for Flet apps. Bridges Python to the `flutter_local_notifications` plugin through a custom Flet extension.

Flet has no built-in notification support, and Python-side approaches (plyer, Pyjnius) fail because Flet's Python process is sandboxed from Android APIs.

## Install

```bash
pip install flet-android-notifications
```

Add to your `pyproject.toml`:

```toml
[project]
dependencies = ["flet>=0.80.5", "flet-android-notifications"]

[tool.flet.android.permission]
"android.permission.POST_NOTIFICATIONS" = true
"android.permission.SCHEDULE_EXACT_ALARM" = true      # for scheduled/periodic
"android.permission.RECEIVE_BOOT_COMPLETED" = true     # survive reboots

[tool.flet.app]
exclude = ["flet_android_notifications"]

[tool.flet.dev_packages]
flet-android-notifications = "flet_android_notifications"
```

## Quick start

```python
from datetime import datetime, timedelta
import flet as ft
from flet_android_notifications import FletAndroidNotifications

def main(page: ft.Page):
    notifications = FletAndroidNotifications()

    async def send(e):
        await notifications.request_permissions()
        await notifications.show_notification(
            notification_id=1, title="Hello", body="It works!",
        )

    page.add(ft.Button(content="Send", on_click=send))

ft.run(main)
```

Instantiate `FletAndroidNotifications` once. Don't add it to `page.overlay` or `page.controls` — it's a service, not a visual control.

See [`examples/`](examples/) for more: [simple](examples/simple.py), [action buttons](examples/action_buttons.py), [scheduled](examples/scheduled.py), [styles](examples/notification_styles.py), [periodic](examples/periodic.py), [timeout](examples/timeout.py), [query](examples/query_notifications.py), [foreground service](examples/foreground_service.py).

## API overview

### Core methods

| Method | Description |
|---|---|
| `show_notification(id, title, body, ...)` | show a notification immediately |
| `schedule_notification(id, title, body, scheduled_time, ...)` | fire at a future time via AlarmManager |
| `periodically_show(id, title, body, repeat_interval, ...)` | repeat every minute / hour / day / week |
| `periodically_show_with_duration(id, title, body, duration_seconds, ...)` | repeat at a custom interval |
| `start_foreground_service(id, title, body, ...)` | start a foreground service with persistent notification |
| `stop_foreground_service()` | stop the foreground service and remove its notification |
| `cancel(notification_id)` | cancel one notification |
| `cancel_all()` | cancel all notifications |

### Query methods

| Method | Returns |
|---|---|
| `get_active_notifications()` | `list[dict]` — currently displayed (id, title, body, channel_id, payload) |
| `get_pending_notifications()` | `list[dict]` — scheduled/periodic (id, title, body, payload) |

### Permission methods

| Method | Returns |
|---|---|
| `request_permissions()` | `bool` — POST_NOTIFICATIONS (Android 13+) |
| `request_exact_alarm_permission()` | `bool` — SCHEDULE_EXACT_ALARM (Android 14+) |

### Tap callback

```python
import json

def on_tap(e):
    data = json.loads(e.data)  # {"payload": "...", "action_id": "..."}

notifications = FletAndroidNotifications(on_notification_tap=on_tap)
```

`action_id` is `""` when the body is tapped (not an action button).

---

## Notification parameters

`show_notification`, `schedule_notification`, `periodically_show`, and `periodically_show_with_duration` all share a common set of parameters. Only the required ones differ per method.

### Required parameters

| Parameter | `show` | `schedule` | `periodically_show` | `periodically_show_with_duration` |
|---|---|---|---|---|
| `notification_id` | int | int | int | int |
| `title` | str | str | str | str |
| `body` | str | str | str | str |
| `scheduled_time` | — | datetime | — | — |
| `repeat_interval` | — | — | str | — |
| `duration_seconds` | — | — | — | int\|float |

`repeat_interval` is one of `"every_minute"`, `"hourly"`, `"daily"`, `"weekly"`.

### Common optional parameters

These work on all four methods above.

**Basics:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `payload` | `str` | `""` | returned in tap callback |
| `actions` | `list[dict]` | `None` | buttons: `[{"id": "...", "title": "..."}]` |
| `importance` | `str` | `"high"` | `none`, `min`, `low`, `default`, `high`, `max` |
| `timeout_after` | `int\|None` | `None` | auto-dismiss after N milliseconds |

**Channel:**

| Parameter | Type | Default |
|---|---|---|
| `channel_id` | `str` | `"flet_notifications"` |
| `channel_name` | `str` | `"Flet Notifications"` |
| `channel_description` | `str` | `"Notifications from Flet app"` |
| `channel_bypass_dnd` | `bool` | `False` |

**Appearance:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `icon` | `str\|None` | `None` | drawable resource for small icon |
| `large_icon` | `str\|None` | `None` | thumbnail on right side |
| `large_icon_type` | `str` | `"drawable_resource"` | or `"file_path"` |
| `color` | `str\|None` | `None` | hex accent color, e.g. `"#FF5722"` |
| `colorized` | `bool` | `False` | color as background (foreground service only) |
| `sub_text` | `str\|None` | `None` | small text below content |
| `visibility` | `str\|None` | `None` | `"public"`, `"private"`, or `"secret"` |

**Behavior:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `play_sound` | `bool` | `True` | play notification sound |
| `enable_vibration` | `bool` | `True` | vibrate |
| `sound` | `str\|None` | `None` | raw resource name (e.g. `"alert_tone"`) |
| `vibration_pattern` | `list[int]\|None` | `None` | e.g. `[0, 500, 200, 500]` |
| `ongoing` | `bool` | `False` | can't be swiped away |
| `auto_cancel` | `bool` | `True` | dismiss on tap |
| `silent` | `bool` | `False` | suppress sound and vibration |
| `only_alert_once` | `bool` | `False` | alert on first show only |

**Styles and progress:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `style` | `BigTextStyle\|BigPictureStyle\|InboxStyle\|None` | `None` | rich expandable style |
| `show_progress` | `bool` | `False` | show progress bar |
| `max_progress` | `int` | `0` | max value |
| `progress` | `int` | `0` | current value |
| `indeterminate` | `bool` | `False` | spinning progress bar |

**Grouping:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `group_key` | `str\|None` | `None` | bundle notifications together |
| `set_as_group_summary` | `bool` | `False` | this is the group summary |
| `group_alert_behavior` | `str` | `"all"` | `"all"`, `"summary"`, `"children"` |

### Schedule-only parameters

These only apply to `schedule_notification`:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `schedule_mode` | `str` | `"inexact_allow_while_idle"` | see table below |
| `match_date_time_components` | `str\|None` | `None` | `"time"` (daily), `"day_of_week_and_time"` (weekly), `"day_of_month_and_time"` (monthly), `"date_and_time"` (yearly) |

**Schedule modes:**

| Mode | Exact alarm permission? | Fires in Doze? |
|---|---|---|
| `"inexact"` | no | no |
| `"inexact_allow_while_idle"` | no | yes |
| `"exact"` | yes | no |
| `"exact_allow_while_idle"` | yes | yes |
| `"alarm_clock"` | yes | yes |

---

## Foreground service

For persistent background tasks (music, GPS tracking, uploads) that require a visible notification:

```python
await notifications.start_foreground_service(
    notification_id=1,  # must not be 0
    title="Uploading",
    body="3 files remaining...",
    foreground_service_types=["special_use"],
    ongoing=True,
)

# when done:
await notifications.stop_foreground_service()
```

**Parameters specific to foreground service:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `start_type` | `str` | `"start_sticky"` | `start_sticky`, `start_not_sticky`, `start_sticky_compatibility`, `start_redeliver_intent` |
| `foreground_service_types` | `list[str]\|None` | `None` | e.g. `["special_use"]`, `["location"]`, `["media_playback"]` |

All other notification parameters (channel, appearance, behavior, etc.) are the same as `show_notification`.

**Important:**
- `notification_id` must not be 0 (Android constraint)
- The notification is **not** removed by `cancel()` or `cancel_all()` — use `stop_foreground_service()`
- Requires `FOREGROUND_SERVICE` permission plus a type-specific permission (e.g. `FOREGROUND_SERVICE_SPECIAL_USE`)

**AndroidManifest.xml** — add inside `<application>`:

```xml
<service android:name="com.dexterous.flutterlocalnotifications.ForegroundService"
    android:exported="false"
    android:foregroundServiceType="specialUse" />
```

Adjust `foregroundServiceType` to match your use case (e.g. `location`, `mediaPlayback`).

**pyproject.toml permissions:**

```toml
[tool.flet.android.permission]
"android.permission.FOREGROUND_SERVICE" = true
"android.permission.FOREGROUND_SERVICE_SPECIAL_USE" = true
```

## Styles

```python
from flet_android_notifications import BigTextStyle, BigPictureStyle, InboxStyle

# expandable long text
style=BigTextStyle("Full text here...", content_title="Expanded title")

# full-width image when expanded
style=BigPictureStyle(drawable_resource="splash")

# list of lines
style=InboxStyle(["Line 1", "Line 2", "Line 3"], summary_text="3 items")
```

## Building the APK

```bash
# first build — generates Flutter template, may fail at Gradle
flet build apk -v

# patch desugaring into build/flutter/android/app/build.gradle.kts:
#   android { compileOptions { isCoreLibraryDesugaringEnabled = true } }
#   dependencies { coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4") }

# rebuild
flet build apk -v
```

The desugaring patch is needed because `flutter_local_notifications` v19+ uses Java 8 APIs. Apply once per clean build directory.

### AndroidManifest.xml for scheduled notifications

Register BroadcastReceivers inside `<application>` in `build/flutter/android/app/src/main/AndroidManifest.xml` so scheduled notifications survive reboots:

```xml
<receiver android:exported="false"
    android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationReceiver" />
<receiver android:exported="false"
    android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationBootReceiver">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
        <action android:name="android.intent.action.MY_PACKAGE_REPLACED" />
        <action android:name="android.intent.action.QUICKBOOT_POWERON" />
        <action android:name="com.htc.intent.action.QUICKBOOT_POWERON" />
    </intent-filter>
</receiver>
```

### Installing on device

Always full-uninstall before installing. Flet caches the extracted Python environment:

```bash
adb uninstall com.yourapp.package
adb install build/apk/app-release.apk
```

On Windows, set `PYTHONIOENCODING=utf-8` before building to avoid Unicode crashes.

## Custom resources

- **Small icons**: vector drawable XML in `res/drawable/` (24dp, white on transparent)
- **Sounds**: audio files in `res/raw/`, reference by name without extension: `sound="alert_tone"`

Add `res/raw/keep.xml` to prevent resource stripping:

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools"
    tools:keep="@raw/*,@drawable/ic_*" />
```

Sound is permanently bound to a channel at creation. Change the sound by using a different `channel_id`.

## Samsung OneUI notes

- **Color**: Samsung's system palette overrides the `color` parameter. Works on stock Android, ignored on Samsung.
- **Brief mode**: Samsung's compact notification view hides expanded content. Swipe down to expand.
- **`colorized`**: only works for foreground service / media-style notifications (all OEMs).

## Limitations

- **Android only.** iOS support would need `DarwinNotificationDetails` in the Dart layer.
- **Desktop**: the service instantiates without error but notifications won't appear.

## How it works

```
Python app → FletAndroidNotifications (ft.Service)
  → _invoke_method() over Flet protocol
    → NotificationsService (FletService, Dart)
      → flutter_local_notifications plugin → Android NotificationManager
```

The extension ships as a Python package with a `flutter/` directory containing the Dart code. `flet build apk` discovers it in site-packages and includes it as a Flutter path dependency.

## License

MIT
