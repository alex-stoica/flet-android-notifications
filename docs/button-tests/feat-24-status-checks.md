# Feature 24 (Phase B) — Permission / status checks

**New API:** `are_notifications_enabled()`, `can_schedule_exact_notifications()`,
`request_full_screen_intent_permission()` (see button 25).
**Demo button:** 24 "Check status (perms/exact)".
**Device:** Galaxy S25, One UI, Android 16. Freshly built/installed APK (Phase B).

## Why
The report flagged that the wrapper had no way to check `areNotificationsEnabled()` /
`canScheduleExactNotifications()`, so a suppressed notification could be wrongly blamed on Samsung.
These checks make the real cause observable.

## Result — on-device, two states
- **Right after `build.py` install** (plain `adb install`, no `-g`):
  `notifications_enabled=False, can_schedule_exact=False`. The check correctly reports that
  POST_NOTIFICATIONS was never granted.
- **After `adb shell pm grant ... POST_NOTIFICATIONS`:**
  `notifications_enabled=True, can_schedule_exact=False`.

So `are_notifications_enabled()` flips False→True with the real permission state, and
`can_schedule_exact_notifications()` reports False because SCHEDULE_EXACT_ALARM is a special,
non-grantable-by-adb permission and was not toggled (consistent with button 27 failing on exact
mode).

## Verdict: ✅ WORKS
Both status methods return accurate, state-tracking values. Use them before blaming the OEM.

## DND policy access (added after review)
The report's `hasNotificationPolicyAccess()` / `requestNotificationPolicyAccess()` **do** exist in
`flutter_local_notifications` v21 (`AndroidFlutterLocalNotificationsPlugin`, lines 223/234) — an
earlier draft of these docs wrongly said they did not. They are now exposed as
`has_notification_policy_access()` and `request_notification_policy_access()` and surfaced in the
demo (button 24 reports `dnd_policy_access=...`; button 24b opens the DND-access settings screen).
This closes the DND-bypass gap: `channel_bypass_dnd` only works with policy access, and the app can
now check/request it. See `../samsung-claims-audit.md` (DND-bypass note).
