from datetime import datetime
import json
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


class NotificationPerson:
    """A person shown in MessagingStyle notifications."""

    _VALID_ICON_TYPES = ("drawable_resource", "file_path", "content_uri")

    def __init__(
        self,
        name: Optional[str] = None,
        *,
        key: Optional[str] = None,
        bot: bool = False,
        important: bool = False,
        uri: Optional[str] = None,
        icon: Optional[str] = None,
        icon_type: str = "drawable_resource",
    ):
        if icon is not None and icon_type not in self._VALID_ICON_TYPES:
            raise ValueError(
                f"person icon_type must be one of {sorted(self._VALID_ICON_TYPES)}, got: {icon_type!r}"
            )
        self.name = name
        self.key = key
        self.bot = bot
        self.important = important
        self.uri = uri
        self.icon = icon
        self.icon_type = icon_type

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "key": self.key,
            "bot": self.bot,
            "important": self.important,
            "uri": self.uri,
            "icon": self.icon,
            "icon_type": self.icon_type,
        }


class NotificationMessage:
    """A single message inside a MessagingStyle notification.

    Messages with person=None are attributed to the style's own person (the
    user); messages with another person render as incoming.
    """

    def __init__(
        self,
        text: str,
        timestamp: datetime,
        *,
        person: Optional[NotificationPerson] = None,
    ):
        if not text:
            raise ValueError("message text must be a non-empty string")
        self.text = text
        self.timestamp = timestamp
        self.person = person

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "timestamp_ms": int(self.timestamp.timestamp() * 1000),
            "person": self.person.to_dict() if self.person else None,
        }


class MessagingStyle:
    """Chat-style notification with per-message senders and avatars.

    `person` is the user themselves (required by Android, needs at least a
    name). Rendering of icons/avatars is OEM-dependent.
    """

    def __init__(
        self,
        person: NotificationPerson,
        *,
        conversation_title: Optional[str] = None,
        group_conversation: bool = False,
        messages: Optional[list[NotificationMessage]] = None,
    ):
        self.person = person
        self.conversation_title = conversation_title
        self.group_conversation = group_conversation
        self.messages = messages or []

    def to_dict(self) -> dict:
        return {
            "type": "messaging",
            "person": self.person.to_dict(),
            "conversation_title": self.conversation_title,
            "group_conversation": self.group_conversation,
            "messages": [message.to_dict() for message in self.messages],
        }


NotificationStyle = Union[BigTextStyle, BigPictureStyle, InboxStyle, MessagingStyle]


class NotificationActionInput:
    """Inline input collected from a notification action."""

    def __init__(
        self,
        *,
        label: Optional[str] = None,
        choices: Optional[list[str]] = None,
        allow_free_form_input: bool = True,
        allowed_mime_types: Optional[list[str]] = None,
    ):
        self.label = label
        self.choices = choices or []
        self.allow_free_form_input = allow_free_form_input
        self.allowed_mime_types = allowed_mime_types or []

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "choices": self.choices,
            "allow_free_form_input": self.allow_free_form_input,
            "allowed_mime_types": self.allowed_mime_types,
        }


class NotificationAction:
    """Android notification action button.

    Existing dict actions are still supported. This class exists to make richer
    Android action features discoverable and validated from Python.
    """

    def __init__(
        self,
        id: str,
        title: str,
        *,
        cancel_notification: bool = True,
        shows_user_interface: bool = True,
        title_color: Optional[str] = None,
        icon: Optional[str] = None,
        icon_type: str = "drawable_resource",
        contextual: bool = False,
        allow_generated_replies: bool = False,
        inputs: Optional[list[Union[NotificationActionInput, dict]]] = None,
        semantic_action: str = "none",
        invisible: bool = False,
    ):
        self.id = id
        self.title = title
        self.cancel_notification = cancel_notification
        self.shows_user_interface = shows_user_interface
        self.title_color = title_color
        self.icon = icon
        self.icon_type = icon_type
        self.contextual = contextual
        self.allow_generated_replies = allow_generated_replies
        self.inputs = inputs or []
        self.semantic_action = semantic_action
        self.invisible = invisible

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "cancel_notification": self.cancel_notification,
            "shows_user_interface": self.shows_user_interface,
            "title_color": self.title_color,
            "icon": self.icon,
            "icon_type": self.icon_type,
            "contextual": self.contextual,
            "allow_generated_replies": self.allow_generated_replies,
            "inputs": [
                input_.to_dict() if hasattr(input_, "to_dict") else dict(input_)
                for input_ in self.inputs
            ],
            "semantic_action": self.semantic_action,
            "invisible": self.invisible,
        }


NotificationActionLike = Union[NotificationAction, dict]


_VALID_VISIBILITIES = {"public", "private", "secret"}

