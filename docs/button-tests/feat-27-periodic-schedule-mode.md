# Feature 27 (Phase B) — Periodic `schedule_mode`

**New API:** `schedule_mode` parameter on `periodically_show` and
`periodically_show_with_duration` (previously hardcoded to `inexactAllowWhileIdle`).
**Demo button:** 27 "Periodic (exact mode)" — uses `schedule_mode="exact_allow_while_idle"`.
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence (in-app log)
- Kickoff `PERIODIC EXACT #27 (kickoff)` posted (`dumpsys` count 1) — the handler runs.
- The periodic registration returned:
  `FAIL periodic exact: NotificationError: PlatformException(exact_alarms_not_permitted,
   Exact alarms are not permitted, null, null)`.

## Verdict: ✅ WORKS (param wired; OS-enforced)
This is the **correct** outcome. The `schedule_mode` param genuinely flows through to the OS, which
rejects exact mode because **SCHEDULE_EXACT_ALARM is not granted** (button 24 reports
`can_schedule_exact=False`). The error is surfaced cleanly as a `NotificationError` rather than
failing silently.

This ties the Phase B features together:
- Use `can_schedule_exact_notifications()` (button 24) to check first.
- If False, either call `request_exact_alarm_permission()` or pass an inexact `schedule_mode`
  (the default `inexact_allow_while_idle`, which buttons 19/20 use successfully).
