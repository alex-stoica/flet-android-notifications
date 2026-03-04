# Dead ends and lessons — flet-android-notifications

## 1. SERIOUS_PYTHON_SITE_PACKAGES wrong path (biggest time sink)

**Wrong**: `build/flutter/build/build_python_3.12.9/python/Lib/site-packages/`
— this is the build-time Python's own site-packages (just pip).

**Right**: `build/site-packages/`
— created by `flet build apk`, contains per-arch subdirs (arm64-v8a/, etc.) with all app dependencies.

**Symptom**: APK ~3.5MB smaller, app shows "No module named 'certifi'" on error screen. Python exits
in <30ms. Logcat shows `PyRun_SimpleString for script result: 0` which looks like success but isn't —
the wrapper script catches the ImportError and sends exit code 100 via callback socket.

**Why it seemed right**: the path contained "site-packages" and existed. The build didn't error out
because Gradle's zipSitePackages task silently creates an empty zip when the source dir has no
matching arch subdirs.

**Lesson**: always verify the APK contains `libpythonsitepackages.so` and that it's non-trivial size.
Quick check: `python -c "import zipfile; z=zipfile.ZipFile('app.apk'); print([n for n in z.namelist() if 'sitepackages' in n])"`

---

## 2. app.zip patching didn't include main.py

**Wrong**: only patching library .py files in `.venv/Lib/site-packages/flet_android_notifications/`.

**Right**: also replace `main.py` at the zip root with the fresh copy from the project.

**Symptom**: code changes to main.py had no effect on device. The hash didn't change because
the zip content was identical.

**Why it seemed right**: the patch was focused on the library package, and main.py was already
in the zip from `flet build`. Easy to forget that `--skip-flet` means the zip's main.py is stale.

**Lesson**: any `--skip-flet` rebuild must patch ALL Python files that changed, not just library code.

---

## 3. Logcat doesn't show Python errors

`serious_python` redirects Python's stdout/stderr to a file (`console.log` in app cache).
The wrapper script in `python.dart` catches exceptions and writes them there. Logcat only shows
the C-level `PyRun_SimpleString` result (0 = no segfault, not "no error").

**Lesson**: to see Python errors, either:
- Read the error screen text on device (it shows console.log contents)
- Add explicit error logging that writes to a known path
- Don't rely on logcat for Python-level diagnostics

---

## 4. res/raw/ sound files and flutter rebuild

Android raw resources must be compiled into the APK by the Android build system. Simply copying
a file to `build/flutter/android/app/src/main/res/raw/` before `flutter build apk` should work,
BUT the file format matters — Android's notification system expects specific formats and the
resource must be discoverable at `R.raw.filename`.

**Open question**: does WAV work, or does it need to be OGG/MP3? Does the resource get compiled
into the APK correctly?

---

## 5. Samsung OneUI quirks (not bugs in our code)

- **Brief mode** (default notification view) ignores programmatic color — must expand fully
- **Auto-grouping**: Samsung groups notifications by app automatically, which can mask
  explicit groupKey behavior
- **Small icon**: Android renders small icons as single-color silhouettes. Using the same
  drawable as the launcher makes it look identical to default.

---

## 6. Never trust "it compiles therefore it works" on Android

Features like color, grouping, icons, and sound depend on:
- The specific OEM skin (Samsung OneUI, Pixel, etc.)
- Android version
- Notification channel immutability (sound/vibration are set once per channel)
- Resource compilation (drawable vs mipmap, res/raw vs assets)

Always test on actual device and have clear diagnostic output per feature.

---

## 7. flet build editable install (.pth) problem

`flet build apk` with `[tool.flet.dev_packages]` creates an editable install in app.zip.
The `.pth` file points to a Windows host path that doesn't exist on Android. The device
falls back to whatever version is on PyPI.

**Workaround**: patch app.zip to replace .pth + dist-info with actual .py files.
The build.py script automates this.