_VALID_IMPORTANCES = {"none", "min", "low", "default", "high", "max"}

_VALID_GROUP_ALERT_BEHAVIORS = {"all", "summary", "children"}

_VALID_SCHEDULE_MODES = {
    "alarm_clock", "exact", "exact_allow_while_idle", "inexact", "inexact_allow_while_idle",
}

_VALID_REPEAT_INTERVALS = {"every_minute", "hourly", "daily", "weekly"}

_VALID_MATCH_COMPONENTS = {"time", "day_of_week_and_time", "day_of_month_and_time", "date_and_time"}

_VALID_LARGE_ICON_TYPES = {"drawable_resource", "file_path"}

_VALID_ACTION_ICON_TYPES = {"drawable_resource", "file_path"}

_VALID_SEMANTIC_ACTIONS = {
    "none", "reply", "mark_as_read", "mark_as_unread", "delete", "archive",
    "mute", "unmute", "thumbs_up", "thumbs_down", "call",
}

_VALID_START_TYPES = {
    "start_sticky", "start_not_sticky", "start_sticky_compatibility", "start_redeliver_intent",
}

_VALID_CATEGORIES = {
    "alarm", "call", "email", "error", "event", "message", "navigation",
    "progress", "promo", "recommendation", "reminder", "service", "social",
    "status", "stopwatch", "transport", "workout",
}

_VALID_FOREGROUND_SERVICE_TYPES = {
    "data_sync", "media_playback", "phone_call", "location", "connected_device",
    "media_projection", "camera", "microphone", "health", "remote_messaging",
    "system_exempted", "short_service", "special_use",
}


def _validate_enum(value: str, valid: set, name: str) -> None:
    if value not in valid:
        raise ValueError(f"{name} must be one of {sorted(valid)}, got: {value!r}")


def _validate_visibility(visibility: str) -> None:
    """Validate visibility is one of public, private, secret."""
    _validate_enum(visibility, _VALID_VISIBILITIES, "visibility")


def _validate_color_hex(color: str) -> None:
    """Validate a hex color string like '#FF5722' or '#80FF5722'."""
    if not color.startswith("#"):
        raise ValueError(f"color must start with '#', got: {color!r}")
    hex_part = color[1:]
    if len(hex_part) not in (6, 8):
        raise ValueError(f"color must be 6 or 8 hex digits after '#', got: {color!r}")
    try:
        int(hex_part, 16)
    except ValueError:
        raise ValueError(f"color contains invalid hex characters: {color!r}")


def _normalize_action_input(input_: Union[NotificationActionInput, dict]) -> dict:
    if isinstance(input_, NotificationActionInput):
        data = input_.to_dict()
    elif isinstance(input_, dict):
        data = dict(input_)
    else:
        raise TypeError(f"action input must be NotificationActionInput or dict, got {type(input_).__name__}")

    data.setdefault("choices", [])
    data.setdefault("allow_free_form_input", True)
    data.setdefault("label", None)
    data.setdefault("allowed_mime_types", [])
    if not isinstance(data["choices"], list) or not all(isinstance(v, str) for v in data["choices"]):
        raise ValueError("action input choices must be a list of strings")
    if not isinstance(data["allowed_mime_types"], list) or not all(
        isinstance(v, str) for v in data["allowed_mime_types"]
    ):
        raise ValueError("action input allowed_mime_types must be a list of strings")
    return data


def _normalize_action(action: NotificationActionLike) -> dict:
    if isinstance(action, NotificationAction):
        data = action.to_dict()
    elif isinstance(action, dict):
        data = dict(action)
    else:
        raise TypeError(f"action must be NotificationAction or dict, got {type(action).__name__}")

    if not isinstance(data.get("id"), str) or not data["id"]:
        raise ValueError("action id must be a non-empty string")
    if not isinstance(data.get("title"), str) or not data["title"]:
        raise ValueError("action title must be a non-empty string")

    data.setdefault("cancel_notification", True)
    data.setdefault("shows_user_interface", True)
    data.setdefault("title_color", None)
    data.setdefault("icon", None)
    data.setdefault("icon_type", "drawable_resource")
    data.setdefault("contextual", False)
    data.setdefault("allow_generated_replies", False)
    data.setdefault("inputs", [])
    data.setdefault("semantic_action", "none")
    data.setdefault("invisible", False)

    if data["title_color"] is not None:
        _validate_color_hex(data["title_color"])
    if data["icon"] is not None:
        _validate_enum(data["icon_type"], _VALID_ACTION_ICON_TYPES, "action icon_type")
    if data["contextual"] and data["icon"] is None:
        raise ValueError("contextual notification actions require an icon")
    _validate_enum(data["semantic_action"], _VALID_SEMANTIC_ACTIONS, "semantic_action")
    data["inputs"] = [_normalize_action_input(input_) for input_ in data["inputs"]]
    return data


