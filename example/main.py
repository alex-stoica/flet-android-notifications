import json
import time
import flet as ft
from flet_android_notifications import FletAndroidNotifications, NotificationError


def main(page: ft.Page):
    page.title = "Notification Test"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    notification_counter = {"value": 0}
    last_send_time = {"value": 0.0}

    status_colors = {
        "pending": ft.Colors.YELLOW,
        "solved": ft.Colors.GREEN,
        "failed": ft.Colors.RED,
    }

    status_indicator = ft.Container(
        width=30,
        height=30,
        border_radius=15,
        bgcolor=ft.Colors.GREY,
    )

    status_text = ft.Text("No status", size=16)
    log_text = ft.Text("", size=12, color=ft.Colors.GREY)

    def update_status(new_status):
        status_indicator.bgcolor = status_colors.get(new_status, ft.Colors.GREY)
        status_text.value = new_status.capitalize()
        page.update()

    def on_solve(e):
        update_status("solved")
        bottom_sheet.open = False
        page.update()

    def on_postpone(e):
        update_status("pending")
        bottom_sheet.open = False
        page.update()

    def on_fail(e):
        update_status("failed")
        bottom_sheet.open = False
        page.update()

    bottom_sheet = ft.BottomSheet(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                tight=True,
                controls=[
                    ft.Text("Task Notification", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("What would you like to do?"),
                    ft.Divider(),
                    ft.Button(
                        content="Solve",
                        icon=ft.Icons.CHECK_CIRCLE,
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.GREEN,
                        on_click=on_solve,
                        width=200,
                    ),
                    ft.Button(
                        content="Postpone",
                        icon=ft.Icons.SCHEDULE,
                        color=ft.Colors.BLACK,
                        bgcolor=ft.Colors.YELLOW,
                        on_click=on_postpone,
                        width=200,
                    ),
                    ft.Button(
                        content="Mark as Failed",
                        icon=ft.Icons.CANCEL,
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED,
                        on_click=on_fail,
                        width=200,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ),
    )

    def on_notification_tap(e):
        try:
            data = json.loads(e.data)
            payload = data.get("payload", "")
            action_id = data.get("action_id", "")
        except (json.JSONDecodeError, TypeError):
            payload = e.data or ""
            action_id = ""

        # Only debounce body taps (Samsung phantom tap workaround).
        # Action button presses are always intentional.
        if not action_id:
            elapsed = time.time() - last_send_time["value"]
            if elapsed < 3:
                return

        if action_id:
            log_text.value = f"Action: {action_id} | Payload: {payload}"
            if action_id == "approve":
                update_status("solved")
            elif action_id == "deny":
                update_status("failed")
            page.update()
        else:
            log_text.value = f"Tapped! Payload: {payload}"
            bottom_sheet.open = True
            page.update()

    notifications = FletAndroidNotifications(
        on_notification_tap=on_notification_tap,
    )

    page.overlay.append(bottom_sheet)

    async def send_notification(e):
        log_text.value = "Requesting permissions..."
        page.update()

        try:
            result = await notifications.request_permissions()
            log_text.value = f"Permission result: {result}"
            page.update()
        except NotificationError as ex:
            log_text.value = f"Permission error: {ex}"
            page.update()
            return

        notification_counter["value"] += 1
        last_send_time["value"] = time.time()
        try:
            result = await notifications.show_notification(
                notification_id=notification_counter["value"],
                title="Task Notification",
                body="You have a task to review! Tap to respond.",
                payload=f"task_{notification_counter['value']}",
                actions=[
                    {"id": "approve", "title": "Approve"},
                    {"id": "deny", "title": "Deny"},
                ],
                channel_id="task_alerts",
                channel_name="Task Alerts",
                channel_description="Alerts for pending tasks",
            )
            log_text.value = f"Sent #{notification_counter['value']}"
            page.update()
        except NotificationError as ex:
            log_text.value = f"Send error: {ex}"
            page.update()

    async def show_sheet_directly(e):
        bottom_sheet.open = True
        page.update()

    page.add(
        ft.Column(
            controls=[
                ft.Row(
                    controls=[status_indicator, status_text],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=30),
                ft.Button(
                    content="Send Native Notification",
                    icon=ft.Icons.NOTIFICATIONS,
                    on_click=send_notification,
                    style=ft.ButtonStyle(padding=20),
                ),
                ft.Container(height=10),
                ft.Button(
                    content="Open Sheet (In-App)",
                    icon=ft.Icons.ARROW_UPWARD,
                    on_click=show_sheet_directly,
                    style=ft.ButtonStyle(padding=10),
                ),
                ft.Container(height=10),
                log_text,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


ft.run(main)
