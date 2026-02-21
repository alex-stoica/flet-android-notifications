# flet-android-notifications

Native Android notifications for Flet apps. Wraps the `flutter_local_notifications` Flutter plugin through a custom Flet extension, giving your Python code full access to Android's notification system.

Flet has no built-in support for native notifications, and every obvious Python approach (plyer, Pyjnius, android-notify) fails because Flet's Python process is sandboxed from Android APIs. This extension solves that by bridging Python to Dart to the Flutter plugin.

## Features

- show, cancel, and cancel all notifications
- schedule notifications for a future time (one-shot or recurring via AlarmManager)
- notification action buttons (e.g. "Approve" / "Deny") with per-button callbacks
- configurable notification channels (id, name, description, importance, sound, vibration)
- tap and action callbacks with payload support
- permission handling for Android 13+ and exact alarm permission for Android 14+
- proper error propagation via `NotificationError`

## Install

```bash
pip install flet-android-notifications
# or
uv add flet-android-notifications
```

In your app's `pyproject.toml`, declare the Android permission and tell Flet where to find the extension for APK builds:

```toml
[project]
dependencies = [
    "flet>=0.80.5",
    "flet-android-notifications",
]

[tool.flet.android.permission]
"android.permission.POST_NOTIFICATIONS" = true
# Required for scheduled notifications:
"android.permission.SCHEDULE_EXACT_ALARM" = true
"android.permission.RECEIVE_BOOT_COMPLETED" = true

[tool.flet.app]
exclude = ["flet_android_notifications"]

[tool.flet.dev_packages]
flet-android-notifications = "flet_android_notifications"
```

The `exclude` line prevents the extension source from being raw-copied into the APK, which would shadow the installed package and break imports.

## Usage

```python
import json
from datetime import datetime, timedelta
import flet as ft
from flet_android_notifications import FletAndroidNotifications, NotificationError


def main(page: ft.Page):

    def on_notification_tap(e):
        data = json.loads(e.data)
        payload = data.get("payload", "")
        action_id = data.get("action_id", "")
        print(f"tapped: payload={payload}, action={action_id}")

    notifications = FletAndroidNotifications(
        on_notification_tap=on_notification_tap,
    )

    async def send_now(e):
        await notifications.request_permissions()
        await notifications.show_notification(
            notification_id=1,
            title="Hello",
            body="This is an instant notification.",
        )

    async def send_with_actions(e):
        await notifications.request_permissions()
        await notifications.show_notification(
            notification_id=2,
            title="Review request",
            body="You have a task to review.",
            payload="task_42",
            actions=[
                {"id": "approve", "title": "Approve"},
                {"id": "deny", "title": "Deny"},
            ],
        )

    async def schedule_30s(e):
        await notifications.request_permissions()
        await notifications.schedule_notification(
            notification_id=10,
            title="Reminder",
            body="This fired 30 seconds after you pressed the button.",
            scheduled_time=datetime.now() + timedelta(seconds=30),
        )

    page.add(
        ft.Column([
            ft.Button(content="Send now", on_click=send_now),
            ft.Button(content="Send with actions", on_click=send_with_actions),
            ft.Button(content="Schedule in 30s", on_click=schedule_30s),
        ])
    )


ft.run(main)
```

Just instantiate `FletAndroidNotifications`. Do not add it to `page.overlay` or `page.controls` -- it's a service, not a visual control, and it registers itself automatically.

See the [`examples/`](examples/) folder for more: [`simple.py`](examples/simple.py), [`action_buttons.py`](examples/action_buttons.py), [`scheduled.py`](examples/scheduled.py).

## API

### `FletAndroidNotifications(on_notification_tap=callback)`

The service. Instantiate once. The `on_notification_tap` callback receives an event where `e.data` is a JSON string:

```json
{"payload": "task_42", "action_id": "approve"}
```

`action_id` is an empty string `""` when the user taps the notification body rather than an action button.

### `await show_notification(...)`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `notification_id` | `int` | required | unique id for this notification |
| `title` | `str` | required | notification title |
| `body` | `str` | required | notification body text |
| `payload` | `str` | `""` | arbitrary string returned in tap callback |
| `actions` | `list[dict]` | `None` | action buttons, each `{"id": "...", "title": "..."}` |
| `channel_id` | `str` | `"flet_notifications"` | Android notification channel id |
| `channel_name` | `str` | `"Flet Notifications"` | channel name shown in system settings |
| `channel_description` | `str` | `"Notifications from Flet app"` | channel description |
| `importance` | `str` | `"high"` | one of `none`, `min`, `low`, `default`, `high`, `max` |
| `play_sound` | `bool` | `True` | play default notification sound |
| `enable_vibration` | `bool` | `True` | vibrate on notification |

