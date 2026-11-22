#!/usr/bin/env python3
"""v23: sheet collapse/expand (tap, touch drag, keyboard), compact compass control (WCAG 2.2 AA),
closer initial Europe view, deferred 3D columns, and throttled mobile load-time budget.
Usage: python3 tests/v23-ux-and-perf-check.py [BASE_URL]
"""
from __future__ import annotations

import asyncio
import gzip
import http.server
import json
import mimetypes
import os
import socketserver
import sys
import threading
import time
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
AXE = open('/workspace/tools-ai/node_modules/axe-core/axe.min.js').read()
TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']
BLOCK_HOSTS = ('kl-contador', 'workers.dev')


def start_gzip_server(directory: Path):
    cache = {}

    class GzipHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            rel = self.path.split('?')[0].lstrip('/') or 'index.html'
            p = (directory / rel).resolve()
            if p.is_dir():
                p = p / 'index.html'
            if not p.exists() or not p.is_file():
                self.send_error(404)
                return
            want_gz = 'gzip' in self.headers.get('Accept-Encoding', '') and p.suffix in (
                '.html', '.js', '.css', '.json', '.txt', '.xml', '.jsonld', '.svg',
            )
            key = (str(p), want_gz)
            if key not in cache:
                raw = p.read_bytes()
                body = gzip.compress(raw, compresslevel=6) if want_gz else raw
                ctype = mimetypes.guess_type(str(p))[0] or 'application/octet-stream'
                cache[key] = (ctype, body, body is not raw)
            ctype, body, is_gz = cache[key]
            self.send_response(200)
            self.send_header('Content-Type', ctype)
            if is_gz:
                self.send_header('Content-Encoding', 'gzip')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    socketserver.ThreadingTCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(('127.0.0.1', 0), GzipHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, httpd.server_address[1]


async def run_axe(pg):
    await pg.add_script_tag(content=AXE)
    return await pg.evaluate(
        '(t) => axe.run(document, {runOnly: {type: "tag", values: t}})'
        '.then(r => r.violations.map(v => [v.id, v.nodes.length, v.nodes[0].target]))',
        TAGS,
    )


async def block_counters(pg, seen_blocked):
    async def handler(route):
        u = route.request.url
        if any(h in u for h in BLOCK_HOSTS):
            seen_blocked.append(u)
            await route.abort()
        else:
            await route.continue_()

    await pg.route('**/*', handler)


async def check_ux(base_url: str):
    chrome = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
    async with async_playwright() as p:
        b = await p.chromium.launch(
            executable_path=chrome if Path(chrome).exists() else None,
            headless=True,
            args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-dev-shm-usage'],
        )

        # 1) Mobile 412x915: initial view, sheet tap/drag/keyboard collapse, compass, axe
        ctx = await b.new_context(
            viewport={'width': 412, 'height': 915},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=2,
            service_workers='block',
            locale='es-ES',
        )
        pg = await ctx.new_page()
        errs, blocked = [], []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await block_counters(pg, blocked)
        await pg.goto(base_url + 'index.html?intro=0&lang=es', wait_until='domcontentloaded', timeout=120000)
        await pg.wait_for_function(
            "typeof VISIBLE !== 'undefined' && VISIBLE.length > 74000 && window.map && map.getSource('pts') && map.getSource('kl-clu')",
            timeout=120000,
        )
        await pg.wait_for_timeout(1000)

        init = await pg.evaluate("""() => {
            const b = map.getBounds();
            return {
                center: [map.getCenter().lng, map.getCenter().lat],
                zoom: map.getZoom(),
                bearing: Math.round(map.getBearing()),
                south: b.getSouth(),
                north: b.getNorth(),
                visNorth: map.unproject([206, 65]).lat,
                visSouth: map.unproject([206, side.getBoundingClientRect().top - 10]).lat,
                hasDE: b.contains([13.4, 52.5]) && b.contains([9.99, 53.55]),
                hasIE: b.contains([-6.283, 53.333]),
                sheet: side.dataset.sheet,
                sheetH: Math.round(side.getBoundingClientRect().height),
                rotHidden: document.getElementById('rotBtns').hidden,
                colDeferred: !map.getLayer('stones'),
            };
        }""")
        assert init['zoom'] >= 3.3, f"initial zoom too far out: {init}"
        assert init['bearing'] == 0, f"initial bearing should be 0: {init}"
        assert init['visSouth'] > 28 and init['visNorth'] < 70, f"initial visible bounds too global: {init}"
        assert init['hasDE'] and init['hasIE'], f"initial bounds missing core markers: {init}"
        assert init['sheet'] == 'peek' and init['sheetH'] > 120, f"bad initial sheet: {init}"
        assert init['rotHidden'] is True, "compass should be hidden when north-up"
        assert init['colDeferred'] is True, "3D stones layer should be deferred at overview zoom"

        # Tap handle -> collapse
        await pg.click('#sheetHandle')
        await pg.wait_for_timeout(300)
        col = await pg.evaluate("""() => {
            const a = document.querySelector('.maplibregl-ctrl-attrib').getBoundingClientRect();
            const s = side.getBoundingClientRect();
            const lbl = document.querySelector('#sheetHandle .sheet-lbl');
            return {
                sheet: side.dataset.sheet,
                h: Math.round(s.height),
                lbl: lbl ? lbl.textContent.trim() : '',
                lblVis: lbl ? getComputedStyle(lbl).display !== 'none' : false,
                exp: sheetHandle.getAttribute('aria-expanded'),
                searchVis: getComputedStyle(side.querySelector('.search')).display !== 'none',
                attrAbove: a.bottom <= s.top + 1,
            };
        }""")
        assert col['sheet'] == 'collapsed' and col['h'] <= 52, f"collapse failed: {col}"
        assert col['lblVis'] and col['lbl'] == 'Buscar · Países', f"collapsed label wrong: {col}"
        assert col['exp'] == 'false' and not col['searchVis'] and col['attrAbove'], f"collapsed state bad: {col}"
        ax_col = await run_axe(pg)
        assert not ax_col, f"axe collapsed violations: {ax_col}"

        # Tapping empty map must NOT pop collapsed sheet open
        await pg.mouse.click(120, 220)
        await pg.wait_for_timeout(250)
        assert await pg.evaluate('side.dataset.sheet') == 'collapsed', "map tap re-opened collapsed sheet"

        # Tap handle -> expand back to peek
        await pg.click('#sheetHandle')
        await pg.wait_for_timeout(300)
        assert await pg.evaluate('side.dataset.sheet') == 'peek', "tap expand failed"

        # Touch drag down -> collapsed
        cdp = await ctx.new_cdp_session(pg)
        hb = await pg.locator('#sheetHandle').bounding_box()
        x, y = hb['x'] + hb['width'] / 2, hb['y'] + hb['height'] / 2
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y}]})
        for i in range(1, 8):
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x, 'y': y + i * 24}]})
            await pg.wait_for_timeout(20)
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        await pg.wait_for_timeout(300)
        assert await pg.evaluate('side.dataset.sheet') == 'collapsed', "touch drag down did not collapse"

        # Touch drag up -> peek, then keyboard ArrowUp -> half, Escape -> collapsed
        hb = await pg.locator('#sheetHandle').bounding_box()
        x, y = hb['x'] + hb['width'] / 2, hb['y'] + hb['height'] / 2
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y}]})
        for i in range(1, 7):
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x, 'y': y - i * 24}]})
            await pg.wait_for_timeout(20)
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        await pg.wait_for_timeout(300)
        assert await pg.evaluate('side.dataset.sheet') == 'peek', "touch drag up did not restore peek"

        await pg.focus('#sheetHandle')
        await pg.keyboard.press('ArrowUp')
        await pg.wait_for_timeout(250)
        assert await pg.evaluate('side.dataset.sheet') == 'half', "ArrowUp did not open half"
        await pg.keyboard.press('Escape')
        await pg.wait_for_timeout(250)
        assert await pg.evaluate('side.dataset.sheet') == 'collapsed', "Escape did not collapse"

        # Language switch updates collapsed label
        await pg.click('#menuBtn')
        await pg.click('#topMenu .lang button[data-lang=de]')
        await pg.wait_for_timeout(200)
        assert await pg.evaluate("document.querySelector('#sheetHandle .sheet-lbl').textContent.trim()") == 'Suche · Länder'
        await pg.click('#topMenu .lang button[data-lang=en]')
        await pg.wait_for_timeout(200)
        assert await pg.evaluate("document.querySelector('#sheetHandle .sheet-lbl').textContent.trim()") == 'Search · Countries'
        await pg.click('#topMenu .lang button[data-lang=es]')
        await pg.keyboard.press('Escape')
        await pg.wait_for_timeout(200)

        # Rotate map -> compact single square compass appears, WCAG 2.2 AA + target size >= 24px, tap resets to 0
        await pg.evaluate('map.jumpTo({bearing: 35})')
        await pg.wait_for_timeout(300)
        rot = await pg.evaluate("""() => {
            const rb = document.getElementById('rotBtns');
            const btns = rb.querySelectorAll('button');
            const r = btns[0].getBoundingClientRect();
            const a = document.querySelector('.maplibregl-ctrl-attrib').getBoundingClientRect();
            const s = side.getBoundingClientRect();
            const ov = (x, y) => !(x.right <= y.left || x.left >= y.right || x.bottom <= y.top || x.top >= y.bottom);
            return {
                hidden: rb.hidden,
                count: btns.length,
                w: Math.round(r.width),
                h: Math.round(r.height),
                aria: btns[0].getAttribute('aria-label'),
                ovAttr: ov(r, a),
                ovSide: ov(r, s),
            };
        }""")
        assert not rot['hidden'] and rot['count'] == 1, f"compass should be 1 button when rotated: {rot}"
        assert rot['w'] >= 24 and rot['h'] >= 24 and rot['w'] <= 44, f"compass target size invalid: {rot}"
        assert '35' in rot['aria'] and not rot['ovAttr'] and not rot['ovSide'], f"compass overlap/label: {rot}"
        ax_rot = await run_axe(pg)
        assert not ax_rot, f"axe rotated violations: {ax_rot}"

        await pg.click('#rotNorth')
        await pg.wait_for_timeout(850)
        assert await pg.evaluate('Math.round(map.getBearing())') == 0, "compass click did not reset north"
        assert await pg.evaluate("document.getElementById('rotBtns').hidden") is True, "compass did not hide at north"

        # Zooming in mounts deferred 3D columns seamlessly
        await pg.evaluate('map.jumpTo({center:[13.4,52.5], zoom:16.5, pitch:45, bearing:0})')
        await pg.wait_for_timeout(500)
        assert await pg.evaluate("!!map.getLayer('stones')") is True, "deferred 3D stones layer did not mount on zoom in"

        assert not errs, f"page errors: {errs}"
        await ctx.close()

        # 2) Initial view check on 360x780 mobile and 1366x800 desktop
        for name, vp, mob in (('360x780', {'width': 360, 'height': 780}, True), ('1366x800', {'width': 1366, 'height': 800}, False)):
            ctx = await b.new_context(viewport=vp, is_mobile=mob, has_touch=mob, service_workers='block', locale='es-ES')
            pg = await ctx.new_page()
            await block_counters(pg, blocked)
            await pg.goto(base_url + 'index.html?intro=0&lang=es', wait_until='domcontentloaded', timeout=120000)
            await pg.wait_for_function("typeof VISIBLE !== 'undefined' && VISIBLE.length > 74000 && window.map", timeout=120000)
            await pg.wait_for_timeout(800)
            v = await pg.evaluate("""() => {
                const b = map.getBounds();
                return {zoom: map.getZoom(), bearing: Math.round(map.getBearing()),
                        hasDE: b.contains([13.4, 52.5]) && b.contains([9.99, 53.55]),
                        hasIE: b.contains([-6.283, 53.333]),
                        south: b.getSouth(), north: b.getNorth()};
            }""")
            assert v['zoom'] >= (3.2 if mob else 4.2), f"{name} zoom too far out: {v}"
            assert v['bearing'] == 0 and v['hasDE'] and v['hasIE'], f"{name} bounds/bearing failed: {v}"
            await ctx.close()

        await b.close()
        print(f"OK v23 UX: 412x915/360x780/1366x800 initial view (z={init['zoom']:.2f}), sheet collapse (tap/drag/keys), compass (36x36, axe 0), deferred 3D")


