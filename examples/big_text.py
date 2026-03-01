"""Big text notification: expands to show a longer message on pull-down."""

import flet as ft
from flet_android_notifications import FletAndroidNotifications, NotificationError, BigTextStyle


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    notifications = FletAndroidNotifications()

    async def send(e):
        await notifications.request_permissions()
        try:
            await notifications.show_notification(
                notification_id=1,
                title="Weekly report",
                body="Your weekly summary is ready.",
                style=BigTextStyle(
                    "Here is your full weekly summary. You completed 12 tasks, "
                    "closed 3 issues, and reviewed 5 pull requests. Your team's "
                    "velocity increased by 15% compared to last week. Great job!",
                    content_title="Weekly report — expanded",
                    summary_text="12 tasks completed",
                ),
            )
        except NotificationError as ex:
            print(f"failed: {ex}")

    page.add(ft.Button(content="Send big text notification", on_click=send))


ft.run(main)
