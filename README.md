# flet-android-notifications

Native Android notifications for Flet apps. Wraps the `flutter_local_notifications` Flutter plugin through a custom Flet extension, giving your Python code full access to Android's notification system.

Flet has no built-in support for native notifications, and every obvious Python approach (plyer, Pyjnius, android-notify) fails because Flet's Python process is sandboxed from Android APIs. This extension solves that by bridging Python to Dart to the Flutter plugin.

## Features

- show, cancel, and cancel all notifications
- notification action buttons (e.g. "Approve" / "Deny") with per-button callbacks
- configurable notification channels (id, name, description, importance, sound, vibration)
- tap and action callbacks with payload support
- permission handling for Android 13+
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

[tool.flet.app]
exclude = ["flet_android_notifications"]

[tool.flet.dev_packages]
flet-android-notifications = "flet_android_notifications"
```

The `exclude` line prevents the extension source from being raw-copied into the APK, which would shadow the installed package and break imports.

## Usage

```python
import json
import flet as ft
from flet_android_notifications import FletAndroidNotifications, NotificationError


def main(page: ft.Page):

    def on_notification_tap(e):
        data = json.loads(e.data)
        payload = data.get("payload", "")
        action_id = data.get("action_id", "")

        if action_id == "approve":
            print(f"approved: {payload}")
        elif action_id == "deny":
            print(f"denied: {payload}")
        else:
            print(f"notification body tapped: {payload}")

    notifications = FletAndroidNotifications(
        on_notification_tap=on_notification_tap,
    )

    async def send(e):
        await notifications.request_permissions()

        try:
            await notifications.show_notification(
                notification_id=1,
                title="New task",
                body="You have a task to review.",
                payload="task_42",
                actions=[
                    {"id": "approve", "title": "Approve"},
                    {"id": "deny", "title": "Deny"},
                ],
            )
        except NotificationError as ex:
            print(f"failed: {ex}")

    page.add(ft.Button(content="Send notification", on_click=send))


ft.run(main)
```

Just instantiate `FletAndroidNotifications`. Do not add it to `page.overlay` or `page.controls` -- it's a service, not a visual control, and it registers itself automatically.

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

On Windows, set `PYTHONIOENCODING=utf-8` before building to avoid Unicode crashes from Rich's spinner characters.

### Installing on device

Always do a full uninstall before installing a new APK. Flet's `serious_python` caches the extracted Python environment and won't pick up code changes with `adb install -r`:

```bash
adb uninstall com.yourapp.package
adb install build/apk/app-release.apk
```

## Limitations

- Android only. The extension wraps `flutter_local_notifications` which supports iOS too, but the Python/Dart code here only configures the Android side. iOS support would need `DarwinNotificationDetails` in the Dart layer.
- No scheduled notifications yet. The `flutter_local_notifications` plugin supports `zonedSchedule()` for OS-level scheduling, but this extension doesn't expose it yet.
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
