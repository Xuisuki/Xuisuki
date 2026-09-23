#!/usr/bin/env python3
"""Генератор графики для профиля Xuisuki.

Вся картинка профиля рисуется здесь и лежит в репозитории: ни одного стороннего
сервиса-генератора, который однажды перестанет отвечать. Каждый файл собирается
дважды — под тёмную и светлую тему GitHub, README выбирает нужный через <picture>.
Логотипы технологий — simple-icons (CC0), пути и фирменные цвета лежат в
tools/icons.json, так что сборка сети не требует.
"""

import datetime
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
ICONS = json.load(open(os.path.join(ROOT, "tools", "icons.json"), encoding="utf-8"))

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,'Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,'SF Mono','JetBrains Mono','Cascadia Code',Menlo,Consolas,monospace"

THEMES = {
    "dark": dict(
        name="dark", panel="#0b0f15", panel2="#121821", border="#232b36",
        text="#e8eef5", muted="#8b96a3", faint="#2b333e", grid="#161c24",
        a1="#8b7bff", a2="#3aa7ff", a3="#2dd4bf", plazma="#ff4fa3", krypta="#f5c542",
        glow=".55", noise=".06",
        heat=["#161b22", "#0f4a55", "#14899a", "#3a9bff", "#8b7bff"],
    ),
    "light": dict(
        name="light", panel="#fbfcfe", panel2="#f1f4f8", border="#d9e0e8",
        text="#1f2328", muted="#57606a", faint="#d5dce4", grid="#edf1f5",
        a1="#6d5ce8", a2="#2f7de1", a3="#0f9f96", plazma="#d61f7a", krypta="#a87606",
        glow=".26", noise=".035",
        heat=["#ebeef2", "#b4e2e8", "#62c3d2", "#5a8ff0", "#6d5ce8"],
    ),
}

REDUCED = """
  @media (prefers-reduced-motion: reduce) {
    * { animation: none !important; }
  }"""


