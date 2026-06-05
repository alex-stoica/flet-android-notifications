# Button 4a — Large icon (thumbnail)

**Source:** `main.py` `send_large_icon` (`show_notification` with `large_icon="splash"`,
`large_icon_type="drawable_resource"`, `icon="ic_notification"`)
**Device:** Galaxy S25, One UI, Android 16. Installed release APK.

## What it tests
The `large_icon` arg — Android renders it as a thumbnail on the right side of the notification.

## How triggered
Foreground + scroll top + `adb shell input tap 540 1000` (calibrated; see note). Read with
`dumpsys notification` + shade screenshot via `adb shell cmd statusbar expand-notifications`.

## Result — hard evidence
`dumpsys notification` record:
```
android.title=String (LARGE ICON #4a)
android.largeIcon=Icon (Icon(typ=BITMAP size=91x91))
numWithLargeIcon=1
```
The `splash` drawable resolved to a real **91×91 bitmap** attached as the large icon. Shade
screenshot shows the thumbnail rendered on the **right side** of the notification.

## Verdict: ✅ WORKS
`large_icon` from a drawable resource renders correctly as a right-side thumbnail on One UI.

## Harness notes (not app bugs)
- Tap calibration runs ~40 px lower than a naive screenshot-fraction estimate for mid-list
  buttons (4a is at y≈1000, not ~950).
- **Open the shade with `adb shell cmd statusbar expand-notifications`, not a swipe** — a
  top-down swipe drag-dismisses the topmost notification.

## Screenshots
- `img/04a-largeicon-shade.png` (thumbnail on right)
