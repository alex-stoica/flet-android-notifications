# Examples

Three standalone examples, each demonstrating a different feature. To test any of them, copy it to your project as `main.py` and build with `flet build apk -v`.

## simple.py — Basic notification

The simplest possible usage. One button, one notification.

**What it does**: Tapping "Send notification" shows a notification with the title "Hello".

**What to test**:
- Tap the button — a notification should appear immediately
- Tap the notification — nothing visible happens (no tap handler in this example)

**Expected output**:
```
[Button: "Send notification"]

-> tap button
-> notification appears: title="Hello", body="This is a basic notification."
```

## action_buttons.py — Notifications with Approve / Deny buttons

Shows a notification with two action buttons. Tapping an action updates the status text with a color.

**What it does**: Tapping "Send notification" shows a notification with "Approve" (green) and "Deny" (red) action buttons. The response is shown in-app.

**What to test**:
- Tap "Send notification" — notification appears with two action buttons
- Tap "Approve" on the notification — status text turns green with "Approved: task_42"
- Send again, tap "Deny" — status text turns red with "Denied: task_42"
- Send again, tap the notification body (not a button) — status shows "Tapped: task_42"

**Expected output**:
```
[Button: "Send notification"]
No response yet

-> tap button, then tap "Approve" on notification
[Button: "Send notification"]
Approved: task_42          <- green text
```

## scheduled.py — Scheduled notifications

Notifications that fire in the future, even if the app is killed.

**What it does**: Schedule a one-shot notification 30 seconds from now. Cancel all pending schedules.

**What to test**:
- Tap "Schedule in 30s" — status shows the target time, notification fires ~30s later
- Tap "Schedule in 30s", then kill the app (swipe from recents) — notification still fires
- Tap "Cancel all" before a scheduled notification fires — it should not fire

**Expected output**:
```
[Button: "Schedule in 30s"]
[Button: "Cancel all"]

-> tap "Schedule in 30s"
Scheduled for 14:32:15

-> wait 30 seconds
-> notification appears: title="Reminder", body="Scheduled for 14:32:15"
```

## Building and deploying

Each example needs a `pyproject.toml` with the Flet configuration. From the repo root:

```bash
# copy the example you want to test
cp examples/simple.py main.py

# build
flet build apk -v

# deploy (full uninstall required — Flet caches the Python environment)
adb uninstall com.flet.flet_android_notifications_demo
adb install build/apk/app-release.apk
```

See the main [README](../README.md) for desugaring patch and AndroidManifest setup instructions.
