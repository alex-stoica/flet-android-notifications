"""Notification with action buttons (Approve / Deny) and tap handling."""

import json
import flet as ft
from flet_android_notifications import FletAndroidNotifications, NotificationError


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    status = ft.Text("No response yet", size=16)

    def on_notification_tap(e):
        data = json.loads(e.data)
        action_id = data.get("action_id", "")
        payload = data.get("payload", "")

        if action_id == "approve":
            status.value = f"Approved: {payload}"
            status.color = ft.Colors.GREEN
        elif action_id == "deny":
            status.value = f"Denied: {payload}"
            status.color = ft.Colors.RED
        else:
            status.value = f"Tapped: {payload}"
            status.color = None
        page.update()

    notifications = FletAndroidNotifications(
        on_notification_tap=on_notification_tap,
    )

    async def send(e):
        await notifications.request_permissions()
        try:
            await notifications.show_notification(
                notification_id=1,
                title="Review request",
                body="You have a task to review.",
                payload="task_42",
                actions=[
                    {"id": "approve", "title": "Approve"},
                    {"id": "deny", "title": "Deny"},
                ],
            )
        except NotificationError as ex:
            print(f"failed: {ex}")

    page.add(
        ft.Column(
            controls=[
                ft.Button(content="Send notification", on_click=send),
                status,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


ft.run(main)
