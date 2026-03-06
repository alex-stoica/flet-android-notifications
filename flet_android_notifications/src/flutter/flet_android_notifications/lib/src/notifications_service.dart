import 'dart:async';
import 'dart:convert';
import 'dart:typed_data' show Int64List;
import 'dart:ui' show Color;
import 'package:flet/flet.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz_data;

class NotificationsService extends FletService {
  NotificationsService({required super.control});

  final FlutterLocalNotificationsPlugin _plugin =
      FlutterLocalNotificationsPlugin();
  Completer<bool>? _initCompleter;
  DateTime? _lastShowTime;

  @override
  void init() {
    super.init();
    control.addInvokeMethodListener(_onMethod);
    _ensureInitialized();
  }

  @override
  void dispose() {
    control.removeInvokeMethodListener(_onMethod);
    super.dispose();
  }

  Future<bool> _ensureInitialized() async {
    if (_initCompleter != null) return _initCompleter!.future;
    _initCompleter = Completer<bool>();

    try {
      tz_data.initializeTimeZones();

      const androidSettings =
          AndroidInitializationSettings('@mipmap/ic_launcher');
      const initSettings = InitializationSettings(android: androidSettings);

      final result = await _plugin.initialize(
        settings: initSettings,
        onDidReceiveNotificationResponse: (response) {
          final hasAction = response.actionId != null && response.actionId!.isNotEmpty;
          // Debounce only body taps — Samsung OneUI fires phantom body taps
          // on show, but action button presses are always intentional.
          if (!hasAction &&
              _lastShowTime != null &&
              DateTime.now().difference(_lastShowTime!).inSeconds < 3) {
            return;
          }
          control.triggerEvent("notification_tap", jsonEncode({
            "payload": response.payload ?? "",
            "action_id": response.actionId ?? "",
          }));
        },
      );
      _initCompleter!.complete(result ?? false);
    } catch (e) {
      _initCompleter!.complete(false);
    }

    return _initCompleter!.future;
  }

  Importance _parseImportance(String value) {
    switch (value) {
      case "none":
        return Importance.none;
      case "min":
        return Importance.min;
      case "low":
        return Importance.low;
      case "default":
        return Importance.defaultImportance;
      case "high":
        return Importance.high;
      case "max":
        return Importance.max;
      default:
        return Importance.high;
    }
  }

  Priority _priorityFromImportance(Importance importance) {
    switch (importance) {
      case Importance.none:
      case Importance.min:
        return Priority.min;
      case Importance.low:
        return Priority.low;
      case Importance.defaultImportance:
        return Priority.defaultPriority;
      case Importance.high:
        return Priority.high;
      case Importance.max:
        return Priority.max;
      default:
        return Priority.defaultPriority;
    }
  }

  AndroidScheduleMode _parseAndroidScheduleMode(String value) {
    switch (value) {
      case "alarm_clock":
        return AndroidScheduleMode.alarmClock;
      case "exact":
        return AndroidScheduleMode.exact;
      case "exact_allow_while_idle":
        return AndroidScheduleMode.exactAllowWhileIdle;
      case "inexact":
        return AndroidScheduleMode.inexact;
      case "inexact_allow_while_idle":
        return AndroidScheduleMode.inexactAllowWhileIdle;
      default:
        return AndroidScheduleMode.inexactAllowWhileIdle;
    }
  }

  DateTimeComponents? _parseDateTimeComponents(String? value) {
    if (value == null) return null;
    switch (value) {
      case "time":
        return DateTimeComponents.time;
      case "day_of_week_and_time":
        return DateTimeComponents.dayOfWeekAndTime;
      case "day_of_month_and_time":
        return DateTimeComponents.dayOfMonthAndTime;
      case "date_and_time":
        return DateTimeComponents.dateAndTime;
      default:
        return null;
    }
  }

