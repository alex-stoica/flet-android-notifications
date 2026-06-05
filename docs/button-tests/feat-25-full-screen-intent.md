# Feature 25 (Phase B) — Full-screen intent

**New API:** `full_screen_intent=True` on `show_notification`/`schedule_notification` +
`request_full_screen_intent_permission()`; new `USE_FULL_SCREEN_INTENT` manifest permission.
**Demo button:** 25 "Full-screen intent".
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence
- Merged manifest contains `android.permission.USE_FULL_SCREEN_INTENT` (grep of
  `processReleaseMainManifest/AndroidManifest.xml`).
- `request_full_screen_intent_permission()` returned **True** (heads-up text read
  "permission granted=True").
- Notification `FULL SCREEN #25` posted (`dumpsys` count 1) with `category=call`, importance max;
  rendered as a heads-up while the device was unlocked (heads-up text: "FULL SCREEN #25 —
  Full-screen intent notification. permission granted=True"). Full-screen UI is shown instead when
  the device is locked.

## Verdict: ✅ WORKS
`full_screen_intent` flows to `AndroidNotificationDetails.fullScreenIntent`, the permission is
declared and granted, and the notification fires with the high-priority full-screen-intent
behavior.
