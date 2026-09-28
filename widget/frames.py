#!/usr/bin/env python3
"""The home-screen widget in thin lines: a plain background, light type and a small weather icon
that moves with the weather (rays turn, a cloud drifts, rain and snow fall, lightning flashes).

Draws every frame of every weather scene once and writes it either as Android vector drawables
plus the widget layouts and colours (the APK build calls this), or as one HTML page that plays
the same frames (to look at them before a build):

    python3 widget/frames.py android/app/src/main/res
    python3 widget/frames.py --preview preview.html
"""
import math
import os
import sys

W, H = 48, 48           # viewport of every frame: the icon in the middle of the widget
N = 20                  # frames in one loop
FPS = 10                # the loop lasts N / FPS = 2 seconds
KINDS = ["clear_d", "clear_n", "fair_d", "fair_n", "cloud", "rain", "snow", "thunder", "fog"]
NAMES = {"clear_d": "Ясно, день", "clear_n": "Ясно, ночь", "fair_d": "Малооблачно, день",
         "fair_n": "Малооблачно, ночь", "cloud": "Пасмурно", "rain": "Дождь", "snow": "Снег",
         "thunder": "Гроза", "fog": "Туман"}

# colours by name: the widget follows the phone's light or dark theme
THEMES = {"light": {"bg": "#E3F6EF", "ink": "#16322D", "mut": "#557D73", "acc": "#0F9D85"},
          "dark": {"bg": "#15171B", "ink": "#ECEEF0", "mut": "#A3A7AE", "acc": "#FFB04A"}}

CLOUD = "M14,38h22a8,8 0,0 0,0 -16a11,11 0,0 0,-21 -2a7,7 0,0 0,-1 18z"
MOON = "M28,9a12,12 0,1 0,11 17a10,10 0,0 1,-11 -17z"


# ---- scene: a list of shapes for one frame -----------------------------------------------------
def stroke(d, c="ink", a=1.0, fill=None, w=1.4):
    return ("path", d, c, a, fill, w)

def at(d, x, y, s=1.0):
    return ("group", d, x, y, s)

def sun(cx, cy, r, turn):
    out = [stroke("M%s,%sa%s,%s 0,1 0,%s,0a%s,%s 0,1 0,-%s,0" % (n(cx - r), n(cy), n(r), n(r), n(2 * r), n(r), n(r), n(2 * r)))]
    rays = ""
    for i in range(8):
        a = (i * 45 + turn) * math.pi / 180
        rays += "M%s,%sL%s,%s" % (n(cx + math.cos(a) * (r + 3.5)), n(cy + math.sin(a) * (r + 3.5)),
                                   n(cx + math.cos(a) * (r + 6.5)), n(cy + math.sin(a) * (r + 6.5)))
    return out + [stroke(rays)]

def cloud(dx=0.0, dy=0.0, a=1.0):
    return [("cloud", dx, dy, a)]

def flake(x, y, a):
    return stroke("M%s,%sv6M%s,%sl5.2,3M%s,%sl5.2,-3" % (n(x), n(y - 3), n(x - 2.6), n(y - 1.5), n(x - 2.6), n(y + 1.5)), a=a)


