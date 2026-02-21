"""Scheduled notifications: fire in the future even if the app is killed."""

import json
from datetime import datetime, timedelta
import flet as ft
from flet_android_notifications import FletAndroidNotifications, NotificationError


def main(page: ft.Page):
    status = ft.Text("", size=14)

    def on_notification_tap(e):
        data = json.loads(e.data)
        status.value = f"Tapped: {data.get('payload', '')}"
        page.update()

    notifications = FletAndroidNotifications(
        on_notification_tap=on_notification_tap,
    )

    async def schedule_30s(e):
        await notifications.request_permissions()
        fire_at = datetime.now() + timedelta(seconds=30)
        try:
            await notifications.schedule_notification(
                notification_id=10,
                title="Reminder",
                body=f"Scheduled for {fire_at.strftime('%H:%M:%S')}",
                scheduled_time=fire_at,
                payload="reminder_30s",
            )
            status.value = f"Scheduled for {fire_at.strftime('%H:%M:%S')}"
            page.update()
        except NotificationError as ex:
            print(f"failed: {ex}")

    async def schedule_daily(e):
        await notifications.request_permissions()
        fire_at = datetime.now() + timedelta(minutes=1)
        try:
            await notifications.schedule_notification(
                notification_id=11,
                title="Daily standup",
                body="Standup starts in 5 minutes.",
                scheduled_time=fire_at,
                match_date_time_components="time",
                payload="daily_standup",
            )
            status.value = f"Daily recurring set for {fire_at.strftime('%H:%M:%S')}"
            page.update()
        except NotificationError as ex:
            print(f"failed: {ex}")

    async def cancel_all(e):
        await notifications.cancel_all()
        status.value = "All cancelled"
        page.update()

    page.add(
        ft.Column(
            controls=[
                ft.Button(content="Schedule in 30s", on_click=schedule_30s),
                ft.Button(content="Schedule daily recurring", on_click=schedule_daily),
                ft.Button(content="Cancel all", on_click=cancel_all),
                status,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


ft.run(main)
