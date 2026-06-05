# Button 18 — Timeout (5 s auto-dismiss)

**Source:** `main.py` `send_timeout` (`timeout_after=5000`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence (`dumpsys`, timed)
- **t + 2 s:** `android.title=String (TIMEOUT #18)` — present.
- **t + 8 s:** record count for `TIMEOUT #18` = **0** — auto-dismissed.

## Verdict: ✅ WORKS
`timeout_after` auto-dismisses the notification after the specified 5 s.
