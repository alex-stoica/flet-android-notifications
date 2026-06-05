# Button 3 — Group (3 children + InboxStyle summary)

**Source:** `main.py` `send_group` (3× `show_notification` with `group_key="test_group"`,
`group_alert_behavior="summary"`, + a 4th with `set_as_group_summary=True` and `InboxStyle`)
**Device:** Galaxy S25, One UI, Android 16. Installed release APK.

## What it tests
Explicit notification grouping via `group_key`, plus a custom `InboxStyle` group summary
("3 new messages" / lines Message 1-3).

## How triggered
Foreground app, scroll to top, `adb shell input tap 540 770`; shade swipe to open; tapped the
group chevron to expand.

## Result
- **Collapsed:** a single stack showing the latest child *"Group child 3 (#3) — Grouped message
  3."* with a **"3" count badge**.
- **Expanded:** all three children render individually (Group child 3/2/1, Grouped message 3/2/1)
  under a group header that reads **"flet-android-notifications-demo"** (the app name).

## Verdict: ✅ WORKS (grouping) + 🟡 OEM caveat (custom summary masked)
`group_key` is honored — the children genuinely bundle into one expandable group. **However** the
explicit `InboxStyle` summary ("3 new messages", custom lines) is **not surfaced**: One UI renders
its own native group header (app name) and shows the latest child collapsed, ignoring the
custom-summary content.

## Claim correction
Report said *"One UI auto-grouping may mask explicit groupKey — needs retest"*. Retest result:
**groupKey is NOT masked** (bundling works); what One UI masks is the **custom group-summary
styling**. Phrase as *"explicit grouping works; custom InboxStyle summary content is not rendered
by One UI's native group header"*, not "grouping unsupported".

## Screenshots
- `img/03-group-shade.png` (collapsed, "3" badge)
- `img/03-group-expanded.png` (3 children expanded)
