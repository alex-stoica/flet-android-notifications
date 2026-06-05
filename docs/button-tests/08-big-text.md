# Button 8 — Big text style

**Source:** `main.py` `send_big_text` (`BigTextStyle(big_text=<long paragraph>)`)
**Device:** Galaxy S25, One UI, Android 16.

## What it tests
`BigTextStyle` — full paragraph shown when expanded, truncated body when collapsed.

## Result — hard evidence (`dumpsys`)
```
android.title=String (BIG TEXT #8)
android.bigText=String (This is a much longer notification body that demonstrates the
  BigTextStyle. When you expand the notification by swiping down, you should see all of
  this text displayed in full instead of being truncated to a single line. ...)
```
The full big-text string is delivered intact.

## Verdict: ✅ WORKS
`BigTextStyle` delivers the expanded text correctly.
