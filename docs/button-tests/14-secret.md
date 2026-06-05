# Button 14 — Secret (lock-screen hidden)

**Source:** `main.py` `send_visibility` (`schedule_notification` at +8 s, `visibility="secret"`,
`importance="default"`)
**Device:** Galaxy S25, One UI, Android 16.

## What it tests
`visibility="secret"` — the notification should fire but **not** show its content on the lock
screen.

## How triggered
Fire button 14, then `adb shell input keyevent 223` (sleep) within 8 s so it fires while the phone
is locked; `keyevent 224` to wake to the lock screen; screenshot; then read `dumpsys`.

## Result — three independent confirmations
1. **Fired while locked:** after firing, `dumpsys` shows `SECRET #14` active (count = 1).
2. **Visibility flag:** across our app's records, exactly one is `vis=SECRET` (the rest are
   `vis=PRIVATE`) — so the secret flag reached Android.
3. **Lock screen:** the lock-screen screenshot shows **no SECRET #14 content** — only clock and
   battery (`img/14-secret-lockscreen.png`).

## Verdict: ✅ WORKS
Fires while locked and is correctly hidden from the lock screen.

## Claim correction
The historical "secret never fired on Samsung" was the **missing `ScheduledNotificationReceiver`**
bug (see `insights/errors.md`), now fixed by `build.py`'s manifest patch — not OEM suppression.
With receivers present it both fires and hides correctly. (Samsung's
Settings > Lock screen > Notifications "hide content" is an independent user setting.)

## Screenshots
- `img/14-secret-lockscreen.png` (locked, no content shown)
