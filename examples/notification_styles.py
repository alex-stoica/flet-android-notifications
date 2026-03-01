"""Showcase of all notification styles: big text, big picture, inbox, and progress bar."""

import flet as ft
from flet_android_notifications import (
    FletAndroidNotifications,
    NotificationError,
    BigTextStyle,
    BigPictureStyle,
    InboxStyle,
)


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    notifications = FletAndroidNotifications()

    async def send_big_text(e):
        await notifications.request_permissions()
        try:
            await notifications.show_notification(
                notification_id=1,
                title="Big text",
                body="Pull down to expand this notification.",
                style=BigTextStyle(
                    "This is the expanded content of a big text notification. "
                    "It can contain multiple sentences and will wrap across "
                    "several lines when the user expands the notification shade.",
                    content_title="Big text — expanded",
                    summary_text="Summary line",
                ),
            )
        except NotificationError as ex:
            print(f"failed: {ex}")

    async def send_big_picture(e):
        await notifications.request_permissions()
        try:
            await notifications.show_notification(
                notification_id=2,
                title="Big picture",
                body="Pull down to see the image.",
                style=BigPictureStyle(
                    drawable_resource="ic_launcher_foreground",
                    content_title="Big picture — expanded",
                    summary_text="App icon as picture",
                ),
            )
        except NotificationError as ex:
            print(f"failed: {ex}")

    async def send_inbox(e):
        await notifications.request_permissions()
        try:
            await notifications.show_notification(
                notification_id=3,
                title="3 new messages",
                body="You have unread messages.",
                style=InboxStyle(
                    [
                        "Alice: Hey, are you coming?",
                        "Bob: The build is green!",
                        "Carol: PR approved.",
                    ],
                    content_title="3 new messages",
                    summary_text="from 3 contacts",
                ),
            )
        except NotificationError as ex:
            print(f"failed: {ex}")

    async def send_progress(e):
        await notifications.request_permissions()
        try:
            await notifications.show_notification(
                notification_id=4,
                title="Uploading",
                body="45% complete",
                show_progress=True,
                max_progress=100,
                progress=45,
            )
        except NotificationError as ex:
            print(f"failed: {ex}")

    page.add(
        ft.Column(
            [
                ft.Button(content="Big text", on_click=send_big_text),
                ft.Button(content="Big picture", on_click=send_big_picture),
                ft.Button(content="Inbox", on_click=send_inbox),
                ft.Button(content="Progress bar", on_click=send_progress),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


ft.run(main)
