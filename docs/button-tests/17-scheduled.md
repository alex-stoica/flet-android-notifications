# Button 17 — Scheduled (10 s delay)

**Source:** `main.py` `send_scheduled` (`schedule_notification`, fire at now+10 s,
default `schedule_mode="inexact_allow_while_idle"`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence (`dumpsys`)
Fired, then **10 seconds later** the record appeared:
```
android.title=String (SCHEDULED #17)
```

## Verdict: ✅ WORKS
The scheduled notification fires on time via `AlarmManager` + `zonedSchedule`. This directly
exercises the `ScheduledNotificationReceiver` that `build.py`'s `step_patch_manifest` injects —
**the historical "scheduled doesn't fire on Samsung" was a missing-receiver bug, now fixed**, not
OEM/Doze behavior.

## Claim correction
Not a Samsung limitation. Scheduled delivery works once the receivers are in the merged manifest
(they are, verified). Real upstream caveat: Samsung is reported to cap `AlarmManager` at ~500
scheduled alarms — a capacity limit, not "scheduling unsupported".