Raises `NotificationError` on failure.

### `await schedule_notification(...)`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `notification_id` | `int` | required | unique id for this notification |
| `title` | `str` | required | notification title |
| `body` | `str` | required | notification body text |
| `scheduled_time` | `datetime` | required | when to fire; naive = local time, aware = converted to UTC |
| `payload` | `str` | `""` | arbitrary string returned in tap callback |
| `actions` | `list[dict]` | `None` | action buttons, each `{"id": "...", "title": "..."}` |
| `channel_id` | `str` | `"flet_notifications"` | Android notification channel id |
| `channel_name` | `str` | `"Flet Notifications"` | channel name shown in system settings |
| `channel_description` | `str` | `"Notifications from Flet app"` | channel description |
| `importance` | `str` | `"high"` | one of `none`, `min`, `low`, `default`, `high`, `max` |
| `play_sound` | `bool` | `True` | play default notification sound |
| `enable_vibration` | `bool` | `True` | vibrate on notification |
| `schedule_mode` | `str` | `"inexact_allow_while_idle"` | how Android schedules the alarm (see table below) |
| `match_date_time_components` | `str\|None` | `None` | for recurring: `"time"` (daily), `"day_of_week_and_time"` (weekly), `"day_of_month_and_time"` (monthly), `"date_and_time"` (yearly), or `None` (one-shot) |

Raises `NotificationError` on failure.

#### Schedule modes

| Mode | Needs `SCHEDULE_EXACT_ALARM`? | Fires during Doze? | Notes |
|---|---|---|---|
| `"inexact"` | No | No | Battery-friendly, may be deferred |
| `"inexact_allow_while_idle"` | No | Yes | Safe default, no special permission needed |
| `"exact"` | Yes | No | Exact time, but deferred during Doze |
| `"exact_allow_while_idle"` | Yes | Yes | Exact time, fires even in Doze |
| `"alarm_clock"` | Yes | Yes | Shows alarm icon in status bar |

### `await request_exact_alarm_permission()`

Request the `SCHEDULE_EXACT_ALARM` permission (required on Android 14+ for exact schedule modes). Returns `"true"` if granted, `"false"` if denied. Inexact modes do not need this permission.

### `await cancel(notification_id)`

Cancel a specific notification by id.

### `await cancel_all()`

Cancel all active notifications.

### `await request_permissions()`

Request the POST_NOTIFICATIONS runtime permission (required on Android 13+). Returns `"true"` if granted, `"false"` if denied.

## Building the APK

```bash
# first build -- generates Flutter template, will likely fail at Gradle
flet build apk -v

# patch desugaring into build/flutter/android/app/build.gradle.kts:
#   android { compileOptions { isCoreLibraryDesugaringEnabled = true } }
#   dependencies { coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4") }

# rebuild -- the patch survives because the template hash is unchanged
flet build apk -v
```

The desugaring patch is needed because `flutter_local_notifications` v19+ uses Java 8 APIs that aren't available on older Android versions without it. You only need to apply this once per clean build directory.

### AndroidManifest.xml setup for scheduled notifications

If you use `schedule_notification()`, you must register the plugin's BroadcastReceivers so that scheduled notifications survive app restarts and device reboots. After your first `flet build apk`, add the following inside the `<application>` tag in `build/flutter/android/app/src/main/AndroidManifest.xml`:

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

Without these receivers, scheduled notifications will fire while the app is running but will be lost if the app is killed or the device restarts.

On Windows, set `PYTHONIOENCODING=utf-8` before building to avoid Unicode crashes from Rich's spinner characters.

### Installing on device

Always do a full uninstall before installing a new APK. Flet's `serious_python` caches the extracted Python environment and won't pick up code changes with `adb install -r`:

```bash
adb uninstall com.yourapp.package
adb install build/apk/app-release.apk
```

## Limitations

- Android only. The extension wraps `flutter_local_notifications` which supports iOS too, but the Python/Dart code here only configures the Android side. iOS support would need `DarwinNotificationDetails` in the Dart layer.
- Desktop does nothing. On desktop, the service instantiates without error but notifications won't appear since there's no native plugin backing it.

## How it works

Flet's architecture is `Python <-> Flet protocol <-> Flutter/Dart <-> platform APIs`. Python can't call Android APIs directly. This extension bridges that gap:

```
your Python app
  -> FletAndroidNotifications (ft.Service)
    -> _invoke_method() over Flet protocol
      -> NotificationsService (FletService, Dart)
        -> flutter_local_notifications plugin
          -> Android NotificationManager
```

The extension is packaged as a standard Python package with a `flutter/` namespace directory containing the Dart code. When you run `flet build apk`, Flet discovers the Dart code in site-packages and includes it as a path dependency in the generated Flutter project.

## License

MIT
