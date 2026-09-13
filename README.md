# flet-android-notifications

Native local notifications for Flet apps: actions, scheduling, progress, rich styles,
and foreground-service timers. Python API backed by `flutter_local_notifications`.

<p align="center">
  <img src="https://raw.githubusercontent.com/alex-stoica/flet-android-notifications/master/docs/screenshots/style-showcase.png" width="45%" alt="Demo notifications: actions, progress, BigText, large icon, BigPicture" />
  &nbsp;
  <img src="https://raw.githubusercontent.com/alex-stoica/flet-android-notifications/master/docs/screenshots/colorized-foreground-service.png" width="45%" alt="Foreground service with red colorized background on Samsung OneUI, plus secret/sub-text/vibration variants" />
</p>

*Real demo notifications on Samsung One UI: actions, progress, rich styles, and a colorized foreground service. Appearance varies by device.*

## Install

```bash
pip install flet-android-notifications
```

Add the dependency and notification permission to your app's `pyproject.toml`:

```toml
[project]
dependencies = ["flet>=0.82.0", "flet-android-notifications"]

[tool.flet.android.permission]
"android.permission.POST_NOTIFICATIONS" = true
```

## Quick start

```python
import flet as ft
from flet_android_notifications import FletAndroidNotifications

def main(page: ft.Page):
    notifications = FletAndroidNotifications()

    async def send(e):
        if not await notifications.request_permissions():
            return
        await notifications.show_notification(
            notification_id=1, title="Hello", body="It works!",
        )

    page.add(ft.Button(content="Send", on_click=send))

ft.run(main)
```

Instantiate `FletAndroidNotifications` once. Don't add it to `page.overlay` or `page.controls` — it's a service, not a visual control.

Build an Android APK using the steps below; desktop preview does not send notifications.

### Build and install

Requires Python 3.11+, Flet 0.82+, Android API 24+, compile SDK 36+, and Java 17.

```bash
# Generate the Flutter project and package the Python app.
flet build apk -v

# Add notification receivers/service and Gradle desugaring.
flet-android-notifications-patch --project-root build/flutter

# Build the patched project.
cd build/flutter
flutter build apk --release
adb install -r build/app/outputs/flutter-apk/app-release.apk
```

The first build may fail because desugaring is missing; patch and rebuild for that
error only. Resolve unrelated failures first. Reapply the patch after regenerating
the Flutter project. `adb install -r` preserves app data and permissions.
On Windows, set `PYTHONIOENCODING=utf-8` before building.

