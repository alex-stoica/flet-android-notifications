# Examples

Five standalone examples, each demonstrating a different feature. To test any of them, copy it to your project as `main.py` and build with `flet build apk -v`.

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

## big_text.py — Big text notification

Shows a notification that expands to reveal a longer message when pulled down.

**What it does**: Tapping "Send big text notification" shows a notification with a short body. Pulling down on the notification reveals the full expanded text.

**What to test**:
- Tap the button — notification appears with "Your weekly summary is ready."
- Pull down on the notification — expanded text shows the full summary with a different title and summary line

**Expected output**:
```
[Button: "Send big text notification"]

-> tap button
-> notification appears: title="Weekly report", body="Your weekly summary is ready."
-> pull down on notification
-> expanded: title="Weekly report — expanded", full summary text, summary="12 tasks completed"
```

## notification_styles.py — All notification styles

Four buttons showcasing big text, big picture, inbox, and progress bar styles.

**What it does**: Each button sends a notification with a different style. Big text expands to show long text, big picture shows an image, inbox shows multiple message lines, and progress bar shows a determinate progress indicator.

**What to test**:
- Tap "Big text" — notification expands to show wrapped multi-line text
- Tap "Big picture" — notification expands to show the app icon as a large image
- Tap "Inbox" — notification expands to show 3 message lines
- Tap "Progress bar" — notification shows a progress bar at 45%

**Expected output**:
```
[Button: "Big text"]
[Button: "Big picture"]
[Button: "Inbox"]
[Button: "Progress bar"]

-> tap "Big text" -> expandable long text notification
-> tap "Big picture" -> notification with app icon image
-> tap "Inbox" -> notification with 3 message lines
-> tap "Progress bar" -> notification with 45% progress bar
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
