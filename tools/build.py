#!/usr/bin/env python3
"""Генератор графики для профиля Xuisuki.

Вся картинка профиля рисуется здесь и лежит в репозитории: ни одного стороннего
сервиса-генератора, который однажды перестанет отвечать. Каждый файл собирается
дважды — под тёмную и светлую тему GitHub, README выбирает нужный через <picture>.
"""

import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,'Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,'SF Mono','JetBrains Mono','Cascadia Code',Menlo,Consolas,monospace"

THEMES = {
    "dark": dict(
        bg="#0d1117", panel="#0f141b", panel2="#131a22", border="#242c37",
        text="#e6edf3", muted="#8b949e", faint="#30363d",
        accent="#cfd8e6", krypta="#f5c542", plazma="#e0559b", grid="#1b222c", net="#39424f",
    ),
    "light": dict(
        bg="#ffffff", panel="#f7f9fb", panel2="#eef2f6", border="#d6dee6",
        text="#1f2328", muted="#59636e", faint="#d1d9e0",
        accent="#4b5563", krypta="#9a6b06", plazma="#b02870", grid="#e8edf2", net="#c2ccd7",
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


# ---------------------------------------------------------------- шапка

def header(t):
    """Имя, род занятий и вращающийся глобус узлов справа."""
    cx, cy, R = 742, 125, 92

    # меридианы: сжимающийся и разжимающийся эллипс даёт вращение шара
    meridians = "".join(
        f'<ellipse cx="{cx}" cy="{cy}" rx="{R}" ry="{R}" fill="none" '
        f'stroke="{t["net"]}" stroke-width="1">'
        f'<animate attributeName="rx" values="{R};0;{R}" dur="18s" '
        f'begin="-{i * 3:.1f}s" repeatCount="indefinite" '
        f'calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" keyTimes="0;0.5;1"/>'
        f'</ellipse>'
        for i in range(6)
    )
    parallels = "".join(
        f'<ellipse cx="{cx}" cy="{cy + off}" rx="{(R * R - off * off) ** .5:.1f}" '
        f'ry="{abs(off) * .30 + 5:.1f}" fill="none" stroke="{t["net"]}" stroke-width="1" opacity=".8"/>'
        for off in (-58, -30, 0, 30, 58)
    )

    # узлы платформы на поверхности шара
    pts = [(-52, -46), (18, -62), (66, -20), (-14, -8), (44, 34), (-40, 30), (6, 62)]
    pins = "".join(
        f'<g class="pin" style="animation-delay:{i * .28:.2f}s">'
        f'<circle cx="{cx + x}" cy="{cy + y}" r="7" fill="{t["accent"]}" opacity=".14"/>'
        f'<circle cx="{cx + x}" cy="{cy + y}" r="2.6" fill="{t["accent"]}"/></g>'
        for i, (x, y) in enumerate(pts)
    )

    # маршруты между узлами: дуга + бегущий по ней пакет
    routes = []
    for i, (a, b) in enumerate(((0, 4), (1, 5), (3, 6))):
        (x1, y1), (x2, y2) = pts[a], pts[b]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        d = f"M{cx + x1},{cy + y1} Q{cx + mx * 1.55:.0f},{cy + my * 1.55 - 26:.0f} {cx + x2},{cy + y2}"
        routes.append(
            f'<path d="{d}" fill="none" stroke="{t["accent"]}" stroke-width="1" opacity=".28"/>'
            f'<circle r="2.4" fill="{t["accent"]}">'
            f'<animate attributeName="opacity" values="0;1;1;0" dur="3.4s" begin="{i * 1.1:.1f}s" repeatCount="indefinite"/>'
            f'<animateMotion dur="3.4s" begin="{i * 1.1:.1f}s" repeatCount="indefinite" path="{d}"/></circle>'
        )
    routes = "".join(routes)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 250" width="900" height="250" role="img" aria-label="prodX — infrastructure engineer">
<defs>
  <radialGradient id="glow" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="{t['accent']}" stop-opacity=".18"/>
    <stop offset="70%" stop-color="{t['accent']}" stop-opacity=".04"/>
    <stop offset="100%" stop-color="{t['accent']}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="shade" cx="34%" cy="30%" r="78%">
    <stop offset="0%" stop-color="{t['panel2']}" stop-opacity=".9"/>
    <stop offset="100%" stop-color="{t['panel']}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse">
    <path d="M26 0H0v26" fill="none" stroke="{t['grid']}" stroke-width="1"/>
  </pattern>
  <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{t['accent']}" stop-opacity="0"/>
    <stop offset="50%" stop-color="{t['accent']}" stop-opacity=".95"/>
    <stop offset="100%" stop-color="{t['accent']}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="{t['panel']}"/>
    <stop offset="100%" stop-color="{t['panel']}" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="card"><rect x="1" y="1" width="898" height="248" rx="16"/></clipPath>
</defs>
<style>
  .t {{ font-family:{SANS}; }}
  .m {{ font-family:{MONO}; }}
  .rise {{ opacity:0; animation:rise .9s cubic-bezier(.2,.7,.3,1) forwards; }}
  @keyframes rise {{ from {{ opacity:0; transform:translateY(12px); }} to {{ opacity:1; transform:none; }} }}
  .pin {{ animation:breathe 3.6s ease-in-out infinite; }}
  @keyframes breathe {{ 0%,100% {{ opacity:.5; }} 50% {{ opacity:1; }} }}
  .globe {{ opacity:0; animation:fadein 1.4s ease .2s forwards; }}
  @keyframes fadein {{ to {{ opacity:1; }} }}
  .bar {{ animation:slide 4s ease-in-out infinite; }}
  @keyframes slide {{ 0%,100% {{ transform:translateX(0); }} 50% {{ transform:translateX(146px); }} }}
{REDUCED}
</style>

<g clip-path="url(#card)">
  <rect width="900" height="250" fill="{t['panel']}"/>
  <rect width="900" height="250" fill="url(#grid)"/>
  <circle cx="{cx}" cy="{cy}" r="150" fill="url(#glow)"/>

  <g class="globe">
    <circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#shade)" stroke="{t['net']}" stroke-width="1.2"/>
    {parallels}
    {meridians}
    {routes}
    {pins}
  </g>

  <rect x="0" y="0" width="470" height="250" fill="url(#fade)"/>

  <g class="rise" style="animation-delay:.05s">
    <text class="m" x="56" y="64" fill="{t['muted']}" font-size="11.5" letter-spacing="3.4">INFRASTRUCTURE · PRIVACY · AUTOMATION</text>
  </g>
  <g class="rise" style="animation-delay:.18s">
    <text class="t" x="54" y="132" fill="{t['text']}" font-size="62" font-weight="700" letter-spacing="-1.6">prodX</text>
  </g>
  <g class="rise" style="animation-delay:.3s">
    <rect x="56" y="150" width="118" height="2" rx="1" fill="{t['faint']}"/>
    <rect class="bar" x="56" y="150" width="40" height="2" rx="1" fill="url(#sweep)"/>
  </g>
  <g class="rise" style="animation-delay:.42s">
    <text class="t" x="56" y="185" fill="{t['text']}" font-size="17" opacity=".93">I build the boring parts that have to keep working</text>
    <text class="t" x="56" y="210" fill="{t['muted']}" font-size="14.5">VPN platform · Telegram commerce · streaming · self-hosted automation</text>
  </g>
</g>
<rect x=".5" y=".5" width="899" height="249" rx="16" fill="none" stroke="{t['border']}"/>
</svg>
"""

# ---------------------------------------------------------------- карточки

def chips(t, items, x, y, accent, size=11.5):
    """Ряд подписей-капсул: ширина считается по длине строки моноширинным шагом."""
    out, cur = [], x
    for i, s in enumerate(items):
        w = len(s) * 6.55 + 20
        out.append(
            f'<g class="chip" style="animation-delay:{.45 + i * .07:.2f}s">'
            f'<rect x="{cur:.0f}" y="{y}" width="{w:.0f}" height="23" rx="11.5" '
            f'fill="{t["panel2"]}" stroke="{t["border"]}"/>'
            f'<text class="m" x="{cur + w / 2:.0f}" y="{y + 15.5}" fill="{t["muted"]}" '
            f'font-size="{size}" text-anchor="middle">{s}</text></g>'
        )
        cur += w + 7
    return "".join(out)


def card(t, *, w, h, accent, name, url, tag, desc, stack, art, art_x):
    """Общий каркас карточки проекта: заголовок, ссылка, описание, стек, иллюстрация."""
    lines = "".join(
        f'<text class="s" x="30" y="{104 + i * 21}" fill="{t["muted"]}" font-size="13.5" '
        f'style="animation-delay:{.3 + i * .06:.2f}s">{s}</text>'
        for i, s in enumerate(desc)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{name} — {tag}">
<defs>
  <radialGradient id="au" cx="88%" cy="20%" r="70%">
    <stop offset="0%" stop-color="{accent}" stop-opacity=".16"/>
    <stop offset="100%" stop-color="{accent}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="{accent}" stop-opacity=".95"/>
    <stop offset="100%" stop-color="{accent}" stop-opacity=".15"/>
  </linearGradient>
  <clipPath id="cc"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14"/></clipPath>
</defs>
<style>
  .s {{ font-family:{SANS}; opacity:0; animation:up .7s cubic-bezier(.2,.7,.3,1) forwards; }}
  .m {{ font-family:{MONO}; }}
  .chip {{ opacity:0; animation:up .6s ease forwards; }}
  @keyframes up {{ from {{ opacity:0; transform:translateY(8px); }} to {{ opacity:1; transform:none; }} }}
{REDUCED}
</style>
<g clip-path="url(#cc)">
  <rect width="{w}" height="{h}" fill="{t['panel']}"/>
  <rect width="{w}" height="{h}" fill="url(#au)"/>
  <rect x="0" y="0" width="3" height="{h}" fill="url(#edge)"/>
  <g transform="translate({art_x},0)">{art}</g>
  <text class="s" x="30" y="47" fill="{t['text']}" font-size="23" font-weight="700" letter-spacing="-.4">{name}</text>
  <text class="m s" x="30" y="72" fill="{accent}" font-size="12" letter-spacing=".6" style="animation-delay:.18s">{url}</text>
  {lines}
  {chips(t, stack, 30, h - 46, accent)}
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="none" stroke="{t['border']}"/>
</svg>
"""


def art_traffic(t, a):
    """Живой график трафика: площадь, бегущий гребень и столбики нагрузки."""
    pts = [0, 14, 8, 26, 20, 42, 34, 52, 40, 62, 55, 74, 66, 88, 78, 96]
    step = 260 / (len(pts) - 1)
    path = " ".join(
        f"{'M' if i == 0 else 'L'}{i * step:.1f},{100 - v * .82:.1f}" for i, v in enumerate(pts)
    )
    bars = "".join(
        f'<rect x="{i * 15}" y="{118 - (12 + (i * 7) % 30)}" width="6" height="{12 + (i * 7) % 30}" rx="2" '
        f'fill="{a}" opacity=".22"><animate attributeName="height" '
        f'values="{12 + (i * 7) % 30};{6 + (i * 11) % 34};{12 + (i * 7) % 30}" dur="{2.4 + (i % 5) * .3:.1f}s" '
        f'repeatCount="indefinite"/><animate attributeName="y" '
        f'values="{118 - (12 + (i * 7) % 30)};{118 - (6 + (i * 11) % 34)};{118 - (12 + (i * 7) % 30)}" '
        f'dur="{2.4 + (i % 5) * .3:.1f}s" repeatCount="indefinite"/></rect>'
        for i in range(17)
    )
    return f"""<g transform="translate(0,26)">
  <path d="{path} L260,118 L0,118 Z" fill="{a}" opacity=".07"/>
  <path d="{path}" fill="none" stroke="{a}" stroke-width="1.8" stroke-linecap="round" opacity=".85"
        stroke-dasharray="420" stroke-dashoffset="420">
    <animate attributeName="stroke-dashoffset" values="420;0" dur="1.6s" fill="freeze"/>
  </path>
  <g opacity=".9">{bars}</g>
  <circle r="3.6" fill="{a}"><animateMotion dur="4.4s" repeatCount="indefinite" path="{path}"/></circle>
</g>"""


def art_bot(t, a):
    """Мини-приложение в Telegram: пузыри сообщений и подсветка кнопки."""
    bubbles = "".join(
        f'<rect x="{18 if i % 2 == 0 else 46}" y="{26 + i * 24}" width="{72 - (i % 2) * 16}" height="15" rx="7.5" '
        f'fill="{a if i % 2 else t["border"]}" opacity="0">'
        f'<animate attributeName="opacity" values="0;{.85 if i % 2 else .55};{.85 if i % 2 else .55};0" '
        f'dur="6s" begin="{i * .5:.1f}s" repeatCount="indefinite"/></rect>'
        for i in range(4)
    )
    return f"""<g transform="translate(0,30)">
  <rect x="4" y="4" width="122" height="146" rx="18" fill="{t['panel2']}" stroke="{t['border']}"/>
  <rect x="49" y="13" width="32" height="5" rx="2.5" fill="{t['border']}"/>
  <g transform="translate(0,4)">{bubbles}</g>
  <rect x="18" y="124" width="94" height="20" rx="10" fill="{a}" opacity=".9"/>
  <rect x="18" y="124" width="94" height="20" rx="10" fill="none" stroke="{a}">
    <animate attributeName="opacity" values=".2;1;.2" dur="2.8s" repeatCount="indefinite"/>
  </rect>
  <circle cx="98" cy="34" r="14" fill="none" stroke="{a}" stroke-width="1" opacity=".35">
    <animate attributeName="r" values="10;19;10" dur="3.4s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".4;0;.4" dur="3.4s" repeatCount="indefinite"/>
  </circle>
</g>"""


def art_film(t, a):
    """Киноплёнка: перфорация уезжает, кадр за кадром загорается."""
    perf = "".join(
        f'<rect x="{8 + i * 22}" y="0" width="12" height="9" rx="2" fill="{t["border"]}"/>'
        f'<rect x="{8 + i * 22}" y="99" width="12" height="9" rx="2" fill="{t["border"]}"/>'
        for i in range(9)
    )
    frames = "".join(
        f'<rect x="{10 + i * 44}" y="18" width="38" height="72" rx="4" fill="{a}" opacity=".12">'
        f'<animate attributeName="opacity" values=".1;.42;.1" dur="3.2s" begin="{i * .4:.1f}s" repeatCount="indefinite"/></rect>'
        for i in range(4)
    )
    return f"""<g transform="translate(0,34)">
  <rect x="0" y="0" width="176" height="108" rx="6" fill="{t['panel2']}" stroke="{t['border']}"/>
  <g>
    {perf}{frames}
    <animateTransform attributeName="transform" type="translate" values="0 0;-22 0" dur="1.9s" repeatCount="indefinite"/>
  </g>
  <circle cx="88" cy="54" r="21" fill="{t['panel']}" opacity=".92"/>
  <circle cx="88" cy="54" r="21" fill="none" stroke="{a}" stroke-width="1.4" opacity=".8"/>
  <path d="M83,45 L99,54 L83,63 Z" fill="{a}"/>
  <circle cx="88" cy="54" r="21" fill="none" stroke="{a}" stroke-width="1">
    <animate attributeName="r" values="21;34;21" dur="3.6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values=".55;0;.55" dur="3.6s" repeatCount="indefinite"/>
  </circle>
</g>"""


# ---------------------------------------------------------------- стек

STACK = [
    ("Core", ["Go", "TypeScript", "Python", "Node.js"]),
    ("Data", ["PostgreSQL", "Redis", "SQLite", "ClickHouse"]),
    ("Infra", ["Docker", "Caddy", "systemd", "Prometheus", "Grafana"]),
    ("Product", ["Next.js", "React", "Tailwind", "grammY", "FastAPI"]),
]


def stack(t):
    a = t["accent"]
    rows = []
    y = 40
    for r, (group, items) in enumerate(STACK):
        rows.append(
            f'<text class="m" x="30" y="{y + 16}" fill="{t["muted"]}" font-size="11" '
            f'letter-spacing="2.2">{group.upper()}</text>'
        )
        x = 122
        for i, s in enumerate(items):
            w = len(s) * 6.9 + 26
            rows.append(
                f'<g class="chip" style="animation-delay:{r * .12 + i * .05:.2f}s">'
                f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{t["panel2"]}" stroke="{t["border"]}"/>'
                f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="none" stroke="{a}" opacity="0">'
                f'<animate attributeName="opacity" values="0;.55;0" dur="5.5s" '
                f'begin="{(r * 4 + i) * .32:.2f}s" repeatCount="indefinite"/></rect>'
                f'<text class="m" x="{x + w / 2:.0f}" y="{y + 17}" fill="{t["text"]}" font-size="11.8" '
                f'text-anchor="middle" opacity=".88">{s}</text></g>'
            )
            x += w + 8
        y += 38
    body = "".join(rows)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {y + 16}" width="900" height="{y + 16}" role="img" aria-label="Tech stack">
<style>
  .t {{ font-family:{SANS}; }} .m {{ font-family:{MONO}; }}
  .chip {{ opacity:0; animation:up .55s ease forwards; }}
  @keyframes up {{ from {{ opacity:0; transform:translateY(7px); }} to {{ opacity:1; transform:none; }} }}
{REDUCED}
</style>
<rect x=".5" y=".5" width="899" height="{y + 15}" rx="14" fill="{t['panel']}" stroke="{t['border']}"/>
{body}
</svg>
"""


def divider(t, label):
    """Тонкая подпись раздела: линия и моноширинная метка."""
    w = len(label) * 8.2 + 30
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 30" width="900" height="30" role="img" aria-label="{label}">
<style>
  .m {{ font-family:{MONO}; }}
  .ln {{ stroke-dasharray:900; stroke-dashoffset:900; animation:draw 1.8s ease .2s forwards; }}
  @keyframes draw {{ to {{ stroke-dashoffset:0; }} }}
{REDUCED}
</style>
<text class="m" x="0" y="19" fill="{t['muted']}" font-size="12" letter-spacing="3.2">{label}</text>
<line class="ln" x1="{w:.0f}" y1="14" x2="900" y2="14" stroke="{t['border']}" stroke-width="1"/>
<circle cx="898" cy="14" r="2" fill="{t['accent']}" opacity=".7"/>
</svg>
"""


# ---------------------------------------------------------------- статистика

GQL = """
query($login:String!){
  user(login:$login){
    followers{ totalCount }
    repositories(ownerAffiliations:OWNER, privacy:PUBLIC){ totalCount }
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


def fetch(login, token):
    """Публичная картина профиля — ровно то, что видит посторонний."""
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


def stats(t, u):
    a = t["accent"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    cur, best = streaks(weeks)
    peak = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=0) or 1

    metrics = [
        (f'{cal["totalContributions"]}', "CONTRIBUTIONS · 12 MONTHS"),
        (f'{u["contributionsCollection"]["totalCommitContributions"]}', "COMMITS"),
        (f"{cur}", "CURRENT STREAK · DAYS"),
        (f"{best}", "LONGEST STREAK · DAYS"),
    ]
    cells, mlabels = [], []
    cw, gap, x0, y0 = 13, 2.8, 30, 138
    seen = set()
    for wi, w in enumerate(weeks[-53:]):
        for d in w["contributionDays"]:
            di = int(__import__("datetime").date.fromisoformat(d["date"]).strftime("%w"))
            lvl = 0 if not d["contributionCount"] else min(4, 1 + int(3 * d["contributionCount"] / peak))
            op = ["1", ".34", ".56", ".78", "1"][lvl]
            fill = a if lvl else t["grid"]
            cells.append(
                f'<rect x="{x0 + wi * (cw + gap):.1f}" y="{y0 + di * (cw + gap):.1f}" width="{cw}" height="{cw}" '
                f'rx="3" fill="{fill}" opacity="{op}" class="cell" style="animation-delay:{wi * .011:.3f}s"/>'
            )
        first = w["contributionDays"][0]["date"]
        mon = first[:7]
        if mon not in seen and first[8:10] <= "07":
            seen.add(mon)
            label = __import__("datetime").date.fromisoformat(first).strftime("%b")
            mlabels.append(
                f'<text class="m" x="{x0 + wi * (cw + gap):.1f}" y="{y0 - 10}" fill="{t["muted"]}" '
                f'font-size="10.5">{label}</text>'
            )

    mrow = "".join(
        f'<g class="s" style="animation-delay:{i * .09:.2f}s">'
        f'<text class="t" x="{30 + i * 218}" y="62" fill="{t["text"]}" font-size="34" font-weight="700" '
        f'letter-spacing="-1">{v}</text>'
        f'<text class="m" x="{30 + i * 218}" y="84" fill="{t["muted"]}" font-size="10" letter-spacing="1.6">{k}</text></g>'
        for i, (v, k) in enumerate(metrics)
    )
    h = y0 + 7 * (cw + gap) + 44
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {h:.0f}" width="900" height="{h:.0f}" role="img" aria-label="GitHub activity">
<style>
  .t {{ font-family:{SANS}; }} .m {{ font-family:{MONO}; }}
  .s {{ opacity:0; animation:up .7s cubic-bezier(.2,.7,.3,1) forwards; }}
  @keyframes up {{ from {{ opacity:0; transform:translateY(9px); }} to {{ opacity:1; transform:none; }} }}
  .cell {{ animation:pop .55s cubic-bezier(.2,.7,.3,1) backwards;
           transform-box:fill-box; transform-origin:center; }}
  @keyframes pop {{ from {{ opacity:0; transform:scale(.35); }} }}
{REDUCED}
</style>
<rect x=".5" y=".5" width="899" height="{h - 1:.0f}" rx="14" fill="{t['panel']}" stroke="{t['border']}"/>
{mrow}
<g class="s" style="animation-delay:.5s">
  <text class="m" x="726" y="{y0 + 7 * (cw + gap) + 16:.0f}" fill="{t['muted']}" font-size="10">less</text>
  <rect x="759" y="{y0 + 7 * (cw + gap) + 7:.0f}" width="9" height="9" rx="2" fill="{t['grid']}"/>
  <rect x="771" y="{y0 + 7 * (cw + gap) + 7:.0f}" width="9" height="9" rx="2" fill="{a}" opacity=".34"/>
  <rect x="783" y="{y0 + 7 * (cw + gap) + 7:.0f}" width="9" height="9" rx="2" fill="{a}" opacity=".56"/>
  <rect x="795" y="{y0 + 7 * (cw + gap) + 7:.0f}" width="9" height="9" rx="2" fill="{a}" opacity=".78"/>
  <rect x="807" y="{y0 + 7 * (cw + gap) + 7:.0f}" width="9" height="9" rx="2" fill="{a}"/>
  <text class="m" x="824" y="{y0 + 7 * (cw + gap) + 16:.0f}" fill="{t['muted']}" font-size="10">more</text>
</g>
<line x1="30" y1="106" x2="870" y2="106" stroke="{t['border']}"/>
{"".join(mlabels)}
{"".join(cells)}
</svg>
"""


# ---------------------------------------------------------------- сборка

PROJECTS = [
    dict(key="prodx", accent="accent", name="prodX", url="prodx.pro", tag="VPN platform",
         desc=["Multi-protocol VPN platform: own node fleet, subscription delivery,",
               "billing, resellers and per-brand white-label panels."],
         stack=["Go", "Next.js", "PostgreSQL", "Xray", "sing-box"],
         art="traffic", w=900, h=196, art_x=600),
    dict(key="krypta", accent="krypta", name="Krypta", url="t.me/KryptaVpn_Robot", tag="Telegram commerce",
         desc=["Telegram bot and Mini App on top of prodX:", "checkout, referrals, AI support."],
         stack=["TypeScript", "grammY", "SQLite"],
         art="bot", w=440, h=214, art_x=290),
    dict(key="plazma", accent="plazma", name="Plazma Kino", url="plazmakino.ru", tag="Streaming",
         desc=["Streaming service: own player, catalog,", "progress sync and mirror delivery."],
         stack=["Node.js", "React", "Redis"],
         art="film", w=440, h=214, art_x=238),
]

ARTS = {"traffic": art_traffic, "bot": art_bot, "film": art_film}


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
            write(f"stack-{name}.svg", stack(t))
            for label in ("PROJECTS", "STACK", "ACTIVITY", "OPEN SOURCE"):
                write(f"div-{label.split()[0].lower()}-{name}.svg", divider(t, label))
            for p in PROJECTS:
                art = ARTS[p["art"]](t, t[p["accent"]])
                write(f"card-{p['key']}-{name}.svg", card(
                    t, w=p["w"], h=p["h"], accent=t[p["accent"]], name=p["name"], url=p["url"],
                    tag=p["tag"], desc=p["desc"], stack=p["stack"], art=art, art_x=p["art_x"]))
        if user:
            write(f"stats-{name}.svg", stats(t, user))
    print("готово:", sorted(os.listdir(ASSETS)))


if __name__ == "__main__":
    main()
