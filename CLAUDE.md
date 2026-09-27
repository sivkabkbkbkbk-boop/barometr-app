# Не18мнеуже — Android app

- `index.html` is the whole app (Capacitor web part). The native Android part (Java plugins, widget,
  layouts, manifest edits) is generated inside `.github/workflows/build.yml`; widget backgrounds come from
  `widget/frames.py` (`python3 widget/frames.py --preview out.html` shows them).
- Every push to any branch builds the APK and publishes it as the latest release, and installed apps offer
  it as an update.

## Rules from the owner

- For any change that alters how the app or the widget looks, first show a preview and ask before
  pushing to GitHub. Changes that do not affect the look can be pushed right away.
- Talk to the owner in Russian.
- The goal of the work: make the app simpler to use and add features that are useful for weather-sensitive
  people. Stay within that. Now and then suggest ideas of your own in that direction, with pictures or without.
