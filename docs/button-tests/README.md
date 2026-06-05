# On-device button test results

Demo buttons fired physically on a **Samsung Galaxy S25 (SM-S931B), One UI, Android 16**. Evidence
is primarily `adb shell dumpsys notification` structured records (more rigorous than screenshots for
proving a feature reached Android), plus shade/lock-screen screenshots (`img/`) for visual features.

**Which APK:** the original buttons **1-23** were verified on the **pre-built release APK**
(`build/apk/...`, built before the Phase B changes; those changes are additive and do not touch the
1-23 code paths). The **Phase B** buttons **24-27/24b** were verified on the **rebuilt APK from the
current working tree**, and a regression sample of 1-23 was re-checked on that rebuilt APK (see
`feat-regression.md`).

Legend: ✅ works · 🟡 works but with an OEM-rendering caveat · ❌ broken.

| # | Button | Verdict | Key evidence |
|---|--------|---------|--------------|
| 1 | Baseline | ✅ | posts; default icon (intrinsic red art, not a tint) |
| 2 | Colored (red) | 🟡 | `color=0xffff0000` reaches OS, **not rendered** on One UI Brief |
| 3 | Group + InboxStyle summary | 🟡 | `group_key` bundles; custom summary masked by One UI native group |
| 4a | Large icon | ✅ | `android.largeIcon=Bitmap 91x91` |
| 4b | Big picture | ✅ | `android.picture=Bitmap 726x838` |
| 5 | Default icon | ✅ | posts with launcher icon |
| 6 | Custom sound | ✅ | channel `mSound=.../raw/test_beep` |
| 7 | Silent | ✅ | channel `mSound=null, mVibrationEnabled=false` |
| 8 | Big text | ✅ | full `android.bigText` delivered |
| 9 | Progress 65% | ✅ | `progress=65 max=100 indeterminate=false` |
| 10 | Indeterminate | ✅ | `progressIndeterminate=true` |
| 11 | Ongoing | ✅ | `flags=ONGOING_EVENT` |
| 12 | Action buttons | ✅ | `Approve`/`Deny` PendingIntents |
| 12b | Rich actions + reply | ✅🟡 | inline RemoteInput + broadcast archive; visuals OEM-dependent |
| 13 | Sub text | ✅ | `android.subText=HELLO-SUB-TEXT` |
| 14 | Secret (lock screen) | ✅ | `vis=SECRET`; fired while locked; **hidden on lock screen** |
| 15 | Only alert once | ✅ | first show alerts; same-id update silent |
| 16 | Custom vibration | ✅ | channel `mVibrationPattern=[0,200,1000,200,1000,200]` |
| 17 | Scheduled (10 s) | ✅ | fired after 10 s (receiver fix) |
| 18 | Timeout (5 s) | ✅ | present t+2 s, gone t+8 s |
| 19 | Periodic (enum) | ✅ | kickoff + registered pending "every minute" |
| 20 | Periodic duration | ✅ | kickoff + registered pending "every 90 s" |
| 21 | Get active | ✅ | returned `Active (19)` JSON |
| 22 | Get pending | ✅ | returned `Pending (2)` JSON |
| 23 | Foreground (colorized red) | ✅ | service runs; `colorized=true color=0xffff0000`; **red renders** |
| — | Request permissions | ✅ | pre-granted at install (`-g`); no dialog |
| — | Cancel all | ✅ | used throughout to clear app notifications |

### Phase B — new features (rebuilt APK)

| # | Button | Verdict | Key evidence |
|---|--------|---------|--------------|
| 24 | Check status (perms/exact/dnd) | ✅ | `enabled=False`→`True` after grant; `can_schedule_exact=False`; `dnd_policy_access` |
| 24b | Request DND policy access | ✅ | `has_/request_notification_policy_access` (added after review) |
| 25 | Full-screen intent | ✅ | `USE_FULL_SCREEN_INTENT` in manifest; perm granted=True; `category=call` heads-up |
| 26 | Channel mgmt (create+list+delete) | ✅ | `demo_managed_ch` created with custom sound; `mDeleted=true` after delete |
| 27 | Periodic (exact mode) | ✅ | `schedule_mode` flows to OS; rejected `exact_alarms_not_permitted` (no SCHEDULE_EXACT_ALARM) — correct |

Phase B detail: `feat-NN-*.md`. These verify the priority feature gaps from the report: permission/
status checks (incl. `has_/request_notification_policy_access` for DND), full-screen intent, channel
management, and the periodic `schedule_mode` parameter.

**Bottom line (buttons 1-23):** all verified working on this one device (Galaxy S25 / One UI /
Android 16). The few non-✅ items are OEM-rendering caveats, not wrapper bugs or "unsupported on
Samsung"; other skins/versions may differ.

Per-button detail: `NN-name.md` in this folder. Screenshots: `img/`.
