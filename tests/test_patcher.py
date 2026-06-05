"""Fixture tests for the AndroidManifest.xml / build.gradle.kts patcher.

The patcher does sentinel-string text insertion on the Flet-generated Android template, which is
brittle if the template shape changes. These tests pin the expected behavior against representative
fixtures so a template/plugin change that breaks patching is caught here instead of mid-build.

Runs under pytest (uses the tmp_path fixture) or standalone: `python tests/test_patcher.py`.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "flet_android_notifications" / "src"))

from flet_android_notifications.patcher import patch_manifest_file, patch_gradle_file

# Representative slices of the Flet-generated template.
MANIFEST = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <application android:label="demo" android:icon="@mipmap/ic_launcher">
        <activity android:name=".MainActivity" android:exported="true" />
    </application>
</manifest>
"""

GRADLE = """plugins { id("com.android.application") }
android {
    namespace = "com.flet.demo"
    compileSdk = 36
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
    }
    defaultConfig {
        applicationId = "com.flet.demo"
        minSdk = 21
        targetSdk = 36
    }
}
dependencies {}
"""

_REQUIRED = (
    "com.dexterous.flutterlocalnotifications.ScheduledNotificationReceiver",
    "com.dexterous.flutterlocalnotifications.ScheduledNotificationBootReceiver",
    "com.dexterous.flutterlocalnotifications.ActionBroadcastReceiver",
    "com.dexterous.flutterlocalnotifications.ForegroundService",
)


def test_manifest_injects_all_required_entries(tmp_path):
    m = tmp_path / "AndroidManifest.xml"
    m.write_text(MANIFEST, encoding="utf-8")
    assert patch_manifest_file(m) is True
    text = m.read_text(encoding="utf-8")
    for sentinel in _REQUIRED:
        assert sentinel in text, f"missing {sentinel}"
    # original content is preserved and entries land inside <application>
    assert ".MainActivity" in text
    assert 'android:foregroundServiceType="specialUse"' in text
    assert text.index("ForegroundService") < text.index("</application>")


def test_manifest_idempotent(tmp_path):
    m = tmp_path / "AndroidManifest.xml"
    m.write_text(MANIFEST, encoding="utf-8")
    assert patch_manifest_file(m) is True
    after_first = m.read_text(encoding="utf-8")
    assert patch_manifest_file(m) is False  # nothing left to add
    assert m.read_text(encoding="utf-8") == after_first  # byte-identical


def test_manifest_only_adds_missing_no_duplicates(tmp_path):
    # Template already contains ForegroundService; the other three must be added,
    # and ForegroundService must not be duplicated.
    partial = MANIFEST.replace(
        "</application>",
        '    <service android:name='
        '"com.dexterous.flutterlocalnotifications.ForegroundService" />\n    </application>',
    )
    m = tmp_path / "AndroidManifest.xml"
    m.write_text(partial, encoding="utf-8")
    assert patch_manifest_file(m) is True
    text = m.read_text(encoding="utf-8")
    assert text.count(
        "com.dexterous.flutterlocalnotifications.ForegroundService"
    ) == 1
    assert "com.dexterous.flutterlocalnotifications.ScheduledNotificationReceiver" in text


def test_manifest_missing_application_tag_raises(tmp_path):
    m = tmp_path / "AndroidManifest.xml"
    m.write_text("<manifest></manifest>", encoding="utf-8")
    raised = False
    try:
        patch_manifest_file(m)
    except ValueError:
        raised = True
    assert raised, "expected ValueError when </application> is absent"


def test_manifest_custom_foreground_service_type(tmp_path):
    m = tmp_path / "AndroidManifest.xml"
    m.write_text(MANIFEST, encoding="utf-8")
    assert patch_manifest_file(m, foreground_service_type="location") is True
    assert 'android:foregroundServiceType="location"' in m.read_text(encoding="utf-8")


def test_gradle_enables_desugaring_multidex_and_dependency(tmp_path):
    g = tmp_path / "build.gradle.kts"
    g.write_text(GRADLE, encoding="utf-8")
    assert patch_gradle_file(g) is True
    text = g.read_text(encoding="utf-8")
    assert "isCoreLibraryDesugaringEnabled = true" in text
    assert "multiDexEnabled = true" in text
    assert "coreLibraryDesugaring(\"com.android.tools:desugar_jdk_libs" in text


def test_gradle_idempotent(tmp_path):
    g = tmp_path / "build.gradle.kts"
    g.write_text(GRADLE, encoding="utf-8")
    assert patch_gradle_file(g) is True
    after_first = g.read_text(encoding="utf-8")
    assert patch_gradle_file(g) is False
    assert g.read_text(encoding="utf-8") == after_first


def test_gradle_without_compileoptions_block(tmp_path):
    # If the template has no compileOptions block, the patcher must create one.
    gradle = GRADLE.replace(
        "    compileOptions {\n        sourceCompatibility = JavaVersion.VERSION_11\n    }\n", ""
    )
    g = tmp_path / "build.gradle.kts"
    g.write_text(gradle, encoding="utf-8")
    assert patch_gradle_file(g) is True
    text = g.read_text(encoding="utf-8")
    assert "compileOptions {" in text
    assert "isCoreLibraryDesugaringEnabled = true" in text


if __name__ == "__main__":
    import tempfile
    import traceback

    failures = 0
    for _name, _fn in sorted(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            _dir = Path(tempfile.mkdtemp())
            try:
                _fn(_dir)
                print(f"PASS {_name}")
            except Exception:
                failures += 1
                print(f"FAIL {_name}")
                traceback.print_exc()
    print(f"\n{'OK' if not failures else 'FAILURES: ' + str(failures)}")
    raise SystemExit(1 if failures else 0)
