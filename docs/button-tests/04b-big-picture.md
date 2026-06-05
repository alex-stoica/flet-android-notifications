# Button 4b — Big picture (full-width)

**Source:** `main.py` `send_big_picture` (`BigPictureStyle(drawable_resource="splash")`)
**Device:** Galaxy S25, One UI, Android 16. Installed release APK.

## What it tests
`BigPictureStyle` — a full-width image shown when the notification is expanded.

## Result — hard evidence (`dumpsys notification`)
```
android.title=String (BIG PICTURE #4b)
android.picture=Bitmap (726x838)
numWithBigPicture=1
```
The `splash` drawable resolved to a **726×838 big-picture bitmap** attached to the notification.

## Verdict: ✅ WORKS
`BigPictureStyle` delivers the image to the OS; it renders full-width on expand (standard One UI
big-picture layout).

## Screenshots
- `img/04b-bigpicture-shade.png` (shade state during test)
