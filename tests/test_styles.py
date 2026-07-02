"""Contract tests for the notification style payloads sent to Dart.

Pins the to_dict() shapes so a Python-side rename can't silently desync from
the Dart parser in notifications_service.dart.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "flet_android_notifications" / "src"))

from flet_android_notifications import MessagingStyle, NotificationMessage, NotificationPerson


def test_messaging_style_to_dict_shape():
    me = NotificationPerson("Me", key="self")
    alex = NotificationPerson("Alex", icon="avatar", icon_type="file_path", important=True)
    ts = datetime(2026, 7, 2, 12, 0, tzinfo=timezone.utc)

    style = MessagingStyle(
        me,
        conversation_title="Team chat",
        group_conversation=True,
        messages=[
            NotificationMessage("hi", ts, person=alex),
            NotificationMessage("hello back", ts),
        ],
    )

    d = style.to_dict()
    assert d["type"] == "messaging"
    assert d["person"]["name"] == "Me"
    assert d["person"]["key"] == "self"
    assert d["conversation_title"] == "Team chat"
    assert d["group_conversation"] is True
    assert d["messages"][0]["text"] == "hi"
    assert d["messages"][0]["timestamp_ms"] == int(ts.timestamp() * 1000)
    assert d["messages"][0]["person"]["icon"] == "avatar"
    assert d["messages"][0]["person"]["icon_type"] == "file_path"
    assert d["messages"][0]["person"]["important"] is True
    assert d["messages"][1]["person"] is None


def test_person_rejects_unknown_icon_type():
    try:
        NotificationPerson("Me", icon="avatar", icon_type="bitmap")
    except ValueError as e:
        assert "icon_type" in str(e)
    else:
        raise AssertionError("expected ValueError for unknown icon_type")


def test_message_rejects_empty_text():
    try:
        NotificationMessage("", datetime.now())
    except ValueError as e:
        assert "text" in str(e)
    else:
        raise AssertionError("expected ValueError for empty text")


if __name__ == "__main__":
    import traceback

    failures = 0
    for _name, _fn in sorted(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            try:
                _fn()
                print(f"PASS {_name}")
            except Exception:
                failures += 1
                print(f"FAIL {_name}")
                traceback.print_exc()
    print(f"\n{'OK' if not failures else 'FAILURES: ' + str(failures)}")
    raise SystemExit(1 if failures else 0)
