# Button 12 — Action buttons

**Source:** `main.py` `send_actions` (`actions=[{Approve},{Deny}]`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence (`dumpsys`, action list)
```
android.title=String (ACTIONS #12)
[0] "Approve" -> PendingIntent{... startActivity}
[1] "Deny"    -> PendingIntent{... startActivity}
```
Both action buttons are attached with valid PendingIntents.

## Verdict: ✅ WORKS
Action buttons render and carry working intents. The tapped action's `id` returns in the
`on_notification_tap` event (`action_id`), per the wrapper's event plumbing.
