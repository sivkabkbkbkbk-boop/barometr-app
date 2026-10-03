# Не18мнеуже — Android app

- `index.html` is the whole app (Capacitor web part). The native Android part (Java plugins, widget,
  layouts, manifest edits) is generated inside `.github/workflows/build.yml`; widget backgrounds come from
  `widget/frames.py` (`python3 widget/frames.py --preview out.html` shows them), notification faces from
  `widget/faces.py` (reads `KFACE` from index.html).
- Every push to any branch builds the APK and publishes it as the latest release, and installed apps offer
  it as an update. Work branch: `claude/github-connection-3lvr1l`. Build status: GitHub Actions runs API.
- The site (privacy policy etc.) is the separate repo `sivkabkbkbkbk-boop/barometr` (`privacy.html`).

## Rules from the owner

- For any change that alters how the app or the widget looks, first show a preview and ask before
  pushing to GitHub. Changes that do not affect the look can be pushed right away.
- Talk to the owner in Russian.
- The goal of the work: make the app simpler to use and add features that are useful for weather-sensitive
  people. Stay within that. Now and then suggest ideas of your own in that direction, with pictures or without.
- Save the owner's usage limit: keep replies short, show pictures only for real visual changes, check
  quietly otherwise.

## Style of the app (keep it)

- Thin line style everywhere: hairline borders, no fills, light type, one ink colour. No extra colours in
  icons or smileys; colour only to mean something (norm / raised, strength of a link).
- Line icons: `lic(emoji)` with the `GLI` table; mood faces: `kf(k)` with `KFACE`, `KPICK` = faces in pickers.
  Smileys: great, meh, bad, weak, head («Мигрень»), dizzy («Кружится»), heart, joints (good, sleepy hidden).
- Sheets: `showSheet(id)` / `hideSheet()`; toasts: `toast(text)`; storage: `store.get/set`.

## How things work (short)

- Marks: `addMark(k)` → `S.marks` (saved) → `rebuildMood()` → `S.mood[day] = {v, kinds, city…}`.
- Weather of past days: `dayFeatures(day, city)`; personal forecast: `fcFor()`, needs 14 marked days.
- Reports: «Нейросеть» card — small on-device MLP (`nnTrain`, 11 inputs → 6 → 1), needs 21 days, 5-fold
  check, canvas `#nnCv`: a personal shape (`nnShape`: seed = hash of the first mark, outline from the marks, a bump per
  marked day) that grows from a small round seed over 14 marked days; points drift, react to touch and scroll. «Что связано…» = tiles with a
  5-step scale (`facLevel`), details in `#facSheet`.
  «Симптомы и погода» = the same tiles (`symLevel`, `symOpen`), same `#facSheet`.
- First run: `introSheet`, steps 0–5 (greeting, «вы женщина/мужчина» + last period date for women, location,
  first mark, reminders, «Приятного пользования» + «Начать»); live smiley scenes `masGo(n)` (`masWho`: bow / moustache).
- Cycle (women only, `SEX=="f"`, `cycOn()`): tab «Цикл» `#pgCycle`, data `CY={list:[{id,s,e}],del,len,plen}` synced
  in the Disk copy (never to friends); `cyStats()` own averages, `cyAt(d)` day + phase (mens/after/mid/pms/late),
  no fertile window. Analysis: `cycFeat(d)` adds mens/pms to «Что связано…», symptoms, the network (`NN_IN`) and
  `fcFor`; weather factors use marks with the phase average taken out. PDF option «Менструальный цикл». Developer menu: tap the version line in Settings 7 times.
- Friends: no server. Data lives on each person's Yandex Disk public folder; invite link carries the key and
  secret; accepting opens the messenger with a reply link at once (`shareSend(true)`). Friends list = compact
  table (pressure, sugar, steps), two-week smiley table below. Group chats need «Вступить» (invitation state
  `G.st`, members `G.ms`).
- Notifications: one line in reliable mode (MoodKeep), faces `kf_<k>` drawables; widget = line-style frames.
- Launcher icons: the owner's cat by weather, whole rounded pictures on a transparent square: `icon-calm.png`
  sun, `icon-mid.png` clouds, `icon-192.png`/`icon-512.png` tornado (default, «bad»); switched by `IconSwitch`.
- Updates: native `ApkUpdate.latest()` reads the releases page (no API limit); «Установить» reopens installer.
- Anonymous stats: GoatCounter `/install` and daily `/open`, switch in Settings.

## Not done yet / ideas the owner has not decided on

- Automatic friend adding needs a small relay (Yandex Cloud suggested, owner chose the serverless reply).
- Ideas: alert when a friend suddenly feels worse; evening warning before personal-trigger weather;
  first-run question «На что вы реагируете?».
