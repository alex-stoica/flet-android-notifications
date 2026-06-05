# Button 7 — Silent

**Source:** `main.py` `send_silent` (`play_sound=False`, `enable_vibration=False`,
`channel_id="silent_ch"`)
**Device:** Galaxy S25, One UI, Android 16.

## What it tests
A notification with no sound and no vibration.

## Result — hard evidence (`dumpsys`)
```
NotificationChannel{mId='silent_ch', mName=Silent, mSound=null,
  mVibrationEnabled=false, mAudioAttributes=null, ...}
android.title=String (SILENT #7)
```
Channel created with `mSound=null` and `mVibrationEnabled=false`.

## Verdict: ✅ WORKS
Silent behavior is honored at the channel level.
