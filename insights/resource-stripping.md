# Android resource stripping

## Problem
Custom resources (drawables, raw sounds) placed in `res/` but only referenced at
runtime via `getIdentifier()` get stripped from the final APK by Android's resource
optimizer — even without `shrinkResources true` in build.gradle.

## Solution
Add `res/raw/keep.xml` with `tools:keep` listing all resource patterns that must survive:

```xml
<resources xmlns:tools="http://schemas.android.com/tools"
    tools:keep="@raw/*,@drawable/ic_*" />
```

## Key details
- `keep.xml` in `res/raw/` is the standard location — works for ALL resource types, not just raw
- Use glob patterns: `@raw/*`, `@drawable/ic_*`, etc.
- Resources referenced in XML layouts survive automatically; only runtime-only refs need keep rules
- The keep.xml itself shows up as a raw resource in the APK (harmless)
- Resource names get obfuscated in the APK (e.g., `res/gR.xml`) — use aapt2 dump to verify by name
- aapt2 location: `~/.gradle/caches/*/transforms/*/transformed/aapt2-*/aapt2.exe`
