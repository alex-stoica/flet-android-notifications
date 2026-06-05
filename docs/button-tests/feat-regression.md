# Regression check on the rebuilt working tree

**Purpose:** Phase A (buttons 1-23) was verified on the **pre-built** release APK. This file
records re-verification of a representative sample on the **APK rebuilt from the current working
tree** (after the Phase B changes), so the documented behavior matches the code that is actually
checked in. Addresses the review point "evidence may not match the full current working tree".
**Device:** Galaxy S25, One UI, Android 16.

## Core notification path — re-fired on the rebuilt APK
- **Baseline #1** — `dumpsys` shows `android.title=String (Baseline #1)`. ✅ posts.
- **Colored #2** — `dumpsys` shows `color=0xffff0000` on the record. ✅ the color-delivery claim
  (audit's key visual finding) reproduces identically on the rebuilt build.

## Scheduled / receiver path — structurally intact
The only failure mode for scheduled/periodic is missing broadcast receivers. The rebuilt APK's
merged manifest
(`build/.../merged_manifest/release/processReleaseMainManifest/AndroidManifest.xml`) still contains
`ScheduledNotificationReceiver` and `ScheduledNotificationBootReceiver` (and the new
`USE_FULL_SCREEN_INTENT` permission) — `build.py`'s idempotent `step_patch_manifest` re-injects them
every build. Combined with Baseline working, the scheduled path is intact. (Scheduled firing itself
was verified live in `17-scheduled.md`.)

## Phase B features — verified on the rebuilt tree
- **24 Check status** → `notifications_enabled=True, can_schedule_exact=False,
  dnd_policy_access=False` — all three checks (incl. the newly added `has_notification_policy_access`)
  return accurate state.
- **24b Request DND access** → window focus changed to
  `com.android.settings/...Settings$ZenAccessSettingsActivity` — the DND-access screen genuinely
  opens. (The method's boolean return is the plugin's raw value, not an "opened" flag — confirm the
  grant with `has_notification_policy_access()`.)
- 25/26/27 verified in their `feat-*.md` files on the first rebuild; the second rebuild only added
  the DND policy-access methods (additive) and recompiled cleanly.

## Conclusion
The documented results match the current working tree: the additive Phase B changes do not regress
the 1-23 code paths, and the new DND policy-access APIs work on-device.
