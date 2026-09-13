import 'dart:async';
import 'dart:convert';

import 'package:flet/flet.dart';
import 'package:flet_android_notifications/src/notifications_service.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:timezone/timezone.dart' as tz;

class TestControl extends Fake implements Control {
  Future<dynamic> Function(String, dynamic)? listener;
  final events = <String>[];
  void Function(String)? beforeEvent;

  @override
  void addInvokeMethodListener(
    Future<dynamic> Function(String, dynamic) value,
  ) {
    listener = value;
  }

  @override
  void removeInvokeMethodListener(
    Future<dynamic> Function(String, dynamic) value,
  ) {
    if (listener == value) listener = null;
  }

  @override
  void triggerEvent(String eventName, [dynamic data]) {
    expect(eventName, 'notification_tap');
    beforeEvent?.call(data as String);
    events.add(data as String);
  }
}

void main() {
  final binding = TestWidgetsFlutterBinding.ensureInitialized();
  const channel = MethodChannel('dexterous.com/flutter/local_notifications');
  const queueKey = 'flet_android_notifications_background_responses';
  late TestControl control;
  late NotificationsService service;
  late List<MethodCall> calls;
  late Future<dynamic> Function(MethodCall) native;

  Future<dynamic> invoke(String name, [dynamic args]) =>
      control.listener!(name, args);

  Map<String, dynamic> scheduleArgs(DateTime instant, {
    String? timeZone,
    String? components,
  }) => {
    'id': 8,
    'title': 'Reminder',
    'body': 'Body',
    'scheduled_epoch_ms': instant.millisecondsSinceEpoch,
    if (timeZone != null) 'time_zone': timeZone,
    'match_date_time_components': components,
    'payload': '',
    'importance': 'default',
    'channel_id': 'reminders',
    'channel_name': 'Reminders',
    'channel_description': '',
    'play_sound': false,
    'enable_vibration': false,
    'actions': <dynamic>[],
    'schedule_mode': 'inexact_allow_while_idle',
  };

  Map<dynamic, dynamic> scheduledPayload() =>
      calls.lastWhere((c) => c.method == 'zonedSchedule').arguments as Map;

  setUp(() {
    debugDefaultTargetPlatformOverride = TargetPlatform.android;
    AndroidFlutterLocalNotificationsPlugin.registerWith();
    SharedPreferences.setMockInitialValues({});
    calls = [];
    native = (call) async {
      if (call.method == 'getNotificationAppLaunchDetails') return null;
      return true;
    };
    binding.defaultBinaryMessenger.setMockMethodCallHandler(channel, (call) {
      calls.add(call);
      return native(call);
    });
    control = TestControl();
    service = NotificationsService(control: control);
  });

  tearDown(() {
    service.dispose();
    binding.defaultBinaryMessenger.setMockMethodCallHandler(channel, null);
    debugDefaultTargetPlatformOverride = null;
  });

  test('replay failure does not complete initialization twice', () async {
    native = (call) async {
      if (call.method == 'getNotificationAppLaunchDetails') {
        throw PlatformException(code: 'replay_failed');
      }
      return true;
    };
    service.init();
    expect(await invoke('are_notifications_enabled'), 'true');
    expect(await invoke('are_notifications_enabled'), 'true');
    expect(calls.where((c) => c.method == 'initialize'), hasLength(1));
  });

  test('failed initialization retries once for concurrent callers', () async {
    final firstAttempt = Completer<bool>();
    var attempts = 0;
    native = (call) async {
      if (call.method == 'initialize') {
        attempts++;
        return attempts == 1 ? firstAttempt.future : true;
      }
      return call.method == 'getNotificationAppLaunchDetails' ? null : true;
    };
    service.init();
    final waiting = invoke('are_notifications_enabled');
    firstAttempt.completeError(PlatformException(code: 'init_failed'));
    await waiting;
    await Future.wait([
      invoke('are_notifications_enabled'),
      invoke('are_notifications_enabled'),
    ]);
    expect(attempts, 2);
  });

  test('launch and queued background actions replay once in order', () async {
    final queued = jsonEncode({'action_id': 'stop', 'notification_id': 2});
    SharedPreferences.setMockInitialValues({
      queueKey: [queued],
    });
    native = (call) async {
      if (call.method == 'getNotificationAppLaunchDetails') {
        return {
          'notificationLaunchedApp': true,
          'notificationResponse': {
            'notificationId': 1,
            'notificationResponseType': 0,
            'payload': 'launch',
          },
        };
      }
      return true;
    };
    service.init();
    await invoke('are_notifications_enabled');
    await invoke('are_notifications_enabled');
    expect(control.events, hasLength(2));
    expect(jsonDecode(control.events.first)['payload'], 'launch');
    expect(control.events.last, queued);
    expect(
      (await SharedPreferences.getInstance()).getStringList(queueKey),
      isNull,
    );
  });

  test('foreground start and stop reach the native plugin', () async {
    service.init();
    expect(
      await invoke('start_foreground_service', {
        'id': 7,
        'title': 'Hosting',
        'body': 'Running',
        'payload': '',
        'importance': 'low',
        'channel_id': 'hosting',
        'channel_name': 'Hosting',
        'channel_description': '',
        'play_sound': false,
        'enable_vibration': false,
        'actions': <dynamic>[],
        'uses_chronometer': true,
        'when': 1000,
        'start_type': 'start_sticky',
      }),
      'ok',
    );
    expect(await invoke('stop_foreground_service'), 'ok');
    expect(
      calls.where((c) => c.method == 'startForegroundService'),
      hasLength(1),
    );
    expect(
      calls.where((c) => c.method == 'stopForegroundService'),
      hasLength(1),
    );
  });

  for (final components in [
    'time', 'day_of_week_and_time', 'day_of_month_and_time', 'date_and_time',
  ].asMap().entries) {
    test('calendar recurrence ${components.value} preserves local time across DST', () async {
      service.init();
      for (final date in [
        ('2026-10-24T06:00:00Z', '2026-10-24T09:00:00'),
        ('2026-10-25T07:00:00Z', '2026-10-25T09:00:00'),
        ('2027-03-27T07:00:00Z', '2027-03-27T09:00:00'),
        ('2027-03-28T06:00:00Z', '2027-03-28T09:00:00'),
      ]) {
        expect(await invoke('schedule_notification', scheduleArgs(
          DateTime.parse(date.$1),
          timeZone: 'Europe/Bucharest', components: components.value,
        )), 'ok');
        expect(scheduledPayload()['timeZoneName'], 'Europe/Bucharest');
        expect(scheduledPayload()['scheduledDateTime'], date.$2);
        expect(scheduledPayload()['matchDateTimeComponents'], components.key);
      }
    });
  }

  test('per-notification zones and legacy payloads ignore global local zone', () async {
    service.init();
    await invoke('are_notifications_enabled');
    tz.setLocalLocation(tz.getLocation('Asia/Tokyo'));
    for (final zone in [
      ('Europe/Bucharest', '2026-10-24T00:30:00'),
      ('America/New_York', '2026-10-23T17:30:00'),
      ('US/Eastern', '2026-10-23T17:30:00'),
      ('UTC', '2026-10-23T21:30:00'),
      (null, '2026-10-23T21:30:00'),
    ]) {
      expect(await invoke('schedule_notification', scheduleArgs(
        DateTime.parse('2026-10-23T21:30:00Z'),
        timeZone: zone.$1, components: 'day_of_week_and_time',
      )), 'ok');
      expect(scheduledPayload()['timeZoneName'], zone.$1 ?? 'UTC');
      expect(scheduledPayload()['scheduledDateTime'], zone.$2);
    }
    expect(tz.local.name, 'Asia/Tokyo');
  });

  test('one-offs preserve both instants in the repeated autumn hour', () async {
    service.init();
    final lastOctoberDay = DateTime.utc(DateTime.now().year + 1, 11, 0);
    final transitionDay = lastOctoberDay.day - lastOctoberDay.weekday % 7;
    for (final hour in [0, 1]) {
      final instant = DateTime.utc(lastOctoberDay.year, 10, transitionDay, hour, 30);
      expect(await invoke('schedule_notification', scheduleArgs(
        instant, timeZone: 'Europe/Bucharest',
      )), 'ok');
      expect(scheduledPayload()['timeZoneName'], 'UTC');
      expect(scheduledPayload()['scheduledDateTime'], instant.toIso8601String().split('.').first);
      expect(scheduledPayload().containsKey('matchDateTimeComponents'), isFalse);
    }
  });

  test('unknown recurrence timezone fails before scheduling natively', () async {
    service.init();
    final result = await invoke('schedule_notification', scheduleArgs(
      DateTime.utc(2030), timeZone: 'Not/A_Zone', components: 'time',
    ));
    expect(result, startsWith('error:'));
    expect(calls.where((c) => c.method == 'zonedSchedule'), isEmpty);
  });

  test('overlapping background callbacks persist separate entries', () async {
    await Future.wait(
      List.generate(
        25,
        (id) => notificationTapBackground(
          NotificationResponse(
            id: id,
            actionId: 'reply',
            notificationResponseType:
                NotificationResponseType.selectedNotificationAction,
          ),
        ),
      ),
    );
    final prefs = await SharedPreferences.getInstance();
    await prefs.reload();
    final keys = prefs.getKeys().where((key) => key.startsWith('${queueKey}_'));
    expect(keys, hasLength(25));
    expect(
      keys
          .map((key) => jsonDecode(prefs.getString(key)!)['notification_id'])
          .toSet(),
      Set.from(List.generate(25, (id) => id)),
    );
  });

  for (final legacy in [false, true]) {
    test(
      'failed handoff retains undelivered entries (legacy=$legacy)',
      () async {
        SharedPreferences.setMockInitialValues(
          legacy
              ? {
                  queueKey: ['first', 'second'],
                }
              : {'${queueKey}_001': 'first', '${queueKey}_002': 'second'},
        );
        control.beforeEvent = (data) {
          if (data == 'second') throw StateError('handoff failed');
        };
        service.init();
        await invoke('are_notifications_enabled');
        final prefs = await SharedPreferences.getInstance();
        await prefs.reload();
        expect(control.events, ['first']);
        if (legacy) {
          expect(prefs.getStringList(queueKey), ['second']);
        } else {
          expect(prefs.getString('${queueKey}_001'), isNull);
          expect(prefs.getString('${queueKey}_002'), 'second');
        }
        service.dispose();
        control.beforeEvent = null;
        service = NotificationsService(control: control)..init();
        await invoke('are_notifications_enabled');
        expect(control.events, ['first', 'second']);
      },
    );
  }

  test('launch lookup failure does not block queued actions', () async {
    SharedPreferences.setMockInitialValues({'${queueKey}_001': 'queued'});
    native = (call) async {
      if (call.method == 'getNotificationAppLaunchDetails') {
        throw PlatformException(code: 'launch_failed');
      }
      return true;
    };
    service.init();
    await invoke('are_notifications_enabled');
    expect(control.events, ['queued']);
  });

  test('an action arriving during replay remains queued', () async {
    SharedPreferences.setMockInitialValues({'${queueKey}_001': 'first'});
    Future<void>? arriving;
    control.beforeEvent = (_) {
      arriving = notificationTapBackground(
        NotificationResponse(
          id: 99,
          actionId: 'later',
          notificationResponseType:
              NotificationResponseType.selectedNotificationAction,
        ),
      );
    };
    service.init();
    await invoke('are_notifications_enabled');
    await arriving;
    final prefs = await SharedPreferences.getInstance();
    await prefs.reload();
    expect(control.events, ['first']);
    final keys = prefs.getKeys().where((key) => key.startsWith('${queueKey}_'));
    expect(keys, hasLength(1));
    expect(jsonDecode(prefs.getString(keys.single)!)['notification_id'], 99);
  });

  test('dispose removes the method listener', () async {
    service.init();
    await invoke('are_notifications_enabled');
    service.dispose();
    expect(control.listener, isNull);
  });
}
