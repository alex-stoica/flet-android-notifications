# Button 11 — Ongoing (sticky)

**Source:** `main.py` `send_ongoing` (`ongoing=True`, `auto_cancel=False`,
`channel_id="ongoing_ch"`, `importance="default"`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence (`dumpsys`)
```
NotificationRecord(... id=15 ... channel=ongoing_ch ... flags=ONGOING_EVENT ...)
android.title=String (ONGOING #11)
```
`FLAG_ONGOING_EVENT` is set (no `AUTO_CANCEL`) — the notification is sticky.

## Verdict: ✅ WORKS
Ongoing/sticky behavior delivered. Dismissed only via `cancel`/`cancel_all` (or the demo's
Cancel all), matching the Android contract.