  GroupAlertBehavior _parseGroupAlertBehavior(String value) {
    switch (value) {
      case "summary":
        return GroupAlertBehavior.summary;
      case "children":
        return GroupAlertBehavior.children;
      default:
        return GroupAlertBehavior.all;
    }
  }

  Color? _parseColor(String? hex) {
    if (hex == null) return null;
    hex = hex.replaceFirst('#', '');
    if (hex.length == 6) hex = 'FF$hex';
    return Color(int.parse(hex, radix: 16));
  }

  AndroidBitmap<Object>? _parseLargeIcon(String? value, String type) {
    if (value == null) return null;
    if (type == "file_path") {
      return FilePathAndroidBitmap(value);
    }
    return DrawableResourceAndroidBitmap(value);
  }

  NotificationVisibility? _parseVisibility(String? value) {
    if (value == null) return null;
    switch (value) {
      case "public":
        return NotificationVisibility.public;
      case "private":
        return NotificationVisibility.private;
      case "secret":
        return NotificationVisibility.secret;
      default:
        return null;
    }
  }

  StyleInformation? _parseStyleInformation(Map<String, dynamic>? style) {
    if (style == null) return null;
    switch (style["type"]) {
      case "big_text":
        return BigTextStyleInformation(
          style["big_text"] as String,
          contentTitle: style["content_title"] as String?,
          summaryText: style["summary_text"] as String?,
        );
      case "big_picture":
        final bitmapType = style["bitmap_type"] as String;
        final bitmapValue = style["bitmap_value"] as String;
        AndroidBitmap<Object> bitmap;
        if (bitmapType == "file_path") {
          bitmap = FilePathAndroidBitmap(bitmapValue);
        } else {
          bitmap = DrawableResourceAndroidBitmap(bitmapValue);
        }
        AndroidBitmap<Object>? largeIcon;
        if (style["large_icon_type"] != null) {
          final iconType = style["large_icon_type"] as String;
          final iconValue = style["large_icon_value"] as String;
          if (iconType == "file_path") {
            largeIcon = FilePathAndroidBitmap(iconValue);
          } else {
            largeIcon = DrawableResourceAndroidBitmap(iconValue);
          }
        }
        return BigPictureStyleInformation(
          bitmap,
          contentTitle: style["content_title"] as String?,
          summaryText: style["summary_text"] as String?,
          largeIcon: largeIcon,
          hideExpandedLargeIcon: style["hide_expanded_large_icon"] as bool? ?? false,
        );
      case "inbox":
        final lines = (style["lines"] as List<dynamic>).cast<String>();
        return InboxStyleInformation(
          lines,
          contentTitle: style["content_title"] as String?,
          summaryText: style["summary_text"] as String?,
        );
      default:
        return null;
    }
  }

  RepeatInterval _parseRepeatInterval(String value) {
    switch (value) {
      case "every_minute":
        return RepeatInterval.everyMinute;
      case "hourly":
        return RepeatInterval.hourly;
      case "daily":
        return RepeatInterval.daily;
      case "weekly":
        return RepeatInterval.weekly;
      default:
        return RepeatInterval.daily;
    }
  }

  AndroidServiceStartType _parseServiceStartType(String value) {
    switch (value) {
      case "start_sticky":
        return AndroidServiceStartType.startSticky;
      case "start_not_sticky":
        return AndroidServiceStartType.startNotSticky;
      case "start_sticky_compatibility":
        return AndroidServiceStartType.startStickyCompatibility;
      case "start_redeliver_intent":
        return AndroidServiceStartType.startRedeliverIntent;
      default:
        return AndroidServiceStartType.startSticky;
    }
  }

