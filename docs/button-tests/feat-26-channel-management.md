# Feature 26 (Phase B) — Channel management

**New API:** `create_notification_channel(...)`, `delete_notification_channel(id)`,
`get_notification_channels()`, plus `create_/delete_notification_channel_group`.
**Demo buttons:** 26 "Channel mgmt (create+list)" and 26 "Delete managed channel".
**Device:** Galaxy S25, One UI, Android 16.

## Why
A channel's sound/vibration/importance are immutable after creation. Without delete+recreate you
cannot change a channel's sound (the "immutable channel" friction the report and button 6 noted).

## Result — hard evidence (`dumpsys notification`)
- **create_notification_channel** → channel created up front with a custom sound:
  `mId='demo_managed_ch', mName=Demo Managed, mImportance=4,
   mSound=android.resource://.../raw/test_beep`. A notification was then posted on it
  (`CHANNEL MGMT #26`, count 1).
- **get_notification_channels** → returned the channel list (count logged in-app).
- **delete_notification_channel** → the channel is now `mDeleted=true`.

## Verdict: ✅ WORKS
Create (with a chosen sound), list, and delete all work. This is the proper fix for changing an
immutable channel's sound: delete then recreate with the new configuration.
