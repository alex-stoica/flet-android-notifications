# Button 20 — Periodic duration (custom interval)

**Source:** `main.py` `send_periodic_duration` (kickoff + `periodically_show_with_duration(
duration_seconds=90)`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence
- **Kickoff:** `dumpsys` shows `PERIODIC DURATION #20` active (count 1); in-app log
  `OK periodic duration #20 (id=28) — kickoff now, next in ~90s`.
- **Registered as pending** (button 22): `{ "id": 28, "title": "PERIODIC DURATION #20", "body":
  "Repeats every 90 seconds." }`.

## Verdict: ✅ WORKS
Custom-duration periodic (`periodicallyShowWithDuration`) registers and the kickoff fires. Same
`schedule_mode` note as button 19.