  Set<AndroidServiceForegroundType>? _parseForegroundServiceTypes(
      List<dynamic>? values) {
    if (values == null || values.isEmpty) return null;
    final map = <String, AndroidServiceForegroundType>{
      "data_sync": AndroidServiceForegroundType.dataSync,
      "media_playback": AndroidServiceForegroundType.mediaPlayback,
      "phone_call": AndroidServiceForegroundType.phoneCall,
      "location": AndroidServiceForegroundType.location,
      "connected_device": AndroidServiceForegroundType.connectedDevice,
      "media_projection": AndroidServiceForegroundType.mediaProjection,
      "camera": AndroidServiceForegroundType.camera,
      "microphone": AndroidServiceForegroundType.microphone,
      "health": AndroidServiceForegroundType.health,
      "remote_messaging": AndroidServiceForegroundType.remoteMessaging,
      "system_exempted": AndroidServiceForegroundType.systemExempted,
      "short_service": AndroidServiceForegroundType.shortService,
      "special_use": AndroidServiceForegroundType.specialUse,
    };
    return values
        .map((v) => map[v as String])
        .whereType<AndroidServiceForegroundType>()
        .toSet();
  }

  NotificationDetails _buildNotificationDetails({
    required String channelId,
    required String channelName,
    required String channelDescription,
    required Importance importance,
    required Priority priority,
    required bool playSound,
    required bool enableVibration,
    required List<AndroidNotificationAction> actions,
    StyleInformation? styleInformation,
    bool showProgress = false,
    int maxProgress = 0,
    int progress = 0,
    bool indeterminate = false,
    String? groupKey,
    bool setAsGroupSummary = false,
    GroupAlertBehavior groupAlertBehavior = GroupAlertBehavior.all,
    String? icon,
    AndroidBitmap<Object>? largeIcon,
    Color? color,
    bool colorized = false,
    String? sound,
    bool ongoing = false,
    bool autoCancel = true,
    bool silent = false,
    bool onlyAlertOnce = false,
    NotificationVisibility? visibility,
    String? subText,
    bool channelBypassDnd = false,
    Int64List? vibrationPattern,
    int? timeoutAfter,
  }) {
    final androidDetails = AndroidNotificationDetails(
      channelId,
      channelName,
      channelDescription: channelDescription,
      importance: importance,
      priority: priority,
      playSound: playSound,
      enableVibration: enableVibration,
      actions: actions,
      styleInformation: styleInformation,
      showProgress: showProgress,
      maxProgress: maxProgress,
      progress: progress,
      indeterminate: indeterminate,
      groupKey: groupKey,
      setAsGroupSummary: setAsGroupSummary,
      groupAlertBehavior: groupAlertBehavior,
      icon: icon,
      largeIcon: largeIcon,
      color: color,
      colorized: colorized,
      sound: sound != null ? RawResourceAndroidNotificationSound(sound) : null,
      ongoing: ongoing,
      autoCancel: autoCancel,
      silent: silent,
      onlyAlertOnce: onlyAlertOnce,
      visibility: visibility,
      subText: subText,
      channelBypassDnd: channelBypassDnd,
      vibrationPattern: vibrationPattern,
      timeoutAfter: timeoutAfter,
    );
    return NotificationDetails(android: androidDetails);
  }

  List<AndroidNotificationAction> _parseActions(List<dynamic> raw) {
    return raw
        .map((action) => AndroidNotificationAction(
              action["id"] as String,
              action["title"] as String,
              cancelNotification: true,
              showsUserInterface: true,
            ))
        .toList();
  }

