"""Foreground service: persistent notification for long-running tasks."""

import flet as ft
from flet_android_notifications import FletAndroidNotifications, NotificationError


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    notifications = FletAndroidNotifications()
    status = ft.Text("Ready")

    async def start_service(e):
        await notifications.request_permissions()
        try:
            await notifications.start_foreground_service(
                notification_id=1,
                title="Background task",
                body="Running in the background...",
                payload="foreground",
                foreground_service_types=["special_use"],
                ongoing=True,
            )
            status.value = "Foreground service started"
        except NotificationError as ex:
            status.value = f"Error: {ex}"
        page.update()

    async def stop_service(e):
        try:
            await notifications.stop_foreground_service()
            status.value = "Foreground service stopped"
        except NotificationError as ex:
            status.value = f"Error: {ex}"
        page.update()

    page.add(
        ft.Button(content="Start foreground service", on_click=start_service),
        ft.Button(content="Stop foreground service", on_click=stop_service),
        status,
    )


ft.run(main)
