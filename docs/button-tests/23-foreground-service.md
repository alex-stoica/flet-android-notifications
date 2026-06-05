# Button 23 — Foreground service (start/stop, colorized red)

**Source:** `main.py` `send_foreground` / `stop_foreground`
(`start_foreground_service(color="#FF0000", colorized=True, foreground_service_types=["special_use"])`)
**Device:** Galaxy S25, One UI, Android 16.

## What it tests
A real Android foreground service with a persistent, **colorized full-red** notification — the
headline "colorized on Samsung" claim.

## Result — hard evidence
- **In-app log:** `OK foreground #23 (id=26) - use stop button to end`.
- **Service running** (`dumpsys activity services`):
  `ServiceRecord{... com.dexterous.flutterlocalnotifications.ForegroundService ...}`.
- **Notification** (`dumpsys notification`): `FOREGROUND #23` active, `android.colorized=Boolean
  (true)`, `color=0xffff0000`.
- **Shade screenshot** (`img/23-foreground-shade.png`): the notification renders with a **solid
  red background** ("FOREGROUND #23 — Foreground service running with special_use type").

## Verdict: ✅ WORKS (including the red background)
Foreground service starts, the `special_use` type is accepted, and **colorized red renders fully
on Samsung One UI**.

## Claim correction (headline)
`colorized=True` is **NOT** unsupported on Samsung. The earlier wrong conclusion was caused by a
**missing `<service ... ForegroundService>` manifest entry** (see `insights/errors.md`); once the
manifest is patched (build.py does this), the full red background renders. This is the single most
important correction in the Samsung audit.

## Note (test harness)
The two "23" buttons sit at the very bottom of the list adjacent to the gesture-nav bar and are
hard to hit by coordinate; the start tap landed reliably around y≈1820 in the bottom-scrolled
view. Not an app issue.
