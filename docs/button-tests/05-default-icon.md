# Button 5 — Default icon (contrast)

**Source:** `main.py` `send_small_icon` (`show_notification` with no `icon` → app launcher icon)
**Device:** Galaxy S25, One UI, Android 16.

## What it tests
A notification with no `icon` override, so Android uses the default launcher small icon — for
visual contrast against the bell (`ic_notification`) used elsewhere.

## Result — hard evidence (`dumpsys`)
`android.title=String (DEFAULT ICON #5)` — posts correctly with the default small icon.

## Verdict: ✅ WORKS
Posts with the launcher icon as expected. (Comparison point only; nothing OEM-specific.)
