"""Check manifest updates and Gradle configuration against generated Android fixtures."""

import sys
import xml.etree.ElementTree as ET
import pytest
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
    assert patch_manifest_file(m, foreground_service_type="specialUse",
                               foreground_service_subtype="User-started demonstration") is True
    text = m.read_text(encoding="utf-8")
    for sentinel in _REQUIRED:
        assert sentinel in text, f"missing {sentinel}"
    # original content is preserved and entries land inside <application>
    assert ".MainActivity" in text
    assert 'android:foregroundServiceType="specialUse"' in text
    assert text.index("ForegroundService") < text.index("</application>")
    assert patch_manifest_file(m, foreground_service_type="specialUse") is False


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


def test_default_preserves_existing_service_without_creating_one(tmp_path):
    path = tmp_path / "AndroidManifest.xml"
    path.write_text(MANIFEST)
    patch_manifest_file(path)
    assert "ForegroundService" not in path.read_text()
    patch_manifest_file(path, foreground_service_type="location")
    assert patch_manifest_file(path) is False
    assert 'foregroundServiceType="location"' in path.read_text()


def test_service_type_change_preserves_other_components(tmp_path):
    path = tmp_path / "AndroidManifest.xml"
    path.write_text(MANIFEST.replace("</application>", '<service android:name="other.Service" /></application>'))
    patch_manifest_file(path, foreground_service_type="specialUse", foreground_service_subtype="Timer demonstration")
    assert patch_manifest_file(path, foreground_service_type="location|microphone")
    text = path.read_text()
    assert 'foregroundServiceType="location|microphone"' in text
    assert "PROPERTY_SPECIAL_USE_FGS_SUBTYPE" not in text
    assert 'android:name="other.Service"' in text
    assert "android.permission.FOREGROUND_SERVICE_LOCATION" in text
    assert "android.permission.FOREGROUND_SERVICE_MICROPHONE" in text
    assert not patch_manifest_file(path, foreground_service_type="location|microphone")


def test_special_use_explanation_updates_and_escapes(tmp_path):
    path = tmp_path / "AndroidManifest.xml"
    path.write_text(MANIFEST)
    for explanation in ("Timer demo", 'User starts A & B "timers"'):
        assert patch_manifest_file(path, foreground_service_type="specialUse", foreground_service_subtype=explanation)
        prop = ET.parse(path).find("application/service/property")
        assert prop.get("{http://schemas.android.com/apk/res/android}value") == explanation
        assert not patch_manifest_file(path, foreground_service_type="specialUse", foreground_service_subtype=explanation)


@pytest.mark.parametrize("kind,subtype", [("specialUse", ""), ("specialUse", "  "), ("invalid", ""), ("", ""), (None, "unused")])
def test_invalid_service_configuration_leaves_file_untouched(tmp_path, kind, subtype):
    path = tmp_path / "AndroidManifest.xml"
    path.write_text(MANIFEST)
    with pytest.raises(ValueError):
        patch_manifest_file(path, foreground_service_type=kind, foreground_service_subtype=subtype)
    assert path.read_text() == MANIFEST


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
