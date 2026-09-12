import 'dart:async';
import 'dart:convert';

import 'package:flet/flet.dart';
import 'package:flet_android_notifications/src/notifications_service.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

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
