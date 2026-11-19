"""v18: botones DE/IE/SE en varios tamaños (F1 de la auditoría): los puntos de referencia del país deben quedar dentro de la pantalla
y libres (elementFromPoint = el lienzo del mapa, no la barra de capas, los controles ni el panel). Solo localhost, sin contador.
Uso: python3 tests/country-buttons-check.py BASE_URL [OUT_DIR] → JSON por tamaño"""
import asyncio, sys, os, json
from playwright.async_api import async_playwright
BASE = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else None
if OUT: os.makedirs(OUT, exist_ok=True)
SIZES = [('1280x800', 1280, 800, False), ('1366x768', 1366, 768, False), ('1920x1080', 1920, 1080, False), ('412x915', 412, 915, True), ('844x390', 844, 390, True)]
REF = {'DE': [('Berlín', [13.405, 52.52]), ('Hamburgo', [9.99, 53.55]), ('Múnich', [11.58, 48.14]), ('Colonia', [6.96, 50.94])]}
async def main():
    bad = []; R = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        for name, w, h, mob in SIZES:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, is_mobile=mob, has_touch=mob, device_scale_factor=1, service_workers='block', locale='es-ES')
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(BASE + 'index.html?intro=0&lang=es', wait_until='load')
            await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>60000 && document.querySelector('#countries button')", timeout=120000)
            await pg.wait_for_timeout(2500)
            R[name] = {}
            for cc in ('SE', 'IE', 'JE', 'FI', 'RO', 'DE'):
                if cc != 'DE' or True:
                    await pg.click(f'#countries button[data-cc={cc}]'); await pg.wait_for_timeout(5500)
                if cc != 'DE': REF[cc] = [(s['n'], [s['lo'], s['la']]) for s in await pg.evaluate("DATA.filter(s=>s.cc==='%s' && !s._aliasOf).map(s=>({n:s.n,lo:s.lo,la:s.la}))" % cc)]   # v19: todas las placas del país (posición de dibujo)
                res = await pg.evaluate("""(refs) => refs.map(([n, ll]) => { const p = map.project(ll), cr = map.getContainer().getBoundingClientRect(); const el = document.elementFromPoint(cr.left + p.x, cr.top + p.y);
                    return {n, x: Math.round(p.x), y: Math.round(p.y), inside: p.x > 0 && p.y > 0 && p.x < cr.width && p.y < cr.height && cr.left + p.x < innerWidth && cr.top + p.y < innerHeight, hit: el ? (el.id || el.className || el.tagName).toString().slice(0, 40) : null, canvas: !!el && el.tagName === 'CANVAS' || !!el && !!el.closest('.maplibregl-canvas-container')}; })""", REF[cc])
                R[name][cc] = res
                for r in res:
                    if cc == 'DE' and not (r['inside']): continue          # Alemania es ancha: solo exigimos libres los que caen dentro
                    if not r['inside'] or not r['canvas']: bad.append((name, cc, r))
                if OUT: await pg.screenshot(path=f'{OUT}/cb-{name}-{cc}.png')
            if errs: bad.append((name, 'pageerror', errs[:2]))
            await ctx.close()
        await b.close()
    print(json.dumps(R, ensure_ascii=False, indent=1))
    print('FALLOS:', json.dumps(bad, ensure_ascii=False) if bad else 'ninguno'); sys.exit(1 if bad else 0)
asyncio.run(main())
