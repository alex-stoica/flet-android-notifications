# Button 1 — Baseline (no new params)

**Source:** `main.py` `send_baseline` (`show_notification` with only id/title/body)
**Device:** Samsung Galaxy S25 (SM-S931B), One UI, Android 16. Installed release APK (no rebuild).

## What it tests
The minimal happy path: a plain `show_notification` with default channel, default importance
(`high`), no styling. Establishes that the wrapper → Dart → `flutter_local_notifications.show`
pipeline reaches the system tray at all.

## How triggered
`adb shell input tap 540 328` (button at top of list), 2 s settle, then capture app + shade.

## Result
- **In-app log / heads-up:** a heads-up banner appeared over the app reading
  *"Baseline #1 — No new params, just a regular notification."* (importance high → heads-up).
- **Shade (collapsed):** `Baseline #1`, timestamp 16:06, body *"No new params, just a regular
  notification."*, app default small icon, expandable chevron present.

## Verdict: ✅ WORKS
Fires reliably, renders correctly on One UI.

## Claim note
The small icon shows a red accent. Per `insights/errors.md`, this red is **intrinsic to the
`ic_launcher` artwork**, not an Android-applied tint — important baseline for judging the `color`
claim on buttons 2 and the Samsung audit. A baseline notification with no `color` set already looks
"reddish" because of the icon art.

## Screenshots
- `img/01-baseline-app.png` (heads-up over app)
- `img/01-baseline-shade.png` (shade)
