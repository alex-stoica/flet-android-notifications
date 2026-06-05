# Button 15 — Only alert once

**Source:** `main.py` `send_only_alert_once` (show "ALERT ONCE #15" with `only_alert_once=True`,
then 2 s later re-show the **same id** as "(updated silently)" with `silent=True`,
`importance="low"`, `channel_id="alert_once_silent_ch"`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence
- **First show:** heads-up banner appeared *"ALERT ONCE #15 — First show — you should hear a
  sou..."* — it alerted.
- **After 2 s:** `dumpsys` title is now `ALERT ONCE #15 (updated silently)` — the same-id update
  replaced the content on a low-importance silent channel, with no second heads-up/alert.

## Verdict: ✅ WORKS
First show alerts; the in-place update is silent. `only_alert_once` + silent update behaves as
documented.
