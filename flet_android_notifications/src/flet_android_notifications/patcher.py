"""Developer / build-time tooling — NOT used at runtime.

Patches a Flet-generated Android project (`AndroidManifest.xml` + `build.gradle.kts`) so that
`flutter_local_notifications` works: injects the required receivers/service and enables Gradle
core-library desugaring + multidex. `flet build apk` regenerates those files on every run and wipes
the entries, so this must run after each clean build. Used by `build.py` and exposed as the
`flet-android-notifications-patch` CLI. The published runtime wrapper never imports this module.
"""

from __future__ import annotations

import argparse
from pathlib import Path


DESUGAR_DEPENDENCY = 'coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")'


def _manifest_entries(foreground_service_type: str) -> tuple[tuple[str, str], ...]:
    return (
        (
            "com.dexterous.flutterlocalnotifications.ScheduledNotificationReceiver",
            """\
        <receiver android:exported="false"
            android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationReceiver" />
""",
        ),
        (
            "com.dexterous.flutterlocalnotifications.ScheduledNotificationBootReceiver",
            """\
        <receiver android:exported="false"
            android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationBootReceiver">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.intent.action.MY_PACKAGE_REPLACED" />
                <action android:name="android.intent.action.QUICKBOOT_POWERON" />
                <action android:name="com.htc.intent.action.QUICKBOOT_POWERON" />
            </intent-filter>
        </receiver>
""",
        ),
        (
            "com.dexterous.flutterlocalnotifications.ActionBroadcastReceiver",
            """\
        <receiver android:exported="false"
            android:name="com.dexterous.flutterlocalnotifications.ActionBroadcastReceiver" />
""",
        ),
        (
            "com.dexterous.flutterlocalnotifications.ForegroundService",
            f"""\
        <service android:name="com.dexterous.flutterlocalnotifications.ForegroundService"
            android:exported="false"
            android:foregroundServiceType="{foreground_service_type}" />
""",
        ),
    )


def patch_manifest_file(
    manifest_path: str | Path,
    *,
    foreground_service_type: str = "specialUse",
) -> bool:
    path = Path(manifest_path)
    text = path.read_text(encoding="utf-8")
    entries = [
        entry
        for sentinel, entry in _manifest_entries(foreground_service_type)
        if sentinel not in text
    ]
    if not entries:
        return False
    if "</application>" not in text:
        raise ValueError(f"no </application> tag found in {path}")

    patched = text.replace(
        "</application>",
        "".join(entries) + "    </application>",
        1,
    )
    path.write_text(patched, encoding="utf-8")
    return True


def _insert_after_first(text: str, marker: str, addition: str) -> str:
    index = text.find(marker)
    if index == -1:
        raise ValueError(f"cannot find marker {marker!r}")
    insert_at = index + len(marker)
    return text[:insert_at] + addition + text[insert_at:]


def patch_gradle_file(gradle_path: str | Path) -> bool:
    path = Path(gradle_path)
    text = path.read_text(encoding="utf-8")
    patched = text

    if "isCoreLibraryDesugaringEnabled" not in patched:
        if "compileOptions {" in patched:
            patched = _insert_after_first(
                patched,
                "compileOptions {",
                "\n        isCoreLibraryDesugaringEnabled = true",
            )
        elif "android {" in patched:
            patched = _insert_after_first(
                patched,
                "android {",
                "\n    compileOptions {\n        isCoreLibraryDesugaringEnabled = true\n    }\n",
            )
        else:
            raise ValueError(f"cannot find android or compileOptions block in {path}")

    if "multiDexEnabled" not in patched:
        if "defaultConfig {" in patched:
            patched = _insert_after_first(
                patched,
                "defaultConfig {",
                "\n        multiDexEnabled = true",
            )
        else:
            raise ValueError(f"cannot find defaultConfig block in {path}")

    if DESUGAR_DEPENDENCY not in patched:
        if "dependencies {}" in patched:
            patched = patched.replace(
                "dependencies {}",
                f"dependencies {{\n    {DESUGAR_DEPENDENCY}\n}}",
                1,
            )
        elif "dependencies {" in patched:
            patched = _insert_after_first(
                patched,
                "dependencies {",
                f"\n    {DESUGAR_DEPENDENCY}",
            )
        else:
            patched = patched.rstrip() + f"\n\ndependencies {{\n    {DESUGAR_DEPENDENCY}\n}}\n"

    if patched == text:
        return False
    path.write_text(patched, encoding="utf-8")
    return True


def patch_android_project(
    project_root: str | Path = "build/flutter",
    *,
    foreground_service_type: str = "specialUse",
) -> dict[str, bool]:
    root = Path(project_root)
    manifest = root / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
    gradle = root / "android" / "app" / "build.gradle.kts"
    if not manifest.exists():
        raise FileNotFoundError(f"AndroidManifest.xml not found at {manifest}")
    if not gradle.exists():
        raise FileNotFoundError(f"build.gradle.kts not found at {gradle}")
    return {
        "manifest": patch_manifest_file(
            manifest,
            foreground_service_type=foreground_service_type,
        ),
        "gradle": patch_gradle_file(gradle),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Patch a Flet-generated Android project for flet-android-notifications."
    )
    parser.add_argument(
        "--project-root",
        default="build/flutter",
        help="Flet-generated Flutter project root. Default: build/flutter",
    )
    parser.add_argument(
        "--foreground-service-type",
        default="specialUse",
        help="AndroidManifest foregroundServiceType value. Default: specialUse",
    )
    args = parser.parse_args(argv)

    result = patch_android_project(
        args.project_root,
        foreground_service_type=args.foreground_service_type,
    )
    for name, changed in result.items():
        print(f"{name}: {'patched' if changed else 'already patched'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