def _normalize_actions(actions: Optional[list[NotificationActionLike]]) -> list[dict]:
    return [_normalize_action(action) for action in actions or []]


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
        actions: Optional[list[NotificationActionLike]] = None,
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
        group_key: Optional[str] = None,
        set_as_group_summary: bool = False,
        group_alert_behavior: str = "all",
        icon: Optional[str] = None,
        large_icon: Optional[str] = None,
        large_icon_type: str = "drawable_resource",
        color: Optional[str] = None,
        colorized: bool = False,
        sound: Optional[str] = None,
        ongoing: bool = False,
        auto_cancel: bool = True,
        silent: bool = False,
        only_alert_once: bool = False,
        visibility: Optional[str] = None,
        sub_text: Optional[str] = None,
        channel_bypass_dnd: bool = False,
        vibration_pattern: Optional[list[int]] = None,
        timeout_after: Optional[int] = None,
        category: Optional[str] = None,
        full_screen_intent: bool = False,
    ):
        """Show an Android notification.

        Args:
            notification_id: Unique integer ID for this notification.
            title: Notification title.
            body: Notification body text.
            payload: Arbitrary string returned in on_notification_tap event.
            actions: List of NotificationAction objects or compatible dicts.
                Dicts must include "id" and "title". Rich Android action
                fields include inputs, title_color, icon, contextual,
                allow_generated_replies, semantic_action, and invisible.
                The tapped action's id is returned as "action_id" in the
                on_notification_tap event data (JSON string). Inline reply
                text is returned as "input".
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
            group_key: Group key for bundling notifications together.
            set_as_group_summary: If True, this notification is the group
                summary. You must manage summary lifecycle yourself.
            group_alert_behavior: "all", "summary", or "children".
            icon: Drawable resource name for the small status bar icon
                (e.g. "ic_notification"). None = app launcher icon. Must
                be a compiled Android drawable, not a file path. Android
                renders small icons as single-color silhouettes.
            large_icon: Large icon shown on the notification's right side.
                Interpreted according to large_icon_type.
            large_icon_type: "drawable_resource" (default) or "file_path".
            color: Hex color string (e.g. "#FF5722" or "#80FF5722"). The
                Android contract says this tints the small icon and
                accent areas. In practice, on Samsung OneUI (Brief mode,
                default on Galaxy) the value reaches the OS but is NOT
                rendered visibly for regular notifications — verified by
                comparing two notifications side-by-side, one with color
                set and one without, both look identical. Renders
                visibly on AOSP/Pixel. Reliable visible color on Samsung
                requires start_foreground_service() with colorized=True.
            colorized: When True, applies color as the notification
                background. Per Android contract, has effect ONLY on
                foreground service or media-style notifications — for a
                regular show_notification call this flag is silently
                ignored. Use start_foreground_service() with color +
                colorized for a fully colored background. Verified working
                on Samsung OneUI when wired up correctly.
            sound: Raw resource name (e.g. "alert_tone" for
                res/raw/alert_tone.mp3). Omit file extension. The sound
                is permanently bound to the channel at creation — changing
                it later requires a different channel_id.
            ongoing: Marks the notification as ongoing. On Android 14+ users
                can still dismiss it by swiping (platform change); only a
                foreground service notification is truly sticky.
            auto_cancel: Dismiss notification when tapped. Default True.
            silent: Suppress sound and vibration.
            only_alert_once: Only alert (sound/vibration) on the first
                show; updates are silent.
            visibility: Lock screen visibility. One of "public" (show
                full content), "private" (hide sensitive content), or
                "secret" (don't show on lock screen at all).
            sub_text: Small text shown below the notification content.
            channel_bypass_dnd: Allow the notification channel to bypass
                do-not-disturb mode. Only takes effect when the channel
                is first created.
            vibration_pattern: Custom vibration pattern as a list of
                millisecond durations, e.g. [0, 500, 200, 500].
            timeout_after: Auto-dismiss the notification after this many
                milliseconds. None means no timeout.

        Raises:
            NotificationError: If the native side reports an error.
        """
        _validate_enum(importance, _VALID_IMPORTANCES, "importance")
        _validate_enum(group_alert_behavior, _VALID_GROUP_ALERT_BEHAVIORS, "group_alert_behavior")
        if large_icon is not None:
            _validate_enum(large_icon_type, _VALID_LARGE_ICON_TYPES, "large_icon_type")
        if color is not None:
            _validate_color_hex(color)
        if visibility is not None:
            _validate_visibility(visibility)
        if category is not None:
            _validate_enum(category, _VALID_CATEGORIES, "category")
        result = await self._invoke_method(
            method_name="show_notification",
            arguments={
                "id": notification_id,
                "title": title,
                "body": body,
                "payload": payload,
                "actions": _normalize_actions(actions),
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
                "group_key": group_key,
                "set_as_group_summary": set_as_group_summary,
                "group_alert_behavior": group_alert_behavior,
                "icon": icon,
                "large_icon": large_icon,
                "large_icon_type": large_icon_type,
                "color": color,
                "colorized": colorized,
                "sound": sound,
                "ongoing": ongoing,
                "auto_cancel": auto_cancel,
                "silent": silent,
                "only_alert_once": only_alert_once,
                "visibility": visibility,
                "sub_text": sub_text,
                "channel_bypass_dnd": channel_bypass_dnd,
                "vibration_pattern": vibration_pattern,
                "timeout_after": timeout_after,
                "category": category,
                "full_screen_intent": full_screen_intent,
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
        actions: Optional[list[NotificationActionLike]] = None,
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
        group_key: Optional[str] = None,
        set_as_group_summary: bool = False,
        group_alert_behavior: str = "all",
        icon: Optional[str] = None,
        large_icon: Optional[str] = None,
        large_icon_type: str = "drawable_resource",
        color: Optional[str] = None,
        colorized: bool = False,
        sound: Optional[str] = None,
        ongoing: bool = False,
        auto_cancel: bool = True,
        silent: bool = False,
        only_alert_once: bool = False,
        visibility: Optional[str] = None,
        sub_text: Optional[str] = None,
        channel_bypass_dnd: bool = False,
        vibration_pattern: Optional[list[int]] = None,
        timeout_after: Optional[int] = None,
        category: Optional[str] = None,
        full_screen_intent: bool = False,
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
            actions: List of NotificationAction objects or compatible dicts.
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
            group_key: Group key for bundling notifications together.
            set_as_group_summary: If True, this notification is the group
                summary. You must manage summary lifecycle yourself.
            group_alert_behavior: "all", "summary", or "children".
            icon: Drawable resource name for the small status bar icon
                (e.g. "ic_notification"). None = app launcher icon. Must
                be a compiled Android drawable, not a file path. Android
                renders small icons as single-color silhouettes.
            large_icon: Large icon shown on the notification's right side.
                Interpreted according to large_icon_type.
            large_icon_type: "drawable_resource" (default) or "file_path".
            color: Hex color string (e.g. "#FF5722" or "#80FF5722"). The
                Android contract says this tints the small icon and
                accent areas. In practice, on Samsung OneUI (Brief mode,
                default on Galaxy) the value reaches the OS but is NOT
                rendered visibly for regular notifications — verified by
                comparing two notifications side-by-side, one with color
                set and one without, both look identical. Renders
                visibly on AOSP/Pixel. Reliable visible color on Samsung
                requires start_foreground_service() with colorized=True.
            colorized: When True, applies color as the notification
                background. Per Android contract, has effect ONLY on
                foreground service or media-style notifications — for a
                regular show_notification call this flag is silently
                ignored. Use start_foreground_service() with color +
                colorized for a fully colored background. Verified working
                on Samsung OneUI when wired up correctly.
            sound: Raw resource name (e.g. "alert_tone" for
                res/raw/alert_tone.mp3). Omit file extension. The sound
                is permanently bound to the channel at creation — changing
                it later requires a different channel_id.
            ongoing: Marks the notification as ongoing. On Android 14+ users
                can still dismiss it by swiping (platform change); only a
                foreground service notification is truly sticky.
            auto_cancel: Dismiss notification when tapped. Default True.
            silent: Suppress sound and vibration.
            only_alert_once: Only alert (sound/vibration) on the first
                show; updates are silent.
            visibility: Lock screen visibility. One of "public" (show
                full content), "private" (hide sensitive content), or
                "secret" (don't show on lock screen at all).
            sub_text: Small text shown below the notification content.
            channel_bypass_dnd: Allow the notification channel to bypass
                do-not-disturb mode. Only takes effect when the channel
                is first created.
            vibration_pattern: Custom vibration pattern as a list of
                millisecond durations, e.g. [0, 500, 200, 500].
            timeout_after: Auto-dismiss the notification after this many
                milliseconds. None means no timeout.

        Raises:
            NotificationError: If the native side reports an error.
        """
        _validate_enum(importance, _VALID_IMPORTANCES, "importance")
        _validate_enum(group_alert_behavior, _VALID_GROUP_ALERT_BEHAVIORS, "group_alert_behavior")
        _validate_enum(schedule_mode, _VALID_SCHEDULE_MODES, "schedule_mode")
        if match_date_time_components is not None:
            _validate_enum(match_date_time_components, _VALID_MATCH_COMPONENTS, "match_date_time_components")
        if large_icon is not None:
            _validate_enum(large_icon_type, _VALID_LARGE_ICON_TYPES, "large_icon_type")
        if color is not None:
            _validate_color_hex(color)
        if visibility is not None:
            _validate_visibility(visibility)
        if category is not None:
            _validate_enum(category, _VALID_CATEGORIES, "category")
        epoch_ms = int(scheduled_time.timestamp() * 1000)
        result = await self._invoke_method(
            method_name="schedule_notification",
            arguments={
                "id": notification_id,
                "title": title,
                "body": body,
                "scheduled_epoch_ms": epoch_ms,
                "payload": payload,
                "actions": _normalize_actions(actions),
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
                "group_key": group_key,
                "set_as_group_summary": set_as_group_summary,
                "group_alert_behavior": group_alert_behavior,
                "icon": icon,
                "large_icon": large_icon,
                "large_icon_type": large_icon_type,
                "color": color,
                "colorized": colorized,
                "sound": sound,
                "ongoing": ongoing,
                "auto_cancel": auto_cancel,
                "silent": silent,
                "only_alert_once": only_alert_once,
                "visibility": visibility,
                "sub_text": sub_text,
                "channel_bypass_dnd": channel_bypass_dnd,
                "vibration_pattern": vibration_pattern,
                "timeout_after": timeout_after,
                "category": category,
                "full_screen_intent": full_screen_intent,
            },
        )
        return self._check_error(result)

    async def periodically_show(
        self,
        notification_id: int,
        title: str,
        body: str,
        repeat_interval: str,
        *,
        schedule_mode: str = "inexact_allow_while_idle",
        payload: str = "",
        actions: Optional[list[NotificationActionLike]] = None,
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
        group_key: Optional[str] = None,
        set_as_group_summary: bool = False,
        group_alert_behavior: str = "all",
        icon: Optional[str] = None,
        large_icon: Optional[str] = None,
        large_icon_type: str = "drawable_resource",
        color: Optional[str] = None,
        colorized: bool = False,
        sound: Optional[str] = None,
        ongoing: bool = False,
        auto_cancel: bool = True,
        silent: bool = False,
        only_alert_once: bool = False,
        visibility: Optional[str] = None,
        sub_text: Optional[str] = None,
        channel_bypass_dnd: bool = False,
        vibration_pattern: Optional[list[int]] = None,
        timeout_after: Optional[int] = None,
        category: Optional[str] = None,
    ):
        """Show a notification that repeats at a fixed interval.

        Args:
            notification_id: Unique integer ID for this notification.
            title: Notification title.
            body: Notification body text.
            repeat_interval: One of "every_minute", "hourly", "daily", "weekly".
            payload: Arbitrary string returned in on_notification_tap event.
            timeout_after: Auto-dismiss after this many milliseconds.
            (All other params are the same as show_notification.)

        Raises:
            NotificationError: If the native side reports an error.
        """
        _validate_enum(importance, _VALID_IMPORTANCES, "importance")
        _validate_enum(group_alert_behavior, _VALID_GROUP_ALERT_BEHAVIORS, "group_alert_behavior")
        _validate_enum(repeat_interval, _VALID_REPEAT_INTERVALS, "repeat_interval")
        _validate_enum(schedule_mode, _VALID_SCHEDULE_MODES, "schedule_mode")
        if large_icon is not None:
            _validate_enum(large_icon_type, _VALID_LARGE_ICON_TYPES, "large_icon_type")
        if color is not None:
            _validate_color_hex(color)
        if visibility is not None:
            _validate_visibility(visibility)
        if category is not None:
            _validate_enum(category, _VALID_CATEGORIES, "category")
        result = await self._invoke_method(
            method_name="periodically_show",
            arguments={
                "id": notification_id,
                "title": title,
                "body": body,
                "repeat_interval": repeat_interval,
                "schedule_mode": schedule_mode,
                "payload": payload,
                "actions": _normalize_actions(actions),
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
                "group_key": group_key,
                "set_as_group_summary": set_as_group_summary,
                "group_alert_behavior": group_alert_behavior,
                "icon": icon,
                "large_icon": large_icon,
                "large_icon_type": large_icon_type,
                "color": color,
                "colorized": colorized,
                "sound": sound,
                "ongoing": ongoing,
                "auto_cancel": auto_cancel,
                "silent": silent,
                "only_alert_once": only_alert_once,
                "visibility": visibility,
                "sub_text": sub_text,
                "channel_bypass_dnd": channel_bypass_dnd,
                "vibration_pattern": vibration_pattern,
                "timeout_after": timeout_after,
                "category": category,
            },
        )
        return self._check_error(result)

    async def periodically_show_with_duration(
        self,
        notification_id: int,
        title: str,
        body: str,
        duration_seconds: Union[int, float],
        *,
        schedule_mode: str = "inexact_allow_while_idle",
        payload: str = "",
        actions: Optional[list[NotificationActionLike]] = None,
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
        group_key: Optional[str] = None,
        set_as_group_summary: bool = False,
        group_alert_behavior: str = "all",
        icon: Optional[str] = None,
        large_icon: Optional[str] = None,
        large_icon_type: str = "drawable_resource",
        color: Optional[str] = None,
        colorized: bool = False,
        sound: Optional[str] = None,
        ongoing: bool = False,
        auto_cancel: bool = True,
        silent: bool = False,
        only_alert_once: bool = False,
        visibility: Optional[str] = None,
        sub_text: Optional[str] = None,
        channel_bypass_dnd: bool = False,
        vibration_pattern: Optional[list[int]] = None,
        timeout_after: Optional[int] = None,
        category: Optional[str] = None,
    ):
        """Show a notification that repeats at a custom duration.

        Args:
            notification_id: Unique integer ID for this notification.
            title: Notification title.
            body: Notification body text.
            duration_seconds: Repeat interval in seconds.
            payload: Arbitrary string returned in on_notification_tap event.
            timeout_after: Auto-dismiss after this many milliseconds.
            (All other params are the same as show_notification.)

        Raises:
            NotificationError: If the native side reports an error.
        """
        _validate_enum(importance, _VALID_IMPORTANCES, "importance")
        _validate_enum(group_alert_behavior, _VALID_GROUP_ALERT_BEHAVIORS, "group_alert_behavior")
        if large_icon is not None:
            _validate_enum(large_icon_type, _VALID_LARGE_ICON_TYPES, "large_icon_type")
        if color is not None:
            _validate_color_hex(color)
        if visibility is not None:
            _validate_visibility(visibility)
        if category is not None:
            _validate_enum(category, _VALID_CATEGORIES, "category")
        _validate_enum(schedule_mode, _VALID_SCHEDULE_MODES, "schedule_mode")
        result = await self._invoke_method(
            method_name="periodically_show_with_duration",
            arguments={
                "id": notification_id,
                "title": title,
                "body": body,
                "duration_ms": int(duration_seconds * 1000),
                "schedule_mode": schedule_mode,
                "payload": payload,
                "actions": _normalize_actions(actions),
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
                "group_key": group_key,
                "set_as_group_summary": set_as_group_summary,
                "group_alert_behavior": group_alert_behavior,
                "icon": icon,
                "large_icon": large_icon,
                "large_icon_type": large_icon_type,
                "color": color,
                "colorized": colorized,
                "sound": sound,
                "ongoing": ongoing,
                "auto_cancel": auto_cancel,
                "silent": silent,
                "only_alert_once": only_alert_once,
                "visibility": visibility,
                "sub_text": sub_text,
                "channel_bypass_dnd": channel_bypass_dnd,
                "vibration_pattern": vibration_pattern,
                "timeout_after": timeout_after,
                "category": category,
            },
        )
        return self._check_error(result)

    async def start_foreground_service(
        self,
        notification_id: int,
        title: str,
        body: str,
        *,
        payload: str = "",
        start_type: str = "start_sticky",
        foreground_service_types: Optional[list[str]] = None,
        actions: Optional[list[NotificationActionLike]] = None,
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
        group_key: Optional[str] = None,
        set_as_group_summary: bool = False,
        group_alert_behavior: str = "all",
        icon: Optional[str] = None,
        large_icon: Optional[str] = None,
        large_icon_type: str = "drawable_resource",
        color: Optional[str] = None,
        colorized: bool = False,
        sound: Optional[str] = None,
        ongoing: bool = False,
        auto_cancel: bool = True,
        silent: bool = False,
        only_alert_once: bool = False,
        visibility: Optional[str] = None,
        sub_text: Optional[str] = None,
        channel_bypass_dnd: bool = False,
        vibration_pattern: Optional[list[int]] = None,
        timeout_after: Optional[int] = None,
        category: Optional[str] = None,
    ):
        """Start an Android foreground service with a persistent notification.

        Foreground services keep the app alive for long-running tasks (music,
        GPS, uploads). The notification cannot be swiped away and is not
        removed by cancel() — use stop_foreground_service() instead.

        Args:
            notification_id: Unique integer ID. Must not be 0 (Android constraint).
            title: Notification title.
            body: Notification body text.
            payload: Arbitrary string returned in on_notification_tap event.
            start_type: Service start type. One of "start_sticky" (default),
                "start_not_sticky", "start_sticky_compatibility",
                "start_redeliver_intent".
            foreground_service_types: List of foreground service types, e.g.
                ["special_use"]. Values: data_sync, media_playback, phone_call,
                location, connected_device, media_projection, camera, microphone,
                health, remote_messaging, system_exempted, short_service,
                special_use.
            (All other params are the same as show_notification.)

        Raises:
            ValueError: If notification_id is 0, or start_type/foreground_service_types invalid.
            NotificationError: If the native side reports an error.
        """
        if notification_id == 0:
            raise ValueError("notification_id must not be 0 for foreground services (Android constraint)")
        _validate_enum(importance, _VALID_IMPORTANCES, "importance")
        _validate_enum(group_alert_behavior, _VALID_GROUP_ALERT_BEHAVIORS, "group_alert_behavior")
        _validate_enum(start_type, _VALID_START_TYPES, "start_type")
        if foreground_service_types is not None:
            for fst in foreground_service_types:
                _validate_enum(fst, _VALID_FOREGROUND_SERVICE_TYPES, "foreground_service_type")
        if large_icon is not None:
            _validate_enum(large_icon_type, _VALID_LARGE_ICON_TYPES, "large_icon_type")
        if color is not None:
            _validate_color_hex(color)
        if visibility is not None:
            _validate_visibility(visibility)
        if category is not None:
            _validate_enum(category, _VALID_CATEGORIES, "category")
        result = await self._invoke_method(
            method_name="start_foreground_service",
            arguments={
                "id": notification_id,
                "title": title,
                "body": body,
                "payload": payload,
                "start_type": start_type,
                "foreground_service_types": foreground_service_types,
                "actions": _normalize_actions(actions),
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
                "group_key": group_key,
                "set_as_group_summary": set_as_group_summary,
                "group_alert_behavior": group_alert_behavior,
                "icon": icon,
                "large_icon": large_icon,
                "large_icon_type": large_icon_type,
                "color": color,
                "colorized": colorized,
                "sound": sound,
                "ongoing": ongoing,
                "auto_cancel": auto_cancel,
                "silent": silent,
                "only_alert_once": only_alert_once,
                "visibility": visibility,
                "sub_text": sub_text,
                "channel_bypass_dnd": channel_bypass_dnd,
                "vibration_pattern": vibration_pattern,
                "timeout_after": timeout_after,
                "category": category,
            },
        )
        return self._check_error(result)

    async def stop_foreground_service(self):
        """Stop the Android foreground service and remove its notification.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="stop_foreground_service",
        )
        return self._check_error(result)

    async def get_active_notifications(self) -> list[dict]:
        """Get all currently active (shown) notifications.

        Returns:
            List of dicts with keys: id, title, body, channel_id, payload.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="get_active_notifications",
        )
        self._check_error(result)
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError) as e:
            raise NotificationError(f"failed to parse response: {e}")

    async def get_pending_notifications(self) -> list[dict]:
        """Get all pending (scheduled) notification requests.

        Returns:
            List of dicts with keys: id, title, body, payload.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="get_pending_notifications",
        )
        self._check_error(result)
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError) as e:
            raise NotificationError(f"failed to parse response: {e}")

    async def get_notification_app_launch_details(self) -> dict:
        """Check whether the app was launched by tapping a notification.

        Returns:
            Dict with "did_notification_launch_app" (bool) and
            "notification_response" (dict or None). When the app was launched
            from a notification, the response holds the same fields as the
            on_notification_tap event data: notification_id, payload,
            action_id, input, response_type.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="get_notification_app_launch_details",
        )
        self._check_error(result)
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError) as e:
            raise NotificationError(f"failed to parse response: {e}")

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

    async def are_notifications_enabled(self) -> bool:
        """Whether notifications are enabled for this app (POST_NOTIFICATIONS).

        Use this instead of assuming a notification was suppressed by the OEM —
        if this returns False, the user has notifications turned off.

        Returns:
            bool: True if notifications are enabled.
        """
        result = await self._invoke_method(method_name="are_notifications_enabled")
        return self._check_error(result) == "true"

    async def open_app_notification_settings(self) -> bool:
        """Open Android's notification settings screen for this app.

        This lets a user re-enable notifications or adjust the app's notification
        channels after :meth:`are_notifications_enabled` returns ``False``.

        Returns:
            bool: True if Android opened the settings screen.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="open_app_notification_settings"
        )
        return self._check_error(result) == "true"

    async def can_schedule_exact_notifications(self) -> bool:
        """Whether the app may schedule exact alarms (SCHEDULE_EXACT_ALARM).

        Exact schedule modes ("alarm_clock", "exact", "exact_allow_while_idle")
        require this. If False, call request_exact_alarm_permission() or fall
        back to an inexact schedule_mode.

        Returns:
            bool: True if exact alarms can be scheduled.
        """
        result = await self._invoke_method(method_name="can_schedule_exact_notifications")
        return self._check_error(result) == "true"

    async def request_full_screen_intent_permission(self) -> bool:
        """Request the USE_FULL_SCREEN_INTENT permission (Android 14+).

        Required for full_screen_intent notifications to launch their
        full-screen UI on Android 14+. The USE_FULL_SCREEN_INTENT permission
        must also be declared in the app manifest.

        Returns:
            bool: True if granted.
        """
        result = await self._invoke_method(method_name="request_full_screen_intent_permission")
        return self._check_error(result) == "true"

    async def has_notification_policy_access(self) -> bool:
        """Whether the app has notification-policy (do-not-disturb) access.

        A channel's channel_bypass_dnd only takes effect when this is True;
        without policy access Android treats bypass as False. Use this to tell
        whether a DND-bypass failure is a missing grant rather than an OEM issue.

        Returns:
            bool: True if notification-policy access is granted.
        """
        result = await self._invoke_method(method_name="has_notification_policy_access")
        return self._check_error(result) == "true"

    async def request_notification_policy_access(self) -> bool:
        """Open the system do-not-disturb (Zen) access screen for this app.

        Opens Settings so the user can grant notification-policy access (needed
        for channel_bypass_dnd). The returned bool is the plugin's raw result
        and is NOT a reliable "opened" indicator — verify the grant afterwards
        with has_notification_policy_access().

        Returns:
            bool: Plugin result (do not interpret as "settings opened").
        """
        result = await self._invoke_method(method_name="request_notification_policy_access")
        return self._check_error(result) == "true"

    async def create_notification_channel(
        self,
        channel_id: str,
        channel_name: str,
        *,
        channel_description: Optional[str] = None,
        group_id: Optional[str] = None,
        importance: str = "default",
        play_sound: bool = True,
        sound: Optional[str] = None,
        enable_vibration: bool = True,
        vibration_pattern: Optional[list[int]] = None,
        show_badge: bool = True,
        channel_bypass_dnd: bool = False,
    ):
        """Create (or update) a notification channel up front.

        A channel's sound/vibration/importance are immutable after creation, so
        to change them you must delete_notification_channel() and recreate with a
        new configuration (the channel_id may be reused once deleted).

        Args:
            channel_id: Channel ID.
            channel_name: Human-readable channel name.
            channel_description: Channel description shown in system settings.
            group_id: Optional channel group ID (see create_notification_channel_group).
            importance: One of "none", "min", "low", "default", "high", "max".
            play_sound: Whether the channel plays a sound.
            sound: Raw resource name for a custom sound (omit extension).
            enable_vibration: Whether the channel vibrates.
            vibration_pattern: Custom vibration pattern (list of ms durations).
            show_badge: Whether the channel shows an app-icon badge.
            channel_bypass_dnd: Whether the channel bypasses do-not-disturb.

        Raises:
            NotificationError: If the native side reports an error.
        """
        _validate_enum(importance, _VALID_IMPORTANCES, "importance")
        result = await self._invoke_method(
            method_name="create_notification_channel",
            arguments={
                "channel_id": channel_id,
                "channel_name": channel_name,
                "channel_description": channel_description,
                "group_id": group_id,
                "importance": importance,
                "play_sound": play_sound,
                "sound": sound,
                "enable_vibration": enable_vibration,
                "vibration_pattern": vibration_pattern,
                "show_badge": show_badge,
                "channel_bypass_dnd": channel_bypass_dnd,
            },
        )
        return self._check_error(result)

    async def delete_notification_channel(self, channel_id: str):
        """Delete a notification channel by ID.

        Use this to change an immutable channel property (sound, vibration,
        importance): delete then recreate with create_notification_channel().

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="delete_notification_channel",
            arguments={"channel_id": channel_id},
        )
        return self._check_error(result)

    async def get_notification_channels(self) -> list[dict]:
        """Get all notification channels registered by this app.

        Returns:
            List of dicts with keys: id, name, description, importance (int),
            play_sound, enable_vibration, bypass_dnd, show_badge.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(method_name="get_notification_channels")
        self._check_error(result)
        try:
            return json.loads(result)
        except (json.JSONDecodeError, TypeError) as e:
            raise NotificationError(f"failed to parse response: {e}")

    async def create_notification_channel_group(
        self,
        group_id: str,
        name: str,
        *,
        description: Optional[str] = None,
    ):
        """Create a notification channel group (a labelled set of channels).

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="create_notification_channel_group",
            arguments={"group_id": group_id, "name": name, "description": description},
        )
        return self._check_error(result)

    async def delete_notification_channel_group(self, group_id: str):
        """Delete a notification channel group and all its channels.

        Raises:
            NotificationError: If the native side reports an error.
        """
        result = await self._invoke_method(
            method_name="delete_notification_channel_group",
            arguments={"group_id": group_id},
        )
        return self._check_error(result)
