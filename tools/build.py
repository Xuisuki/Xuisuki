#!/usr/bin/env python3
"""Build self-contained, responsive motion artwork with no network access.

SVG images embed their bitmaps. Content hashes keep refreshes deterministic.
All motion has a readable prefers-reduced-motion fallback.
"""
import base64
import hashlib
from html import escape
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "source"
ICONS = json.loads((ROOT / "tools/icons.json").read_text())
FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif"
MONO = "'SFMono-Regular', Consolas, 'Liberation Mono', monospace"


def embedded(name, mime):
    return "data:" + mime + ";base64," + base64.b64encode((SOURCE / name).read_bytes()).decode()


def text(x, y, value, size=28, fill="#eef5ff", **attrs):
    attributes = " ".join(f'{k.rstrip("_").replace("_", "-")}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" {attributes}>{escape(value)}</text>'


def icon(key, x, y, size=28, color=None):
    data = ICONS[key]
    return f'<g transform="translate({x} {y}) scale({size / 24})"><path fill="{color or "#" + data["hex"]}" d="{data["path"]}"/></g>'


STYLE = '''
text{font-family:FONT} .mono{font-family:MONO}
.float{animation:float 6s ease-in-out infinite}
.float-slow{animation:float 8s ease-in-out -3s infinite}
.breath{animation:breath 5s ease-in-out infinite}
.orbit{animation:orbit 14s linear infinite}
.orbit-reverse{animation:orbit 20s linear reverse infinite}
.spark{animation:spark 4s ease-in-out infinite}
@keyframes float{0%,100%{transform:translate(0,0)}50%{transform:translate(-4px,-12px)}}
@keyframes breath{0%,100%{opacity:.4}50%{opacity:.9}}
@keyframes orbit{to{stroke-dashoffset:-800}}
@keyframes spark{0%,100%{opacity:.2}50%{opacity:1}}
@media(prefers-reduced-motion:reduce){.float,.float-slow,.breath,.orbit,.orbit-reverse,.spark{animation:none;transform:none}}
'''.replace("FONT", FONT).replace("MONO", MONO)


def document(width, height, title, desc, body, extra_defs=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>
<defs>
<linearGradient id="panel" x2="1" y2="1"><stop stop-color="#111d32"/><stop offset="1" stop-color="#060c1a"/></linearGradient>
<linearGradient id="edge" x2="1" y2="1"><stop stop-color="#82d8ff" stop-opacity=".4"/><stop offset=".5" stop-color="#4b75ff" stop-opacity=".06"/><stop offset="1" stop-color="#96d8ff" stop-opacity=".2"/></linearGradient>
<linearGradient id="ice"><stop stop-color="#c9f1ff"/><stop offset=".5" stop-color="#61caff"/><stop offset="1" stop-color="#7c7dff"/></linearGradient>
<radialGradient id="aura"><stop stop-color="#2579e7" stop-opacity=".44"/><stop offset=".45" stop-color="#1a4fac" stop-opacity=".2"/><stop offset="1" stop-color="#071020" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5"/></filter>
<clipPath id="canvas"><rect width="{width}" height="{height}" rx="28"/></clipPath>
{extra_defs}</defs><style>{STYLE}</style><g clip-path="url(#canvas)">{body}</g></svg>\n'''


def stars(width, height):
    return "".join(f'<circle class="spark" style="animation-delay:-{i % 5}s" cx="{(i * 137 + 39) % width}" cy="{(i * 89 + 31) % height}" r="{1.2 if i % 3 else 2}" fill="#9edbff"/>' for i in range(24))


def hero(compact=False):
    w, h = (600, 760) if compact else (1200, 660)
    cx, cy = (429, 451) if compact else (927, 327)
    art_x, art_y, art_w, art_h = (203, 280, 412, 618) if compact else (694, -12, 468, 702)
    body = f'<rect width="{w}" height="{h}" fill="#060c19"/><ellipse class="breath" cx="{cx}" cy="{cy}" rx="{w * .47}" ry="{h * .64}" fill="url(#aura)"/>'
    for offset in range(-4, 5):
        body += f'<path d="M{cx + offset * 29} {h * .7}L{cx + offset * 240} {h}" stroke="#77baff" stroke-opacity=".065"/>'
    for y in (h * .76, h * .85, h * .96):
        body += f'<path d="M0 {y}H{w}" stroke="#77baff" stroke-opacity=".08"/>'
    body += stars(w, h) + f'<g transform="translate({cx} {cy}) rotate(-28)">'
    for r, ry, opacity in ((250, 132, ".15"), (210, 102, ".35"), (285, 155, ".09")):
        body += f'<ellipse rx="{r}" ry="{ry}" fill="none" stroke="#63caff" stroke-opacity="{opacity}" stroke-width="1.5"/>'
    body += '<ellipse class="orbit" rx="250" ry="132" fill="none" stroke="url(#ice)" stroke-width="3" stroke-dasharray="165 635"/><ellipse class="orbit-reverse" rx="210" ry="102" fill="none" stroke="#99e6ff" stroke-width="2" stroke-dasharray="80 720"/></g>'
    body += f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="28" fill="none" stroke="url(#edge)" stroke-width="1.5"/>'
    left = 36 if compact else 64
    body += f'<path d="M{left} 48l12 18-12 18M{left + 18} 48l-12 18 12 18" fill="none" stroke="url(#ice)" stroke-width="3" stroke-linecap="round"/>'
    body += text(left + 39, 74, "prodX / Xuisuki", 22 if compact else 24, "#d7eaff", letter_spacing=".5")
    body += text(w - 32 if compact else w - 48, 71, "∞", 34, "#75ccff", text_anchor="end")
    if compact:
        body += text(left, 174, "Xuisuki", 85, font_weight="750", letter_spacing="-5")
        body += text(left, 222, "Серверные системы,", 27, "#aec2df")
        body += text(left, 260, "Telegram-сервисы и приложения.", 27, "#aec2df")
        body += text(26, 357, "INFINITY", 91, "none", stroke="#426694", stroke_width="1", letter_spacing="6", font_weight="750", opacity=".65")
        body += '<rect x="36" y="401" width="291" height="146" rx="15" fill="#102139" fill-opacity=".62" stroke="#567da8" stroke-opacity=".3"/>'
        body += text(57, 440, "無限", 32, "#6b9acd")
        body += text(57, 478, "BEYOND THE LIMIT", 17, "#759abd", class_="mono", letter_spacing="1.2")
        body += '<path d="M57 511H210" stroke="#73c6f6" stroke-opacity=".3"/><path class="orbit" d="M57 511H210" stroke="#9ce6ff" stroke-width="2" stroke-dasharray="38 762"/>'
        body += text(left, 627, "МОИ ПРОЕКТЫ", 18, "#83a5d0", letter_spacing="2.2", font_weight="600")
        body += text(left, 667, "pxost", 32, font_weight="650")
        body += text(left, 703, "Plazma Kino / Krypta", 22, "#a4bbd8")
    else:
        body += text(left, 251, "Xuisuki", 112, font_weight="750", letter_spacing="-6")
        body += text(left + 2, 322, "Серверные системы,", 33, "#afc5e2")
        body += text(left + 2, 369, "Telegram-сервисы и приложения.", 33, "#afc5e2")
        body += text(581, 529, "INFINITY", 138, "none", stroke="#3e689e", stroke_width="1.3", letter_spacing="3", font_weight="750", opacity=".7")
        body += '<rect x="849" y="94" width="288" height="112" rx="15" fill="#112a48" fill-opacity=".62" stroke="#89c4ff" stroke-opacity=".25"/>'
        body += text(873, 140, "無限", 34, "#80a7d2")
        body += text(873, 177, "BEYOND THE LIMIT", 18, "#729fc9", class_="mono", letter_spacing="1.2")
        body += text(left, 512, "СОЗДАЮ И РАЗВИВАЮ", 19, "#83a5d0", letter_spacing="2.6", font_weight="650")
        body += text(left, 558, "pxost / Plazma Kino / Krypta", 28, "#d5e5fa", font_weight="500")
        body += '<path d="M64 603H597" stroke="#7ebdf4" stroke-opacity=".2"/><path class="orbit" d="M64 603H597" stroke="url(#ice)" stroke-width="2" stroke-dasharray="125 675"/>'
    body += f'<g class="float"><image x="{art_x}" y="{art_y}" width="{art_w}" height="{art_h}" xlink:href="{embedded("gojo-3d.png", "image/png")}"/></g>'
    near = f'M{cx - 94} {cy + 136}C{cx - 21} {cy + 192},{cx + 150} {cy + 150},{cx + 207} {cy + 59}'
    body += f'<path class="breath" d="{near}" fill="none" stroke="#60bfff" stroke-width="8" filter="url(#glow)"/><path class="orbit" d="{near}" fill="none" stroke="url(#ice)" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="114 686"/>'
    return document(w, h, "Xuisuki / prodX — Infinity", "Серверные системы, Telegram-сервисы и приложения. Анимированная композиция с 3D-рендером Сатору Годжо. Проекты: pxost, Plazma Kino, Krypta.", body)


PROJECTS = [
    {"key": "pxost", "title": "pxost", "label": "TELEGRAM / PUBLISHING", "accent": "#a591ff", "rgb": "120,80,230", "logo": "pxost-original.svg", "mime": "image/svg+xml", "url": "https://t.me/pxostbot", "lines": ["Редактор и отложенный постинг.", "Контент-план и ИИ для каналов."], "stack": [("python", "Python"), ("fastapi", "FastAPI"), ("react", "React"), ("postgresql", "PostgreSQL")]},
    {"key": "plazma", "title": "Plazma Kino", "label": "WEB / DESKTOP / ANDROID TV", "accent": "#5ce5b3", "rgb": "35,175,129", "logo": "plazma-original.svg", "mime": "image/svg+xml", "url": "https://plazmazerkalo.fun/", "lines": ["Фильмы, сериалы и аниме.", "Веб, приложения и Android TV."], "stack": [("nodedotjs", "Node.js"), ("react", "React"), ("kotlin", "Kotlin"), ("redis", "Redis")]},
    {"key": "krypta", "title": "Krypta", "label": "TELEGRAM / VPN", "accent": "#ecd393", "rgb": "176,144,68", "logo": "krypta-original.jpg", "mime": "image/jpeg", "url": "https://t.me/KryptaVpn_Robot", "lines": ["VPN-подписки в Telegram.", "Бот, мини-приложение и платежи."], "stack": [("typescript", "TypeScript"), ("telegram", "grammY"), ("react", "React"), ("sqlite", "SQLite")]},
]


def project_card(project, compact=False):
    w, h = (600, 329) if compact else (1200, 272)
    accent = project["accent"]
    left, top = (30, 39) if compact else (47, 43)
    title_y, description_y = (96, 146) if compact else (100, 151)
    logo_x, logo_y, logo_size = (451, 44, 88) if compact else (943, 62, 136)
    extra_defs = f'''<radialGradient id="brand-aura"><stop stop-color="rgb({project['rgb']})" stop-opacity=".23"/><stop offset="1" stop-color="rgb({project['rgb']})" stop-opacity="0"/></radialGradient>
<clipPath id="logo-crop"><rect x="{logo_x}" y="{logo_y}" width="{logo_size}" height="{logo_size}" rx="{logo_size * .24}"/></clipPath>'''
    body = f'<rect width="{w}" height="{h}" rx="28" fill="url(#panel)"/><ellipse class="breath" cx="{logo_x + logo_size / 2}" cy="{logo_y + logo_size / 2}" rx="{logo_size * 2}" ry="{h}" fill="url(#brand-aura)"/>'
    body += f'<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="28" fill="none" stroke="url(#edge)" stroke-width="1.5"/>'
    body += text(left, top, project["label"], 16 if compact else 18, accent, letter_spacing="1.7", font_weight="600")
    body += text(left, title_y, project["title"], 43 if compact else 51, font_weight="700", letter_spacing="-1.5")
    for i, line in enumerate(project["lines"]):
        body += text(left, description_y + i * 35, line, 25 if compact else 28, "#aebfd9")
    body += '<g class="float-slow">'
    for dx, dy, opacity in ((21, 22, ".13"), (10, 11, ".2")):
        body += f'<rect x="{logo_x - 14 + dx}" y="{logo_y - 14 + dy}" width="{logo_size + 28}" height="{logo_size + 28}" rx="24" fill="{accent}" fill-opacity=".04" stroke="{accent}" stroke-opacity="{opacity}"/>'
    body += f'<rect x="{logo_x - 14}" y="{logo_y - 14}" width="{logo_size + 28}" height="{logo_size + 28}" rx="24" fill="#0b1528" stroke="{accent}" stroke-opacity=".45"/>'
    if project["key"] == "pxost":
        body += f'<rect x="{logo_x}" y="{logo_y}" width="{logo_size}" height="{logo_size}" rx="22" fill="#5824ce"/><image x="{logo_x + 14}" y="{logo_y + 11}" width="{logo_size - 28}" height="{logo_size - 22}" xlink:href="{embedded(project["logo"], project["mime"])}"/>'
    else:
        body += f'<image x="{logo_x}" y="{logo_y}" width="{logo_size}" height="{logo_size}" clip-path="url(#logo-crop)" xlink:href="{embedded(project["logo"], project["mime"])}"/>'
    body += '</g>'
    stack_y, x = (238 if compact else 227), left
    for key, label in project["stack"]:
        size = 22 if compact else 25
        body += icon(key, x, stack_y - size + 3, size) + text(x + size + 7, stack_y, label, 18 if compact else 22, "#c3d1e8")
        x += len(label) * (10 if compact else 12) + size + (21 if compact else 34)
    if compact:
        body += text(left, 297, "Открыть проект", 23, accent, font_weight="500") + text(w - 31, 301, "↗", 32, accent, text_anchor="end")
    else:
        body += text(1056, 243, "↗", 36, accent)
    return document(w, h, project["title"], " ".join(project["lines"]) + " " + " · ".join(label for _, label in project["stack"]), body, extra_defs)


LANGUAGES = [("go", "Go"), ("python", "Python"), ("typescript", "TypeScript"), ("javascript", "JavaScript"), ("kotlin", "Kotlin"), ("swift", "Swift"), ("gnubash", "Bash"), ("godotengine", "GDScript")]
TOOLS = [("react", "React"), ("fastapi", "FastAPI"), ("postgresql", "PostgreSQL"), ("redis", "Redis"), ("docker", "Docker"), ("linux", "Linux")]


def stack(compact=False):
    w, h = (600, 967) if compact else (1200, 550)
    left = 30 if compact else 47
    body = f'<rect width="{w}" height="{h}" fill="url(#panel)"/><rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="28" fill="none" stroke="url(#edge)" stroke-width="1.5"/>'
    body += text(left, 46, "ЯЗЫКИ И ТЕХНОЛОГИИ", 18, "#83a5d0", letter_spacing="2", font_weight="600") + text(left, 101, "Рабочий стек", 43, font_weight="700", letter_spacing="-1.4")
    cols, tile_w, tile_h, gap = (2, 261, 134, 18) if compact else (4, 261, 115, 20)
    for i, (key, label) in enumerate(LANGUAGES):
        x, y = left + (i % cols) * (tile_w + gap), 135 + (i // cols) * (tile_h + gap)
        brand = "#" + ICONS[key]["hex"]
        body += f'<rect x="{x}" y="{y}" width="{tile_w}" height="{tile_h}" rx="17" fill="#0b1527" stroke="#243b59"/><path d="M{x + 21} {y + tile_h - 1}H{x + tile_w - 21}" stroke="{brand}" stroke-opacity=".36"/><g class="spark" style="animation-delay:-{i * .7}s"><circle cx="{x + tile_w - 20}" cy="{y + 20}" r="2.5" fill="{brand}"/></g>'
        body += icon(key, x + 22, y + (29 if compact else 26), 44) + text(x + 84, y + (60 if compact else 57), label, 26, "#e3edfb", font_weight="600")
        body += text(x + 84, y + (91 if compact else 86), "ЯЗЫК" if key != "godotengine" else "GODOT", 14, "#6989b0", letter_spacing="1.8")
    tools_top = 784 if compact else 452
    body += text(left, tools_top - 32, "ФРЕЙМВОРКИ / ДАННЫЕ / ИНФРАСТРУКТУРА", 16 if compact else 18, "#83a5d0", letter_spacing="1.1", font_weight="600")
    for i, (key, label) in enumerate(TOOLS):
        x = left + (i % 3) * 182 if compact else left + i * 185
        y = tools_top + (i // 3) * 71 if compact else tools_top
        body += icon(key, x, y, 27) + text(x + 35, y + 22, label, 20 if compact else 22, "#b6cae5")
    body += f'<path d="M{left} {h - 37}H{w - left}" stroke="#47638b" stroke-opacity=".24"/>'
    return document(w, h, "Рабочий стек Xuisuki", "Языки: " + ", ".join(label for _, label in LANGUAGES) + ". Технологии: " + ", ".join(label for _, label in TOOLS) + ".", body)


def write_asset(name, contents):
    (ASSETS / name).write_text(contents, encoding="utf-8")
    version = hashlib.sha256(contents.encode()).hexdigest()[:12]
    print(f"built: assets/{name}")
    return f"assets/{name}?v={version}"


def picture(prefix, alt, urls):
    return f'''<picture>
  <source media="(max-width: 1000px)" srcset="{urls[prefix + '-compact']}">
  <img alt="{escape(alt, quote=True)}" src="{urls[prefix]}" width="100%">
</picture>'''


def main():
    if len(sys.argv) > 1 and sys.argv[1:] != ["art"]:
        raise SystemExit("Usage: build.py [art]")
    urls = {}
    for compact in (False, True):
        suffix = "-compact" if compact else ""
        urls["infinity" + suffix] = write_asset("infinity" + suffix + ".svg", hero(compact))
        for project in PROJECTS:
            key = "project-" + project["key"] + suffix
            urls[key] = write_asset(key + ".svg", project_card(project, compact))
        urls["technologies" + suffix] = write_asset("technologies" + suffix + ".svg", stack(compact))
    readme = picture("infinity", "Xuisuki / prodX — серверные системы, Telegram-сервисы и приложения. Infinity / Сатору Годжо.", urls) + "\n\n"
    for project in PROJECTS:
        readme += f'<a href="{project["url"]}">\n' + picture("project-" + project["key"], project["title"] + " — " + " ".join(project["lines"]), urls) + "\n</a>\n\n"
    readme += picture("technologies", "Языки: Go, Python, TypeScript, JavaScript, Kotlin, Swift, Bash, GDScript. React, FastAPI, PostgreSQL, Redis, Docker, Linux.", urls)
    readme += '''

<details>
<summary>Проекты и технологии — текстовая версия</summary>

**Xuisuki / prodX** — серверные системы, Telegram-сервисы и приложения.

- **[pxost](https://t.me/pxostbot)** — редактор и отложенный постинг в Telegram. Контент-план и ИИ для каналов. Python · FastAPI · React · PostgreSQL.
- **[Plazma Kino](https://plazmazerkalo.fun/)** — фильмы, сериалы и аниме. Веб, приложения и Android TV. Node.js · React · Kotlin · Redis.
- **[Krypta](https://t.me/KryptaVpn_Robot)** — VPN-подписки внутри Telegram. Бот, мини-приложение и платежи. TypeScript · grammY · React · SQLite.

Go · Python · TypeScript · JavaScript · Kotlin · Swift · Bash · GDScript.

React · FastAPI · PostgreSQL · Redis · Docker · Linux.

</details>

<p align="right"><a href="https://prodx.pro">prodx.pro ↗</a></p>
'''
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
