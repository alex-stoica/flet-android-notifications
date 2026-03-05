# Examples

Nine standalone examples. Copy any to your project as `main.py` and build with `flet build apk -v`.

| Example | What it demonstrates |
|---|---|
| [`simple.py`](simple.py) | one button, one notification — minimal setup |
| [`action_buttons.py`](action_buttons.py) | Approve / Deny action buttons with tap callback |
| [`scheduled.py`](scheduled.py) | fire a notification 30s in the future, cancel pending |
| [`big_text.py`](big_text.py) | expandable long text notification |
| [`notification_styles.py`](notification_styles.py) | big text, big picture, inbox, and progress bar styles |
| [`advanced_options.py`](advanced_options.py) | ongoing, silent, only-alert-once, visibility, sub text, DnD bypass, custom vibration |
| [`periodic.py`](periodic.py) | repeating notifications (every minute, custom 90s interval) |
| [`timeout.py`](timeout.py) | auto-dismissing notifications (5s, 10s, no timeout) |
| [`query_notifications.py`](query_notifications.py) | inspect active (displayed) and pending (scheduled) notifications |

## What to look for

**simple** — tap button, notification appears. That's it.

**action_buttons** — notification shows Approve / Deny buttons. Tapping one updates in-app status text with the action id and payload.

**scheduled** — schedule fires in ~30s even if the app is killed. "Cancel all" prevents pending notifications from firing.

**big_text** — swipe down on the notification to see the expanded text. Collapsed view shows the short body.

**notification_styles** — four buttons, each a different style. Big text and inbox expand on swipe-down. Big picture shows a full-width image. Progress bar shows at 45%.

**advanced_options** — eight buttons, each isolating one param. Ongoing can't be swiped away. Silent has no sound/vibration. Secret is hidden on lock screen. Custom vibration has a distinct buzz pattern.

**periodic** — "Every minute" starts repeating. "Cancel all" stops it. Android may batch or delay in doze mode.

**timeout** — 5s/10s notifications vanish from the shade on their own. Compare with "No timeout" which stays.

**query** — send some notifications, then tap "Get active" to see what's displayed. Schedule some, then "Get pending" to see what's queued. Results shown as JSON in the app.

## Building

```bash
cp examples/simple.py main.py
flet build apk -v
adb uninstall com.flet.flet_android_notifications_demo
adb install build/apk/app-release.apk
```

See the main [README](../README.md) for desugaring patch and AndroidManifest setup.