  Future<dynamic> _onMethod(String name, dynamic args) async {
    try {
      switch (name) {
        case "show_notification":
          final a = Map<String, dynamic>.from(args as Map);
          final importance = _parseImportance(a["importance"] as String);
          final rawStyle = a["style"];
          final styleInfo = _parseStyleInformation(
              rawStyle != null ? Map<String, dynamic>.from(rawStyle as Map) : null);
          await _showNotification(
            a["id"] as int,
            a["title"] as String,
            a["body"] as String,
            payload: a["payload"] as String,
            channelId: a["channel_id"] as String,
            channelName: a["channel_name"] as String,
            channelDescription: a["channel_description"] as String,
            importance: importance,
            priority: _priorityFromImportance(importance),
            playSound: a["play_sound"] as bool,
            enableVibration: a["enable_vibration"] as bool,
            actions: _parseActions(a["actions"] as List<dynamic>),
            styleInformation: styleInfo,
            showProgress: a["show_progress"] as bool? ?? false,
            maxProgress: a["max_progress"] as int? ?? 0,
            progress: a["progress"] as int? ?? 0,
            indeterminate: a["indeterminate"] as bool? ?? false,
            groupKey: a["group_key"] as String?,
            setAsGroupSummary: a["set_as_group_summary"] as bool? ?? false,
            groupAlertBehavior: _parseGroupAlertBehavior(
                a["group_alert_behavior"] as String? ?? "all"),
            icon: a["icon"] as String?,
            largeIcon: _parseLargeIcon(
                a["large_icon"] as String?,
                a["large_icon_type"] as String? ?? "drawable_resource"),
            color: _parseColor(a["color"] as String?),
            colorized: a["colorized"] as bool? ?? false,
            sound: a["sound"] as String?,
            ongoing: a["ongoing"] as bool? ?? false,
            autoCancel: a["auto_cancel"] as bool? ?? true,
            silent: a["silent"] as bool? ?? false,
            onlyAlertOnce: a["only_alert_once"] as bool? ?? false,
            visibility: _parseVisibility(a["visibility"] as String?),
            subText: a["sub_text"] as String?,
            channelBypassDnd: a["channel_bypass_dnd"] as bool? ?? false,
            vibrationPattern: a["vibration_pattern"] != null
                ? Int64List.fromList(
                    (a["vibration_pattern"] as List<dynamic>).cast<int>())
                : null,
            timeoutAfter: a["timeout_after"] as int?,
          );
          return "ok";
        case "schedule_notification":
          final a = Map<String, dynamic>.from(args as Map);
          final importance = _parseImportance(a["importance"] as String);
          final rawStyle = a["style"];
          final styleInfo = _parseStyleInformation(
              rawStyle != null ? Map<String, dynamic>.from(rawStyle as Map) : null);
          await _scheduleNotification(
            a["id"] as int,
            a["title"] as String,
            a["body"] as String,
            scheduledEpochMs: a["scheduled_epoch_ms"] as int,
            payload: a["payload"] as String,
            channelId: a["channel_id"] as String,
            channelName: a["channel_name"] as String,
            channelDescription: a["channel_description"] as String,
            importance: importance,
            priority: _priorityFromImportance(importance),
            playSound: a["play_sound"] as bool,
            enableVibration: a["enable_vibration"] as bool,
            actions: _parseActions(a["actions"] as List<dynamic>),
            scheduleMode: _parseAndroidScheduleMode(
                a["schedule_mode"] as String),
            matchDateTimeComponents: _parseDateTimeComponents(
                a["match_date_time_components"] as String?),
            styleInformation: styleInfo,
            showProgress: a["show_progress"] as bool? ?? false,
            maxProgress: a["max_progress"] as int? ?? 0,
            progress: a["progress"] as int? ?? 0,
            indeterminate: a["indeterminate"] as bool? ?? false,
            groupKey: a["group_key"] as String?,
            setAsGroupSummary: a["set_as_group_summary"] as bool? ?? false,
            groupAlertBehavior: _parseGroupAlertBehavior(
                a["group_alert_behavior"] as String? ?? "all"),
            icon: a["icon"] as String?,
            largeIcon: _parseLargeIcon(
                a["large_icon"] as String?,
                a["large_icon_type"] as String? ?? "drawable_resource"),
            color: _parseColor(a["color"] as String?),
            colorized: a["colorized"] as bool? ?? false,
            sound: a["sound"] as String?,
            ongoing: a["ongoing"] as bool? ?? false,
            autoCancel: a["auto_cancel"] as bool? ?? true,
            silent: a["silent"] as bool? ?? false,
            onlyAlertOnce: a["only_alert_once"] as bool? ?? false,
            visibility: _parseVisibility(a["visibility"] as String?),
            subText: a["sub_text"] as String?,
            channelBypassDnd: a["channel_bypass_dnd"] as bool? ?? false,
            vibrationPattern: a["vibration_pattern"] != null
                ? Int64List.fromList(
                    (a["vibration_pattern"] as List<dynamic>).cast<int>())
                : null,
            timeoutAfter: a["timeout_after"] as int?,
          );
          return "ok";
        case "periodically_show":
          await _ensureInitialized();
          final a = Map<String, dynamic>.from(args as Map);
          final importance = _parseImportance(a["importance"] as String);
          final rawStyle = a["style"];
          final styleInfo = _parseStyleInformation(
              rawStyle != null ? Map<String, dynamic>.from(rawStyle as Map) : null);
          final details = _buildNotificationDetails(
            channelId: a["channel_id"] as String,
            channelName: a["channel_name"] as String,
            channelDescription: a["channel_description"] as String,
            importance: importance,
            priority: _priorityFromImportance(importance),
            playSound: a["play_sound"] as bool,
            enableVibration: a["enable_vibration"] as bool,
            actions: _parseActions(a["actions"] as List<dynamic>),
            styleInformation: styleInfo,
            showProgress: a["show_progress"] as bool? ?? false,
            maxProgress: a["max_progress"] as int? ?? 0,
            progress: a["progress"] as int? ?? 0,
            indeterminate: a["indeterminate"] as bool? ?? false,
            groupKey: a["group_key"] as String?,
            setAsGroupSummary: a["set_as_group_summary"] as bool? ?? false,
            groupAlertBehavior: _parseGroupAlertBehavior(
                a["group_alert_behavior"] as String? ?? "all"),
            icon: a["icon"] as String?,
            largeIcon: _parseLargeIcon(
                a["large_icon"] as String?,
                a["large_icon_type"] as String? ?? "drawable_resource"),
            color: _parseColor(a["color"] as String?),
            colorized: a["colorized"] as bool? ?? false,
            sound: a["sound"] as String?,
            ongoing: a["ongoing"] as bool? ?? false,
            autoCancel: a["auto_cancel"] as bool? ?? true,
            silent: a["silent"] as bool? ?? false,
            onlyAlertOnce: a["only_alert_once"] as bool? ?? false,
            visibility: _parseVisibility(a["visibility"] as String?),
            subText: a["sub_text"] as String?,
            channelBypassDnd: a["channel_bypass_dnd"] as bool? ?? false,
            vibrationPattern: a["vibration_pattern"] != null
                ? Int64List.fromList(
                    (a["vibration_pattern"] as List<dynamic>).cast<int>())
                : null,
            timeoutAfter: a["timeout_after"] as int?,
          );
          await _plugin.periodicallyShow(
            id: a["id"] as int,
            title: a["title"] as String,
            body: a["body"] as String,
            notificationDetails: details,
            repeatInterval: _parseRepeatInterval(a["repeat_interval"] as String),
            androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
            payload: a["payload"] as String,
          );
          return "ok";
        case "periodically_show_with_duration":
          await _ensureInitialized();
          final a = Map<String, dynamic>.from(args as Map);
          final importance = _parseImportance(a["importance"] as String);
          final rawStyle = a["style"];
          final styleInfo = _parseStyleInformation(
              rawStyle != null ? Map<String, dynamic>.from(rawStyle as Map) : null);
          final details = _buildNotificationDetails(
            channelId: a["channel_id"] as String,
            channelName: a["channel_name"] as String,
            channelDescription: a["channel_description"] as String,
            importance: importance,
            priority: _priorityFromImportance(importance),
            playSound: a["play_sound"] as bool,
            enableVibration: a["enable_vibration"] as bool,
            actions: _parseActions(a["actions"] as List<dynamic>),
            styleInformation: styleInfo,
            showProgress: a["show_progress"] as bool? ?? false,
            maxProgress: a["max_progress"] as int? ?? 0,
            progress: a["progress"] as int? ?? 0,
            indeterminate: a["indeterminate"] as bool? ?? false,
            groupKey: a["group_key"] as String?,
            setAsGroupSummary: a["set_as_group_summary"] as bool? ?? false,
            groupAlertBehavior: _parseGroupAlertBehavior(
                a["group_alert_behavior"] as String? ?? "all"),
            icon: a["icon"] as String?,
            largeIcon: _parseLargeIcon(
                a["large_icon"] as String?,
                a["large_icon_type"] as String? ?? "drawable_resource"),
            color: _parseColor(a["color"] as String?),
            colorized: a["colorized"] as bool? ?? false,
            sound: a["sound"] as String?,
            ongoing: a["ongoing"] as bool? ?? false,
            autoCancel: a["auto_cancel"] as bool? ?? true,
            silent: a["silent"] as bool? ?? false,
            onlyAlertOnce: a["only_alert_once"] as bool? ?? false,
            visibility: _parseVisibility(a["visibility"] as String?),
            subText: a["sub_text"] as String?,
            channelBypassDnd: a["channel_bypass_dnd"] as bool? ?? false,
            vibrationPattern: a["vibration_pattern"] != null
                ? Int64List.fromList(
                    (a["vibration_pattern"] as List<dynamic>).cast<int>())
                : null,
            timeoutAfter: a["timeout_after"] as int?,
          );
          await _plugin.periodicallyShowWithDuration(
            id: a["id"] as int,
            title: a["title"] as String,
            body: a["body"] as String,
            notificationDetails: details,
            repeatDurationInterval: Duration(milliseconds: a["duration_ms"] as int),
            androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
            payload: a["payload"] as String,
          );
          return "ok";
        case "start_foreground_service":
          await _ensureInitialized();
          final a = Map<String, dynamic>.from(args as Map);
          final importance = _parseImportance(a["importance"] as String);
          final rawStyle = a["style"];
          final styleInfo = _parseStyleInformation(
              rawStyle != null ? Map<String, dynamic>.from(rawStyle as Map) : null);
          final details = _buildNotificationDetails(
            channelId: a["channel_id"] as String,
            channelName: a["channel_name"] as String,
            channelDescription: a["channel_description"] as String,
            importance: importance,
            priority: _priorityFromImportance(importance),
            playSound: a["play_sound"] as bool,
            enableVibration: a["enable_vibration"] as bool,
            actions: _parseActions(a["actions"] as List<dynamic>),
            styleInformation: styleInfo,
            showProgress: a["show_progress"] as bool? ?? false,
            maxProgress: a["max_progress"] as int? ?? 0,
            progress: a["progress"] as int? ?? 0,
            indeterminate: a["indeterminate"] as bool? ?? false,
            groupKey: a["group_key"] as String?,
            setAsGroupSummary: a["set_as_group_summary"] as bool? ?? false,
            groupAlertBehavior: _parseGroupAlertBehavior(
                a["group_alert_behavior"] as String? ?? "all"),
            icon: a["icon"] as String?,
            largeIcon: _parseLargeIcon(
                a["large_icon"] as String?,
                a["large_icon_type"] as String? ?? "drawable_resource"),
            color: _parseColor(a["color"] as String?),
            colorized: a["colorized"] as bool? ?? false,
            sound: a["sound"] as String?,
            ongoing: a["ongoing"] as bool? ?? false,
            autoCancel: a["auto_cancel"] as bool? ?? true,
            silent: a["silent"] as bool? ?? false,
            onlyAlertOnce: a["only_alert_once"] as bool? ?? false,
            visibility: _parseVisibility(a["visibility"] as String?),
            subText: a["sub_text"] as String?,
            channelBypassDnd: a["channel_bypass_dnd"] as bool? ?? false,
            vibrationPattern: a["vibration_pattern"] != null
                ? Int64List.fromList(
                    (a["vibration_pattern"] as List<dynamic>).cast<int>())
                : null,
            timeoutAfter: a["timeout_after"] as int?,
          );
          final android = _plugin.resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();
          await android?.startForegroundService(
            a["id"] as int,
            a["title"] as String,
            a["body"] as String,
            notificationDetails: details.android,
            payload: a["payload"] as String,
            startType: _parseServiceStartType(a["start_type"] as String),
            foregroundServiceTypes: _parseForegroundServiceTypes(
                a["foreground_service_types"] as List<dynamic>?),
          );
          return "ok";
        case "stop_foreground_service":
          await _ensureInitialized();
          final android = _plugin.resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();
          await android?.stopForegroundService();
          return "ok";
        case "get_active_notifications":
          await _ensureInitialized();
          final active = await _plugin.getActiveNotifications();
          final list = active.map((n) => {
            "id": n.id,
            "title": n.title ?? "",
            "body": n.body ?? "",
            "channel_id": n.channelId ?? "",
            "payload": n.payload ?? "",
          }).toList();
          return jsonEncode(list);
        case "get_pending_notifications":
          await _ensureInitialized();
          final pending = await _plugin.pendingNotificationRequests();
          final list = pending.map((n) => {
            "id": n.id,
            "title": n.title ?? "",
            "body": n.body ?? "",
            "payload": n.payload ?? "",
          }).toList();
          return jsonEncode(list);
        case "cancel":
          final a = Map<String, dynamic>.from(args as Map);
          await _plugin.cancel(id: a["id"] as int);
          return "ok";
        case "cancel_all":
          await _plugin.cancelAll();
          return "ok";
        case "request_permissions":
          final granted = await _requestPermissions();
          return granted.toString();
        case "request_exact_alarm_permission":
          final granted = await _requestExactAlarmPermission();
          return granted.toString();
      }
      return null;
    } catch (e) {
      return "error:$e";
    }
  }

