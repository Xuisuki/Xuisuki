#!/usr/bin/env python3
"""Build the profile's monochrome motion wordmark, without network access.

Project descriptions stay in README.md and use GitHub's native typography.
Artwork is transparent, animated, and has separate light and dark variants.
Reduced motion keeps a fully readable static composition.
Cache keys depend on content, so unchanged builds do not create daily commits.
"""

import hashlib
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
THEMES = {
    "light": {"text": "#1f2328", "muted": "#59636e", "rule": "#d1d9e0"},
    "dark": {"text": "#e6edf3", "muted": "#9198a1", "rule": "#3d444d"},
}


def header(theme):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="152" viewBox="0 0 900 152" role="img" aria-labelledby="title desc">
  <title id="title">Xuisuki / prodX</title>
  <desc id="desc">Xuisuki / prodX. Selected work: pxost, Krypta, Plazma Kino. Gentle typography and line animation.</desc>
  <defs>
    <clipPath id="name-window"><path d="M0 12H680V119H0Z"/></clipPath>
    <clipPath id="work-window"><path d="M690 79H900V119H690Z"/></clipPath>
    <clipPath id="line-window"><path d="M0 141H900V147H0Z"/></clipPath>
  </defs>
  <style>
    .name {{ animation: name-in 1.2s cubic-bezier(.16,1,.3,1) both; }}
    .signature {{ animation: signature-in 1s ease .45s both; }}
    .rule {{ stroke-dasharray: 900; animation: rule-in 1.5s cubic-bezier(.16,1,.3,1) .15s both; }}
    .scan {{ animation: scan 8s cubic-bezier(.45,0,.55,1) 1.6s infinite both; }}
    .work {{ opacity: 0; animation: work-cycle 12s cubic-bezier(.22,.61,.36,1) infinite; }}
    .work-1 {{ animation-delay: -12s; }}
    .work-2 {{ animation-delay: -8s; }}
    .work-3 {{ animation-delay: -4s; }}
    @keyframes name-in {{
      from {{ opacity: 0; transform: translateY(42px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes signature-in {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    @keyframes rule-in {{ from {{ stroke-dashoffset: 900; }} to {{ stroke-dashoffset: 0; }} }}
    @keyframes scan {{
      0% {{ opacity: 0; transform: translateX(-110px); }}
      12% {{ opacity: .55; }}
      85% {{ opacity: .55; }}
      100% {{ opacity: 0; transform: translateX(950px); }}
    }}
    @keyframes work-cycle {{
      0% {{ opacity: 0; transform: translateY(13px); }}
      5%, 27% {{ opacity: 1; transform: translateY(0); }}
      33%, 100% {{ opacity: 0; transform: translateY(-13px); }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .name, .signature, .rule {{ animation: none; opacity: 1; transform: none; stroke-dashoffset: 0; }}
      .scan {{ display: none; }}
      .work {{ animation: none; opacity: 0; transform: none; }}
      .work-1 {{ opacity: 1; }}
    }}
  </style>
  <g clip-path="url(#name-window)">
    <g class="name"><text x="0" y="106" fill="{theme['text']}" font-family="Georgia, 'Times New Roman', serif" font-size="94" letter-spacing="-4">Xuisuki</text></g>
  </g>
  <text class="signature" x="898" y="52" fill="{theme['muted']}" font-family="ui-monospace, 'SF Mono', Consolas, monospace" font-size="17" text-anchor="end">prodX</text>
  <g clip-path="url(#work-window)" fill="{theme['text']}" font-family="ui-monospace, 'SF Mono', Consolas, monospace" font-size="20" text-anchor="end">
    <g class="work work-1"><text x="898" y="106">pxost</text></g>
    <g class="work work-2"><text x="898" y="106">Krypta</text></g>
    <g class="work work-3"><text x="898" y="106">Plazma Kino</text></g>
  </g>
  <path class="rule" d="M0 143.5H900" fill="none" stroke="{theme['rule']}"/>
  <g clip-path="url(#line-window)">
    <path class="scan" d="M0 143.5H100" fill="none" stroke="{theme['text']}" stroke-width="1.5" stroke-linecap="round"/>
  </g>
</svg>
'''


def main():
    # Keep the previous `build.py art` invocation working for server tooling.
    if len(sys.argv) > 1 and sys.argv[1:] != ["art"]:
        raise SystemExit("Usage: build.py [art]")
    ASSETS.mkdir(exist_ok=True)
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    for name, theme in THEMES.items():
        svg = header(theme)
        path = ASSETS / f"header-{name}.svg"
        path.write_text(svg, encoding="utf-8")
        version = hashlib.sha256(svg.encode()).hexdigest()[:12]
        pattern = rf"assets/header-{name}\.svg(?:\?v=[A-Za-z0-9_-]+)?"
        readme, count = re.subn(pattern, f"assets/header-{name}.svg?v={version}", readme)
        if count != 1:
            raise RuntimeError(f"Expected one {name} header reference in README, found {count}")
        print(f"built: {path.relative_to(ROOT)}")
    readme_path.write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
