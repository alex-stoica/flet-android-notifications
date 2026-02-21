"""Minimal example: show a notification when you tap a button."""

import flet as ft
from flet_android_notifications import FletAndroidNotifications, NotificationError


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    notifications = FletAndroidNotifications()

    async def send(e):
        await notifications.request_permissions()
        try:
            await notifications.show_notification(
                notification_id=1,
                title="Hello",
                body="This is a basic notification.",
                payload="hello",
            )
        except NotificationError as ex:
            print(f"failed: {ex}")

    page.add(ft.Button(content="Send notification", on_click=send))


ft.run(main)