  Future<void> _showNotification(
    int id,
    String title,
    String body, {
    required String payload,
    required String channelId,
    required String channelName,
    required String channelDescription,
    required Importance importance,
    required Priority priority,
    required bool playSound,
    required bool enableVibration,
    required List<AndroidNotificationAction> actions,
    StyleInformation? styleInformation,
    bool showProgress = false,
    int maxProgress = 0,
    int progress = 0,
    bool indeterminate = false,
    String? groupKey,
    bool setAsGroupSummary = false,
    GroupAlertBehavior groupAlertBehavior = GroupAlertBehavior.all,
    String? icon,
    AndroidBitmap<Object>? largeIcon,
    Color? color,
    bool colorized = false,
    String? sound,
    bool ongoing = false,
    bool autoCancel = true,
    bool silent = false,
    bool onlyAlertOnce = false,
    NotificationVisibility? visibility,
    String? subText,
    bool channelBypassDnd = false,
    Int64List? vibrationPattern,
    int? timeoutAfter,
  }) async {
    final initialized = await _ensureInitialized();
    if (!initialized) {
      throw Exception('Notification plugin failed to initialize');
    }
    _lastShowTime = DateTime.now();

    final details = _buildNotificationDetails(
      channelId: channelId,
      channelName: channelName,
      channelDescription: channelDescription,
      importance: importance,
      priority: priority,
      playSound: playSound,
      enableVibration: enableVibration,
      actions: actions,
      styleInformation: styleInformation,
      showProgress: showProgress,
      maxProgress: maxProgress,
      progress: progress,
      indeterminate: indeterminate,
      groupKey: groupKey,
      setAsGroupSummary: setAsGroupSummary,
      groupAlertBehavior: groupAlertBehavior,
      icon: icon,
      largeIcon: largeIcon,
      color: color,
      colorized: colorized,
      sound: sound,
      ongoing: ongoing,
      autoCancel: autoCancel,
      silent: silent,
      onlyAlertOnce: onlyAlertOnce,
      visibility: visibility,
      subText: subText,
      channelBypassDnd: channelBypassDnd,
      vibrationPattern: vibrationPattern,
      timeoutAfter: timeoutAfter,
    );

    await _plugin.show(id: id, title: title, body: body, notificationDetails: details, payload: payload);
  }

