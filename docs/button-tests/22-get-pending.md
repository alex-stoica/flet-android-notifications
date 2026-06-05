# Button 22 — Get pending notifications

**Source:** `main.py` `query_pending` (`get_pending_notifications()`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence (in-app log, `img/22-getpending-log.png`)
Returned `Pending (2)`:
```
[
  { "id": 27, "title": "PERIODIC #19",          "body": "Repeats every minute." },
  { "id": 28, "title": "PERIODIC DURATION #20", "body": "Repeats every 90 seconds." }
]
```

## Verdict: ✅ WORKS
`pendingNotificationRequests()` returns the scheduled/periodic notifications with correct fields.
Confirms buttons 19 and 20 genuinely registered recurring schedules.

## Note (test harness)
This button sits near the list bottom where the scroll position is non-deterministic (the list
overscrolls/bounces), so the tap required several attempts. Not an app issue.
