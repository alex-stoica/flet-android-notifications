"""Diagnostic test app for all notification features.

Each button tests a single feature. Status text shows OK/FAIL + notification ID.
Instructions under each button explain what to look for on the device.
"""

import asyncio
import json
import traceback
from datetime import datetime, timedelta
import flet as ft
from flet_android_notifications import (
    FletAndroidNotifications,
    InboxStyle,
    BigPictureStyle,
    BigTextStyle,
)


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    notifications = FletAndroidNotifications()
    notif_id = 0

    def next_id():
        nonlocal notif_id
        notif_id += 1
        return notif_id

    log = ft.Text("ready", selectable=True, size=12)

    def set_log(msg):
        log.value = msg
        page.update()

    def on_tap(e):
        set_log(f"TAP event: {e.data}")

    notifications.on_notification_tap = on_tap

    async def request(e):
        granted = await notifications.request_permissions()
        set_log(f"permissions: {'granted' if granted else 'denied'}")

    # -- 1. baseline: plain notification --
    async def send_baseline(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="Baseline #1",
                body="No new params, just a regular notification.",
            )
            set_log(f"OK baseline #1 (id={nid})")
        except Exception as ex:
            set_log(f"FAIL baseline: {type(ex).__name__}: {ex}\n{traceback.format_exc()}")

    # -- 2. color (pure red for max visibility) --
    async def send_colored(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="COLORED #2",
                body="Should have RED accent color on small icon.",
                color="#FF0000",
                icon="ic_notification",
            )
            set_log(f"OK colored #2 (id={nid})")
        except Exception as ex:
            set_log(f"FAIL colored: {type(ex).__name__}: {ex}")

    # -- 3. grouping with InboxStyle summary --
    async def send_group(e):
        try:
            await notifications.cancel_all()
            ids = []
            for i in range(3):
                nid = next_id()
                ids.append(nid)
                await notifications.show_notification(
                    notification_id=nid,
                    title=f"Group child {i + 1} (#3)",
                    body=f"Grouped message {i + 1}.",
                    group_key="test_group",
                    group_alert_behavior="summary",
                    icon="ic_notification",
                )
            nid = next_id()
            ids.append(nid)
            await notifications.show_notification(
                notification_id=nid,
                title="GROUP SUMMARY #3",
                body="You have 3 messages.",
                group_key="test_group",
                set_as_group_summary=True,
                style=InboxStyle(
                    lines=["Message 1", "Message 2", "Message 3"],
                    content_title="3 new messages",
                    summary_text="test_group",
                ),
                icon="ic_notification",
            )
            set_log(f"OK group #3 (ids={ids})")
        except Exception as ex:
            set_log(f"FAIL group: {type(ex).__name__}: {ex}")

    # -- 4a. large icon (thumbnail) --
    async def send_large_icon(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="LARGE ICON #4a",
                body="Small thumbnail on right side (Android large_icon is always a thumbnail).",
                large_icon="splash",
                large_icon_type="drawable_resource",
                icon="ic_notification",
            )
            set_log(f"OK large icon #4a (id={nid})")
        except Exception as ex:
            set_log(f"FAIL large icon: {type(ex).__name__}: {ex}")

    # -- 4b. big picture style --
    async def send_big_picture(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="BIG PICTURE #4b",
                body="Expand to see full-width image.",
                style=BigPictureStyle(
                    drawable_resource="splash",
                    content_title="Big picture — expanded",
                    summary_text="full-width image from splash drawable",
                ),
                icon="ic_notification",
            )
            set_log(f"OK big picture #4b (id={nid})")
        except Exception as ex:
            set_log(f"FAIL big picture: {type(ex).__name__}: {ex}")

    # -- 5. default small icon contrast test --
    async def send_small_icon(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="DEFAULT ICON #5",
                body="Uses default launcher icon — compare with bell on other notifications.",
            )
            set_log(f"OK default icon #5 (id={nid})")
        except Exception as ex:
            set_log(f"FAIL default icon: {type(ex).__name__}: {ex}")

    # -- 6. custom sound --
    async def send_sound(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="SOUND #6",
                body="Should play a short 880Hz beep.",
                sound="test_beep",
                channel_id="beep_channel",
                channel_name="Beep Channel",
                icon="ic_notification",
            )
            set_log(f"OK sound #6 (id={nid})")
        except Exception as ex:
            set_log(f"FAIL sound: {type(ex).__name__}: {ex}")

    # -- 7. silent --
    async def send_silent(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="SILENT #7",
                body="No sound, no vibration.",
                play_sound=False,
                enable_vibration=False,
                channel_id="silent_ch",
                channel_name="Silent",
                icon="ic_notification",
            )
            set_log(f"OK silent #7 (id={nid})")
        except Exception as ex:
            set_log(f"FAIL silent: {type(ex).__name__}: {ex}")

    # -- 8. big text style --
    async def send_big_text(e):
        try:
            nid = next_id()
            long_text = (
                "This is a much longer notification body that demonstrates the BigTextStyle. "
                "When you expand the notification by swiping down, you should see all of this text "
                "displayed in full instead of being truncated to a single line. "
                "This is useful for showing email previews, long messages, or detailed alerts."
            )
            await notifications.show_notification(
                notification_id=nid,
                title="BIG TEXT #8",
                body="Expand to read the full message...",
                style=BigTextStyle(
                    big_text=long_text,
                    content_title="Big text — expanded",
                    summary_text="detailed content",
                ),
                icon="ic_notification",
            )
            set_log(f"OK big text #8 (id={nid})")
        except Exception as ex:
            set_log(f"FAIL big text: {type(ex).__name__}: {ex}")

    # -- 9. progress bar (determinate) --
    async def send_progress(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="PROGRESS #9",
                body="Downloading... 65%",
                show_progress=True,
                max_progress=100,
                progress=65,
                ongoing=True,
                icon="ic_notification",
            )
            set_log(f"OK progress #9 (id={nid})")
        except Exception as ex:
            set_log(f"FAIL progress: {type(ex).__name__}: {ex}")

    # -- 10. progress bar (indeterminate) --
    async def send_indeterminate(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="INDETERMINATE #10",
                body="Processing...",
                show_progress=True,
                indeterminate=True,
                ongoing=True,
                icon="ic_notification",
            )
            set_log(f"OK indeterminate #10 (id={nid})")
        except Exception as ex:
            set_log(f"FAIL indeterminate: {type(ex).__name__}: {ex}")

    # -- 11. ongoing (can't swipe away) --
    async def send_ongoing(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="ONGOING #11",
                body="This can't be swiped away. Use cancel all to dismiss.",
                ongoing=True,
                auto_cancel=False,
                channel_id="ongoing_ch",
                channel_name="Ongoing",
                importance="default",
                icon="ic_notification",
            )
            set_log(f"OK ongoing #11 (id={nid})")
        except Exception as ex:
            set_log(f"FAIL ongoing: {type(ex).__name__}: {ex}")

    # -- 12. action buttons --
    async def send_actions(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="ACTIONS #12",
                body="Tap an action button below.",
                payload=f"payload_for_{nid}",
                actions=[
                    {"id": "approve", "title": "Approve"},
                    {"id": "deny", "title": "Deny"},
                ],
                icon="ic_notification",
            )
            set_log(f"OK actions #12 (id={nid}) — tap an action, check log")
        except Exception as ex:
            set_log(f"FAIL actions: {type(ex).__name__}: {ex}")

    # -- 13. sub text --
    async def send_sub_text(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="SUB TEXT #13",
                body="Look for 'HELLO-SUB-TEXT' in notification header.",
                sub_text="HELLO-SUB-TEXT",
                channel_id="subtext_ch",
                channel_name="Sub Text",
                icon="ic_notification",
            )
            set_log(f"OK sub text #13 (id={nid})")
        except Exception as ex:
            set_log(f"FAIL sub text: {type(ex).__name__}: {ex}")

    # -- 14. visibility (secret — hidden on lock screen).
    # Schedules at +8s so user has time to lock the screen before it fires.
    # NOTE: importance MUST be at least "default" — IMPORTANCE_MIN (the previous
    # value here) makes the notification have no sound/heads-up/status-icon and
    # buries it in a hidden shade section, which is indistinguishable from
    # "didn't fire". visibility="secret" already does the lock-screen-hide job;
    # they are independent dimensions.
    async def send_visibility(e):
        try:
            nid = next_id()
            fire_at = datetime.now() + timedelta(seconds=8)
            await notifications.schedule_notification(
                notification_id=nid,
                title="SECRET #14",
                body="LOCK YOUR PHONE NOW — fires in 8s. Should NOT show on lock screen.",
                scheduled_time=fire_at,
                visibility="secret",
                channel_id="secret_ch_v2",
                channel_name="Secret",
                importance="default",
                icon="ic_notification",
            )
            set_log(f"OK secret #14 (id={nid}) — lock phone NOW, fires in 8s")
        except Exception as ex:
            set_log(f"FAIL visibility: {type(ex).__name__}: {ex}")

    # -- 15. only alert once --
    async def send_only_alert_once(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="ALERT ONCE #15",
                body="First show — you should hear a sound NOW.",
                only_alert_once=True,
                channel_id="alert_once_ch",
                channel_name="Alert Once",
                icon="ic_notification",
            )
            await asyncio.sleep(2)
            # update same ID but on a silent channel — guarantees no re-alert
            await notifications.show_notification(
                notification_id=nid,
                title="ALERT ONCE #15 (updated silently)",
                body="This update was SILENT — no sound or vibration.",
                only_alert_once=True,
                silent=True,
                play_sound=False,
                enable_vibration=False,
                channel_id="alert_once_silent_ch",
                channel_name="Alert Once Silent",
                importance="low",
                icon="ic_notification",
            )
            set_log(f"OK alert once #15 (id={nid}) — second show was silent")
        except Exception as ex:
            set_log(f"FAIL only alert once: {type(ex).__name__}: {ex}")

    # -- 16. custom vibration pattern --
    async def send_vibration(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="VIBRATION #16",
                body="3 short buzzes with long pauses (no sound).",
                vibration_pattern=[0, 200, 1000, 200, 1000, 200],
                play_sound=False,
                channel_id="vibration_ch3",
                channel_name="Vibration Pattern",
                icon="ic_notification",
            )
            set_log(f"OK vibration #16 (id={nid})")
        except Exception as ex:
            set_log(f"FAIL vibration: {type(ex).__name__}: {ex}")

    # -- 17. scheduled notification (10 seconds from now) --
    async def send_scheduled(e):
        try:
            nid = next_id()
            fire_at = datetime.now() + timedelta(seconds=10)
            await notifications.schedule_notification(
                notification_id=nid,
                title="SCHEDULED #17",
                body=f"Fired at {fire_at.strftime('%H:%M:%S')} (10s delay).",
                scheduled_time=fire_at,
                icon="ic_notification",
            )
            set_log(f"OK scheduled #17 (id={nid}) — fires in ~10s")
        except Exception as ex:
            set_log(f"FAIL scheduled: {type(ex).__name__}: {ex}")

    # -- 18. timeout_after (auto-dismiss after 5s) --
    async def send_timeout(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="TIMEOUT #18",
                body="Auto-dismisses after 5 seconds.",
                timeout_after=5000,
                icon="ic_notification",
            )
            set_log(f"OK timeout #18 (id={nid}) — disappears in 5s")
        except Exception as ex:
            set_log(f"FAIL timeout: {type(ex).__name__}: {ex}")

    # -- 19. periodic notification using PRESET interval enum.
    # Calls flutter_local_notifications.periodicallyShow which only accepts the
    # fixed enum values: every_minute, hourly, daily, weekly. For arbitrary
    # intervals (e.g. 90s, 5min) use button 20 instead.
    # periodicallyShow fires the FIRST notification at now+interval (so a 60s
    # wait for every_minute). The kickoff show_notification below gives the
    # user instant feedback that the call worked.
    async def send_periodic(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="PERIODIC #19 (kickoff)",
                body="Periodic scheduled. Next one in ~1 minute.",
                icon="ic_notification",
            )
            await notifications.periodically_show(
                notification_id=nid,
                title="PERIODIC #19",
                body="Repeats every minute.",
                repeat_interval="every_minute",
                icon="ic_notification",
            )
            set_log(f"OK periodic #19 (id={nid}) — kickoff now, next in ~60s")
        except Exception as ex:
            set_log(f"FAIL periodic: {type(ex).__name__}: {ex}")

    # -- 20. periodic with ARBITRARY duration (any number of seconds).
    # Calls flutter_local_notifications.periodicallyShowWithDuration which
    # takes a Duration, so anything from a few seconds upward is allowed.
    # Use this when you need a custom interval not covered by button 19's
    # preset enum (90s here, but could be 30s, 5min, 12h, etc).
    async def send_periodic_duration(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title="PERIODIC DURATION #20 (kickoff)",
                body="Periodic scheduled. Next one in ~90 seconds.",
                icon="ic_notification",
            )
            await notifications.periodically_show_with_duration(
                notification_id=nid,
                title="PERIODIC DURATION #20",
                body="Repeats every 90 seconds.",
                duration_seconds=90,
                icon="ic_notification",
            )
            set_log(f"OK periodic duration #20 (id={nid}) — kickoff now, next in ~90s")
        except Exception as ex:
            set_log(f"FAIL periodic duration: {type(ex).__name__}: {ex}")

    # -- 21. get active notifications --
    async def query_active(e):
        try:
            active = await notifications.get_active_notifications()
            set_log(f"Active ({len(active)}):\n{json.dumps(active, indent=2)}")
        except Exception as ex:
            set_log(f"FAIL get active: {type(ex).__name__}: {ex}")

    # -- 22. get pending notifications --
    async def query_pending(e):
        try:
            pending = await notifications.get_pending_notifications()
            set_log(f"Pending ({len(pending)}):\n{json.dumps(pending, indent=2)}")
        except Exception as ex:
            set_log(f"FAIL get pending: {type(ex).__name__}: {ex}")

    # -- 23. foreground service --
    async def send_foreground(e):
        try:
            nid = next_id()
            await notifications.start_foreground_service(
                notification_id=nid,
                title="FOREGROUND #23",
                body="Foreground service running with special_use type.",
                foreground_service_types=["special_use"],
                icon="ic_notification",
            )
            set_log(f"OK foreground #23 (id={nid}) - use stop button to end")
        except Exception as ex:
            set_log(f"FAIL foreground: {type(ex).__name__}: {ex}\n{traceback.format_exc()}")

    async def stop_foreground(e):
        try:
            await notifications.stop_foreground_service()
            set_log("foreground service stopped")
        except Exception as ex:
            set_log(f"FAIL stop foreground: {type(ex).__name__}: {ex}")

    async def cancel_all(e):
        await notifications.cancel_all()
        set_log("all cancelled")

    def hint(text):
        return ft.Text(text, size=10, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)

    page.add(
        ft.Column(
            [
                ft.Button(content="Request permissions", on_click=request),
                log,
                ft.Divider(),
                ft.Button(content="1. Baseline (no new params)", on_click=send_baseline),
                ft.Divider(height=1),
                ft.Button(content="2. Colored (pure red)", on_click=send_colored),
                hint("color tints the small icon only (look closely — it's red).\n"
                     "background tint is OS-stripped on Samsung; works on Pixel/AOSP."),
                ft.Divider(height=1),
                ft.Button(content="3. Group (3 + summary)", on_click=send_group),
                hint("should see collapsed group with InboxStyle summary.\n"
                     "children use group_alert_behavior=summary."),
                ft.Divider(height=1),
                ft.Button(content="4a. Large icon (thumbnail)", on_click=send_large_icon),
                hint("small thumbnail on right side of notification.\n"
                     "this is how Android large_icon works — always small."),
                ft.Divider(height=1),
                ft.Button(content="4b. Big picture (full-width)", on_click=send_big_picture),
                hint("swipe DOWN to expand — shows full-width splash image.\n"
                     "use BigPictureStyle for truly large images."),
                ft.Divider(height=1),
                ft.Button(content="5. Default icon (contrast)", on_click=send_small_icon),
                hint("uses DEFAULT launcher icon — compare with bell\n"
                     "shape on other notifications to see the difference."),
                ft.Divider(height=1),
                ft.Button(content="6. Custom sound (880Hz beep)", on_click=send_sound),
                hint("plays test_beep from res/raw/. uses 'beep_channel'.\n"
                     "sound is bound to channel — uninstall app to reset."),
                ft.Divider(height=1),
                ft.Button(content="7. Silent", on_click=send_silent),
                hint("no sound, no vibration."),
                ft.Divider(height=1),
                ft.Button(content="8. Big text style", on_click=send_big_text),
                hint("swipe DOWN to expand — shows full paragraph.\n"
                     "collapsed view shows truncated body."),
                ft.Divider(height=1),
                ft.Button(content="9. Progress bar (65%)", on_click=send_progress),
                hint("shows determinate progress bar at 65%.\n"
                     "notification is ongoing (can't swipe away)."),
                ft.Divider(height=1),
                ft.Button(content="10. Indeterminate progress", on_click=send_indeterminate),
                hint("shows spinning/sliding progress bar.\n"
                     "notification is ongoing (can't swipe away)."),
                ft.Divider(height=1),
                ft.Button(content="11. Ongoing (sticky)", on_click=send_ongoing),
                hint("can't be swiped away. use 'cancel all' to remove.\n"
                     "Samsung OneUI may allow swipe — that's a known OEM quirk."),
                ft.Divider(height=1),
                ft.Button(content="12. Action buttons", on_click=send_actions),
                hint("shows Approve / Deny buttons.\n"
                     "tap one — check log for tap event data."),
                ft.Divider(height=1),
                ft.Button(content="13. Sub text", on_click=send_sub_text),
                hint("look for 'HELLO-SUB-TEXT' in notification header\n"
                     "next to app name, or below body when expanded."),
                ft.Divider(height=1),
                ft.Button(content="14. Secret (lock screen)", on_click=send_visibility),
                hint("tap, then LOCK YOUR PHONE within 8s — fires while locked.\n"
                     "with visibility='secret' it should NOT show on lock screen.\n"
                     "Samsung: also set Settings > Lock screen > Notifications to 'hide content'."),
                ft.Divider(height=1),
                ft.Button(content="15. Only alert once", on_click=send_only_alert_once),
                hint("first show plays sound, then 1s later updates silently.\n"
                     "you should only hear ONE alert sound."),
                ft.Divider(height=1),
                ft.Button(content="16. Custom vibration", on_click=send_vibration),
                hint("3 short buzzes with long pauses, NO sound.\n"
                     "Samsung: check Settings > Sounds > Vibration intensity."),
                ft.Divider(height=1),
                ft.Button(content="17. Scheduled (10s delay)", on_click=send_scheduled),
                hint("fires in ~10 seconds. close app to verify\n"
                     "it still fires even when app is not in foreground."),
                ft.Divider(height=1),
                ft.Button(content="18. Timeout (5s auto-dismiss)", on_click=send_timeout),
                hint("notification disappears after 5 seconds.\n"
                     "watch the shade — it should vanish on its own."),
                ft.Divider(height=1),
                ft.Button(content="19. Periodic (preset enum)", on_click=send_periodic),
                hint("uses preset enum (every_minute/hourly/daily/weekly only).\n"
                     "kickoff fires now, recurring at +60s. 'cancel all' to stop."),
                ft.Divider(height=1),
                ft.Button(content="20. Periodic duration (custom)", on_click=send_periodic_duration),
                hint("uses arbitrary Duration (90s here; could be any seconds).\n"
                     "kickoff fires now, recurring at +90s. 'cancel all' to stop."),
                ft.Divider(height=1),
                ft.Button(content="21. Get active notifications", on_click=query_active),
                hint("shows currently displayed notifications.\n"
                     "send some first, then tap this."),
                ft.Divider(height=1),
                ft.Button(content="22. Get pending notifications", on_click=query_pending),
                hint("shows scheduled/periodic notifications.\n"
                     "schedule or set periodic first, then tap this."),
                ft.Divider(height=1),
                ft.Button(content="23. Foreground service (start)", on_click=send_foreground),
                hint("starts foreground service with special_use type.\n"
                     "persistent notification, can't be swiped away."),
                ft.Button(content="23. Foreground service (stop)", on_click=stop_foreground),
                ft.Divider(),
                ft.Button(content="Cancel all", on_click=cancel_all),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
        ),
    )


ft.run(main)
