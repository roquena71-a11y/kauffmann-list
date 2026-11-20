"""v19 ronda 4 (auditoría C-F1): la atribución de OpenStreetMap/OpenFreeMap queda visible (no tapada por la hoja inferior) y axe (WCAG 2.2 AA) da 0
en 320×568, 360×640, 360×740, 390×844, 412×915, 844×390 y 667×375, con la ficha cerrada (inicio) y abierta (buscar «Moses» y abrir la ficha).
Solo localhost; sin contador. Uso: python3 tests/attribution-check.py BASE_URL [OUT_DIR]"""
import asyncio, sys, os
from playwright.async_api import async_playwright
BASE = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else None
AXE = open('/workspace/tools-ai/node_modules/axe-core/axe.min.js').read()
TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']
SIZES = [(320, 568), (360, 640), (360, 740), (390, 844), (412, 915), (844, 390), (667, 375)]
PROBE = """() => { const a = document.querySelector('.maplibregl-ctrl-attrib'), b = document.querySelector('.maplibregl-ctrl-attrib-button'), side = document.querySelector('.side');
  const rect = e => { const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; };
  const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect(), rs = side.getBoundingClientRect();
  const hit = (r) => { const el = document.elementFromPoint((r.left + r.right) / 2, (r.top + r.bottom) / 2); return !!el && !!el.closest('.maplibregl-ctrl-attrib'); };
  const overlap = !(ra.right <= rs.left || ra.left >= rs.right || ra.bottom <= rs.top || ra.top >= rs.bottom);
  return {attr: rect(a), btn: rect(b), side: rect(side), btnHit: hit(rb), attrHit: hit(ra), overlap, vh: innerHeight, sheet: side.dataset.sheet || null}; }"""
async def run_axe(pg):
    await pg.add_script_tag(content=AXE)
    return await pg.evaluate("(t)=>axe.run(document,{runOnly:{type:'tag',values:t}}).then(r=>r.violations.map(v=>[v.id,v.nodes.length,v.nodes[0].target]))", TAGS)
async def main():
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        for w, h in SIZES:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, is_mobile=True, has_touch=True, service_workers='block', locale='es-ES')
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(BASE + 'index.html?intro=0&lang=es', wait_until='load')
            await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>60000 && document.querySelector('#countries button') && document.querySelector('.maplibregl-ctrl-attrib-button')", timeout=180000)
            await pg.wait_for_timeout(2500)
            for state in ('cerrada', 'abierta'):
                if state == 'abierta':
                    await pg.fill('#q', 'Moses'); await pg.wait_for_timeout(1200)
                    await pg.evaluate("document.querySelector('#results button').click()");   # v20: clic por JS (con 27 países la fila de países ocupa más y el primer resultado queda bajo la hoja); lo que se prueba es la atribución
                    await pg.wait_for_selector('#detail:not([hidden])', timeout=20000); await pg.wait_for_timeout(1500)
                r = await pg.evaluate(PROBE); ax = await run_axe(pg)
                print(w, h, state, r, 'axe', ax, flush=True)
                if OUT: os.makedirs(OUT, exist_ok=True); await pg.screenshot(path=f'{OUT}/attr-{w}x{h}-{state}.png')
                if not r['btnHit'] or not r['attrHit'] or r['overlap']: bad.append((w, h, state, 'atribución tapada', r))
                if ax: bad.append((w, h, state, 'axe', ax))
            if errs: bad.append((w, h, 'errores', errs[:2]))
            await ctx.close()
        await b.close()
    if bad: print('FALLO', bad); sys.exit(1)
    print('OK: atribución visible y axe 0 en 7 tamaños con la ficha cerrada y abierta')
asyncio.run(main())
