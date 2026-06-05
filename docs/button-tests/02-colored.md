# Button 2 — Colored (pure red)

**Source:** `main.py` `send_colored` (`show_notification` with `color="#FF0000"`, `icon="ic_notification"`)
**Device:** Samsung Galaxy S25 (SM-S931B), One UI, Android 16. Installed release APK.

## What it tests
Whether the `color` arg paints a visible accent on a regular notification.

## How triggered
`adb shell input tap 540 510`, then `adb shell dumpsys notification --noredact` to read the
actual `color=` value the OS received, plus a shade screenshot to judge visible rendering.

## Result — hard evidence
`dumpsys notification` for our package:
- **COLORED #2 (id=2):** `Notification(... color=0xffff0000 ...)` — the red **reaches Android**.
- **Baseline #1 (id=1):** `Notification(... color=0x00000000 ...)` — no color, as expected.

Shade screenshot: COLORED #2 looks **identical** to the baseline — black title/body on white,
same red bell small-icon. The red on the icon is the **intrinsic `ic_notification` artwork**, not
an OS tint (baseline, with `color=0x0`, shows the same red icon).

## Verdict: 🟡 PARTIAL / OEM-dependent (NOT "unsupported on Samsung")
The value is delivered correctly to the OS (proven: `color=0xffff0000`). Samsung One UI **Brief
mode** simply does not render an accent tint for regular notifications. AOSP/Pixel does. So the
correct phrasing is *"color is delivered but not reliably rendered on tested One UI Brief mode"*,
never *"unsupported on Samsung"*.

## Bonus finding (feeds the grouping audit)
With two notifications present, the dump shows Android created an
`AUTOGROUP_SUMMARY` / `g:Aggregate_NormalNotificationSection` automatically — One UI auto-grouped
them with a "2" badge **without any explicit `group_key`**. This is the auto-grouping behavior to
keep in mind for button 3.

## Screenshots
- `img/02-colored-shade.png`
