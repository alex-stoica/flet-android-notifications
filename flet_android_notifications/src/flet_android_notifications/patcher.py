"""Patch generated Android manifests and Gradle files before building notification apps."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ANDROID = "http://schemas.android.com/apk/res/android"
NAME = f"{{{ANDROID}}}name"
PLUGIN = "com.dexterous.flutterlocalnotifications."
SUBTYPE = "android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE"
SERVICE_TYPES = {
    "camera", "connectedDevice", "dataSync", "health", "location", "mediaPlayback",
    "mediaProcessing", "mediaProjection", "microphone", "phoneCall", "remoteMessaging",
    "shortService", "specialUse", "systemExempted",
}
DESUGAR_DEPENDENCY = 'coreLibraryDesugaring("com.android.tools:desugar_jdk_libs:2.1.4")'


def patch_manifest_file(
    manifest_path: str | Path,
    *,
    foreground_service_type: str | None = None,
    foreground_service_subtype: str = "",
) -> bool:
    path = Path(manifest_path)
    tree = ET.parse(path, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
    manifest = tree.getroot()
    application = manifest.find("application")
    if application is None:
        raise ValueError("Android manifest has no application")
    before = ET.tostring(manifest)
    types = set(foreground_service_type.split("|")) if foreground_service_type is not None else set()
    if types - SERVICE_TYPES:
        raise ValueError("Unsupported foreground service type")
    service = next((s for s in application.findall("service") if s.get(NAME) == PLUGIN + "ForegroundService"), None)
    explanation = foreground_service_subtype.strip()
    if "specialUse" in types and not explanation and service is not None:
        explanation = next((p.get(f"{{{ANDROID}}}value", "").strip() for p in service.findall("property") if p.get(NAME) == SUBTYPE), "")
    if "specialUse" in types and not explanation:
        raise ValueError("specialUse requires an app-specific foreground_service_subtype")
    if foreground_service_subtype and "specialUse" not in types:
        raise ValueError("foreground_service_subtype requires specialUse")
    for name in ("ScheduledNotificationReceiver", "ScheduledNotificationBootReceiver", "ActionBroadcastReceiver"):
        if any(r.get(NAME) == PLUGIN + name for r in application.findall("receiver")):
            continue
        receiver = ET.SubElement(application, "receiver", {NAME: PLUGIN + name, f"{{{ANDROID}}}exported": "false"})
        if name == "ScheduledNotificationBootReceiver":
            intent = ET.SubElement(receiver, "intent-filter")
            for action in ("android.intent.action.BOOT_COMPLETED", "android.intent.action.MY_PACKAGE_REPLACED",
                           "android.intent.action.QUICKBOOT_POWERON", "com.htc.intent.action.QUICKBOOT_POWERON"):
                ET.SubElement(intent, "action", {NAME: action})
    permissions = {"POST_NOTIFICATIONS", "RECEIVE_BOOT_COMPLETED"}
    if types:
        if service is None:
            service = ET.SubElement(application, "service", {NAME: PLUGIN + "ForegroundService"})
        service.set(f"{{{ANDROID}}}exported", "false")
        service.set(f"{{{ANDROID}}}foregroundServiceType", foreground_service_type)
        subtype = next((p for p in service.findall("property") if p.get(NAME) == SUBTYPE), None)
        if "specialUse" in types:
            if subtype is None:
                subtype = ET.SubElement(service, "property", {NAME: SUBTYPE})
            subtype.set(f"{{{ANDROID}}}value", explanation)
        elif subtype is not None:
            service.remove(subtype)
        permissions.add("FOREGROUND_SERVICE")
        for kind in types - {"shortService"}:
            permissions.add("FOREGROUND_SERVICE_" + re.sub(r"([a-z])([A-Z])", r"\1_\2", kind).upper())
    for permission in sorted(permissions):
        name = "android.permission." + permission
        if not any(p.get(NAME) == name for p in manifest.findall("uses-permission")):
            ET.SubElement(manifest, "uses-permission", {NAME: name})
    if ET.tostring(manifest) == before:
        return False
    ET.register_namespace("android", ANDROID)
    ET.register_namespace("tools", "http://schemas.android.com/tools")
    ET.indent(tree, space="    ")
    tree.write(path, encoding="utf-8", xml_declaration=True)
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
    foreground_service_type: str | None = None,
    foreground_service_subtype: str = "",
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
            foreground_service_subtype=foreground_service_subtype,
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
        help="Declare or update a foreground service; omitted preserves existing configuration.",
    )
    parser.add_argument("--foreground-service-subtype", default="",
                        help="App-specific explanation required for specialUse.")
    args = parser.parse_args(argv)

    result = patch_android_project(
        args.project_root,
        foreground_service_type=args.foreground_service_type,
        foreground_service_subtype=args.foreground_service_subtype,
    )
    for name, changed in result.items():
        print(f"{name}: {'patched' if changed else 'already patched'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
