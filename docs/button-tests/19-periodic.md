# Button 19 — Periodic (preset enum)

**Source:** `main.py` `send_periodic` (kickoff `show_notification` + `periodically_show(
repeat_interval="every_minute")`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence
- **Kickoff:** `dumpsys` shows `android.title=String (PERIODIC #19)` immediately; in-app log
  `OK periodic #19 (id=27) — kickoff now, next in ~60s`.
- **Registered as pending** (via button 22 `get_pending_notifications`):
  `{ "id": 27, "title": "PERIODIC #19", "body": "Repeats every minute." }`.
- `dumpsys alarm` shows 13+ alarms registered for the package.

## Verdict: ✅ WORKS
The preset-enum periodic registers via `AlarmManager` and the kickoff fires. (Recurring fire is
+60 s; not waited out, but the pending registration confirms it is scheduled.)

## Note
The wrapper currently hardcodes `AndroidScheduleMode.inexactAllowWhileIdle` for periodic — Phase B
adds a `schedule_mode` parameter so callers can choose exact modes.
