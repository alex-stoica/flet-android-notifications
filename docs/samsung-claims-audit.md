# Samsung "unsupported" claims — on-device re-audit

Re-judged on a **Samsung Galaxy S25 (SM-S931B), One UI, Android 16**, with `adb dumpsys` +
screenshots. Source for each verdict is the per-button file in `button-tests/`. Guiding rule from
`insights/errors.md`: **do not blame Samsung before checking the merged manifest**; "didn't fire at
all" is almost always a manifest/permission/channel issue, while visual-only differences are the
genuinely OEM-dependent ones.

| Report claim | Re-audited verdict | Evidence |
|---|---|---|
| `colorized=True` foreground bg unsupported on Samsung | **FALSE — works** | `colorized=true`, `color=0xffff0000`, ForegroundService running, **solid red background renders** (`button-tests/23-foreground-service.md`) |
| Scheduled/periodic "doesn't fire on Samsung" | **FALSE — fires** | scheduled fired after 10 s; periodics registered as pending; `dumpsys alarm` has the alarms (`17/19/20`). Was a missing-receiver bug, now patched |
| Lock-screen `visibility="secret"` unsupported | **FALSE — works** | `vis=SECRET`, fired while locked, no content on lock screen (`14-secret.md`) |
| Regular `color` on `show_notification` | **Delivered, not rendered (OEM)** | `color=0xffff0000` reaches OS but One UI **Brief mode** paints no tint; identical to a no-color notification. Renders on AOSP/Pixel (`02-colored.md`) |
| `colorized=True` on **regular** notifications | **Android contract, not Samsung** | colorized applies only to foreground-service / media-style notifications; silently ignored otherwise |
| Grouping / One UI auto-grouping masks `groupKey` | **groupKey works; custom summary masked** | children bundle under `group_key`; One UI substitutes its own group header for the custom `InboxStyle` summary (`03-group.md`) |
| Action title color / icons / contextual | **Callbacks work; visuals OEM** | `Reply` (inline RemoteInput) + `Archive` (broadcast) intents fire; title-color/contextual rendering is One UI-styled (`12b-rich-actions.md`) |
| Vibration / custom sound unsupported | **FALSE — works** | custom sound bound to channel (`mSound=.../raw/test_beep`), custom pattern on channel (`mVibrationPattern=[...]`). Feeling it depends on device vibration-intensity/DND settings (`06`, `16`) |
| Samsung ~500 `AlarmManager` limit | **Real upstream caveat** | a capacity limit, not "scheduling unsupported"; relevant only at very high pending counts |

## DND-bypass note
`channel_bypass_dnd` only takes effect when the app has notification-policy (do-not-disturb)
access; without it Android treats bypass as False (our channels show `mBypassDnd=false` in
`dumpsys`). `flutter_local_notifications` v21 **does** expose `hasNotificationPolicyAccess()` /
`requestNotificationPolicyAccess()` (on `AndroidFlutterLocalNotificationsPlugin`), and the wrapper
now surfaces both as `has_notification_policy_access()` / `request_notification_policy_access()`
(demo buttons 24 / 24b). So a DND-bypass failure is **observable as a missing policy grant** —
check `has_notification_policy_access()` before blaming Samsung; if False, call
`request_notification_policy_access()` to open the system DND-access screen.

## Summary
Of the report's Samsung "unsupported" items, **none is actually unsupported**. Four were
manifest/permission bugs already fixed (colorized FG, scheduled, periodic, secret). The rest are
**visual OEM-rendering** differences (regular `color`, custom group summary, action styling) where
the value reaches Android correctly but One UI renders it its own way. Phrase all of these as
*"delivered to the OS; rendered differently / not painted on tested One UI Brief mode"*, never
*"unsupported on Samsung"*.