  Future<void> _scheduleNotification(
    int id,
    String title,
    String body, {
    required int scheduledEpochMs,
    required String payload,
    required String channelId,
    required String channelName,
    required String channelDescription,
    required Importance importance,
    required Priority priority,
    required bool playSound,
    required bool enableVibration,
    required List<AndroidNotificationAction> actions,
    required AndroidScheduleMode scheduleMode,
    required DateTimeComponents? matchDateTimeComponents,
    StyleInformation? styleInformation,
    bool showProgress = false,
    int maxProgress = 0,
    int progress = 0,
    bool indeterminate = false,
    String? groupKey,
    bool setAsGroupSummary = false,
    GroupAlertBehavior groupAlertBehavior = GroupAlertBehavior.all,
    String? icon,
    AndroidBitmap<Object>? largeIcon,
    Color? color,
    bool colorized = false,
    String? sound,
    bool ongoing = false,
    bool autoCancel = true,
    bool silent = false,
    bool onlyAlertOnce = false,
    NotificationVisibility? visibility,
    String? subText,
    bool channelBypassDnd = false,
    Int64List? vibrationPattern,
    int? timeoutAfter,
  }) async {
    final initialized = await _ensureInitialized();
    if (!initialized) {
      throw Exception('Notification plugin failed to initialize');
    }

    final scheduledDate = tz.TZDateTime.from(
      DateTime.fromMillisecondsSinceEpoch(scheduledEpochMs, isUtc: true),
      tz.local,
    );

    final details = _buildNotificationDetails(
      channelId: channelId,
      channelName: channelName,
      channelDescription: channelDescription,
      importance: importance,
      priority: priority,
      playSound: playSound,
      enableVibration: enableVibration,
      actions: actions,
      styleInformation: styleInformation,
      showProgress: showProgress,
      maxProgress: maxProgress,
      progress: progress,
      indeterminate: indeterminate,
      groupKey: groupKey,
      setAsGroupSummary: setAsGroupSummary,
      groupAlertBehavior: groupAlertBehavior,
      icon: icon,
      largeIcon: largeIcon,
      color: color,
      colorized: colorized,
      sound: sound,
      ongoing: ongoing,
      autoCancel: autoCancel,
      silent: silent,
      onlyAlertOnce: onlyAlertOnce,
      visibility: visibility,
      subText: subText,
      channelBypassDnd: channelBypassDnd,
      vibrationPattern: vibrationPattern,
      timeoutAfter: timeoutAfter,
    );

    await _plugin.zonedSchedule(
      id: id,
      title: title,
      body: body,
      scheduledDate: scheduledDate,
      notificationDetails: details,
      androidScheduleMode: scheduleMode,
      payload: payload,
      matchDateTimeComponents: matchDateTimeComponents,
    );
  }

  Future<bool> _requestPermissions() async {
    await _ensureInitialized();

    final android = _plugin.resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>();
    if (android == null) return false;

    final granted = await android.requestNotificationsPermission();
    return granted ?? false;
  }

  Future<bool> _requestExactAlarmPermission() async {
    await _ensureInitialized();

    final android = _plugin.resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>();
    if (android == null) return false;

    final granted = await android.requestExactAlarmsPermission();
    return granted ?? false;
  }
}
