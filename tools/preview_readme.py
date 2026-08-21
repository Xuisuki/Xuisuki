#!/usr/bin/env python3
"""Снимает README ровно так, как его собрал рендерер GitHub."""
import os, asyncio
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "/tmp/claude-0/-root/aeefff89-37a4-48b0-8b34-e28791677e11/scratchpad"
BODY = open(os.path.join(OUT, "readme.html")).read()

SHELL = """<!doctype html><meta charset=utf-8><base href="file://%s/">
<style>
 :root{color-scheme:%s}
 body{margin:0;background:%s;color:%s;
      font:16px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',Noto Sans,Helvetica,Arial,sans-serif}
 .box{max-width:896px;margin:0 auto;padding:32px 16px}
 img{max-width:100%%;box-sizing:content-box}
 a{color:%s;text-decoration:none} p{margin:0 0 16px}
 sub{font-size:12px;color:%s}
</style>
<div class=box>%s</div>"""


async def main():
    for theme, bg, fg, link, muted in (
        ("dark", "#0d1117", "#e6edf3", "#4493f8", "#8b949e"),
        ("light", "#ffffff", "#1f2328", "#0969da", "#59636e"),
    ):
        path = os.path.join(OUT, f"readme-{theme}.html")
        open(path, "w").write(SHELL % (ROOT, theme, bg, fg, link, muted, BODY))
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await b.new_page(viewport={"width": 1000, "height": 900},
                                  device_scale_factor=2, color_scheme=theme)
            await pg.goto("file://" + path)
            await pg.wait_for_timeout(2400)
            await pg.screenshot(path=os.path.join(OUT, f"readme-{theme}.png"), full_page=True)
            # в ряд ли встали две половинные карточки
            box = await pg.evaluate("""() => {
              const im=[...document.querySelectorAll('img')].filter(i=>i.getAttribute('width')==='49%');
              return im.length===2 ? {y1:im[0].getBoundingClientRect().top, y2:im[1].getBoundingClientRect().top,
                                      w1:im[0].getBoundingClientRect().width} : null; }""")
            print(theme, "две карточки в ряд:", box and abs(box["y1"] - box["y2"]) < 4, box)
            await b.close()

asyncio.run(main())
