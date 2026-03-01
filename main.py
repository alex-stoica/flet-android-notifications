"""Diagnostic test app for grouping, icons, color, and sound.

Each button tests a single feature. Status text shows OK/FAIL + notification ID.
Instructions under each button explain what to look for on the device.
"""

import traceback
import flet as ft
from flet_android_notifications import FletAndroidNotifications, InboxStyle, BigPictureStyle


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

    async def request(e):
        granted = await notifications.request_permissions()
        set_log(f"permissions: {'granted' if granted else 'denied'}")

    # -- 1. baseline: plain notification --
    async def send_baseline(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title=f"Baseline #{nid}",
                body="No new params, just a regular notification.",
            )
            set_log(f"OK baseline #{nid}")
        except Exception as ex:
            set_log(f"FAIL baseline: {type(ex).__name__}: {ex}\n{traceback.format_exc()}")

    # -- 2. color (pure red for max visibility) --
    async def send_colored(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title=f"COLORED #{nid}",
                body="Should have RED accent color on small icon.",
                color="#FF0000",
                icon="ic_notification",
            )
            set_log(f"OK colored #{nid}")
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
                    title=f"Group child {i + 1} (#{nid})",
                    body=f"Grouped message {i + 1}.",
                    group_key="test_group",
                    group_alert_behavior="summary",
                    icon="ic_notification",
                )
            nid = next_id()
            ids.append(nid)
            await notifications.show_notification(
                notification_id=nid,
                title=f"GROUP SUMMARY (#{nid})",
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
            set_log(f"OK group ids={ids}")
        except Exception as ex:
            set_log(f"FAIL group: {type(ex).__name__}: {ex}")

    # -- 4. large icon (thumbnail) --
    async def send_large_icon(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title=f"LARGE ICON #{nid}",
                body="Small thumbnail on right side (Android large_icon is always a thumbnail).",
                large_icon="splash",
                large_icon_type="drawable_resource",
                icon="ic_notification",
            )
            set_log(f"OK large icon #{nid}")
        except Exception as ex:
            set_log(f"FAIL large icon: {type(ex).__name__}: {ex}")

    # -- 4b. big picture style --
    async def send_big_picture(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title=f"BIG PICTURE #{nid}",
                body="Expand to see full-width image.",
                style=BigPictureStyle(
                    drawable_resource="splash",
                    content_title="Big picture — expanded",
                    summary_text="full-width image from splash drawable",
                ),
                icon="ic_notification",
            )
            set_log(f"OK big picture #{nid}")
        except Exception as ex:
            set_log(f"FAIL big picture: {type(ex).__name__}: {ex}")

    # -- 5. custom small icon contrast test --
    async def send_small_icon(e):
        try:
            nid = next_id()
            # use default icon (no icon param) so user can compare with bell
            await notifications.show_notification(
                notification_id=nid,
                title=f"DEFAULT ICON #{nid}",
                body="Uses default launcher icon — compare with bell on other notifications.",
            )
            set_log(f"OK default icon #{nid}")
        except Exception as ex:
            set_log(f"FAIL default icon: {type(ex).__name__}: {ex}")

    # -- 6. custom sound --
    async def send_sound(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title=f"SOUND #{nid}",
                body="Should play a short 880Hz beep.",
                sound="test_beep",
                channel_id="beep_channel",
                channel_name="Beep Channel",
                icon="ic_notification",
            )
            set_log(f"OK sound #{nid}")
        except Exception as ex:
            set_log(f"FAIL sound: {type(ex).__name__}: {ex}")

    # -- 7. silent --
    async def send_silent(e):
        try:
            nid = next_id()
            await notifications.show_notification(
                notification_id=nid,
                title=f"SILENT #{nid}",
                body="No sound, no vibration.",
                play_sound=False,
                enable_vibration=False,
                channel_id="silent_ch",
                channel_name="Silent",
                icon="ic_notification",
            )
            set_log(f"OK silent #{nid}")
        except Exception as ex:
            set_log(f"FAIL silent: {type(ex).__name__}: {ex}")

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
                hint("swipe DOWN on notification to expand it fully.\n"
                     "Samsung Brief mode hides color — must expand."),
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
                ft.Divider(),
                ft.Button(content="Cancel all", on_click=cancel_all),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
        ),
    )


ft.run(main)
