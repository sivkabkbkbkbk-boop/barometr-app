#!/usr/bin/env python3
"""Weather backgrounds for the home-screen widget.

Draws every frame of every weather scene once and writes it either as Android vector
drawables plus the widget layouts (the APK build calls this), or as one HTML page that
plays the same frames (to look at them before a build):

    python3 widget/frames.py android/app/src/main/res
    python3 widget/frames.py --preview preview.html
"""
import math
import os
import sys

W, H = 184, 76          # viewport of every frame, the shape of a 2x1 widget
N = 20                  # frames in one loop
FPS = 10                # the loop lasts N / FPS = 2 seconds
KINDS = ["clear_d", "clear_n", "fair_d", "fair_n", "cloud", "rain", "snow", "thunder", "fog"]
NAMES = {"clear_d": "Ясно, день", "clear_n": "Ясно, ночь", "fair_d": "Малооблачно, день",
         "fair_n": "Малооблачно, ночь", "cloud": "Пасмурно", "rain": "Дождь", "snow": "Снег",
         "thunder": "Гроза", "fog": "Туман"}

CLOUD = "M10,30h34a10,10 0,0 0,0 -20a14,14 0,0 0,-26 -4a10,10 0,0 0,-8 24z"
MOON = "M0,0a13,13 0,1 0,14 17a11,11 0,0 1,-14 -17z"
BOLT = "M0,0l-10,20h9l-6,18l16,-24h-9l7,-14z"


# ---- scene: a list of shapes for one frame -------------------------------------------------
def bg(c1, c2, x1=0, y1=0, x2=0, y2=H):
    return ("bg", c1, c2, x1, y1, x2, y2)

def glow(cx, cy, r, c):
    return ("glow", cx, cy, r, c)

def circle(cx, cy, r, c, a=1.0):
    return ("circle", cx, cy, r, c, a)

def shape(d, x, y, s, c, a=1.0):
    return ("shape", d, x, y, s, c, a)

def line(x1, y1, x2, y2, c, w, a):
    return ("line", x1, y1, x2, y2, c, w, a)

def veil(c, a):
    return ("veil", c, a)


def rain_lines(p, c, a, count=18, top=4, span=44, step=10.5, x0=8):
    out = []
    for i in range(count):
        x = x0 + i * step
        y = (i * 23 + p * span) % span + top
        out.append(line(x, y, x - 4, y + 11, c, 1.6, a))
    return out