def scene(kind, f):
    p = f / N                       # phase 0..1, the loop is seamless at 1
    sn = math.sin(2 * math.pi * p)
    if kind == "clear_d":
        return sun(24, 24, 8, p * 45)
    if kind == "clear_n":
        out = [stroke(MOON)]
        for i, (x, y) in enumerate([(38, 8), (42, 20), (33, 36)]):
            out.append(stroke("M%s,%sh.01" % (n(x), n(y)), a=.35 + .6 * (.5 + .5 * math.sin(2 * math.pi * (p + i * .33))), w=2))
        return out
    if kind == "fair_d":
        return sun(17, 16, 6, p * 45) + cloud(6 + 1.6 * sn, 6)
    if kind == "fair_n":
        return [at(MOON, -4, -4, .8)] + cloud(6 + 1.6 * sn, 6)
    if kind == "cloud":
        return cloud(-3 + 1.5 * sn, -5) + cloud(2 - 1.5 * sn, 2)
    if kind == "rain":
        out = cloud(0, -7)
        for i, x in enumerate((18, 26, 34)):
            q = (p + i / 3) % 1
            out.append(stroke("M%s,%sl-2,6" % (n(x - q * 2), n(33 + q * 8)), a=math.sin(math.pi * q)))
        return out
    if kind == "snow":
        out = cloud(0, -7)
        for i, x in enumerate((17, 26, 35)):
            q = (p + i / 3) % 1
            out.append(flake(x + math.sin(2 * math.pi * q) * .8, 36 + q * 8, math.sin(math.pi * q)))
        return out
    if kind == "thunder":
        out = cloud(0, -7)
        flash = 1.0 if f in (12, 13) else .5 if f == 14 else .25
        out.append(stroke("M27,32l-5,7h5l-4,7", c="acc", a=flash, w=1.6))
        return out
    if kind == "fog":
        out = cloud(0, -8)
        for i, (x1, y, x2) in enumerate([(10, 38, 36), (14, 44, 40)]):
            dx = 2.5 * sn * (1 if i % 2 == 0 else -1)
            out.append(stroke("M%s,%sH%s" % (n(x1 + dx), n(y), n(x2 + dx)), a=.8))
        return out
    raise ValueError(kind)


