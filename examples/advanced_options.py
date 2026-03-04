"""Advanced notification options — one button per feature."""

import flet as ft
from flet_android_notifications import FletAndroidNotifications


def main(page: ft.Page):
    page.title = "Advanced options"
    notifications = FletAndroidNotifications()
    counter = {"only_alert": 0}

    async def send_ongoing(e):
        await notifications.request_permissions()
        await notifications.show_notification(
            notification_id=1,
            title="Ongoing",
            body="Try swiping this away — you can't.",
            ongoing=True,
            channel_id="ongoing_ch",
            channel_name="Ongoing",
        )

    async def send_silent(e):
        await notifications.request_permissions()
        await notifications.show_notification(
            notification_id=2,
            title="Silent",
            body="No sound, no vibration.",
            silent=True,
        )

    async def send_only_alert_once(e):
        counter["only_alert"] += 1
        await notifications.request_permissions()
        await notifications.show_notification(
            notification_id=3,
            title="Only alert once",
            body=f"Tap #{counter['only_alert']} — only the first one makes noise.",
            only_alert_once=True,
        )

    async def send_secret(e):
        await notifications.request_permissions()
        await notifications.show_notification(
            notification_id=4,
            title="Secret",
            body="This is hidden on the lock screen.",
            visibility="secret",
        )

    async def send_sub_text(e):
        await notifications.request_permissions()
        await notifications.show_notification(
            notification_id=5,
            title="New message",
            body="Hey, are you coming tonight?",
            sub_text="via Email",
        )

    async def send_bypass_dnd(e):
        await notifications.request_permissions()
        await notifications.show_notification(
            notification_id=6,
            title="Bypass DnD",
            body="This should appear even in do-not-disturb.",
            channel_bypass_dnd=True,
            channel_id="dnd_bypass_ch",
            channel_name="DnD bypass",
            importance="max",
        )

    async def send_vibration(e):
        await notifications.request_permissions()
        await notifications.show_notification(
            notification_id=7,
            title="Custom vibration",
            body="Feel the pattern: wait, buzz, pause, buzz.",
            vibration_pattern=[0, 500, 200, 500],
            channel_id="vibration_ch",
            channel_name="Vibration",
        )

    async def send_ongoing_no_cancel(e):
        await notifications.request_permissions()
        await notifications.show_notification(
            notification_id=8,
            title="Ongoing + no cancel",
            body="Can't swipe, can't tap to dismiss. Cancel via code.",
            ongoing=True,
            auto_cancel=False,
        )

    page.add(
        ft.Column(
            [
                ft.ElevatedButton("Ongoing", on_click=send_ongoing),
                ft.ElevatedButton("Silent", on_click=send_silent),
                ft.ElevatedButton("Only alert once", on_click=send_only_alert_once),
                ft.ElevatedButton("Lock screen: secret", on_click=send_secret),
                ft.ElevatedButton("Sub text", on_click=send_sub_text),
                ft.ElevatedButton("Bypass DnD", on_click=send_bypass_dnd),
                ft.ElevatedButton("Custom vibration", on_click=send_vibration),
                ft.ElevatedButton("Ongoing + no cancel", on_click=send_ongoing_no_cancel),
            ],
            spacing=10,
        )
    )


ft.app(main)
