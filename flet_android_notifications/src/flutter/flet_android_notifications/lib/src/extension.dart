import 'package:flet/flet.dart';

import 'notifications_service.dart';

class Extension extends FletExtension {
  @override
  FletService? createService(Control control) {
    switch (control.type) {
      case "flet_android_notifications":
        return NotificationsService(control: control);
      default:
        return null;
    }
  }
}