More runnable [examples](https://github.com/alex-stoica/flet-android-notifications/tree/master/examples):
actions, scheduling, styles, periodic notifications, queries, and foreground services.

## Actions and taps

```python
import json

def on_tap(e):
    data = json.loads(e.data)  # {"payload": "...", "action_id": "..."}

notifications = FletAndroidNotifications(on_notification_tap=on_tap)
```

`action_id` is `""` when the body is tapped (not an action button). Inline reply text is returned as `data["input"]`.

Register the handler when creating the service. Queued background taps replay at
initialization; delivery is best-effort and interrupted replay can repeat an event.

### Action buttons and inline replies

```python
from flet_android_notifications import NotificationAction, NotificationActionInput

await notifications.show_notification(
    notification_id=10,
    title="Message",
    body="Reply from the notification shade.",
    actions=[
        NotificationAction(
            "reply",
            "Reply",
            semantic_action="reply",
            allow_generated_replies=True,
            inputs=[NotificationActionInput(label="Type a reply")],
        ),
        NotificationAction(
            "archive",
            "Archive",
            semantic_action="archive",
            shows_user_interface=False,
        ),
    ],
)
```

Existing dict actions still work. `NotificationAction` additionally supports `title_color`, `icon`, `icon_type`, `contextual`, `allow_generated_replies`, `inputs`, `semantic_action`, and `invisible`. Android requires contextual actions to include a valid icon. Visual rendering of some action details is OEM-dependent, so verify on target devices.

---

## Scheduling

```python
from datetime import datetime, timedelta

await notifications.schedule_notification(
    notification_id=2,
    title="Reminder",
    body="Take a break",
    scheduled_time=datetime.now() + timedelta(minutes=30),
)
```

The default timing is inexact. For exact modes, declare `SCHEDULE_EXACT_ALARM`
and check `can_schedule_exact_notifications()`; request access with
`request_exact_alarm_permission()` if needed. Declare `RECEIVE_BOOT_COMPLETED`
to restore schedules after reboot. Add these under `tool.flet.android.permission`.

For calendar reminders that stay at the same local time across daylight-saving
changes, set `time_zone` to an IANA name (or pass a datetime with `ZoneInfo`):

```python
await notifications.schedule_notification(
    notification_id=3,
    title="Daily reminder",
    body="Take a break",
    scheduled_time=datetime(2026, 10, 24, 9, 0),
    time_zone="Europe/Bucharest",
    match_date_time_components="time",
)
```

A naive datetime uses `time_zone` when provided; an aware datetime keeps its
instant and uses the selected zone for recurrence. Without a named zone,
recurrence retains the previous UTC behavior. One-off notifications keep their
instant, and interval-based repeats remain elapsed-time schedules.
Recreate existing recurring schedules after upgrading: their original timezone
was not saved. The chosen zone stays fixed if the device's timezone changes.

## Foreground service

Start a native foreground service with a visible notification. This does not,
by itself, guarantee that Python work continues after the app is killed.

```python
await notifications.start_foreground_service(
    notification_id=1,  # must not be 0
    title="Hosting",
    body="Currently hosting",
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
| `when` | `datetime\|None` | `None` | Header timestamp / timer base; Android uses now if omitted. Naive datetimes use local time. |
| `show_when` | `bool` | `True` | Show the header timestamp or timer |
| `uses_chronometer` | `bool` | `False` | Show a live elapsed-time counter in place of the timestamp |
| `chronometer_count_down` | `bool` | `False` | With `uses_chronometer=True`, count down toward a future `when` |

The timer options above are available starting in **0.11.0**; their defaults
preserve existing timestamp behavior. They expose native functionality already
provided by `flutter_local_notifications`, without a fork or custom layout.

All other notification parameters (channel, appearance, behavior, etc.) are the same as `show_notification`.

**Important:**

- `notification_id` must not be 0 (Android constraint)
- The notification is **not** removed by `cancel()` or `cancel_all()` — use `stop_foreground_service()`
- Requires `FOREGROUND_SERVICE` permission plus a type-specific permission (e.g. `FOREGROUND_SERVICE_SPECIAL_USE`)

**AndroidManifest.xml** — add inside `<application>`:

The package patcher can add this entry automatically.

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

### Dismissal on Android 14+

`ongoing=True` does **not** guarantee a non-dismissible notification, including
foreground-service notifications. Android 14+ allows individual dismissal while
unlocked; ongoing notifications still resist "Clear all" and lock-screen dismissal.
Exceptions include media and call-style notifications
([Android behavior changes](https://developer.android.com/about/versions/14/behavior-changes-all#non-dismissable-notifications)).

## Styles

```python
from datetime import datetime
from flet_android_notifications import (
    BigTextStyle, BigPictureStyle, InboxStyle,
    MessagingStyle, NotificationMessage, NotificationPerson,
)

# expandable long text
style=BigTextStyle("Full text here...", content_title="Expanded title")

# full-width image when expanded
style=BigPictureStyle(drawable_resource="splash")

# list of lines
style=InboxStyle(["Line 1", "Line 2", "Line 3"], summary_text="3 items")

# chat style with per-message senders (first person is the user themselves;
# messages with person=None are attributed to them)
style=MessagingStyle(
    NotificationPerson("Me"),
    conversation_title="Team chat",
    messages=[
        NotificationMessage("hi", datetime.now(), person=NotificationPerson("Alex")),
        NotificationMessage("hello back", datetime.now()),
    ],
)
```

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
| `get_notification_app_launch_details()` | `dict` with `did_notification_launch_app` and the launching tap's `notification_response` |

### Permission & status methods

| Method | Returns |
|---|---|
| `request_permissions()` | `bool` — request POST_NOTIFICATIONS (Android 13+) |
| `request_exact_alarm_permission()` | `bool` — request exact-alarm access (Android 12+) |
| `request_full_screen_intent_permission()` | `bool` — request USE_FULL_SCREEN_INTENT (Android 14+) |
| `are_notifications_enabled()` | `bool` — are notifications enabled for the app |
| `can_schedule_exact_notifications()` | `bool` — may the app schedule exact alarms |
| `has_notification_policy_access()` | `bool` — has do-not-disturb policy access (gates `channel_bypass_dnd`) |
| `request_notification_policy_access()` | opens the system DND-access screen; confirm afterwards with `has_notification_policy_access()` |

Use the status checks (`are_notifications_enabled`, `can_schedule_exact_notifications`,
`has_notification_policy_access`) to tell *why* a notification didn't appear instead of guessing.

`open_app_notification_settings()` opens the Android notification-settings screen
for this app, so users can re-enable notifications or adjust channels.

### Channel management methods

Channel sound/vibration/importance are fixed after creation. Use a new channel ID
for different defaults, or let users change settings via `open_app_notification_settings()`.
Deleting and recreating the same ID restores its old settings
([Android reference](https://developer.android.com/reference/android/app/NotificationManager#deleteNotificationChannel(java.lang.String))).

| Method | Description |
|---|---|
| `create_notification_channel(channel_id, channel_name, ...)` | create/configure a channel up front (sound, importance, vibration, bypass_dnd, group_id, …) |
| `delete_notification_channel(channel_id)` | delete a channel |
| `get_notification_channels()` | `list[dict]` — id, name, description, importance, play_sound, enable_vibration, bypass_dnd, show_badge |
| `create_notification_channel_group(group_id, name, ...)` | create a channel group |
| `delete_notification_channel_group(group_id)` | delete a channel group and its channels |

## Notification parameters

All notification methods share appearance, channel, behavior, style, and grouping options.
See the [parameter reference](https://github.com/alex-stoica/flet-android-notifications/blob/master/docs/notification-parameters.md)
for types, defaults, scheduling modes, and method-specific exceptions.

## Custom resources

- **Small icons**: vector drawable XML in `res/drawable/` (24dp, white on transparent)
- **Sounds**: audio files in `res/raw/`, reference by name without extension: `sound="alert_tone"`

Add `res/raw/keep.xml` to prevent resource stripping:

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools"
    tools:keep="@raw/*,@drawable/ic_*" />
```

A channel's sound is fixed at creation; use a new `channel_id` for a new default sound.

## Device rendering

Android controls layout; exact positioning is not customizable here. Colors and
action styling vary by device. The demo was tested on a Galaxy S25 (Android 16);
full-background `colorized=True` was observed with a foreground service.

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

## Building this repo's demo

Use `python build.py` with Flet CLI and Flutter installed. `--skip-install` builds
without a device; `--skip-flet` refreshes Python/Dart sources in an existing build.
Run the full build after dependency, asset, or packaging changes.

The repo's `tool.flet.dev_packages` and `tool.flet.app.exclude` settings are for
local development only. Do not copy them into a PyPI-installed app.

## License

MIT
