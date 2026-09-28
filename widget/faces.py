#!/usr/bin/env python3
"""The mood faces for the notification, drawn in thin lines like in the app.

Reads the faces (KFACE) from index.html and writes Android vector drawables kf_<kind>.xml:
res/drawable (dark lines for a light shade) and res/drawable-night (light lines for a dark shade).

    python3 widget/faces.py android/app/src/main/res
    python3 widget/faces.py --preview out.html      # the faces as they will look, for a quick check
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INK = {"drawable": "#FF1F2328", "drawable-night": "#FFECEEF0"}


def faces():
    src = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    body = src[src.index("const KFACE={"):]
    body = body[:body.index("};")]
    return dict(re.findall(r"(\w+):'([^']*)'", body))


def paths(svg):
    """Every visible shape of a face as path data; groups hidden with opacity="0" are left out."""
    svg = re.sub(r'<g[^>]*opacity="0"[^>]*>.*?</g>', "", svg)
    out = []
    for m in re.finditer(r"<(circle|path)\b([^>]*)/>", svg):
        tag, attrs = m.group(1), dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(2)))
        if tag == "path":
            out.append(attrs["d"])
        else:
            cx, cy, r = (float(attrs[k]) for k in ("cx", "cy", "r"))
            out.append(f"M{cx - r:g},{cy:g}a{r:g},{r:g} 0 1,0 {2 * r:g},0a{r:g},{r:g} 0 1,0 {-2 * r:g},0")
    return out


def vector(ds, color):
    items = "\n".join(
        f'    <path android:pathData="{d}" android:strokeColor="{color}" android:strokeWidth="1.5"'
        f' android:strokeLineCap="round" android:strokeLineJoin="round" android:fillColor="#00000000"/>'
        for d in ds)
    return ('<?xml version="1.0" encoding="utf-8"?>\n'
            '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
            '    android:width="32dp" android:height="32dp" android:viewportWidth="40" android:viewportHeight="40">\n'
            f"{items}\n</vector>\n")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--preview":
        cells = ""
        for k, s in faces().items():
            shapes = "".join('<path d="%s"/>' % d for d in paths(s))
            cells += '<div><svg viewBox="0 0 40 40">%s</svg><br>%s</div>' % (shapes, k)
        open(sys.argv[2], "w", encoding="utf-8").write(
            "<style>body{display:flex;gap:18px;font:12px sans-serif}svg{width:48px;height:48px;fill:none;"
            "stroke:#1f2328;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}</style>" + cells)
        return
    res = sys.argv[1]
    for folder, color in INK.items():
        os.makedirs(os.path.join(res, folder), exist_ok=True)
        for k, s in faces().items():
            open(os.path.join(res, folder, f"kf_{k}.xml"), "w", encoding="utf-8").write(vector(paths(s), color))


if __name__ == "__main__":
    main()