def write(name, body):
    path = os.path.join(ASSETS, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return path


def lum(hexcolor):
    r, g, b = (int(hexcolor[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return .2126 * r + .7152 * g + .0722 * b


def brand(t, key):
    """Фирменный цвет знака; чёрные и слишком тёмные знаки на тёмной теме берут цвет текста."""
    c = ICONS[key]["hex"]
    if t["name"] == "dark" and lum(c) < .25:
        return t["text"]
    return "#" + c


def icon(t, key, x, y, size, color=None):
    return (f'<svg x="{x:.1f}" y="{y:.1f}" width="{size}" height="{size}" viewBox="0 0 24 24">'
            f'<path d="{ICONS[key]["path"]}" fill="{color or brand(t, key)}"/></svg>')


def defs_common(t):
    """Размытие для «света», зерно и маска-виньетка — общие для всех больших карточек."""
    return f"""
  <filter id="blur" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="48"/></filter>
  <filter id="soft" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="7"/></filter>
  <filter id="grain" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" stitchTiles="stitch"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">
    <circle cx="1.2" cy="1.2" r="1.2" fill="{t['faint']}"/>
  </pattern>"""


def blob(cx, cy, r, color, opacity, path, dur):
    """Пятно света, медленно плывущее по кругу, — из них складывается «северное сияние»."""
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="{opacity}">'
            f'<animateTransform attributeName="transform" type="translate" values="{path}" '
            f'dur="{dur}s" repeatCount="indefinite" calcMode="spline" '
            f'keySplines="{";".join([".45 0 .55 1"] * (len(path.split(";")) - 1))}"/></circle>')


# ---------------------------------------------------------------- шапка

def header(t):
    W, H = 900, 320
    cx, cy = 705, 160
    g = t["glow"]

    orbits = []
    for i, (rx, ry, rot, col, dur, r) in enumerate((
        (182, 54, -14, t["a2"], 11, 4.2),
        (136, 38, 22, t["plazma"], 8, 5),
        (228, 70, 4, t["krypta"], 15, 4.6),
    )):
        d = f"M{cx - rx},{cy} a{rx},{ry} 0 1,0 {2 * rx},0 a{rx},{ry} 0 1,0 {-2 * rx},0"
        orbits.append(
            f'<g transform="rotate({rot} {cx} {cy})">'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="url(#orb)" stroke-width="1.1"/>'
            f'<g><circle r="{r * 3}" fill="{col}" opacity=".22" filter="url(#soft)"/>'
            f'<circle r="{r}" fill="{col}"/>'
            f'<animateMotion dur="{dur}s" begin="-{i * 2.3:.1f}s" repeatCount="indefinite" path="{d}"/></g></g>'
        )

    stars = "".join(
        f'<circle cx="{480 + (i * 97) % 410}" cy="{20 + (i * 53) % 280}" r="{.7 + (i % 3) * .35:.2f}" fill="{t["text"]}">'
        f'<animate attributeName="opacity" values=".08;.7;.08" dur="{3 + i % 5}s" begin="{(i * .37) % 4:.2f}s" repeatCount="indefinite"/></circle>'
        for i in range(34)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Xuisuki — full-stack engineer">
<defs>{defs_common(t)}
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">
    <stop offset="0" stop-color="{t['text']}"/>
    <stop offset=".45" stop-color="{t['text']}"/>
    <stop offset=".62" stop-color="{t['a3']}"/>
    <stop offset=".8" stop-color="{t['a1']}"/>
    <stop offset="1" stop-color="{t['text']}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0" dur="7s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="orb" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{t['muted']}" stop-opacity=".05"/>
    <stop offset=".5" stop-color="{t['muted']}" stop-opacity=".55"/>
    <stop offset="1" stop-color="{t['muted']}" stop-opacity=".05"/>
  </linearGradient>
  <radialGradient id="core" cx="40%" cy="36%" r="70%">
    <stop offset="0" stop-color="#ffffff" stop-opacity=".95"/>
    <stop offset=".25" stop-color="{t['a3']}"/>
    <stop offset=".75" stop-color="{t['a1']}"/>
    <stop offset="1" stop-color="{t['a1']}" stop-opacity=".2"/>
  </radialGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{t['panel']}" stop-opacity=".92"/>
    <stop offset=".42" stop-color="{t['panel']}" stop-opacity=".7"/>
    <stop offset=".62" stop-color="{t['panel']}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{t['a3']}" stop-opacity="0"/>
    <stop offset=".5" stop-color="{t['a3']}"/>
    <stop offset="1" stop-color="{t['a1']}" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="card"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18"/></clipPath>
</defs>
<style>
  .t {{ font-family:{SANS}; }} .m {{ font-family:{MONO}; }}
  .rise {{ opacity:0; animation:rise .9s cubic-bezier(.2,.7,.3,1) forwards; }}
  @keyframes rise {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:none; }} }}
  .sys {{ opacity:0; animation:fadein 1.6s ease .25s forwards; }}
  @keyframes fadein {{ to {{ opacity:1; }} }}
  .core {{ transform-box:fill-box; transform-origin:center; animation:pulse 5s ease-in-out infinite; }}
  @keyframes pulse {{ 0%,100% {{ transform:scale(1); }} 50% {{ transform:scale(1.07); }} }}
  .bar {{ animation:slide 4.2s ease-in-out infinite; }}
  @keyframes slide {{ 0%,100% {{ transform:translateX(0); }} 50% {{ transform:translateX(120px); }} }}
{REDUCED}
</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{t['panel']}"/>
  <g filter="url(#blur)">
    {blob(640, 70, 150, t['a1'], g, "0 0;-90 50;30 90;0 0", 24)}
    {blob(820, 250, 160, t['a2'], g, "0 0;-60 -70;-140 10;0 0", 28)}
    {blob(470, 280, 120, t['a3'], g, "0 0;90 -40;20 -90;0 0", 21)}
    {blob(880, 40, 90, t['plazma'], float(g) * .6, "0 0;-50 60;-10 20;0 0", 19)}
  </g>
  <rect width="{W}" height="{H}" fill="url(#dots)" opacity=".55"/>
  {stars}
  <g class="sys">
    <circle cx="{cx}" cy="{cy}" r="70" fill="{t['a3']}" opacity=".25" filter="url(#soft)"/>
    <circle class="core" cx="{cx}" cy="{cy}" r="30" fill="url(#core)"/>
    {"".join(orbits)}
  </g>
  <rect width="{W}" height="{H}" fill="url(#fade)"/>
  <rect width="{W}" height="{H}" filter="url(#grain)" opacity="{t['noise']}"/>

  <g class="rise" style="animation-delay:.05s">
    <text class="m" x="56" y="78" fill="{t['muted']}" font-size="11.5" letter-spacing="3.4">FULL-STACK ENGINEER · BACKEND · PRODUCT</text>
  </g>
  <g class="rise" style="animation-delay:.16s">
    <text class="t" x="52" y="152" fill="url(#name)" font-size="70" font-weight="800" letter-spacing="-2.4">Xuisuki</text>
  </g>
  <g class="rise" style="animation-delay:.28s">
    <rect x="56" y="172" width="150" height="2" rx="1" fill="{t['faint']}"/>
    <rect class="bar" x="56" y="172" width="30" height="2" rx="1" fill="url(#sweep)"/>
  </g>
  <g class="rise" style="animation-delay:.4s">
    <text class="t" x="56" y="210" fill="{t['text']}" font-size="18" opacity=".95">I design and ship products end to end —</text>
    <text class="t" x="56" y="236" fill="{t['text']}" font-size="18" opacity=".95">from the database to the button a customer taps.</text>
  </g>
  <g class="rise" style="animation-delay:.52s">
    <text class="m" x="56" y="272" fill="{t['muted']}" font-size="12.5" letter-spacing=".4">Go · TypeScript · Python · Kotlin  /  streaming · Telegram commerce · AI tools</text>
  </g>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{t['border']}"/>
</svg>
"""


# ---------------------------------------------------------------- путь

JOURNEY = [
    ("APR 2026", "Web studio work", ["Sites for an ISP and a shop,", "landing pages, first deploys"]),
    ("MAY 2026", "Network backend in Go", ["gRPC services, PostgreSQL,", "billing and a node fleet"]),
    ("JUN 2026", "LLM gateway", ["40+ model providers behind", "one API, token billing"]),
    ("JUL 2026", "Plazma Kino · Krypta", ["Online cinema and a Telegram", "commerce bot with Mini App"]),
    ("AUG 2026", "Apps, TV and games", ["Android TV in Kotlin, desktop,", "a Godot game, server cockpit"]),
    ("SEP 2026", "AI products", ["Product-card generator, video", "autopilot, admin panels"]),
]


def journey(t):
    W, H, ly = 900, 330, 165
    xs = [60 + i * 156 for i in range(len(JOURNEY))]
    cols = [t["a3"], t["a2"], t["a1"], t["plazma"], t["krypta"], t["a3"]]
    items = []
    for i, ((date, title, lines), x) in enumerate(zip(JOURNEY, xs)):
        up = i % 2 == 0
        anchor = "start" if i == 0 else "end" if i == len(xs) - 1 else "middle"
        tx = x - 10 if i == 0 else x + 10 if i == len(xs) - 1 else x
        y0 = 58 if up else 214
        tick = f'<line x1="{x}" y1="{ly - 14 if up else ly + 14}" x2="{x}" y2="{y0 + 76 if up else y0 - 18}" stroke="{cols[i]}" stroke-width="1" opacity=".45" stroke-dasharray="2 3"/>'
        body = "".join(
            f'<text class="t" x="{tx}" y="{y0 + 44 + k * 18}" fill="{t["muted"]}" font-size="13" text-anchor="{anchor}">{s}</text>'
            for k, s in enumerate(lines)
        )
        now = i == len(xs) - 1
        items.append(
            f'<g class="rise" style="animation-delay:{.25 + i * .14:.2f}s">{tick}'
            f'<text class="m" x="{tx}" y="{y0}" fill="{cols[i]}" font-size="11" letter-spacing="2" text-anchor="{anchor}">{date}{"  · NOW" if now else ""}</text>'
            f'<text class="t" x="{tx}" y="{y0 + 22}" fill="{t["text"]}" font-size="16.5" font-weight="700" text-anchor="{anchor}">{title}</text>'
            f'{body}'
            f'<circle cx="{x}" cy="{ly}" r="14" fill="{cols[i]}" opacity=".18" filter="url(#soft)"/>'
            f'<circle cx="{x}" cy="{ly}" r="6.5" fill="{t["panel"]}" stroke="{cols[i]}" stroke-width="2"/>'
            f'<circle cx="{x}" cy="{ly}" r="2.6" fill="{cols[i]}"/>'
            + (f'<circle cx="{x}" cy="{ly}" r="7" fill="none" stroke="{cols[i]}" stroke-width="1.4">'
               f'<animate attributeName="r" values="7;20;7" dur="2.6s" repeatCount="indefinite"/>'
               f'<animate attributeName="opacity" values=".9;0;.9" dur="2.6s" repeatCount="indefinite"/></circle>' if now else "")
            + '</g>'
        )
    line = f"M{xs[0]},{ly} L{xs[-1]},{ly}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Journey: what I have built, month by month">
<defs>{defs_common(t)}
  <linearGradient id="path" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{t['a3']}"/><stop offset=".45" stop-color="{t['a1']}"/>
    <stop offset=".65" stop-color="{t['plazma']}"/><stop offset=".82" stop-color="{t['krypta']}"/>
    <stop offset="1" stop-color="{t['a3']}"/>
  </linearGradient>
  <clipPath id="card"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18"/></clipPath>
</defs>
<style>
  .t {{ font-family:{SANS}; }} .m {{ font-family:{MONO}; }}
  .rise {{ opacity:0; animation:rise .8s cubic-bezier(.2,.7,.3,1) forwards; }}
  @keyframes rise {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:none; }} }}
  .draw {{ stroke-dasharray:800; stroke-dashoffset:800; animation:draw 1.9s cubic-bezier(.5,0,.2,1) .1s forwards; }}
  @keyframes draw {{ to {{ stroke-dashoffset:0; }} }}
{REDUCED}
</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{t['panel']}"/>
  <g filter="url(#blur)">
    {blob(200, 165, 110, t['a3'], float(t['glow']) * .45, "0 0;60 20;0 0", 20)}
    {blob(700, 165, 120, t['plazma'], float(t['glow']) * .35, "0 0;-60 -15;0 0", 23)}
  </g>
  <rect width="{W}" height="{H}" fill="url(#dots)" opacity=".45"/>
  <path d="{line}" stroke="{t['faint']}" stroke-width="2"/>
  <path class="draw" d="{line}" stroke="url(#path)" stroke-width="2.4" stroke-linecap="round"/>
  <g><circle r="9" fill="{t['text']}" opacity=".35" filter="url(#soft)"/><circle r="2.6" fill="{t['text']}"/>
    <animateMotion dur="6s" repeatCount="indefinite" path="{line}" keyPoints="0;1" keyTimes="0;1" calcMode="linear"/>
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.92;1" dur="6s" repeatCount="indefinite"/></g>
  {"".join(items)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{t['border']}"/>
</svg>
"""


# ---------------------------------------------------------------- карточки проектов

def pills(t, items, x, y):
    out, cur = [], x
    for i, (key, label) in enumerate(items):
        w = len(label) * 7.1 + 44
        out.append(
            f'<g class="rise" style="animation-delay:{.5 + i * .07:.2f}s">'
            f'<rect x="{cur:.0f}" y="{y}" width="{w:.0f}" height="28" rx="14" fill="{t["panel2"]}" fill-opacity=".75" stroke="{t["border"]}"/>'
            f'{icon(t, key, cur + 11, y + 6, 16)}'
            f'<text class="t" x="{cur + 33:.0f}" y="{y + 18.5}" fill="{t["text"]}" font-size="12.5" opacity=".9">{label}</text></g>'
        )
        cur += w + 8
    return "".join(out)


def project(t, *, W, H, accent, kicker, name, url, lines, stack, art):
    a = t[accent]
    g = float(t["glow"])
    body = "".join(
        f'<text class="t" x="40" y="{146 + k * 23}" fill="{t["muted"]}" font-size="15">{s}</text>'
        for k, s in enumerate(lines)
    )
    uw = len(url) * 7.6 + 46
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{name} — {kicker.lower()}">
<defs>{defs_common(t)}
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{t['panel']}" stop-opacity=".95"/>
    <stop offset=".45" stop-color="{t['panel']}" stop-opacity=".75"/>
    <stop offset=".62" stop-color="{t['panel']}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{a}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="vfade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".2" stop-color="#fff"/>
    <stop offset=".8" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <mask id="vmask"><rect width="{W}" height="{H}" fill="url(#vfade)"/></mask>
  <clipPath id="card"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18"/></clipPath>
</defs>
<style>
  .t {{ font-family:{SANS}; }} .m {{ font-family:{MONO}; }}
  .rise {{ opacity:0; animation:rise .8s cubic-bezier(.2,.7,.3,1) forwards; }}
  @keyframes rise {{ from {{ opacity:0; transform:translateY(9px); }} to {{ opacity:1; transform:none; }} }}
  .float {{ animation:float 6s ease-in-out infinite; }}
  @keyframes float {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(-8px); }} }}
{REDUCED}
</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{t['panel']}"/>
  <g filter="url(#blur)">
    {blob(W - 230, 60, 150, a, g * .9, "0 0;-70 60;20 40;0 0", 22)}
    {blob(W - 60, H - 30, 130, t['a1'], g * .6, "0 0;-50 -50;0 0", 26)}
  </g>
  <rect width="{W}" height="{H}" fill="url(#dots)" opacity=".4"/>
  {art}
  <rect width="{W}" height="{H}" fill="url(#fade)"/>
  <rect width="{W}" height="{H}" filter="url(#grain)" opacity="{t['noise']}"/>
  <rect x="0" y="0" width="3" height="{H}" fill="url(#edge)"/>
  <g class="rise" style="animation-delay:.05s">
    <text class="m" x="40" y="54" fill="{a}" font-size="11.5" letter-spacing="3">{kicker}</text>
  </g>
  <g class="rise" style="animation-delay:.14s">
    <text class="t" x="38" y="98" fill="{t['text']}" font-size="38" font-weight="800" letter-spacing="-1.2">{name}</text>
    <rect x="{52 + len(name) * 20.5:.0f}" y="73" width="{uw:.0f}" height="30" rx="15" fill="{a}" fill-opacity=".1" stroke="{a}" stroke-opacity=".55"/>
    <circle cx="{52 + len(name) * 20.5 + 16:.0f}" cy="88" r="3.4" fill="{a}">
      <animate attributeName="opacity" values="1;.25;1" dur="2.2s" repeatCount="indefinite"/></circle>
    <text class="m" x="{52 + len(name) * 20.5 + 28:.0f}" y="92.5" fill="{a}" font-size="12.5">{url} ↗</text>
  </g>
  <g class="rise" style="animation-delay:.26s">{body}</g>
  {pills(t, stack, 40, H - 60)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{t['border']}"/>
</svg>
"""


def art_cinema(t, W, H):
    """Стена постеров под наклоном: колонки бесконечно едут вверх, по центру стеклянная кнопка."""
    hues = [t["plazma"], t["a1"], t["a2"], t["a3"], t["krypta"]]
    cols = []
    for c in range(5):
        cards = []
        for r in range(8):
            col = hues[(c * 2 + r) % len(hues)]
            y = r * 118
            cards.append(
                f'<rect x="0" y="{y}" width="84" height="108" rx="10" fill="{col}" fill-opacity=".16" stroke="{col}" stroke-opacity=".35"/>'
                f'<rect x="10" y="{y + 76}" width="{40 + (r * 13 + c * 7) % 28}" height="5" rx="2.5" fill="{col}" opacity=".55"/>'
                f'<rect x="10" y="{y + 88}" width="{26 + (r * 7 + c * 11) % 22}" height="4" rx="2" fill="{t["muted"]}" opacity=".35"/>'
            )
        d = 18 + c * 3
        cols.append(
            f'<g transform="translate({c * 96},{-(c % 2) * 60})"><g>{"".join(cards)}'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -472" dur="{d}s" repeatCount="indefinite"/></g></g>'
        )
    px, py = W - 250, H / 2
    return f"""<g mask="url(#vmask)"><g transform="translate({W - 470},-40) rotate(-14) skewX(-6)">{"".join(cols)}</g></g>
  <g class="float">
    <circle cx="{px}" cy="{py}" r="46" fill="{t['plazma']}" opacity=".35" filter="url(#soft)"/>
    <circle cx="{px}" cy="{py}" r="34" fill="{t['panel']}" fill-opacity=".55" stroke="{t['plazma']}" stroke-opacity=".8" stroke-width="1.4"/>
    <path d="M{px - 8},{py - 13} L{px + 15},{py} L{px - 8},{py + 13} Z" fill="{t['plazma']}"/>
    <circle cx="{px}" cy="{py}" r="34" fill="none" stroke="{t['plazma']}" stroke-width="1.2">
      <animate attributeName="r" values="34;58;34" dur="3.4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values=".7;0;.7" dur="3.4s" repeatCount="indefinite"/></circle>
  </g>"""


def art_phone(t, W, _H):
    """Мини-приложение в телефоне: карточка тарифа, пилюля оплаты, бегущие уведомления."""
    a = t["krypta"]
    x, y = W - 300, 26
    msgs = "".join(
        f'<g opacity="0"><rect x="{x - 150 + (i % 2) * 20}" y="{y + 40 + i * 48}" width="{150 - (i % 2) * 30}" height="34" rx="17" '
        f'fill="{t["panel2"]}" fill-opacity=".85" stroke="{a if i % 2 else t["border"]}" stroke-opacity=".7"/>'
        f'<circle cx="{x - 132 + (i % 2) * 20}" cy="{y + 57 + i * 48}" r="6" fill="{a if i % 2 else t["a3"]}" opacity=".8"/>'
        f'<rect x="{x - 118 + (i % 2) * 20}" y="{y + 54 + i * 48}" width="{80 - (i % 2) * 26}" height="6" rx="3" fill="{t["muted"]}" opacity=".5"/>'
        f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.15;.8;1" dur="7s" begin="{i * 1.4:.1f}s" repeatCount="indefinite"/></g>'
        for i in range(3)
    )
    return f"""<g class="float">
  <rect x="{x - 20}" y="{y + 20}" width="200" height="260" rx="40" fill="{a}" opacity=".22" filter="url(#soft)"/>
  <rect x="{x}" y="{y}" width="176" height="300" rx="30" fill="{t['panel']}" fill-opacity=".92" stroke="{t['border']}" stroke-width="1.5"/>
  <rect x="{x + 66}" y="{y + 12}" width="44" height="7" rx="3.5" fill="{t['faint']}"/>
  <text class="m" x="{x + 20}" y="{y + 48}" fill="{t['muted']}" font-size="8.5" letter-spacing="1.6">KRYPTA · SUBSCRIPTION</text>
  <text class="t" x="{x + 20}" y="{y + 74}" fill="{t['text']}" font-size="19" font-weight="800">Unlimited</text>
  <text class="t" x="{x + 20}" y="{y + 94}" fill="{a}" font-size="17" font-style="italic" font-family="Georgia,serif">5 devices</text>
  <rect x="{x + 16}" y="{y + 108}" width="144" height="84" rx="16" fill="{a}" fill-opacity=".12" stroke="{a}" stroke-opacity=".6"/>
  <text class="t" x="{x + 30}" y="{y + 142}" fill="{t['text']}" font-size="24" font-weight="800">28 days</text>
  <text class="t" x="{x + 30}" y="{y + 162}" fill="{t['muted']}" font-size="10">left · auto-renew on</text>
  <rect x="{x + 30}" y="{y + 172}" width="60" height="5" rx="2.5" fill="{a}" opacity=".7"/>
  <rect x="{x + 16}" y="{y + 206}" width="144" height="34" rx="17" fill="none" stroke="{a}" stroke-width="1.4"/>
  <text class="t" x="{x + 88}" y="{y + 227}" fill="{a}" font-size="12" font-weight="700" text-anchor="middle">Pay with Stars</text>
  <rect x="{x + 16}" y="{y + 206}" width="144" height="34" rx="17" fill="none" stroke="{a}">
    <animate attributeName="opacity" values=".1;.9;.1" dur="2.6s" repeatCount="indefinite"/></rect>
  <rect x="{x + 22}" y="{y + 256}" width="132" height="30" rx="15" fill="{t['panel2']}" stroke="{t['border']}"/>
  <circle cx="{x + 50}" cy="{y + 271}" r="4" fill="{a}"/><circle cx="{x + 88}" cy="{y + 271}" r="4" fill="{t['muted']}" opacity=".6"/>
  <circle cx="{x + 126}" cy="{y + 271}" r="4" fill="{t['muted']}" opacity=".6"/>
</g>
{msgs}"""


PROJECTS = [
    dict(key="plazma", accent="plazma", W=900, H=270, kicker="ONLINE CINEMA", name="Plazma Kino",
         url="plazmazerkalo.fun", art=art_cinema,
         lines=["Own catalog of 60,000+ films and series, a clean player",
                "and apps for web, desktop and Android TV with synced",
                "progress. Delivery heals itself: signed beacon + mirrors."],
         stack=[("nodedotjs", "Node.js"), ("react", "React"), ("kotlin", "Kotlin"),
                ("redis", "Redis"), ("caddy", "Caddy")]),
    dict(key="krypta", accent="krypta", W=900, H=270, kicker="TELEGRAM COMMERCE", name="Krypta",
         url="t.me/KryptaVpn_Robot", art=art_phone,
         lines=["Telegram bot + Mini App that sells subscriptions end to end:",
                "Stars, crypto and card payments, trials and referrals,",
                "plus its own admin panel for billing, users and nodes."],
         stack=[("typescript", "TypeScript"), ("telegram", "grammY"), ("react", "React"),
                ("framer", "Framer Motion"), ("sqlite", "SQLite")]),
]


# ---------------------------------------------------------------- стек

LANGS = [("go", "Go"), ("typescript", "TypeScript"), ("javascript", "JavaScript"), ("python", "Python"),
         ("kotlin", "Kotlin"), ("postgresql", "SQL"), ("gnubash", "Bash"), ("godotengine", "GDScript")]

TOOLS = [("react", "React"), ("nextdotjs", "Next.js"), ("nodedotjs", "Node.js"), ("tailwindcss", "Tailwind"),
         ("framer", "Framer Motion"), ("threedotjs", "Three.js"), ("webgl", "WebGL"), ("fastapi", "FastAPI"),
         ("postgresql", "PostgreSQL"), ("redis", "Redis"), ("sqlite", "SQLite"), ("docker", "Docker"),
         ("caddy", "Caddy"), ("linux", "Linux"), ("prometheus", "Prometheus"), ("grafana", "Grafana"),
         ("telegram", "Telegram Bot API")]


def stack(t):
    W = 900
    out = [f'<text class="m" x="32" y="42" fill="{t["muted"]}" font-size="11" letter-spacing="2.6">LANGUAGES</text>']
    tw, th, gap, x0, y0 = 97, 116, 7.3, 32, 60
    for i, (key, label) in enumerate(LANGS):
        c = brand(t, key)
        x = x0 + i * (tw + gap)
        out.append(
            f'<g class="rise" style="animation-delay:{i * .06:.2f}s">'
            f'<rect x="{x:.1f}" y="{y0}" width="{tw}" height="{th}" rx="18" fill="{c}" fill-opacity=".07" stroke="{c}" stroke-opacity=".28"/>'
            f'<circle cx="{x + tw / 2:.1f}" cy="{y0 + 46}" r="26" fill="{c}" opacity="{.28 if t["name"] == "dark" else .16}" filter="url(#soft)"/>'
            f'{icon(t, key, x + tw / 2 - 20, y0 + 26, 40)}'
            f'<text class="t" x="{x + tw / 2:.1f}" y="{y0 + 98}" fill="{t["text"]}" font-size="13.5" font-weight="600" text-anchor="middle">{label}</text>'
            f'<rect x="{x:.1f}" y="{y0}" width="{tw}" height="{th}" rx="18" fill="none" stroke="{c}" stroke-width="1.3" opacity="0">'
            f'<animate attributeName="opacity" values="0;.9;0" dur="{len(LANGS) * .7:.1f}s" begin="{1 + i * .7:.1f}s" repeatCount="indefinite"/></rect>'
            '</g>'
        )
    y = y0 + th + 46
    out.append(f'<text class="m" x="32" y="{y}" fill="{t["muted"]}" font-size="11" letter-spacing="2.6">FRAMEWORKS · DATA · INFRASTRUCTURE</text>')
    y += 16
    x = 32
    for i, (key, label) in enumerate(TOOLS):
        w = len(label) * 7.3 + 48
        if x + w > W - 32:
            x, y = 32, y + 44
        c = brand(t, key)
        out.append(
            f'<g class="rise" style="animation-delay:{.4 + i * .035:.2f}s">'
            f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="34" rx="17" fill="{c}" fill-opacity=".06" stroke="{t["border"]}"/>'
            f'{icon(t, key, x + 13, y + 8, 18)}'
            f'<text class="t" x="{x + 38:.1f}" y="{y + 21.5}" fill="{t["text"]}" font-size="13" opacity=".92">{label}</text></g>'
        )
        x += w + 8
    H = y + 34 + 30
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Languages: {', '.join(l for _, l in LANGS)}">
<defs>{defs_common(t)}<clipPath id="card"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18"/></clipPath></defs>
<style>
  .t {{ font-family:{SANS}; }} .m {{ font-family:{MONO}; }}
  .rise {{ opacity:0; animation:rise .7s cubic-bezier(.2,.7,.3,1) forwards; }}
  @keyframes rise {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:none; }} }}
{REDUCED}
</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{t['panel']}"/>
  <g filter="url(#blur)">{blob(820, 40, 120, t['a2'], float(t['glow']) * .35, "0 0;-80 30;0 0", 24)}</g>
  <rect width="{W}" height="{H}" fill="url(#dots)" opacity=".35"/>
  {"".join(out)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{t['border']}"/>
</svg>
"""


def divider(t, label):
    """Подпись раздела: метка, линия-градиент и искра, бегущая по ней."""
    w = len(label) * 8.4 + 34
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 34" width="900" height="34" role="img" aria-label="{label}">
<defs>
  <linearGradient id="ln" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{t['a3']}" stop-opacity=".9"/><stop offset=".5" stop-color="{t['a1']}" stop-opacity=".5"/>
    <stop offset="1" stop-color="{t['border']}" stop-opacity=".2"/>
  </linearGradient>
</defs>
<style>
  .m {{ font-family:{MONO}; }}
  .ln {{ stroke-dasharray:900; stroke-dashoffset:900; animation:draw 1.6s ease .15s forwards; }}
  @keyframes draw {{ to {{ stroke-dashoffset:0; }} }}
{REDUCED}
</style>
<circle cx="5" cy="17" r="4" fill="none" stroke="{t['a3']}" stroke-width="1.5"/>
<text class="m" x="18" y="22" fill="{t['text']}" font-size="12.5" font-weight="600" letter-spacing="3.4">{label}</text>
<line class="ln" x1="{w:.0f}" y1="17" x2="900" y2="17" stroke="url(#ln)" stroke-width="1.2"/>
<circle r="2.2" cy="17" fill="{t['a3']}">
  <animate attributeName="cx" values="{w:.0f};900" dur="4.5s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;1;0" dur="4.5s" repeatCount="indefinite"/></circle>
</svg>
"""


# ---------------------------------------------------------------- статистика

GQL = """
query($login:String!){
  user(login:$login){
    repositories(ownerAffiliations:OWNER, isFork:false, first:100){
      totalCount
      nodes{ languages(first:12, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name color } } } }
    }
    contributionsCollection{
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ contributionCount date } }
      }
      totalCommitContributions
      totalPullRequestContributions
      restrictedContributionsCount
    }
  }
}"""

# календарь берёт полгода: вклады начались весной 2026, год назад пустые клетки
WEEKS = 26

# разметка и служебные файлы кодом не считаются: иначе HTML витрин забивает всю полосу
NOT_CODE = {"HTML", "CSS", "SCSS", "Vim Snippet", "Makefile", "Dockerfile", "Procfile", "Batchfile"}


def fetch(login, token):
    """Статистика по личному токену: в неё входят и приватные репозитории."""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": GQL, "variables": {"login": login}}).encode(),
        headers={"Authorization": "bearer " + token, "Content-Type": "application/json",
                 "User-Agent": "profile-builder"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def streaks(weeks):
    days = [d for w in weeks for d in w["contributionDays"]]
    best = cur = run = 0
    for d in days:
        if d["contributionCount"] > 0:
            run += 1
            best = max(best, run)
        else:
            run = 0
    for d in reversed(days):
        if d["contributionCount"] > 0:
            cur += 1
        elif cur or d is not days[-1]:
            break
    return cur, best


def languages(u, top=7):
    size, color = {}, {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            if n in NOT_CODE:
                continue
            size[n] = size.get(n, 0) + e["size"]
            color[n] = e["node"]["color"] or "#8b949e"
    total = sum(size.values()) or 1
    rows = sorted(size.items(), key=lambda kv: -kv[1])
    out = [(n, s / total, color[n]) for n, s in rows[:top]]
    rest = sum(s for _, s in rows[top:]) / total
    if rest > 0:
        out.append(("Other", rest, "#8b949e"))
    return out


def stats(t, u):
    W = 900
    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]
    weeks = cal["weeks"][-WEEKS:]
    days = [d for w in weeks for d in w["contributionDays"]]
    cur, best = streaks(weeks)
    peak = max((d["contributionCount"] for d in days), default=0) or 1
    active = sum(1 for d in days if d["contributionCount"])

    metrics = [
        (cal["totalContributions"], "CONTRIBUTIONS", "last 12 months", t["a3"]),
        (cc["totalCommitContributions"], "COMMITS", "incl. private repos", t["a2"]),
        (cc["totalPullRequestContributions"], "PULL REQUESTS", "opened", t["a1"]),
        (u["repositories"]["totalCount"], "REPOSITORIES", "owned, not forks", t["plazma"]),
    ]
    tiles = []
    tw, gap = 204, 10
    for i, (v, k, sub, c) in enumerate(metrics):
        x = 32 + i * (tw + gap)
        tiles.append(
            f'<g class="rise" style="animation-delay:{i * .08:.2f}s">'
            f'<rect x="{x}" y="28" width="{tw}" height="104" rx="18" fill="{t["panel2"]}" fill-opacity=".7" stroke="{t["border"]}"/>'
            f'<circle cx="{x + tw - 30}" cy="56" r="34" fill="{c}" opacity="{float(t["glow"]) * .5:.2f}" filter="url(#soft)"/>'
            f'<text class="m" x="{x + 20}" y="56" fill="{t["muted"]}" font-size="10.5" letter-spacing="1.8">{k}</text>'
            f'<text class="t" x="{x + 18}" y="100" fill="{t["text"]}" font-size="38" font-weight="800" letter-spacing="-1.4">{v}</text>'
            f'<rect x="{x + 20}" y="112" width="26" height="3" rx="1.5" fill="{c}"/>'
            f'<text class="t" x="{x + 54}" y="116" fill="{t["muted"]}" font-size="11">{sub}</text></g>'
        )

    cells, mlabels, seen = [], [], set()
    cw, cg, x0, y0 = 24, 5, 90, 196
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            di = int(datetime.date.fromisoformat(d["date"]).strftime("%w"))
            n = d["contributionCount"]
            lvl = 0 if not n else min(4, 1 + int(3.999 * (n / peak) ** .55))
            cells.append(
                f'<rect x="{x0 + wi * (cw + cg):.1f}" y="{y0 + di * (cw + cg):.1f}" width="{cw}" height="{cw}" '
                f'rx="6" fill="{t["heat"][lvl]}" class="cell" style="animation-delay:{wi * .012:.3f}s"/>'
            )
        first = w["contributionDays"][0]["date"]
        if first[:7] not in seen and first[8:10] <= "07":
            seen.add(first[:7])
            mlabels.append(
                f'<text class="m" x="{x0 + wi * (cw + cg):.1f}" y="{y0 - 10}" fill="{t["muted"]}" font-size="10.5">'
                f'{datetime.date.fromisoformat(first).strftime("%b")}</text>'
            )
    for di, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        mlabels.append(f'<text class="m" x="{x0 - 12}" y="{y0 + di * (cw + cg) + 16:.1f}" fill="{t["muted"]}" '
                       f'font-size="9.5" text-anchor="end">{lab}</text>')
    hy = y0 + 7 * (cw + cg)
    legend = "".join(
        f'<rect x="{770 + i * 14}" y="{hy + 10:.0f}" width="10" height="10" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(t["heat"])
    )
    facts = (f"last {WEEKS} weeks  ·  {active} active days  ·  current streak {cur}  ·  longest streak {best}  ·  busiest day {peak}")

    langs = languages(u)
    by = hy + 84
    segs, leg, cx = [], [], 32.0
    span = W - 64
    for i, (n, share, c) in enumerate(langs):
        w = max(2.0, share * span)
        segs.append(
            f'<rect x="{cx:.1f}" y="{by}" width="{w - 2:.1f}" height="12" rx="3" fill="{c}">'
            f'<animate attributeName="width" values="0;{w - 2:.1f}" dur=".9s" begin="{.3 + i * .08:.2f}s" fill="freeze" '
            f'calcMode="spline" keySplines=".2 .7 .3 1"/></rect>'
        )
        cx += w
    lx, ly = 32.0, by + 40
    for n, share, c in langs:
        label = f"{n} {share * 100:.1f}%"
        wl = len(label) * 7.2 + 30
        if lx + wl > W - 32:
            lx, ly = 32.0, ly + 24
        leg.append(f'<circle cx="{lx + 5:.1f}" cy="{ly - 4}" r="5" fill="{c}"/>'
                   f'<text class="t" x="{lx + 16:.1f}" y="{ly}" fill="{t["text"]}" font-size="12.5">{n} '
                   f'<tspan fill="{t["muted"]}">{share * 100:.1f}%</tspan></text>')
        lx += wl
    H = ly + 30

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" width="{W}" height="{H:.0f}" role="img" aria-label="GitHub activity: {cal['totalContributions']} contributions in the last 12 months">
<defs>{defs_common(t)}<clipPath id="card"><rect x="1" y="1" width="{W - 2}" height="{H - 2:.0f}" rx="18"/></clipPath>
  <clipPath id="bar"><rect x="32" y="{by}" width="{span}" height="12" rx="6"/></clipPath></defs>
<style>
  .t {{ font-family:{SANS}; }} .m {{ font-family:{MONO}; }}
  .rise {{ opacity:0; animation:rise .7s cubic-bezier(.2,.7,.3,1) forwards; }}
  @keyframes rise {{ from {{ opacity:0; transform:translateY(9px); }} to {{ opacity:1; transform:none; }} }}
  .cell {{ animation:pop .5s cubic-bezier(.2,.7,.3,1) backwards; transform-box:fill-box; transform-origin:center; }}
  @keyframes pop {{ from {{ opacity:0; transform:scale(.3); }} }}
{REDUCED}
</style>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H:.0f}" fill="{t['panel']}"/>
  <g filter="url(#blur)">{blob(120, 40, 130, t['a3'], float(t['glow']) * .35, "0 0;80 30;0 0", 24)}</g>
  {"".join(tiles)}
  {"".join(mlabels)}
  {"".join(cells)}
  <g class="rise" style="animation-delay:.6s">
    <text class="t" x="{x0}" y="{hy + 19:.0f}" fill="{t['muted']}" font-size="12">{facts}</text>
    <text class="m" x="740" y="{hy + 19:.0f}" fill="{t['muted']}" font-size="10" text-anchor="end">less</text>
    {legend}
    <text class="m" x="{774 + 5 * 14}" y="{hy + 19:.0f}" fill="{t['muted']}" font-size="10">more</text>
  </g>
  <line x1="32" y1="{by - 30}" x2="{W - 32}" y2="{by - 30}" stroke="{t['border']}"/>
  <text class="m" x="32" y="{by - 10}" fill="{t['muted']}" font-size="10.5" letter-spacing="1.8">LANGUAGES · SHARE OF CODE ACROSS ALL REPOSITORIES</text>
  <rect x="32" y="{by}" width="{span}" height="12" rx="6" fill="{t['grid']}"/>
  <g clip-path="url(#bar)">{"".join(segs)}</g>
  {"".join(leg)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1:.0f}" rx="18" fill="none" stroke="{t['border']}"/>
</svg>
"""