def scene(kind, f):
    p = f / N                       # phase 0..1, the loop is seamless at 1
    sn = math.sin(2 * math.pi * p)
    if kind == "clear_d":
        return [bg("#3d8ee8", "#e9a23b", 0, 0, W, H), glow(102, 4, 70 * (1 + .08 * sn), "#fff6c8"),
                circle(102, 4, 14 + sn, "#fff4c2")]
    if kind == "clear_n":
        stars = [(20, 14), (48, 8), (96, 18), (120, 6), (70, 30), (140, 40), (30, 50), (108, 60), (160, 64), (8, 34)]
        out = [bg("#0e1a3a", "#2a2f63", 0, 0, W, H)]
        for i, (x, y) in enumerate(stars):
            out.append(circle(x, y, 1.4 if i % 3 == 0 else .9, "#ffffff", .5 + .4 * math.sin(2 * math.pi * (p + i * .37))))
        out.append(shape(MOON, 100, 6, 1, "#f3f0d8"))
        return out
    if kind == "fair_d":
        return [bg("#4b9be6", "#9fcbf0", 0, 0, W, H), glow(100, 10, 55, "#fff6c8"), circle(100, 10, 12, "#fff1b0"),
                shape(CLOUD, 80 + 2 * sn, 24, 1.1, "#ffffff", .8)]
    if kind == "fair_n":
        return [bg("#1a2547", "#3b4668", 0, 0, W, H), circle(30, 16, 1.2, "#ffffff", .7), circle(70, 10, .9, "#ffffff", .7),
                shape(MOON, 98, 6, .92, "#f3f0d8"), shape(CLOUD, 78 + 2 * sn, 26, 1.1, "#c9d2e6", .45)]
    if kind == "cloud":
        return [bg("#5d6a7c", "#8793a2"), shape(CLOUD, 60 + 3 * sn, 2, 1.6, "#e3e8ee", .35),
                shape(CLOUD, 90 - 3 * sn, 40, 1.3, "#e3e8ee", .22)]
    if kind == "rain":
        return [bg("#3c4a63", "#617089"), shape(CLOUD, 64, -6, 1.6, "#8f9bb0", .45)] + rain_lines(p, "#bcd3ff", .55)
    if kind == "snow":
        out = [bg("#647b9c", "#9aacc6"), shape(CLOUD, 64, -6, 1.5, "#eef3fa", .3)]
        for i in range(22):
            x = (i * 37) % 180 + 4 + (1.5 * math.sin(2 * math.pi * (p + i * .21)) if i % 2 else 0)
            y = (i * 29 + p * 70) % 70 + 3
            out.append(circle(x, y, 2.2 if i % 3 == 0 else 1.4, "#ffffff", .85))
        return out
    if kind == "thunder":
        out = [bg("#2a2140", "#4a3b63"), shape(CLOUD, 58, -8, 1.7, "#6b5c86", .6)]
        out += rain_lines(p, "#c9b6ff", .4, count=12, top=16, span=40, step=12, x0=10)
        if f in (12, 13):           # the flash: two frames in each loop
            out += [veil("#ffffff", .13 if f == 12 else .07), shape(BOLT, 104, 22, 1, "#ffd54a", 1 if f == 12 else .6)]
        return out
    if kind == "fog":
        out = [bg("#737d88", "#9aa2ab")]
        for a, y, b, w, d in [(10, 20, 150, 6, 1), (40, 34, 170, 5, -1), (0, 48, 120, 7, 1), (60, 62, 176, 5, -1)]:
            dx = 4 * sn * d
            out.append(line(a + dx, y, b + dx, y, "#ffffff", w, .22))
        return out
    raise ValueError(kind)


