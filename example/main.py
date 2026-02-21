import json
from datetime import datetime, timedelta
import flet as ft
from flet_android_notifications import FletAndroidNotifications, NotificationError


def main(page: ft.Page):
    page.title = "Schedule Test"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    log = ft.Text("", size=12, color=ft.Colors.GREY)

    def add_log(msg):
        log.value = f"{msg}\n{log.value}"[:500]
        page.update()

    def on_notification_tap(e):
        data = json.loads(e.data)
        payload = data.get("payload", "")
        action_id = data.get("action_id", "")
        if action_id:
            add_log(f"ACTION: {action_id} | payload={payload}")
        else:
            add_log(f"TAP: payload={payload}")

    notifications = FletAndroidNotifications(
        on_notification_tap=on_notification_tap,
    )

    async def request_perms(e):
        try:
            r = await notifications.request_permissions()
            add_log(f"Notification permission: {r}")
        except NotificationError as ex:
            add_log(f"Perm error: {ex}")

    async def request_alarm_perm(e):
        try:
            r = await notifications.request_exact_alarm_permission()
            add_log(f"Exact alarm permission: {r}")
        except NotificationError as ex:
            add_log(f"Alarm perm error: {ex}")

    async def show_now(e):
        try:
            await notifications.show_notification(
                notification_id=1,
                title="Instant",
                body="This showed immediately.",
                payload="instant",
            )
            add_log("Showed instant notification")
        except NotificationError as ex:
            add_log(f"Show error: {ex}")

    async def schedule_10s(e):
        fire_at = datetime.now() + timedelta(seconds=10)
        try:
            await notifications.schedule_notification(
                notification_id=10,
                title="10s Timer",
                body=f"Scheduled for {fire_at.strftime('%H:%M:%S')}",
                scheduled_time=fire_at,
                payload="scheduled_10s",
            )
            add_log(f"Scheduled for {fire_at.strftime('%H:%M:%S')} (10s)")
        except NotificationError as ex:
            add_log(f"Schedule error: {ex}")

    async def schedule_30s(e):
        fire_at = datetime.now() + timedelta(seconds=30)
        try:
            await notifications.schedule_notification(
                notification_id=30,
                title="30s Timer",
                body=f"Scheduled for {fire_at.strftime('%H:%M:%S')}",
                scheduled_time=fire_at,
                payload="scheduled_30s",
            )
            add_log(f"Scheduled for {fire_at.strftime('%H:%M:%S')} (30s)")
        except NotificationError as ex:
            add_log(f"Schedule error: {ex}")

    async def schedule_exact_10s(e):
        fire_at = datetime.now() + timedelta(seconds=10)
        try:
            await notifications.schedule_notification(
                notification_id=11,
                title="Exact 10s",
                body=f"Exact alarm at {fire_at.strftime('%H:%M:%S')}",
                scheduled_time=fire_at,
                payload="exact_10s",
                schedule_mode="exact_allow_while_idle",
            )
            add_log(f"Exact scheduled for {fire_at.strftime('%H:%M:%S')}")
        except NotificationError as ex:
            add_log(f"Exact schedule error: {ex}")

    async def cancel_all(e):
        try:
            await notifications.cancel_all()
            add_log("Cancelled all")
        except NotificationError as ex:
            add_log(f"Cancel error: {ex}")

    page.add(
        ft.Column(
            controls=[
                ft.Text("Scheduled Notifications Test", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Button(content="Request Notification Permission", on_click=request_perms),
                ft.Button(content="Request Exact Alarm Permission", on_click=request_alarm_perm),
                ft.Divider(),
                ft.Button(content="Show Now (instant)", on_click=show_now),
                ft.Button(content="Schedule in 10s (inexact)", on_click=schedule_10s),
                ft.Button(content="Schedule in 30s (inexact)", on_click=schedule_30s),
                ft.Button(content="Schedule in 10s (exact)", on_click=schedule_exact_10s),
                ft.Divider(),
                ft.Button(content="Cancel All", on_click=cancel_all, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE),
                ft.Container(height=10),
                ft.Text("Log:", weight=ft.FontWeight.BOLD),
                log,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )
    )


ft.run(main)
