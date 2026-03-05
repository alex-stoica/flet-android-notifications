"""Periodic notifications: repeat at fixed intervals or custom durations."""

import flet as ft
from flet_android_notifications import FletAndroidNotifications, NotificationError


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    notifications = FletAndroidNotifications()
    status = ft.Text("Ready")

    async def every_minute(e):
        await notifications.request_permissions()
        try:
            await notifications.periodically_show(
                notification_id=100,
                title="Periodic",
                body="This repeats every minute.",
                repeat_interval="every_minute",
                payload="periodic_minute",
            )
            status.value = "Started: every minute"
        except NotificationError as ex:
            status.value = f"Error: {ex}"
        page.update()

    async def every_90s(e):
        await notifications.request_permissions()
        try:
            await notifications.periodically_show_with_duration(
                notification_id=101,
                title="Custom periodic",
                body="This repeats every 90 seconds.",
                duration_seconds=90,
                payload="periodic_90s",
            )
            status.value = "Started: every 90 seconds"
        except NotificationError as ex:
            status.value = f"Error: {ex}"
        page.update()

    async def stop_all(e):
        await notifications.cancel_all()
        status.value = "Cancelled all"
        page.update()

    page.add(
        ft.Button(content="Every minute", on_click=every_minute),
        ft.Button(content="Every 90 seconds", on_click=every_90s),
        ft.Button(content="Cancel all", on_click=stop_all),
        status,
    )


ft.run(main)
