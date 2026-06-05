# Button 9 — Progress bar (determinate, 65%)

**Source:** `main.py` `send_progress` (`show_progress=True`, `max_progress=100`, `progress=65`,
`ongoing=True`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence (`dumpsys`)
```
android.title=String (PROGRESS #9)
android.progress=Integer (65)
android.progressMax=Integer (100)
android.progressIndeterminate=Boolean (false)
```

## Verdict: ✅ WORKS
Determinate progress bar at 65/100 delivered correctly; the notification is ongoing
(`flags=ONGOING_EVENT`).
