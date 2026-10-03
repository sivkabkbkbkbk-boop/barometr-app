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
- Every push that people will notice: add an entry at the top of `WHATS_NEW` in index.html (new unique id, short
  Russian items `[icon from GLI, text]`, no `"` inside the text). Updated apps show it once in «Что нового»; the
  newest entry is also the release description on GitHub (the build reads it).
- Save the owner's usage limit: keep replies short, show pictures only for real visual changes, check
  quietly otherwise.

## Style of the app (keep it)

- Thin line style everywhere: hairline borders, no fills, light type, one ink colour. No extra colours in
  icons or smileys; colour only to mean something (norm / raised, strength of a link).
- Line icons: `lic(emoji)` with the `GLI` table; mood faces: `kf(k)` with `KFACE`, `KPICK` = faces in pickers.
  Marking is two steps: `KPICK` = great «Отлично» / meh «Нормально» / bad «Плохо» (one tap); after meh or bad `askSym`
  opens «Что не так?» with `SYMS` = head, heart, weak «Упадок сил», joints, dizzy; symptom marks carry `with:1` and do not
  lower the day's score twice (`rebuildMood`). Shade does the same natively (`MoodNotify.askSym`, extra `w`). Faces are the
  owner's line set redrawn in `KFACE` (parts: .spark .eyes .brows .bolt .ecg .drop .bat .tick .spl/.spr .orb for `KF_ANIM`).
  good, sleepy hidden (old marks).
- Sheets: `showSheet(id)` / `hideSheet()`; toasts: `toast(text)`; storage: `store.get/set`.

## How things work (short)

- Marks: `addMark(k)` → `S.marks` (saved) → `rebuildMood()` → `S.mood[day] = {v, kinds, city…}`.
- Weather of past days: `dayFeatures(day, city)`; personal forecast: `fcFor()`, needs 14 marked days.
- Reports: «Нейросеть» card — on-device models (`nnTrain`: 5 small MLPs 15 inputs → 6 → 1 averaged, or a plain
  logistic regression `lrTrain`, whichever guesses later days better in `nnCheck`, a time-ordered check); inputs include the
  sharpest 3-hour pressure fall `drop3`, Kp 1–2 days before, day off; columns missing on >40% of days are left out;
  trained in a Blob worker (`nnLearn`); needs 21 days; canvas `#nnCv`: a personal shape (`nnShape`: seed = hash of the first mark, outline from the marks, a bump per
  marked day) that grows from a small round seed over 14 marked days; points drift, react to touch and scroll. «Что связано…» = tiles with a
  5-step scale (`facLevel`), details in `#facSheet`; marks adjusted for day off and cycle phase, other weather signs judged
  by partial correlation beyond the strongest one, strength = cautious end of the 95% range, FDR > 20% capped low.
  «Симптомы и погода» = the same tiles (`symLevel`, `symOpen`), same `#facSheet`.
- First run: `introSheet`, steps 0–6 (greeting, «Вы… женщина/мужчина», for women «Самочувствие и цикл» + last period date, location,
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
