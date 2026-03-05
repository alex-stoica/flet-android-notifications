"""Query demo: inspect active and pending notifications."""

import json
from datetime import datetime, timedelta
import flet as ft
from flet_android_notifications import FletAndroidNotifications, NotificationError


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    notifications = FletAndroidNotifications()
    output = ft.Text("Ready", selectable=True)

    async def send_three(e):
        await notifications.request_permissions()
        try:
            for i in range(1, 4):
                await notifications.show_notification(
                    notification_id=i,
                    title=f"Notification {i}",
                    body=f"Body of notification {i}",
                    payload=f"n{i}",
                )
            output.value = "Sent notifications 1, 2, 3"
        except NotificationError as ex:
            output.value = f"Error: {ex}"
        page.update()

    async def schedule_two(e):
        await notifications.request_permissions()
        try:
            now = datetime.now()
            for i, nid in enumerate([10, 11]):
                await notifications.schedule_notification(
                    notification_id=nid,
                    title=f"Scheduled {nid}",
                    body=f"Fires in {5 + i} minutes",
                    scheduled_time=now + timedelta(minutes=5 + i),
                    payload=f"s{nid}",
                )
            output.value = "Scheduled notifications 10, 11"
        except NotificationError as ex:
            output.value = f"Error: {ex}"
        page.update()

    async def get_active(e):
        try:
            active = await notifications.get_active_notifications()
            output.value = f"Active ({len(active)}):\n{json.dumps(active, indent=2)}"
        except NotificationError as ex:
            output.value = f"Error: {ex}"
        page.update()

    async def get_pending(e):
        try:
            pending = await notifications.get_pending_notifications()
            output.value = f"Pending ({len(pending)}):\n{json.dumps(pending, indent=2)}"
        except NotificationError as ex:
            output.value = f"Error: {ex}"
        page.update()

    async def cancel(e):
        await notifications.cancel_all()
        output.value = "Cancelled all"
        page.update()

    page.add(
        ft.Button(content="Send 3 notifications", on_click=send_three),
        ft.Button(content="Schedule 2", on_click=schedule_two),
        ft.Button(content="Get active", on_click=get_active),
        ft.Button(content="Get pending", on_click=get_pending),
        ft.Button(content="Cancel all", on_click=cancel),
        output,
    )


ft.run(main)
