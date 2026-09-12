"""Automated build+deploy script for flet-android-notifications demo.

Pipeline:
  flet build apk
    -> refresh staged Python sources (or legacy app.zip)
    -> copy test resources into res/raw/
    -> flutter build apk --release
    -> adb install -r + launch
"""

import hashlib
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "flet_android_notifications" / "src"))
from flet_android_notifications.patcher import patch_gradle_file, patch_manifest_file

BUILD_FLUTTER = ROOT / "build" / "flutter"
APP_ZIP = BUILD_FLUTTER / "app" / "app.zip"
APP_ZIP_HASH = BUILD_FLUTTER / "app" / "app.zip.hash"
RES_DIR = BUILD_FLUTTER / "android" / "app" / "src" / "main" / "res"
PUBSPEC = BUILD_FLUTTER / "pubspec.yaml"
def _find_flutter() -> Path:
    """Resolve Flutter binary: $FLUTTER_BIN > PATH > latest in ~/flutter/."""
    if env_bin := os.environ.get("FLUTTER_BIN"):
        return Path(env_bin)
    if which_bin := shutil.which("flutter"):
        return Path(which_bin)
    flutter_root = Path.home() / "flutter"
    if flutter_root.is_dir():
        versions = sorted(
            (d for d in flutter_root.iterdir() if d.is_dir() and (d / "bin" / "flutter.bat").exists()),
            key=lambda d: d.name,
        )
        if versions:
            return versions[-1] / "bin" / "flutter.bat"
    print("ERROR: cannot find Flutter. Set FLUTTER_BIN or add flutter to PATH.")
    sys.exit(1)


PACKAGE_SRC = ROOT / "flet_android_notifications" / "src" / "flet_android_notifications"
TEST_RESOURCES = ROOT / "test_resources"
PACKAGE_ID = "com.flet.flet_android_notifications_demo"

DART_SRC = ROOT / "flet_android_notifications" / "src" / "flutter" / "flet_android_notifications"
DART_BUILD = ROOT / "build" / "flutter-packages" / "flet_android_notifications"

ANDROID_MANIFEST = BUILD_FLUTTER / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
APP_GRADLE = BUILD_FLUTTER / "android" / "app" / "build.gradle.kts"

SITE_PKG_PREFIX = ".venv/Lib/site-packages/flet_android_notifications/"


