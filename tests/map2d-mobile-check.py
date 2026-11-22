#!/usr/bin/env python3
"""v23: el mapa clásico 2D (#map) debe tener altura visible en el teléfono (p. ej. 390×844, 360×800)
y seguir funcionando en el escritorio. Falla si #map mide 0 px (Leaflet no pinta nada).
Uso: python3 tests/map2d-mobile-check.py [BASE_URL]
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
CHROME = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
SIZES = [
    ('390x844', 390, 844, True),
    ('360x800', 360, 800, True),
    ('1280x800', 1280, 800, False),
]


async def block_external(pg):
    async def abort(route):
        await route.abort()
    await pg.route('**/*kl-contador*', abort)
    await pg.route('**/*.workers.dev/**', abort)
    await pg.route('**/tile.openstreetmap.org/**', abort)


async def measure(pg):
    return await pg.evaluate("""() => {
        const el = document.getElementById('map');
        if (!el) return {missing: true};
        const r = el.getBoundingClientRect();
        const pane = el.querySelector('.leaflet-map-pane, .leaflet-pane');
        return {
            missing: false,
            width: Math.round(r.width),
            height: Math.round(r.height),
            leaflet: el.classList.contains('leaflet-container'),
            pane: !!pane,
            aria: (el.getAttribute('aria-label') || el.getAttribute('role') || '')
        };
    }""")


async def main():
    base = (sys.argv[1].rstrip('/') + '/') if len(sys.argv) > 1 else None
    httpd = None
    if not base:
        import http.server, socketserver, threading
        class H(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *a, **k):
                super().__init__(*a, directory=str(ROOT), **k)
            def log_message(self, *args):
                pass
        socketserver.ThreadingTCPServer.allow_reuse_address = True
        httpd = socketserver.ThreadingTCPServer(('127.0.0.1', 0), H)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        base = f'http://127.0.0.1:{httpd.server_address[1]}/'
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch(
            executable_path=CHROME if Path(CHROME).exists() else None,
            headless=True,
            args=['--disable-dev-shm-usage'],
        )
        for name, w, h, mob in SIZES:
            ctx = await b.new_context(
                viewport={'width': w, 'height': h},
                is_mobile=mob,
                has_touch=mob,
                service_workers='block',
                locale='es-ES',
            )
            pg = await ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await block_external(pg)
            await pg.goto(base + '2d/index.html', wait_until='domcontentloaded', timeout=60000)
            await pg.wait_for_function("typeof L!=='undefined' && document.getElementById('map')", timeout=30000)
            await pg.wait_for_timeout(200)
            m = await measure(pg)
            ok_h = (not m.get('missing')) and m.get('height', 0) > 0
            ok_w = m.get('width', 0) > 0
            ok_l = m.get('leaflet') and m.get('pane')
            # En el teléfono el mapa debe ocupar una parte útil de la pantalla, no un recuadro de 1 px.
            if mob:
                ok_h = ok_h and m['height'] >= 150
            else:
                ok_h = ok_h and m['height'] >= 200
            if not (ok_h and ok_w and ok_l) or errs:
                bad.append((name, m, errs[:2]))
            await ctx.close()
        await b.close()
    if httpd:
        httpd.shutdown()
    if bad:
        print('FAIL map2d-mobile:', bad)
        sys.exit(1)
    print('OK: el mapa 2D tiene altura visible en 390x844/360x800 y en el escritorio (Leaflet renderizado)')


if __name__ == '__main__':
    asyncio.run(main())
