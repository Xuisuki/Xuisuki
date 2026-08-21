#!/usr/bin/env python3
"""Собирает превью README в браузере и снимает его. Смотреть глазами до публикации."""
import os, sys, asyncio
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "/tmp/claude-0/-root/aeefff89-37a4-48b0-8b34-e28791677e11/scratchpad"

# как блоки лежат в README: строка = ряд картинок
LAYOUT = [["header"], ["card-prodx"], ["card-krypta", "card-plazma"], ["stack"], ["stats"]]

PAGE = """<!doctype html><meta charset=utf-8>
<style>
 body{margin:0;padding:24px;background:%s;font-family:-apple-system,'Segoe UI',Roboto,sans-serif}
 .w{max-width:896px;margin:0 auto;display:flex;flex-direction:column;gap:16px}
 .row{display:flex;gap:16px} .row img{flex:1 1 0;min-width:0;max-width:100%%;display:block}
</style>
<div class=w>%s</div>"""


async def main():
    for theme in ("dark", "light"):
        rows = "".join(
            "<div class=row>" + "".join(
                f'<img src="{ROOT}/assets/{n}-{theme}.svg">' for n in row
                if os.path.exists(f"{ROOT}/assets/{n}-{theme}.svg")
            ) + "</div>"
            for row in LAYOUT
        )
        path = os.path.join(OUT, f"page-{theme}.html")
        open(path, "w").write(PAGE % ("#0d1117" if theme == "dark" else "#ffffff", rows))
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await b.new_page(viewport={"width": 960, "height": 900}, device_scale_factor=2)
            await pg.goto("file://" + path)
            await pg.wait_for_timeout(2200)
            await pg.screenshot(path=os.path.join(OUT, f"preview-{theme}.png"), full_page=True)
            await b.close()
    print("ok:", OUT)

asyncio.run(main())
