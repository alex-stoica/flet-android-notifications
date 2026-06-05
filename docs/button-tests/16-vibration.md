# Button 16 — Custom vibration pattern

**Source:** `main.py` `send_vibration` (`vibration_pattern=[0,200,1000,200,1000,200]`,
`play_sound=False`, `channel_id="vibration_ch3"`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence (`dumpsys`)
```
android.title=String (VIBRATION #16)
NotificationChannel{mId='vibration_ch3' ... mVibrationPattern=[0, 200, 1000, 200, 1000, 200] ...}
```
The custom pattern is set on the channel exactly as specified.

## Verdict: ✅ WORKS
Custom vibration pattern delivered and bound to the channel.

## Claim note
Vibration is **not** Samsung-unsupported. Whether you physically feel it depends on
Settings > Sounds > Vibration intensity and DND/silent mode — device settings, not a wrapper or
OEM "unsupported" issue. The pattern is correctly registered on the channel.