async def check_load_budget():
    httpd, port = start_gzip_server(ROOT)
    chrome = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
    try:
        t0 = time.perf_counter()
        async with async_playwright() as p:
            b = await p.chromium.launch(
                executable_path=chrome if Path(chrome).exists() else None,
                headless=True,
                args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-dev-shm-usage'],
            )
            ctx = await b.new_context(
                viewport={'width': 412, 'height': 915},
                is_mobile=True,
                has_touch=True,
                device_scale_factor=2,
                service_workers='block',
                locale='es-ES',
            )
            pg = await ctx.new_page()
            errs, blocked = [], []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await block_counters(pg, blocked)

            cdp = await ctx.new_cdp_session(pg)
            await cdp.send('Network.enable')
            await cdp.send('Network.emulateNetworkConditions', {
                'offline': False,
                'latency': 50,
                'downloadThroughput': int(20 * 1024 * 1024 / 8),
                'uploadThroughput': int(20 * 1024 * 1024 / 16),
            })
            await cdp.send('Emulation.setCPUThrottlingRate', {'rate': 2})

            await pg.goto(f'http://127.0.0.1:{port}/index.html?intro=0&lang=es', wait_until='domcontentloaded', timeout=120000)
            t_dcl = round((time.perf_counter() - t0) * 1000)
            await pg.wait_for_function("typeof VISIBLE !== 'undefined' && VISIBLE.length > 74000", timeout=120000)
            t_vis = round((time.perf_counter() - t0) * 1000)
            await pg.wait_for_function("window.map && map.getSource('pts') && map.getSource('kl-clu')", timeout=120000)
            t_ov = round((time.perf_counter() - t0) * 1000)
            paints = await pg.evaluate("Object.fromEntries(performance.getEntriesByType('paint').map(x => [x.name, Math.round(x.startTime)]))")
            await b.close()

        fcp = paints.get('first-contentful-paint', 9999)
        assert not errs, f"load budget page errors: {errs}"
        assert fcp <= 1500, f"FCP {fcp}ms exceeded 1500ms budget"
        assert t_dcl <= 2500, f"DCL {t_dcl}ms exceeded 2500ms budget"
        assert t_ov <= 12500, f"overlays {t_ov}ms exceeded 12500ms 4G-2xCPU budget (v22 baseline ~18800ms)"
        print(f"OK v23 load budget (412x915 gzip 4G 20Mbps 2xCPU): fcp={fcp}ms dcl={t_dcl}ms vis={t_vis}ms overlays={t_ov}ms")
    finally:
        httpd.shutdown()


async def main():
    if len(sys.argv) > 1:
        await check_ux(sys.argv[1].rstrip('/') + '/')
    else:
        httpd, port = start_gzip_server(ROOT)
        try:
            await check_ux(f'http://127.0.0.1:{port}/')
        finally:
            httpd.shutdown()
    await check_load_budget()


if __name__ == '__main__':
    asyncio.run(main())
