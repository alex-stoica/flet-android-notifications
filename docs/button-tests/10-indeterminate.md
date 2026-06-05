# Button 10 — Indeterminate progress

**Source:** `main.py` `send_indeterminate` (`show_progress=True`, `indeterminate=True`,
`ongoing=True`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence (`dumpsys`)
```
android.title=String (INDETERMINATE #10)
android.progress=Integer (0)
android.progressMax=Integer (0)
android.progressIndeterminate=Boolean (true)
```

## Verdict: ✅ WORKS
Indeterminate progress flag delivered; renders as a spinning/sliding bar. Ongoing.
