# Button 21 — Get active notifications

**Source:** `main.py` `query_active` (`get_active_notifications()`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence (in-app log, `img/21-getactive-log.png`)
Returned `Active (19)` — a JSON list of all currently-shown notifications with `id`, `title`,
`body`, `channel_id`, `payload`. Sample entries:
```
{ "id": 20, "title": "VIBRATION #16",  "channel_id": "vibration_ch3" }
{ "id": 10, "title": "SOUND #6",       "channel_id": "beep_channel" }
{ "id": 24, "title": "ALERT ONCE #15 (updated silently)", "channel_id": "alert_once_silent_ch" }
```

## Verdict: ✅ WORKS
`getActiveNotifications()` returns the live notifications with correct fields — also a nice
cross-check that earlier buttons' channels (vibration_ch3, beep_channel, alert_once_silent_ch) were
created as expected.
