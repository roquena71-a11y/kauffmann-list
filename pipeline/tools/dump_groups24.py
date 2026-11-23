#!/usr/bin/env python3
"""v29: vuelca de la web LOCAL los grupos de columnas tal como se dibujan (window.KLGroups + DATA).
Bloquea kl-contador y *.workers.dev. Uso: dump_groups24.py BASE_URL salida.json [--raw]
--raw añade ?alignoff=1 (dibujo sin data/align-v24.json: entrada de align24.py)."""
import asyncio, json, os, sys, time
from playwright.async_api import async_playwright
BLOCK = ('kl-contador', 'workers.dev')

async def main(base, out, raw):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get('CHROME_BIN', '/usr/bin/google-chrome'), headless=True,
                                    args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-dev-shm-usage'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block', locale='es-ES')
        pg = await ctx.new_page(); errs = []; blocked = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        async def rh(route):
            u = route.request.url
            if any(x in u for x in BLOCK): blocked.append(u); await route.abort(); return
            await route.continue_()
        await pg.route('**/*', rh)
        t0 = time.time()
        await pg.goto(base.rstrip('/') + '/index.html?intro=0&lang=es' + ('&alignoff=1' if raw else ''), wait_until='load', timeout=120000)
        await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>75000 && window.KLGroups && DATA.every(s=>s._dla!==undefined || s._aliasOf)", timeout=600000)
        if not raw:
            await pg.wait_for_function("window.KLAlign && KLAlign.ready", timeout=120000)
        d = await pg.evaluate("""() => ({
          groups: KLGroups.map(pg => ({ids: pg.g.map(s => String(s.id)), all: pg.all.map(s => String(s.id)), la0: pg.la0, lo0: pg.lo0, ang: pg.ang, step: pg.step})),
          stones: DATA.map(s => [String(s.id), s.src || null, s.cc || null, s.a || null, s.sla ?? s.la, s.slo ?? s.lo, s._dla, s._dlo, s._ang || 0, s._aliasOf || null, !!s._added]),
          align: window.KLAlign ? {ready: KLAlign.ready, applied: KLAlign.applied, file: KLAlign.file} : null
        })""")
        await b.close()
    d['errs'] = errs; d['blocked'] = len(blocked)
    json.dump(d, open(out, 'w'))
    print('dump', out, 'grupos', len(d['groups']), 'placas', len(d['stones']), 'errores', errs[:3], 't=%.1fs' % (time.time() - t0))
    if errs: sys.exit(1)

asyncio.run(main(sys.argv[1], sys.argv[2], '--raw' in sys.argv))
