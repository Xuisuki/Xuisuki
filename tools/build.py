#!/usr/bin/env python3
"""Build the profile's monochrome wordmark, without network access.

Project descriptions stay in README.md and use GitHub's native typography.
Artwork is transparent and has separate light and dark theme variants.
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
  <desc id="desc">A monochrome typographic wordmark for the Xuisuki profile.</desc>
  <text x="0" y="106" fill="{theme['text']}" font-family="Georgia, 'Times New Roman', serif" font-size="94" letter-spacing="-4">Xuisuki</text>
  <text x="898" y="106" fill="{theme['muted']}" font-family="ui-monospace, 'SF Mono', Consolas, monospace" font-size="19" text-anchor="end">prodX</text>
  <path d="M0 143.5H900" fill="none" stroke="{theme['rule']}"/>
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
