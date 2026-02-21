import json
import flet as ft
from typing import Optional


class NotificationError(Exception):
    """Raised when a notification operation fails on the native side."""

    pass


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
            "true" if granted, "false" if denied.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="request_permissions",
        )
        return self._check_error(result)
