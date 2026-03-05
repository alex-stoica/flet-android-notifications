"""Timeout demo: notifications that auto-dismiss after a duration."""

import flet as ft
from flet_android_notifications import FletAndroidNotifications, NotificationError


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    notifications = FletAndroidNotifications()
    status = ft.Text("Ready")

    async def timeout_5s(e):
        await notifications.request_permissions()
        try:
            await notifications.show_notification(
                notification_id=200,
                title="5s timeout",
                body="This disappears after 5 seconds.",
                timeout_after=5000,
            )
            status.value = "Sent: 5s timeout"
        except NotificationError as ex:
            status.value = f"Error: {ex}"
        page.update()

    async def timeout_10s(e):
        await notifications.request_permissions()
        try:
            await notifications.show_notification(
                notification_id=201,
                title="10s timeout",
                body="This disappears after 10 seconds.",
                timeout_after=10000,
            )
            status.value = "Sent: 10s timeout"
        except NotificationError as ex:
            status.value = f"Error: {ex}"
        page.update()

    async def no_timeout(e):
        await notifications.request_permissions()
        try:
            await notifications.show_notification(
                notification_id=202,
                title="No timeout",
                body="This stays until dismissed manually.",
            )
            status.value = "Sent: no timeout"
        except NotificationError as ex:
            status.value = f"Error: {ex}"
        page.update()

    page.add(
        ft.Button(content="5s timeout", on_click=timeout_5s),
        ft.Button(content="10s timeout", on_click=timeout_10s),
        ft.Button(content="No timeout", on_click=no_timeout),
        status,
    )


ft.run(main)