# ---- output: Android vector drawable ------------------------------------------------------------
def n(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")

def to_vector(shapes):
    o = ['<?xml version="1.0" encoding="utf-8"?>',
         '<vector xmlns:android="http://schemas.android.com/apk/res/android"',
         '    android:width="%ddp" android:height="%ddp" android:viewportWidth="%d" android:viewportHeight="%d">' % (W, H, W, H)]
    for s in shapes:
        t = s[0]
        if t == "path":
            _, d, c, a, fill, w = s
            o.append('  <path android:pathData="%s" android:strokeColor="@color/wx_%s" android:strokeAlpha="%s" android:strokeWidth="%s"'
                     ' android:strokeLineCap="round" android:strokeLineJoin="round" android:fillColor="%s"/>'
                     % (d, c, n(a), n(w), "@color/wx_%s" % fill if fill else "#00000000"))
        elif t == "group":
            _, d, x, y, sc = s
            o.append('  <group android:translateX="%s" android:translateY="%s" android:scaleX="%s" android:scaleY="%s">'
                     '<path android:pathData="%s" android:strokeColor="@color/wx_ink" android:strokeWidth="%s"'
                     ' android:strokeLineCap="round" android:strokeLineJoin="round" android:fillColor="#00000000"/></group>'
                     % (n(x), n(y), n(sc), n(sc), d, n(1.4 / sc)))
        elif t == "cloud":         # filled with the background, so a sun or moon behind it is hidden
            _, dx, dy, a = s
            o.append('  <group android:translateX="%s" android:translateY="%s"><path android:pathData="%s" android:fillColor="@color/wx_bg"'
                     ' android:strokeColor="@color/wx_ink" android:strokeAlpha="%s" android:strokeWidth="1.4" android:strokeLineCap="round"'
                     ' android:strokeLineJoin="round"/></group>' % (n(dx), n(dy), CLOUD, n(a)))
    o.append('</vector>')
    return "\n".join(o) + "\n"


# ---- output: SVG for the preview page ------------------------------------------------------------
def to_svg(shapes, th):
    c = THEMES[th]
    o = []
    for s in shapes:
        t = s[0]
        if t == "path":
            _, d, col, a, fill, w = s
            o.append('<path d="%s" stroke="%s" stroke-opacity="%s" stroke-width="%s" fill="%s"/>' % (d, c[col], n(a), n(w), c[fill] if fill else "none"))
        elif t == "group":
            _, d, x, y, sc = s
            o.append('<path transform="translate(%s %s) scale(%s)" d="%s" stroke="%s" stroke-width="%s" fill="none"/>' % (n(x), n(y), n(sc), d, c["ink"], n(1.4 / sc)))
        elif t == "cloud":
            _, dx, dy, a = s
            o.append('<path transform="translate(%s %s)" d="%s" fill="%s" stroke="%s" stroke-opacity="%s" stroke-width="1.4"/>' % (n(dx), n(dy), CLOUD, c["bg"], c["ink"], n(a)))
    return ('<svg viewBox="0 0 %d %d" style="stroke-linecap:round;stroke-linejoin:round">%s</svg>' % (W, H, "".join(o)))


# ---- widget layouts ---------------------------------------------------------------------------
IMG = '<ImageView android:id="@+id/wx_f%d" android:layout_width="match_parent" android:layout_height="match_parent" android:scaleType="fitCenter" />'

def body(icon):
    return '''    <LinearLayout android:layout_width="match_parent" android:layout_height="match_parent" android:orientation="vertical"
        android:gravity="center_vertical" android:paddingLeft="14dp" android:paddingRight="14dp" android:paddingTop="6dp" android:paddingBottom="6dp">
        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal">
            <TextView android:id="@+id/wx_city" android:layout_width="0dp" android:layout_weight="1" android:layout_height="wrap_content"
                android:textSize="12sp" android:textColor="@color/wx_mut" android:fontFamily="sans-serif-light" android:maxLines="1" android:ellipsize="end" />
            <TextView android:id="@+id/wx_hilo" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:textSize="11sp" android:textColor="@color/wx_mut" android:fontFamily="sans-serif-light" android:maxLines="1" android:paddingLeft="4dp" />
        </LinearLayout>
        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content" android:orientation="horizontal"
            android:gravity="center_vertical">
            <TextView android:id="@+id/wx_temp" android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:textSize="32sp" android:textColor="@color/wx_ink" android:fontFamily="sans-serif-thin" android:maxLines="1" />
            <FrameLayout android:layout_width="0dp" android:layout_weight="1" android:layout_height="40dp">
%s
            </FrameLayout>
            <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:orientation="vertical" android:gravity="end">
                <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="horizontal">
                    <TextView android:id="@+id/wx_press" android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:textSize="11sp" android:textColor="@color/wx_ink" android:fontFamily="sans-serif-light" android:maxLines="1" />
                    <TextView android:id="@+id/wx_parr" android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:textSize="11sp" android:maxLines="1" />
                </LinearLayout>
                <LinearLayout android:layout_width="wrap_content" android:layout_height="wrap_content" android:orientation="horizontal">
                    <TextView android:id="@+id/wx_kpdot" android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:textSize="8sp" android:text="●" android:paddingRight="3dp" />
                    <TextView android:id="@+id/wx_kp" android:layout_width="wrap_content" android:layout_height="wrap_content"
                        android:textSize="11sp" android:textColor="@color/wx_ink" android:fontFamily="sans-serif-light" android:maxLines="1" />
                </LinearLayout>
            </LinearLayout>
        </LinearLayout>
    </LinearLayout>
''' % icon

HEAD = '''<?xml version="1.0" encoding="utf-8"?>
<!-- generated by widget/frames.py; @android:id/background lets Android 12+ round the corners -->
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android" android:id="@android:id/background"
    android:layout_width="match_parent" android:layout_height="match_parent" android:background="@drawable/wx_bg">
'''

def layout_anim():
    imgs = "\n".join("                    " + IMG % i for i in range(N))
    icon = ('                <ViewFlipper android:id="@+id/wx_flip" android:layout_width="match_parent" android:layout_height="match_parent"\n'
            '                    android:autoStart="true" android:flipInterval="%d">\n%s\n                </ViewFlipper>' % (1000 // FPS, imgs))
    return HEAD + body(icon) + '</FrameLayout>\n'

def layout_static():
    return HEAD + body("                " + IMG % 0) + '</FrameLayout>\n'

BG = '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="@color/wx_bg" /><corners android:radius="22dp" /><stroke android:width="1dp" android:color="@color/wx_line" />
</shape>
'''

def colors(th):
    c = THEMES[th]
    line = "#26%s" % c["ink"][1:]
    return ('<?xml version="1.0" encoding="utf-8"?>\n<resources>\n' +
            "".join('    <color name="wx_%s">%s</color>\n' % (k, v) for k, v in list(c.items()) + [("line", line)]) + "</resources>\n")


def write_android(res):
    for d in ("drawable", "layout", "values", "values-night"):
        os.makedirs(os.path.join(res, d), exist_ok=True)
    for k in KINDS:
        for f in range(N):
            with open(os.path.join(res, "drawable", "wxf_%s_%02d.xml" % (k, f)), "w", encoding="utf-8") as fh:
                fh.write(to_vector(scene(k, f)))
    with open(os.path.join(res, "drawable", "wx_bg.xml"), "w", encoding="utf-8") as fh:
        fh.write(BG)
    with open(os.path.join(res, "values", "wx_colors.xml"), "w", encoding="utf-8") as fh:
        fh.write(colors("light"))
    with open(os.path.join(res, "values-night", "wx_colors.xml"), "w", encoding="utf-8") as fh:
        fh.write(colors("dark"))
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
    col = {"light": {"g": "#1f9d55", "y": "#c98500", "r": "#d9463a", "m": "#557d73"},
           "dark": {"g": "#8be38f", "y": "#f2c94c", "r": "#ff7a6b", "m": "#a3a7ae"}}
    rows = []
    for th in ("light", "dark"):
        c, cc, cards = THEMES[th], col[th], []
        for k in KINDS:
            t, hl, pr, ar, a, kp = sample[k]
            frames = "".join('<div class="fr">%s</div>' % to_svg(scene(k, f), th) for f in range(N))
            dot = cc["r"] if kp >= 5 else cc["y"] if kp >= 4 else cc["g"]
            cards.append('<div class="item"><div class="w" style="background:%s;color:%s;border-color:%s26"><div class="top" style="color:%s"><span>Великий Новгород</span><span>%s</span></div>'
                         '<div class="main"><span class="t">%s</span><div class="ic">%s</div><div class="rt"><div>%s <span style="color:%s">%s</span></div>'
                         '<div><span style="font-size:8px;color:%s">●</span> Kp %d%s</div></div></div></div><small>%s</small></div>'
                         % (c["bg"], c["ink"], c["ink"], c["mut"], hl, t, frames, pr, cc[a], ar, dot, kp, " буря" if kp >= 5 else "", NAMES[k]))
        rows.append('<h2>%s</h2><div class="grid">%s</div>' % ("Светлая тема телефона" if th == "light" else "Тёмная тема телефона", "".join(cards)))
    page = '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Виджет в линиях</title><style>
*{box-sizing:border-box}body{margin:0;background:#0b0c0e;color:#eef0f3;font:15px/1.45 system-ui,sans-serif;padding:20px 16px 32px}
h1{font-size:18px;font-weight:400;margin:0 0 6px;text-align:center}h2{font-size:14px;font-weight:400;color:#a3a7ae;text-align:center;margin:22px 0 10px}
.lead{color:#a3a7ae;margin:0 auto 10px;font-size:13px;text-align:center;max-width:560px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:18px 14px;max-width:740px;margin:0 auto}
.item{display:flex;flex-direction:column;gap:6px;align-items:center}.item small{color:#a3a7ae;font-size:12.5px}
.w{position:relative;width:216px;height:80px;border-radius:22px;border:1px solid;padding:6px 14px;display:flex;flex-direction:column;justify-content:center;font-weight:300}
.top{display:flex;justify-content:space-between;font-size:12px}.top span:first-child{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.top span:last-child{font-size:11px;flex:none;padding-left:4px}.main{display:flex;align-items:center}
.t{font-size:32px;font-weight:100;letter-spacing:-.5px;line-height:1.1}.ic{position:relative;flex:1;height:40px}
.fr{position:absolute;inset:0;visibility:hidden}.fr svg{width:100%%;height:100%%;display:block}
.rt{text-align:right;font-size:11px;line-height:1.4;white-space:nowrap}
</style></head><body><h1>Виджет в линиях — значок погоды двигается, %d кадров в секунду</h1>
<p class="lead">Фон и цвет линий сами меняются вместе с темой телефона. Это те же кадры, что попадут в приложение.</p>
%s
<script>let f=0;const W=[...document.querySelectorAll(".ic")];function show(){W.forEach(w=>{w.querySelectorAll(".fr").forEach((x,i)=>x.style.visibility=i===f?"visible":"hidden");});f=(f+1)%%%d;}show();setInterval(show,%d);</script>
</body></html>''' % (FPS, "".join(rows), N, 1000 // FPS)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--preview":
        write_preview(sys.argv[2])
    elif len(sys.argv) == 2:
        write_android(sys.argv[1])
    else:
        sys.exit(__doc__)