# ---------------------------------------------------------------- сборка

SECTIONS = ("JOURNEY", "PROJECTS", "STACK", "ACTIVITY")


def main():
    os.makedirs(ASSETS, exist_ok=True)
    login = os.environ.get("PROFILE_LOGIN", "Xuisuki")
    token = os.environ.get("GITHUB_TOKEN", "")
    only = sys.argv[1] if len(sys.argv) > 1 else ""

    user = None
    if token:
        try:
            user = fetch(login, token)
        except Exception as exc:            # без сети рисуем всё, кроме статистики
            print("stats: пропущено —", exc, file=sys.stderr)

    for name, t in THEMES.items():
        if only in ("", "art"):
            write(f"header-{name}.svg", header(t))
            write(f"journey-{name}.svg", journey(t))
            write(f"stack-{name}.svg", stack(t))
            for label in SECTIONS:
                write(f"div-{label.lower()}-{name}.svg", divider(t, label))
            for p in PROJECTS:
                write(f"card-{p['key']}-{name}.svg", project(
                    t, W=p["W"], H=p["H"], accent=p["accent"], kicker=p["kicker"],
                    name=p["name"], url=p["url"], lines=p["lines"], stack=p["stack"],
                    art=p["art"](t, p["W"], p["H"])))
        if user:
            write(f"stats-{name}.svg", stats(t, user))
    print("готово:", sorted(os.listdir(ASSETS)))


if __name__ == "__main__":
    main()
