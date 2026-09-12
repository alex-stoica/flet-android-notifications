# Notification parameter reference

[Setup and examples](https://github.com/alex-stoica/flet-android-notifications#quick-start)

`show_notification`, `schedule_notification`, `periodically_show`, and `periodically_show_with_duration` all share a common set of parameters. Only the required ones differ per method.

### Required parameters

| Parameter | `show` | `schedule` | `periodically_show` | `periodically_show_with_duration` |
|---|---|---|---|---|
| `notification_id` | int | int | int | int |
| `title` | str | str | str | str |
| `body` | str | str | str | str |
| `scheduled_time` | — | datetime | — | — |
| `repeat_interval` | — | — | str | — |
| `duration_seconds` | — | — | — | int\|float |

`repeat_interval` is one of `"every_minute"`, `"hourly"`, `"daily"`, `"weekly"`.

### Common optional parameters

These work on all four methods above (exceptions are noted in the Description column).

**Basics:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `payload` | `str` | `""` | returned in tap callback |
| `actions` | `list[NotificationAction\|dict]` | `None` | action buttons and optional inline reply inputs |
| `importance` | `str` | `"high"` | `none`, `min`, `low`, `default`, `high`, `max` |
| `timeout_after` | `int\|None` | `None` | auto-dismiss after N milliseconds |
| `category` | `str\|None` | `None` | notification type hint for DND filtering |
| `full_screen_intent` | `bool` | `False` | launch a full-screen / high-priority heads-up UI. **`show_notification` and `schedule_notification` only.** Needs `USE_FULL_SCREEN_INTENT` (Android 14+, see `request_full_screen_intent_permission()`) |

**Channel:**

| Parameter | Type | Default |
|---|---|---|
| `channel_id` | `str` | `"flet_notifications"` |
| `channel_name` | `str` | `"Flet Notifications"` |
| `channel_description` | `str` | `"Notifications from Flet app"` |
| `channel_bypass_dnd` | `bool` | `False` |

`channel_bypass_dnd` only takes effect when the app has do-not-disturb policy access — check with
`has_notification_policy_access()` and request it via `request_notification_policy_access()`. A
channel's sound/importance/vibration are fixed at creation; use the channel-management methods to
configure channels. Use a new channel ID for different defaults; deleting and
recreating the same ID restores its old settings.

**Appearance:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `icon` | `str\|None` | `None` | drawable resource for small icon |
| `large_icon` | `str\|None` | `None` | thumbnail on right side |
| `large_icon_type` | `str` | `"drawable_resource"` | or `"file_path"` |
| `color` | `str\|None` | `None` | hex accent color, e.g. `"#FF5722"` |
| `colorized` | `bool` | `False` | color as background — only takes effect on `start_foreground_service` calls |
| `sub_text` | `str\|None` | `None` | small text below content |
| `visibility` | `str\|None` | `None` | `"public"`, `"private"`, or `"secret"` |

**Behavior:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `play_sound` | `bool` | `True` | play notification sound |
| `enable_vibration` | `bool` | `True` | vibrate |
| `sound` | `str\|None` | `None` | raw resource name (e.g. `"alert_tone"`) |
| `vibration_pattern` | `list[int]\|None` | `None` | e.g. `[0, 500, 200, 500]` |
| `ongoing` | `bool` | `False` | sticky on Android 13 and below, dismissible on 14+ (see note) |
| `auto_cancel` | `bool` | `True` | dismiss on tap |
| `silent` | `bool` | `False` | suppress sound and vibration |
| `only_alert_once` | `bool` | `False` | alert on first show only |

> **Android 14+:** users can individually dismiss ongoing notifications while unlocked,
> including foreground-service notifications. Lock-screen and "Clear all" protection
> remain; exceptions include media and call-style notifications
> ([platform change](https://developer.android.com/about/versions/14/behavior-changes-all#non-dismissable-notifications)).

**Styles and progress:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `style` | `BigTextStyle\|BigPictureStyle\|InboxStyle\|MessagingStyle\|None` | `None` | rich expandable style |
| `show_progress` | `bool` | `False` | show progress bar |
| `max_progress` | `int` | `0` | max value |
| `progress` | `int` | `0` | current value |
| `indeterminate` | `bool` | `False` | spinning progress bar |

**Grouping:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `group_key` | `str\|None` | `None` | bundle notifications together |
| `set_as_group_summary` | `bool` | `False` | this is the group summary |
| `group_alert_behavior` | `str` | `"all"` | `"all"`, `"summary"`, `"children"` |

### Scheduling parameters

| Parameter | Applies to | Type | Default | Description |
|---|---|---|---|---|
| `schedule_mode` | `schedule_notification`, `periodically_show`, `periodically_show_with_duration` | `str` | `"inexact_allow_while_idle"` | see modes below |
| `match_date_time_components` | `schedule_notification` only | `str\|None` | `None` | `"time"` (daily), `"day_of_week_and_time"` (weekly), `"day_of_month_and_time"` (monthly), `"date_and_time"` (yearly) |

`schedule_mode` lets the periodic methods choose an exact mode too (previously they were hardcoded
to `inexact_allow_while_idle`). Exact modes require `SCHEDULE_EXACT_ALARM` — check first with
`can_schedule_exact_notifications()`, otherwise the OS rejects them with `exact_alarms_not_permitted`.

**Schedule modes:**

| Mode | Exact alarm permission? | Fires in Doze? |
|---|---|---|
| `"inexact"` | no | no |
| `"inexact_allow_while_idle"` | no | yes |
| `"exact"` | yes | no |
| `"exact_allow_while_idle"` | yes | yes |
| `"alarm_clock"` | yes | yes |

---
