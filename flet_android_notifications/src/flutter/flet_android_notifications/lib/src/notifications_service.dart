import 'dart:async';
import 'dart:convert';
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
        initSettings,
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

  NotificationDetails _buildNotificationDetails({
    required String channelId,
    required String channelName,
    required String channelDescription,
    required Importance importance,
    required Priority priority,
    required bool playSound,
    required bool enableVibration,
    required List<AndroidNotificationAction> actions,
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
          );
          return "ok";
        case "schedule_notification":
          final a = Map<String, dynamic>.from(args as Map);
          final importance = _parseImportance(a["importance"] as String);
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
          );
          return "ok";
        case "cancel":
          final a = Map<String, dynamic>.from(args as Map);
          await _plugin.cancel(a["id"] as int);
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
  }) async {
    await _ensureInitialized();
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
    );

    await _plugin.show(id, title, body, details, payload: payload);
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
  }) async {
    await _ensureInitialized();

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
    );

    await _plugin.zonedSchedule(
      id,
      title,
      body,
      scheduledDate,
      details,
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
