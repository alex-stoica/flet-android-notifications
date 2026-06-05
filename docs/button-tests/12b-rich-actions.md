# Button 12b — Rich actions + inline reply

**Source:** `main.py` `send_rich_actions` (typed `NotificationAction` + `NotificationActionInput`;
Reply with inline input + Archive contextual/broadcast)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence (`dumpsys`, action list)
```
android.title=String (RICH ACTIONS #12b)
[0] "Reply"   -> PendingIntent{... startActivity}     (RemoteInput inline reply)
[1] "Archive" -> PendingIntent{... broadcastIntent}   (shows_user_interface=False -> broadcast)
android.text=String (Reply inline or archive from the notification.)
```
Reply carries an inline `RemoteInput`; Archive routes to a broadcast (no UI) because
`shows_user_interface=False`/`contextual=True`.

## Verdict: ✅ WORKS (callbacks) + 🟡 OEM-dependent visuals
Typed actions + inline reply are delivered correctly. The **visual** styling of action buttons
(title color, contextual placement, icons) is OEM-dependent on One UI and may differ from AOSP —
this is rendering only and does not affect the callbacks/`input` text returned to the app.
