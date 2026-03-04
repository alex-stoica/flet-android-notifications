# Build and test log — grouping, icons, color, sound

## SERIOUS_PYTHON_SITE_PACKAGES must point to build/site-packages/

### Problem
When running `flutter build apk` directly (bypassing `flet build`), the
`SERIOUS_PYTHON_SITE_PACKAGES` env var must point to `build/site-packages/` (the parent of
arch dirs like `arm64-v8a/`). The Gradle plugin in `serious_python_android` uses
`$srcDir/$abi` to zip site-packages into `libpythonsitepackages.so`.

### What didn't work
Pointing to `build/flutter/build/build_python_3.12.9/python/Lib/site-packages/` — this is
the build Python's own site-packages (just pip), not the app's packages.

### What worked
`SERIOUS_PYTHON_SITE_PACKAGES=<project>/build/site-packages/` — this dir is created by
`flet build apk` and contains per-arch subdirs with all the Python dependencies.

### Symptoms when wrong
- APK is ~3.5MB smaller (missing `libpythonsitepackages.so`)
- App shows "No module named 'certifi'" on the error screen
- Python starts and exits in <30ms with result 0 (the wrapper script catches the ImportError)
- No obvious error in logcat — `PyRun_SimpleString for script result: 0` looks like success

---


## Build packaging issue (biggest time sink)

### Problem
`flet build apk` with `[tool.flet.dev_packages]` does an **editable install** into the
app.zip venv. The `.pth` file points to a Windows path (`C:\Users\alexs\...`) which doesn't
exist on Android. The device falls back to the PyPI version (v0.1.0) which lacks the new params.

### What didn't work
- `pip install -e flet_android_notifications/` — editable install, same `.pth` problem
- `pip install flet_android_notifications/` — installs locally but flet build creates its own
  isolated venv via uv, ignores system packages
- Relying on `[tool.flet.dev_packages]` alone — broken for mobile builds

### What worked
Patching `app.zip` after flet build: remove the `.pth` redirect and old dist-info, add the
actual `.py` files to `.venv/Lib/site-packages/flet_android_notifications/`. Then rebuild
the Flutter APK using:
```
SERIOUS_PYTHON_SITE_PACKAGES=<build/site-packages path> flutter build apk --release
```
from `build/flutter/`.

### Lesson
Always verify what's inside `app.zip` after `flet build`. The `build/site-packages/` directory
has the correct files, but `app.zip` (which is what runs on device) may not. For dev iteration
the patch-and-rebuild approach is fastest.

---

## Test results on Samsung device (OneUI)

### Color (`color="#FF5722"`)
- **Status**: notification appears, no visible accent color change
- **Root cause**: unknown — need to investigate whether `Color(int.parse(...))` is deprecated
  in the Flutter version used, or if Samsung OneUI overrides accent colors. The
  `AndroidNotificationDetails.color` param should tint the small icon and header.

### Grouping (`group_key`, `set_as_group_summary`)
- **Status**: 3 separate notifications appear, no visible grouping bundle
- **Possible causes**:
  - Samsung OneUI auto-groups by app, may ignore explicit `groupKey`
  - The summary notification might need `InboxStyle` or similar to render correctly
  - The children might need to be posted before the summary (order matters)
  - Need to verify the Dart `groupKey` param is actually reaching `AndroidNotificationDetails`

### Icons (`icon`, `large_icon`)
- **Status**: small icon unchanged from default; large icon not visible
- **Possible causes for small icon**: `ic_launcher_foreground` might not exist as
  `@drawable/ic_launcher_foreground` — the plugin looks in drawable, but flet might put it in
  mipmap only. Also, on Android 13+, the small icon may be overridden by the monochrome icon.
- **Possible causes for large icon**: `DrawableResourceAndroidBitmap("ic_launcher_foreground")`
  may fail silently if the resource isn't in the expected location.

### Sound (`sound="slow_spring_board"`)
- **Status**: `PlatformException(invalid_sound, The resource slow_spring_board could not be
  found. Please make sure it has been added as a raw resource...)`
- **Root cause**: no `res/raw/slow_spring_board.mp3` file exists. This is expected — the sound
  feature works correctly (validates + errors), we just need an actual sound file for testing.
  The error message confirms the Dart → Android plumbing is correct.

### Silent (`play_sound=False, enable_vibration=False`)
- **Status**: works correctly
