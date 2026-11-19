"""Auditoría C: con el service worker activo, /proyecto y /2d (sin barra final) deben abrir su página, no la portada.
El servidor (como GitHub Pages) responde 301 → /proyecto/; el service worker tiene que dejar pasar la redirección.
Uso: python3 tests/sw-redirect-browser-check.py http://127.0.0.1:8842/   (Chrome real, service worker activo; no publica nada)"""
import asyncio, json, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1]
async def main():
    out = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 412, 'height': 915}, is_mobile=True, has_touch=True)
        pg = await ctx.new_page()
        await pg.goto(BASE + 'index.html?intro=0', wait_until='load')
        await pg.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.controller || (location.reload(), false)", timeout=60000, polling=4000)
        out['sw'] = await pg.evaluate("caches.keys()")
        for path, want in (('proyecto', '/proyecto/'), ('2d', '/2d/'), ('proyecto/', '/proyecto/')):
            await pg.goto(BASE + path, wait_until='load'); await pg.wait_for_timeout(800)
            info = await pg.evaluate("[location.pathname, document.title, !!navigator.serviceWorker.controller]")
            ok = info[0].endswith(want) and 'Kauffmann List' not in info[1]
            out[path] = info + [ok]
        await b.close()
    print(json.dumps(out, ensure_ascii=False, indent=1))
    bad = [k for k, v in out.items() if k != 'sw' and not v[-1]]
    assert not bad, bad
    print('sw-redirect-browser-check: OK')
asyncio.run(main())
