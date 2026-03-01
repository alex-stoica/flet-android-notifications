from datetime import datetime
import flet as ft
from typing import Optional, Union


class NotificationError(Exception):
    """Raised when a notification operation fails on the native side."""

    pass


class BigTextStyle:
    """Expandable big text notification style.

    When the notification is expanded, shows the full big_text content
    instead of the truncated body.
    """

    def __init__(
        self,
        big_text: str,
        *,
        content_title: Optional[str] = None,
        summary_text: Optional[str] = None,
    ):
        self.big_text = big_text
        self.content_title = content_title
        self.summary_text = summary_text

    def to_dict(self) -> dict:
        return {
            "type": "big_text",
            "big_text": self.big_text,
            "content_title": self.content_title,
            "summary_text": self.summary_text,
        }


class BigPictureStyle:
    """Notification style that shows a large image when expanded.

    Provide exactly one of file_path or drawable_resource for the main image.
    Optionally provide a large icon via large_icon_file_path or large_icon_drawable_resource.
    """

    def __init__(
        self,
        *,
        file_path: Optional[str] = None,
        drawable_resource: Optional[str] = None,
        content_title: Optional[str] = None,
        summary_text: Optional[str] = None,
        large_icon_file_path: Optional[str] = None,
        large_icon_drawable_resource: Optional[str] = None,
        hide_expanded_large_icon: bool = False,
    ):
        if file_path and drawable_resource:
            raise ValueError("provide exactly one of file_path or drawable_resource, not both")
        if not file_path and not drawable_resource:
            raise ValueError("provide exactly one of file_path or drawable_resource")
        self.file_path = file_path
        self.drawable_resource = drawable_resource
        self.content_title = content_title
        self.summary_text = summary_text
        self.large_icon_file_path = large_icon_file_path
        self.large_icon_drawable_resource = large_icon_drawable_resource
        self.hide_expanded_large_icon = hide_expanded_large_icon

    def to_dict(self) -> dict:
        bitmap_type = "file_path" if self.file_path else "drawable_resource"
        bitmap_value = self.file_path or self.drawable_resource
        d = {
            "type": "big_picture",
            "bitmap_type": bitmap_type,
            "bitmap_value": bitmap_value,
            "content_title": self.content_title,
            "summary_text": self.summary_text,
            "hide_expanded_large_icon": self.hide_expanded_large_icon,
        }
        if self.large_icon_file_path:
            d["large_icon_type"] = "file_path"
            d["large_icon_value"] = self.large_icon_file_path
        elif self.large_icon_drawable_resource:
            d["large_icon_type"] = "drawable_resource"
            d["large_icon_value"] = self.large_icon_drawable_resource
        return d


class InboxStyle:
    """Notification style that shows a list of text lines when expanded."""

    def __init__(
        self,
        lines: list[str],
        *,
        content_title: Optional[str] = None,
        summary_text: Optional[str] = None,
    ):
        self.lines = lines
        self.content_title = content_title
        self.summary_text = summary_text

    def to_dict(self) -> dict:
        return {
            "type": "inbox",
            "lines": self.lines,
            "content_title": self.content_title,
            "summary_text": self.summary_text,
        }


NotificationStyle = Union[BigTextStyle, BigPictureStyle, InboxStyle]