# ---- output: Android vector drawable ------------------------------------------------------------
def n(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")

def argb(c, a=1.0):
    return "#%02X%s" % (round(max(0, min(1, a)) * 255), c[1:].upper())

def circle_d(cx, cy, r):
    return "M%s,%sa%s,%s 0,1 0,%s,0a%s,%s 0,1 0,-%s,0z" % (n(cx - r), n(cy), n(r), n(r), n(2 * r), n(r), n(r), n(2 * r))

def to_vector(shapes):
    o = ['<?xml version="1.0" encoding="utf-8"?>',
         '<vector xmlns:android="http://schemas.android.com/apk/res/android" xmlns:aapt="http://schemas.android.com/aapt"',
         '    android:width="%ddp" android:height="%ddp" android:viewportWidth="%d" android:viewportHeight="%d">' % (W, H, W, H)]
    for s in shapes:
        t = s[0]
        if t == "bg":
            _, c1, c2, x1, y1, x2, y2 = s
            o.append('  <path android:pathData="M0,0h%dv%dh-%dz"><aapt:attr name="android:fillColor">'
                     '<gradient android:type="linear" android:startX="%s" android:startY="%s" android:endX="%s" android:endY="%s">'
                     '<item android:offset="0" android:color="%s"/><item android:offset="1" android:color="%s"/></gradient>'
                     '</aapt:attr></path>' % (W, H, W, n(x1), n(y1), n(x2), n(y2), argb(c1), argb(c2)))
        elif t == "glow":
            _, cx, cy, r, c = s
            o.append('  <path android:pathData="%s"><aapt:attr name="android:fillColor">'
                     '<gradient android:type="radial" android:centerX="%s" android:centerY="%s" android:gradientRadius="%s">'
                     '<item android:offset="0" android:color="%s"/><item android:offset="0.3" android:color="%s"/>'
                     '<item android:offset="1" android:color="%s"/></gradient></aapt:attr></path>'
                     % (circle_d(cx, cy, r), n(cx), n(cy), n(r), argb(c, .9), argb(c, .45), argb(c, 0)))
        elif t == "circle":
            _, cx, cy, r, c, a = s
            o.append('  <path android:pathData="%s" android:fillColor="%s" android:fillAlpha="%s"/>' % (circle_d(cx, cy, r), c, n(a)))
        elif t == "shape":
            _, d, x, y, sc, c, a = s
            o.append('  <group android:translateX="%s" android:translateY="%s" android:scaleX="%s" android:scaleY="%s">'
                     '<path android:pathData="%s" android:fillColor="%s" android:fillAlpha="%s"/></group>'
                     % (n(x), n(y), n(sc), n(sc), d, c, n(a)))
        elif t == "line":
            _, x1, y1, x2, y2, c, w, a = s
            o.append('  <path android:pathData="M%s,%sL%s,%s" android:strokeColor="%s" android:strokeWidth="%s" '
                     'android:strokeAlpha="%s" android:strokeLineCap="round"/>' % (n(x1), n(y1), n(x2), n(y2), c, n(w), n(a)))
        elif t == "veil":
            _, c, a = s
            o.append('  <path android:pathData="M0,0h%dv%dh-%dz" android:fillColor="%s" android:fillAlpha="%s"/>' % (W, H, W, c, n(a)))
    o.append('</vector>')
    return "\n".join(o) + "\n"


# ---- output: SVG for the preview page ------------------------------------------------------------
def to_svg(shapes, uid):
    o, defs = [], []
    for i, s in enumerate(shapes):
        t, gid = s[0], "%s_%d" % (uid, i)
        if t == "bg":
            _, c1, c2, x1, y1, x2, y2 = s
            defs.append('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="%s" y1="%s" x2="%s" y2="%s">'
                        '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (gid, n(x1), n(y1), n(x2), n(y2), c1, c2))
            o.append('<rect width="%d" height="%d" fill="url(#%s)"/>' % (W, H, gid))
        elif t == "glow":
            _, cx, cy, r, c = s
            defs.append('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s">'
                        '<stop offset="0" stop-color="%s" stop-opacity=".9"/><stop offset=".3" stop-color="%s" stop-opacity=".45"/>'
                        '<stop offset="1" stop-color="%s" stop-opacity="0"/></radialGradient>' % (gid, n(cx), n(cy), n(r), c, c, c))
            o.append('<circle cx="%s" cy="%s" r="%s" fill="url(#%s)"/>' % (n(cx), n(cy), n(r), gid))
        elif t == "circle":
            _, cx, cy, r, c, a = s
            o.append('<circle cx="%s" cy="%s" r="%s" fill="%s" fill-opacity="%s"/>' % (n(cx), n(cy), n(r), c, n(a)))
        elif t == "shape":
            _, d, x, y, sc, c, a = s
            o.append('<path transform="translate(%s %s) scale(%s)" d="%s" fill="%s" fill-opacity="%s"/>' % (n(x), n(y), n(sc), d, c, n(a)))
        elif t == "line":
            _, x1, y1, x2, y2, c, w, a = s
            o.append('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-opacity="%s" stroke-linecap="round"/>'
                     % (n(x1), n(y1), n(x2), n(y2), c, n(w), n(a)))
        elif t == "veil":
            _, c, a = s
            o.append('<rect width="%d" height="%d" fill="%s" fill-opacity="%s"/>' % (W, H, c, n(a)))
    return '<svg viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid slice"><defs>%s</defs>%s</svg>' % (W, H, "".join(defs), "".join(o))


# ---- widget layouts ---------------------------------------------------------------------------
TEXT = '''    <LinearLayout android:layout_width="match_parent" android:layout_height="match_parent" android:orientation="vertical"
        android:gravity="center_vertical" android:paddingLeft="12dp" android:paddingRight="12dp" android:paddingTop="6dp" android:paddingBottom="6dp">
        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal">
            <TextView android:id="@+id/wx_city" android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content"
                android:textSize="12sp" android:textColor="#E6FFFFFF" android:maxLines="1" android:ellipsize="end" %(sh)s />
            <TextView android:id="@+id/wx_hilo" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:textSize="11sp" android:textColor="#E6FFFFFF" android:maxLines="1" android:paddingLeft="4dp" %(sh)s />
        </LinearLayout>
        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal"
            android:gravity="center_vertical">
            <TextView android:id="@+id/wx_temp" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:textSize="30sp" android:textStyle="bold" android:textColor="#FFFFFFFF" android:maxLines="1" %(sh)s />
            <LinearLayout android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content"
                android:orientation="vertical" android:gravity="end">
                <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="horizontal">
                    <TextView android:id="@+id/wx_press" android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:textSize="11sp" android:textColor="#FFFFFFFF" android:maxLines="1" %(sh)s />
                    <TextView android:id="@+id/wx_parr" android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:textSize="11sp" android:textStyle="bold" android:maxLines="1" %(sh)s />
                </LinearLayout>
                <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="horizontal">
                    <TextView android:id="@+id/wx_kpdot" android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:textSize="9sp" android:text="●" android:paddingRight="3dp" />
                    <TextView android:id="@+id/wx_kp" android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:textSize="11sp" android:textColor="#FFFFFFFF" android:maxLines="1" %(sh)s />
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>
    </LinearLayout>
''' % {"sh": 'android:shadowColor="#55000000" android:shadowRadius="3" android:shadowDy="1"'}

HEAD = '''<?xml version="1.0" encoding="utf-8"?>
<!-- generated by widget/frames.py; @android:id/background lets Android 12+ round the corners -->
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android" android:id="@android:id/background"
    android:layout_width="match_parent" android:layout_height="match_parent">
'''
IMG = '<ImageView android:id="@+id/wx_f%d" android:layout_width="match_parent" android:layout_height="match_parent" android:scaleType="centerCrop" />'


def layout_anim():
    imgs = "\n".join("        " + IMG % i for i in range(N))
    return (HEAD + '    <ViewFlipper android:id="@+id/wx_flip" android:layout_width="match_parent" android:layout_height="match_parent"\n'
            '        android:autoStart="true" android:flipInterval="%d">\n%s\n    </ViewFlipper>\n' % (1000 // FPS, imgs)
            + TEXT + '</FrameLayout>\n')


def layout_static():
    return HEAD + "    " + IMG % 0 + "\n" + TEXT + '</FrameLayout>\n'


def write_android(res):
    os.makedirs(os.path.join(res, "drawable"), exist_ok=True)
    os.makedirs(os.path.join(res, "layout"), exist_ok=True)
    for k in KINDS:
        for f in range(N):
            with open(os.path.join(res, "drawable", "wxf_%s_%02d.xml" % (k, f)), "w", encoding="utf-8") as fh:
                fh.write(to_vector(scene(k, f)))
    with open(os.path.join(res, "layout", "wx_widget_anim.xml"), "w", encoding="utf-8") as fh:
        fh.write(layout_anim())
    with open(os.path.join(res, "layout", "wx_widget.xml"), "w", encoding="utf-8") as fh:
        fh.write(layout_static())
    print("widget: %d frames x %d scenes" % (N, len(KINDS)))


def write_preview(path):
    sample = {"clear_d": ("+18°", "+21° +9°", "745", "↑1", "g", 2), "clear_n": ("+9°", "+18° +7°", "744", "→", "m", 2),
              "fair_d": ("+15°", "+17° +8°", "741", "↓1", "g", 3), "fair_n": ("+10°", "+15° +8°", "740", "↓1", "g", 3),
              "cloud": ("+12°", "+13° +8°", "738", "↓1", "g", 3), "rain": ("+11°", "+12° +7°", "731", "↓3", "r", 4),
              "snow": ("−3°", "−1° −6°", "748", "↑2", "r", 2), "thunder": ("+22°", "+27° +16°", "736", "↓3", "r", 5),
              "fog": ("+7°", "+11° +5°", "742", "→", "m", 2)}
    col = {"g": "#b6ffb9", "r": "#ffb3a8", "m": "rgba(255,255,255,.75)"}
    cards = []
    for k in KINDS:
        t, hl, pr, ar, c, kp = sample[k]
        frames = "".join('<div class="fr">%s</div>' % to_svg(scene(k, f), "%s%d" % (k, f)) for f in range(N))
        dot = "#ffb3a8" if kp >= 5 else "#ffe28a" if kp >= 4 else "#b6ffb9"
        cards.append('<div class="item"><div class="w">%s<div class="in"><div class="top"><span>Великий Новгород</span><span>%s</span></div>'
                     '<div class="main"><span class="t">%s</span><div class="rt"><div>%s <b style="color:%s">%s</b></div>'
                     '<div><span style="font-size:9px;color:%s">●</span> Kp %d%s</div></div></div></div></div><small>%s</small></div>'
                     % (frames, hl, t, pr, col[c], ar, dot, kp, " буря" if kp >= 5 else "", NAMES[k]))
    page = '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Виджет: фон по погоде</title><style>
*{box-sizing:border-box}body{margin:0;background:#0b0c0e;color:#eef0f3;font:15px/1.45 system-ui,sans-serif;padding:20px 16px 32px}
h1{font-size:18px;margin:0 0 6px;text-align:center}.lead{color:#a3a7ae;margin:0 auto 18px;font-size:14px;text-align:center;max-width:540px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:18px 14px;max-width:680px;margin:0 auto}
.item{display:flex;flex-direction:column;gap:6px;align-items:center}.item small{color:#a3a7ae;font-size:12.5px}
.w{position:relative;width:196px;height:76px;border-radius:22px;overflow:hidden;color:#fff;text-shadow:0 1px 3px rgb(0 0 0 / .33)}
.fr{position:absolute;inset:0;visibility:hidden}.fr svg{width:100%%;height:100%%;display:block}
.in{position:absolute;inset:0;padding:6px 12px;display:flex;flex-direction:column;justify-content:center}
.top{display:flex;justify-content:space-between;font-size:12px;opacity:.9}.top span:first-child{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.top span:last-child{font-size:11px;flex:none;padding-left:4px}.main{display:flex;align-items:center}
.t{font-size:30px;font-weight:700;letter-spacing:-.5px;line-height:1.1}.rt{margin-left:auto;text-align:right;font-size:11px;line-height:1.35;white-space:nowrap}
</style></head><body><h1>Фон виджета по погоде — %d кадров в секунду</h1>
<p class="lead">Это те же кадры, что попадут в приложение: их рисует одна и та же программа. На телефонах, где оболочка блокирует анимацию, останется первый кадр.</p>
<div class="grid">%s</div>
<script>let f=0;const W=[...document.querySelectorAll(".w")];function show(){W.forEach(w=>{const fr=w.querySelectorAll(".fr");fr.forEach((x,i)=>x.style.visibility=i===f?"visible":"hidden");});f=(f+1)%%%d;}show();setInterval(show,%d);</script>
</body></html>''' % (FPS, "".join(cards), N, 1000 // FPS)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--preview":
        write_preview(sys.argv[2])
    elif len(sys.argv) == 2:
        write_android(sys.argv[1])
    else:
        sys.exit(__doc__)
