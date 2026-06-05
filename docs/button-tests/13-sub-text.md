# Button 13 — Sub text

**Source:** `main.py` `send_sub_text` (`sub_text="HELLO-SUB-TEXT"`, `channel_id="subtext_ch"`)
**Device:** Galaxy S25, One UI, Android 16.

## Result — hard evidence (`dumpsys`)
```
android.title=String (SUB TEXT #13)
android.subText=String (HELLO-SUB-TEXT)
```

## Verdict: ✅ WORKS
`sub_text` is delivered and renders in the notification header next to the app name on One UI.
