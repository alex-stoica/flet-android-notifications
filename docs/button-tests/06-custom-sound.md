# Button 6 — Custom sound (880 Hz beep)

**Source:** `main.py` `send_sound` (`sound="test_beep"`, `channel_id="beep_channel"`)
**Device:** Galaxy S25, One UI, Android 16.

## What it tests
A custom notification sound from `res/raw/test_beep`, bound to a dedicated channel.

## Result — hard evidence (`dumpsys`)
```
NotificationChannel{mId='beep_channel', mName=Beep Channel, mImportance=4,
  mSound=android.resource://com.flet.flet_android_notifications_demo/raw/test_beep,
  mVibrationEnabled=true, ...}
android.title=String (SOUND #6)
mSound= android.resource://com.flet.flet_android_notifications_demo/raw/test_beep
```
The raw resource resolved and is correctly set as the channel sound URI.

## Verdict: ✅ WORKS
Custom sound is delivered and bound to the channel.

## Claim note
The sound is bound to the channel **at channel creation** and is immutable thereafter — to change
it you must use a new `channel_id` (or delete+recreate the channel, which the wrapper could not do
before Phase B). This is an Android channel-immutability rule, **not** a Samsung limitation.