@ft.control("flet_android_notifications")
class FletAndroidNotifications(ft.Service):
    on_notification_tap: Optional[ft.ControlEventHandler["FletAndroidNotifications"]] = None

    def _check_error(self, result):
        """Check if Dart returned an error and raise if so."""
        if isinstance(result, str) and result.startswith("error:"):
            raise NotificationError(result[6:])
        return result

    async def show_notification(
        self,
        notification_id: int,
        title: str,
        body: str,
        *,
        payload: str = "",
        actions: Optional[list[dict]] = None,
        channel_id: str = "flet_notifications",
        channel_name: str = "Flet Notifications",
        channel_description: str = "Notifications from Flet app",
        importance: str = "high",
        play_sound: bool = True,
        enable_vibration: bool = True,
        style: Optional[NotificationStyle] = None,
        show_progress: bool = False,
        max_progress: int = 0,
        progress: int = 0,
        indeterminate: bool = False,
    ):
        """Show an Android notification.

        Args:
            notification_id: Unique integer ID for this notification.
            title: Notification title.
            body: Notification body text.
            payload: Arbitrary string returned in on_notification_tap event.
            actions: List of action buttons shown on the notification. Each is
                a dict with "id" and "title" keys, e.g.
                [{"id": "approve", "title": "Approve"}, {"id": "deny", "title": "Deny"}].
                The tapped action's id is returned as "action_id" in the
                on_notification_tap event data (JSON string).
            channel_id: Android notification channel ID.
            channel_name: Human-readable channel name (shown in system settings).
            channel_description: Channel description (shown in system settings).
            importance: One of "none", "min", "low", "default", "high", "max".
            play_sound: Whether to play the default notification sound.
            enable_vibration: Whether to vibrate on notification.
            style: Notification style (BigTextStyle, BigPictureStyle, or InboxStyle).
            show_progress: Whether to show a progress bar.
            max_progress: Maximum progress value (0 = indeterminate when show_progress is True).
            progress: Current progress value.
            indeterminate: Whether the progress bar is indeterminate.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="show_notification",
            arguments={
                "id": notification_id,
                "title": title,
                "body": body,
                "payload": payload,
                "actions": actions or [],
                "channel_id": channel_id,
                "channel_name": channel_name,
                "channel_description": channel_description,
                "importance": importance,
                "play_sound": play_sound,
                "enable_vibration": enable_vibration,
                "style": style.to_dict() if style else None,
                "show_progress": show_progress,
                "max_progress": max_progress,
                "progress": progress,
                "indeterminate": indeterminate,
            },
        )
        return self._check_error(result)

    async def schedule_notification(
        self,
        notification_id: int,
        title: str,
        body: str,
        scheduled_time: datetime,
        *,
        payload: str = "",
        actions: Optional[list[dict]] = None,
        channel_id: str = "flet_notifications",
        channel_name: str = "Flet Notifications",
        channel_description: str = "Notifications from Flet app",
        importance: str = "high",
        play_sound: bool = True,
        enable_vibration: bool = True,
        schedule_mode: str = "inexact_allow_while_idle",
        match_date_time_components: Optional[str] = None,
        style: Optional[NotificationStyle] = None,
        show_progress: bool = False,
        max_progress: int = 0,
        progress: int = 0,
        indeterminate: bool = False,
    ):
        """Schedule an Android notification for a future time.

        Uses Android's AlarmManager via zonedSchedule(). The notification
        fires even if the app is killed or the device restarts (if the
        required BroadcastReceivers are registered in AndroidManifest.xml).

        Args:
            notification_id: Unique integer ID for this notification.
            title: Notification title.
            body: Notification body text.
            scheduled_time: When to fire. If naive (no tzinfo), treated as
                local time. If timezone-aware, converted to UTC internally.
            payload: Arbitrary string returned in on_notification_tap event.
            actions: List of action buttons, each {"id": "...", "title": "..."}.
            channel_id: Android notification channel ID.
            channel_name: Human-readable channel name.
            channel_description: Channel description.
            importance: One of "none", "min", "low", "default", "high", "max".
            play_sound: Whether to play the default notification sound.
            enable_vibration: Whether to vibrate on notification.
            schedule_mode: One of "alarm_clock", "exact",
                "exact_allow_while_idle", "inexact",
                "inexact_allow_while_idle" (default). Exact modes require
                SCHEDULE_EXACT_ALARM permission.
            match_date_time_components: For recurring notifications. One of
                "time" (daily), "day_of_week_and_time" (weekly),
                "day_of_month_and_time" (monthly), "date_and_time" (yearly),
                or None (one-shot, default).
            style: Notification style (BigTextStyle, BigPictureStyle, or InboxStyle).
            show_progress: Whether to show a progress bar.
            max_progress: Maximum progress value (0 = indeterminate when show_progress is True).
            progress: Current progress value.
            indeterminate: Whether the progress bar is indeterminate.

        Raises:
            NotificationError: If the native side reports an error.
        """
        epoch_ms = int(scheduled_time.timestamp() * 1000)
        result = await self._invoke_method(
            method_name="schedule_notification",
            arguments={
                "id": notification_id,
                "title": title,
                "body": body,
                "scheduled_epoch_ms": epoch_ms,
                "payload": payload,
                "actions": actions or [],
                "channel_id": channel_id,
                "channel_name": channel_name,
                "channel_description": channel_description,
                "importance": importance,
                "play_sound": play_sound,
                "enable_vibration": enable_vibration,
                "schedule_mode": schedule_mode,
                "match_date_time_components": match_date_time_components,
                "style": style.to_dict() if style else None,
                "show_progress": show_progress,
                "max_progress": max_progress,
                "progress": progress,
                "indeterminate": indeterminate,
            },
        )
        return self._check_error(result)

    async def cancel(self, notification_id: int):
        """Cancel a specific notification by ID.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="cancel",
            arguments={"id": notification_id},
        )
        return self._check_error(result)

    async def cancel_all(self):
        """Cancel all active notifications.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="cancel_all",
        )
        return self._check_error(result)

    async def request_permissions(self):
        """Request notification permissions (required on Android 13+).

        Returns:
            bool: True if granted, False if denied.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="request_permissions",
        )
        return self._check_error(result) == "true"

    async def request_exact_alarm_permission(self):
        """Request the SCHEDULE_EXACT_ALARM permission (Android 14+).

        Required before using exact schedule modes ("alarm_clock", "exact",
        "exact_allow_while_idle"). Inexact modes do not need this permission.

        Returns:
            bool: True if granted, False if denied.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="request_exact_alarm_permission",
        )
        return self._check_error(result) == "true"
