"""v19 ronda 3: los 6 países en 9 tamaños (teléfono vertical y horizontal, escritorio); cada placa debe verse ENTERA: su recuadro de 32 px (centro y 8 puntos) cae dentro del mapa y sobre el lienzo, no bajo botones, hoja ni controles.
v18: botones DE/IE/SE en varios tamaños (F1 de la auditoría): los puntos de referencia del país deben quedar dentro de la pantalla
y libres (elementFromPoint = el lienzo del mapa, no la barra de capas, los controles ni el panel). Solo localhost, sin contador.
Uso: python3 tests/country-buttons-check.py BASE_URL [OUT_DIR] → JSON por tamaño"""
import asyncio, sys, os, json
from playwright.async_api import async_playwright
BASE = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else None
if OUT: os.makedirs(OUT, exist_ok=True)
SIZES = [('320x568', 320, 568, True), ('1280x800', 1280, 800, False), ('1366x768', 1366, 768, False), ('1920x1080', 1920, 1080, False), ('360x640', 360, 640, True), ('360x740', 360, 740, True), ('390x844', 390, 844, True), ('412x915', 412, 915, True), ('844x390', 844, 390, True), ('667x375', 667, 375, True)]
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
            allcc = await pg.evaluate("[...document.querySelectorAll('#countries button[data-cc]')].map(b=>b.dataset.cc)")
            OLD = ['SE', 'IE', 'JE', 'FI', 'RO']
            todo = [c for c in allcc if c not in OLD and c != 'DE'] if name in ('320x568', '360x740', '1280x800', '1920x1080') else []   # v20: los países nuevos en 4 tamaños (el resto, los 6 de siempre)
            for cc in OLD + todo + ['DE']:
                more = await pg.query_selector('#countries button.more')
                if more and await more.is_visible() and await pg.evaluate("(c)=>{const b=document.querySelector(`#countries button[data-cc=${c}]`);return !b || getComputedStyle(b).display==='none'}", cc):
                    if await more.get_attribute('aria-expanded') != 'true': await more.click(); await pg.wait_for_timeout(250)
                await pg.evaluate("(c)=>document.querySelector(`#countries button[data-cc=${c}]`).scrollIntoView({block:'nearest'})", cc)
                await pg.click(f'#countries button[data-cc={cc}]'); await pg.wait_for_timeout(5500 if cc in OLD + ['DE'] else 3300)
                if cc != 'DE': REF[cc] = [(s['n'], [s['lo'], s['la']]) for s in await pg.evaluate("DATA.filter(s=>s.cc==='%s' && !s._aliasOf).map(s=>({n:s.n,lo:s.lo,la:s.la}))" % cc)]   # v19: todas las placas del país (posición de dibujo)
                res = await pg.evaluate("""(refs) => refs.map(([n, ll]) => { const p = map.project(ll), cr = map.getContainer().getBoundingClientRect();
                    const onCanvas = (x, y) => { const el = document.elementFromPoint(cr.left + x, cr.top + y); return !!el && (el.tagName === 'CANVAS' || !!el.closest('.maplibregl-canvas-container')); };
                    const inMap = (x, y) => x > 0 && y > 0 && x < cr.width && y < cr.height && cr.left + x < innerWidth && cr.top + y < innerHeight;
                    const pts = []; for (const dx of [-16, 0, 16]) for (const dy of [-16, 0, 16]) pts.push([p.x + dx, p.y + dy]);
                    const el = document.elementFromPoint(cr.left + p.x, cr.top + p.y);
                    return {n, x: Math.round(p.x), y: Math.round(p.y), inside: inMap(p.x, p.y), hit: el ? (el.id || el.className || el.tagName).toString().slice(0, 40) : null, canvas: onCanvas(p.x, p.y),
                            whole: pts.every(([x, y]) => inMap(x, y) && onCanvas(x, y)), covered: pts.filter(([x, y]) => !(inMap(x, y) && onCanvas(x, y))).length}; })""", REF[cc])
                R[name][cc] = res
                for r in res:
                    if (cc == 'DE' or len(REF[cc]) >= 50) and not (r['inside']): continue          # países anchos (Alemania, Francia, Italia…): solo exigimos libres los que caen dentro
                    if not r['inside'] or not r['canvas'] or not r['whole']: bad.append((name, cc, r))
                if OUT: await pg.screenshot(path=f'{OUT}/cb-{name}-{cc}.png')
            if errs: bad.append((name, 'pageerror', errs[:2]))
            await ctx.close()
        await b.close()
    print(json.dumps(R, ensure_ascii=False, indent=1))
    print('FALLOS:', json.dumps(bad, ensure_ascii=False) if bad else 'ninguno'); sys.exit(1 if bad else 0)
asyncio.run(main())
