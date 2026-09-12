import sys
import io
import zipfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setattr(build, "ROOT", tmp_path)
    monkeypatch.setattr(build, "BUILD_FLUTTER", tmp_path / "build/flutter")
    monkeypatch.setattr(build, "PACKAGE_SRC", tmp_path / "package")
    monkeypatch.setattr(build, "APP_ZIP", tmp_path / "build/flutter/app/app.zip")
    monkeypatch.setattr(build, "APP_ZIP_HASH", tmp_path / "build/flutter/app/app.zip.hash")
    (tmp_path / "package").mkdir()
    (tmp_path / "package/__init__.py").write_text("VERSION = 'new'")
    (tmp_path / "main.py").write_text("print('new demo')")
    return tmp_path


DESUGARING_FAILURE = (
    "Execution failed for task ':app:checkReleaseAarMetadata'.\n"
    "Dependency ':flutter_local_notifications' requires core library\n"
    "desugaring to be enabled for :app.\n"
)


@pytest.mark.parametrize("code,output,generated,allowed", [
    (0, "Built APK", False, True),
    (1, DESUGARING_FAILURE, True, True),
    (1, DESUGARING_FAILURE, False, False),
    (1, "Could not resolve dependencies", True, False),
    (1, "Execution failed for task ':app:compileReleaseKotlin'.", True, False),
    (1, DESUGARING_FAILURE + "Execution failed for task ':other:compile'.", True, False),
])
def test_initial_build_only_tolerates_known_patchable_failure(
    project, monkeypatch, code, output, generated, allowed,
):
    manifest = project / "AndroidManifest.xml"
    gradle = project / "build.gradle.kts"
    monkeypatch.setattr(build, "ANDROID_MANIFEST", manifest)
    monkeypatch.setattr(build, "APP_GRADLE", gradle)
    if generated:
        manifest.touch()
        gradle.touch()
    process = MagicMock()
    process.__enter__.return_value = process
    process.stdout = io.StringIO(output)
    process.wait.return_value = code
    monkeypatch.setattr(build.subprocess, "Popen", lambda *args, **kwargs: process)
    if allowed:
        build.step_flet_build()
    else:
        with pytest.raises(SystemExit) as error:
            build.step_flet_build()
        assert error.value.code == code


def test_current_staging_refreshes_source_without_legacy_zip(project):
    staged = project / "build/python-app"
    staged.mkdir(parents=True)
    (staged / "main.pyc").write_bytes(b"old bytecode")
    for arch in ("arm64-v8a", "x86_64"):
        package = project / "build/site-packages" / arch / "flet_android_notifications"
        package.mkdir(parents=True)
        (package / "__init__.pyc").write_bytes(b"old bytecode")
    build.step_patch_app_zip()
    build.step_update_hash()
    assert (staged / "main.py").read_text() == "print('new demo')"
    assert not (staged / "main.pyc").exists()
    for package in (project / "build/site-packages").glob("*/flet_android_notifications"):
        assert (package / "__init__.py").read_text() == "VERSION = 'new'"
        assert not (package / "__init__.pyc").exists()


def test_incomplete_staging_fails_before_modifying_source(project):
    staged = project / "build/python-app"
    staged.mkdir(parents=True)
    with pytest.raises(FileNotFoundError, match="full flet build"):
        build.step_patch_app_zip()
    assert not (staged / "main.py").exists()


def test_legacy_zip_still_refreshes_source_and_hash(project):
    build.APP_ZIP.parent.mkdir(parents=True)
    with zipfile.ZipFile(build.APP_ZIP, "w") as archive:
        archive.writestr("main.py", "old")
        archive.writestr("assets/keep.txt", "keep")
    build.step_patch_app_zip()
    build.step_update_hash()
    with zipfile.ZipFile(build.APP_ZIP) as archive:
        assert archive.read("main.py") == b"print('new demo')"
        assert archive.read("assets/keep.txt") == b"keep"
        assert archive.read(build.SITE_PKG_PREFIX + "__init__.py") == b"VERSION = 'new'"
    assert len(build.APP_ZIP_HASH.read_text()) == 64


def test_dart_copy_excludes_tests_and_generated_files(project, monkeypatch):
    source = project / "dart"
    destination = project / "build/flutter-packages/notifications"
    destination.mkdir(parents=True)
    for name in ("lib/extension.dart", "test/test.dart", ".dart_tool/generated.dart"):
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("// fixture")
    (source / "pubspec.yaml").write_text("name: notifications")
    monkeypatch.setattr(build, "DART_SRC", source)
    monkeypatch.setattr(build, "DART_BUILD", destination)
    build.step_copy_dart_source()
    assert (destination / "lib/extension.dart").exists()
    assert (destination / "pubspec.yaml").exists()
    assert not (destination / "test").exists()
    assert not (destination / ".dart_tool").exists()


def test_install_preserves_data_and_does_not_launch_after_failure(project, monkeypatch):
    apk = build.BUILD_FLUTTER / "build/app/outputs/flutter-apk/app-release.apk"
    apk.parent.mkdir(parents=True)
    apk.touch()
    calls = []
    monkeypatch.setattr(build, "run", lambda cmd: calls.append(cmd))
    build.step_install()
    assert calls[0] == ["adb", "install", "-r", str(apk)]
    assert len(calls) == 2
    assert all("uninstall" not in cmd for cmd in calls)

    calls.clear()
    def fail(cmd):
        calls.append(cmd)
        raise SystemExit(1)
    monkeypatch.setattr(build, "run", fail)
    with pytest.raises(SystemExit):
        build.step_install()
    assert len(calls) == 1