def run(cmd, cwd=None, env=None):
    """Run a command, stream output, and raise on failure."""
    print(f"\n>>> {cmd if isinstance(cmd, str) else ' '.join(str(c) for c in cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=cwd, env=env, shell=isinstance(cmd, str))
    if result.returncode != 0:
        print(f"FAILED with exit code {result.returncode}")
        sys.exit(1)
    return result.returncode


def step_flet_build():
    """Step 1: run flet build apk."""
    print("\n=== Step 1: flet build apk ===")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    with subprocess.Popen(
        "flet build apk -v --no-rich-output --skip-flutter-doctor",
        cwd=str(ROOT), env=env, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
    ) as process:
        output = []
        for line in process.stdout:
            print(line, end="", flush=True)
            output.append(line)
        code = process.wait()
    if code == 0:
        return
    log = re.sub(r"\s+", " ", "".join(output))
    failed_tasks = re.findall(r"Execution failed for task '([^']+)'", log)
    expected = (
        failed_tasks == [":app:checkReleaseAarMetadata"]
        and "Dependency ':flutter_local_notifications' requires core library desugaring to be enabled" in log
        and ANDROID_MANIFEST.is_file() and APP_GRADLE.is_file()
    )
    if not expected:
        raise SystemExit(code)
    print("Continuing to apply the required Android desugaring patch.")


def step_patch_manifest():
    """Step 1b: inject flutter_local_notifications receivers + foreground service into AndroidManifest.

    Required for schedule_notification, periodically_show, and foreground service to fire/run
    at all — not just to survive reboots. flet build wipes AndroidManifest.xml each run.
    """
    print("\n=== Step 1b: patch AndroidManifest.xml ===")
    if not ANDROID_MANIFEST.exists():
        print(f"ERROR: {ANDROID_MANIFEST} not found. Run flet build first.")
        sys.exit(1)
    changed = patch_manifest_file(ANDROID_MANIFEST)
    print(f"  {'injected receivers + foreground service into' if changed else 'already patched'} {ANDROID_MANIFEST.name}")


def step_patch_gradle():
    """Step 1c: enable core library desugaring in app/build.gradle.kts.

    flutter_local_notifications v19+ uses Java 8 APIs that need desugaring. flet build
    regenerates build.gradle.kts each run.
    """
    print("\n=== Step 1c: patch build.gradle.kts (desugaring) ===")
    if not APP_GRADLE.exists():
        print(f"ERROR: {APP_GRADLE} not found. Run flet build first.")
        sys.exit(1)
    changed = patch_gradle_file(APP_GRADLE)
    print(f"  {'enabled desugaring + multidex in' if changed else 'already patched'} {APP_GRADLE.name}")


def step_patch_pubspec_paths():
    """Step 1d: keep generated path dependencies relative to the build directory."""
    print("\n=== Step 1d: patch pubspec path dependencies ===")
    if not PUBSPEC.exists():
        print(f"ERROR: {PUBSPEC} not found. Run flet build first.")
        sys.exit(1)

    desired_path = "../flutter-packages/flet_android_notifications"
    text = PUBSPEC.read_text()
    lines = text.splitlines()
    changed = False

    for index, line in enumerate(lines):
        if line.strip() != "flet_android_notifications:":
            continue
        for path_index in range(index + 1, min(index + 6, len(lines))):
            stripped = lines[path_index].lstrip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("path:"):
                indent = lines[path_index][: len(lines[path_index]) - len(stripped)]
                replacement = f"{indent}path: {desired_path}"
                if lines[path_index] != replacement:
                    lines[path_index] = replacement
                    changed = True
                break
            if not lines[path_index].startswith(" "):
                break
        break

    if changed:
        PUBSPEC.write_text("\n".join(lines) + "\n")
    print(f"  {'rewrote' if changed else 'already relative'} flet_android_notifications path")


def step_patch_app_zip():
    """Refresh Python sources in current or legacy Flet builds."""
    staged_app = ROOT / "build" / "python-app"
    if staged_app.is_dir():
        destinations = list((ROOT / "build" / "site-packages").glob("*/flet_android_notifications"))
        if not destinations:
            raise FileNotFoundError("No staged notification package. Run a full flet build first.")
        _copy_python_sources(ROOT, staged_app, [ROOT / "main.py"])
        for destination in destinations:
            _copy_python_sources(PACKAGE_SRC, destination, PACKAGE_SRC.glob("*.py"))
        print("  refreshed staged Python sources")
        return

    print("\n=== Step 2: patch app.zip ===")
    if not APP_ZIP.exists():
        print(f"ERROR: {APP_ZIP} not found. Run flet build first.")
        sys.exit(1)

    tmp_zip = APP_ZIP.with_suffix(".tmp")

    # files to inject
    py_files = list(PACKAGE_SRC.glob("*.py"))
    print(f"  injecting {len(py_files)} .py files from {PACKAGE_SRC}")

    with zipfile.ZipFile(APP_ZIP, "r") as zin, zipfile.ZipFile(tmp_zip, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            # skip .pth redirects and editable finders for our package
            if "__editable__" in item.filename and "flet_android_notifications" in item.filename:
                print(f"  removing: {item.filename}")
                continue
            # skip old dist-info for flet-android-notifications (not the demo)
            if "flet_android_notifications-" in item.filename and "dist-info" in item.filename:
                # keep the demo dist-info, skip the library one
                if "demo" not in item.filename:
                    print(f"  removing: {item.filename}")
                    continue
            # skip existing package .py files (we'll re-add fresh copies)
            if item.filename.startswith(SITE_PKG_PREFIX) and item.filename.endswith(".py"):
                print(f"  replacing: {item.filename}")
                continue
            # replace main.py with fresh copy from project root
            if item.filename == "main.py":
                print(f"  replacing: main.py")
                continue
            zout.writestr(item, zin.read(item.filename))

        # add fresh main.py from project root
        main_py = ROOT / "main.py"
        if main_py.exists():
            print(f"  adding: main.py (from project root)")
            zout.write(main_py, "main.py")

        # add fresh .py files
        for py_file in py_files:
            arcname = SITE_PKG_PREFIX + py_file.name
            print(f"  adding: {arcname}")
            zout.write(py_file, arcname)

    tmp_zip.replace(APP_ZIP)
    print("  app.zip patched successfully")

    # also patch site-packages arch dirs so SERIOUS_PYTHON_SITE_PACKAGES doesn't override with stale copies
    site_packages = ROOT / "build" / "site-packages"
    if site_packages.exists():
        for arch_pkg_dir in site_packages.glob("*/flet_android_notifications"):
            if arch_pkg_dir.is_dir():
                for py_file in py_files:
                    dest = arch_pkg_dir / py_file.name
                    shutil.copy2(py_file, dest)
                print(f"  patched site-packages: {arch_pkg_dir.parent.name}")


def _copy_python_sources(source_dir, destination_dir, sources):
    for source in sources:
        destination = destination_dir / source.relative_to(source_dir)
        shutil.copy2(source, destination)
        # Flet can leave sourceless bytecode beside the refreshed source.
        destination.with_suffix(".pyc").unlink(missing_ok=True)


def step_update_hash():
    """Step 3: regenerate app.zip.hash."""
    if (ROOT / "build" / "python-app").is_dir():
        return
    print("\n=== Step 3: regenerate app.zip.hash ===")
    sha256 = hashlib.sha256(APP_ZIP.read_bytes()).hexdigest()
    APP_ZIP_HASH.write_text(sha256)
    print(f"  hash: {sha256}")


def step_copy_test_resources():
    """Step 4: copy test resources (sounds, drawables) and add keep rules."""
    print("\n=== Step 4: copy test resources ===")
    raw_dir = RES_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    drawable_dir = RES_DIR / "drawable"
    drawable_dir.mkdir(parents=True, exist_ok=True)

    # copy sound files to res/raw/
    for f in TEST_RESOURCES.iterdir():
        if f.is_file() and f.suffix in (".wav", ".mp3", ".ogg"):
            dest = raw_dir / f.name
            shutil.copy2(f, dest)
            print(f"  copied: {f.name} -> {dest}")

    # Copy vector and bitmap notification icons to res/drawable/.
    for f in TEST_RESOURCES.iterdir():
        if f.is_file() and f.suffix in (".xml", ".png"):
            dest = drawable_dir / f.name
            shutil.copy2(f, dest)
            print(f"  copied: {f.name} -> {dest}")

    # add keep.xml to prevent aapt2 from stripping unreferenced resources
    keep_xml = raw_dir / "keep.xml"
    keep_xml.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<resources xmlns:tools="http://schemas.android.com/tools"\n'
        '    tools:keep="@raw/*,@drawable/ic_*" />\n'
    )
    print(f"  created: {keep_xml}")


def step_copy_dart_source():
    """Step 5: copy updated Dart source to build/flutter-packages/."""
    print("\n=== Step 5: copy Dart source ===")
    if not DART_BUILD.exists():
        print(f"  skipping — {DART_BUILD} not found (run full flet build first)")
        return
    pubspec = DART_SRC / "pubspec.yaml"
    if pubspec.exists():
        shutil.copy2(pubspec, DART_BUILD / "pubspec.yaml")
        print("  copied: pubspec.yaml")
    for dart_file in (DART_SRC / "lib").rglob("*.dart"):
        rel = dart_file.relative_to(DART_SRC)
        dest = DART_BUILD / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dart_file, dest)
        print(f"  copied: {rel}")


def step_flutter_build():
    """Step 6: flutter build apk --release."""
    print("\n=== Step 6: flutter build apk --release ===")
    # SERIOUS_PYTHON_SITE_PACKAGES must point to the parent of arch dirs (arm64-v8a/, etc.)
    # flet build creates this at build/site-packages/
    site_packages = ROOT / "build" / "site-packages"
    if not site_packages.exists():
        print(f"ERROR: {site_packages} not found. Run flet build first.")
        sys.exit(1)

    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    env["SERIOUS_PYTHON_SITE_PACKAGES"] = str(site_packages)
    print(f"  SERIOUS_PYTHON_SITE_PACKAGES={site_packages}")

    run([str(_find_flutter()), "build", "apk", "--release"], cwd=str(BUILD_FLUTTER), env=env)


def step_install():
    """Install an update without erasing app data, then launch."""
    print("\n=== Step 7: install on device ===")
    apk = BUILD_FLUTTER / "build" / "app" / "outputs" / "flutter-apk" / "app-release.apk"
    if not apk.exists():
        print(f"ERROR: APK not found at {apk}")
        sys.exit(1)

    run(["adb", "install", "-r", str(apk)])
    print("  installed successfully")

    # launch
    run(["adb", "shell", "monkey", "-p", PACKAGE_ID, "-c", "android.intent.category.LAUNCHER", "1"])
    print("  launched app")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Build and deploy flet-android-notifications demo")
    parser.add_argument("--skip-flet", action="store_true", help="skip flet build apk (reuse existing build dir)")
    parser.add_argument("--skip-install", action="store_true", help="skip adb install + launch")
    args = parser.parse_args()

    if not args.skip_flet:
        step_flet_build()

    step_patch_manifest()
    step_patch_gradle()
    step_patch_pubspec_paths()
    step_patch_app_zip()
    step_update_hash()
    step_copy_test_resources()
    step_copy_dart_source()
    step_flutter_build()

    if not args.skip_install:
        step_install()

    print("\n=== DONE ===")


if __name__ == "__main__":
    main()
