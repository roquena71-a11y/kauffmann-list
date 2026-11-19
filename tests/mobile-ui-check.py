"""v17: comprobación en navegador de la interfaz del teléfono y del escritorio (no publica nada).
axe (WCAG 2.2 AA) en varios estados, tamaño de los objetivos (≥24 px), teclado, hoja inferior, capas, menú,
países, cuadros dorados agrupados (Dublín a escala regional) y desbordamiento horizontal.
Uso: python3 tests/mobile-ui-check.py http://127.0.0.1:8842/  → escribe shots/mobile-ui-check.json"""
import asyncio, json, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1]
AXE = open('/workspace/tools-ai/node_modules/axe-core/axe.min.js').read()
TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']
TARGETS = """() => { const bad=[]; const vis=e=>{const r=e.getBoundingClientRect(), cs=getComputedStyle(e); return r.width>0&&r.height>0&&cs.visibility!=='hidden'&&cs.display!=='none'&&r.bottom>0&&r.top<innerHeight};
  for (const e of document.querySelectorAll('button, a[href], input, [role=button]')) { if (!vis(e) || e.closest('.maplibregl-ctrl-attrib, .intro, p, li, dd, .note, .foot p')) continue;
    const r=e.getBoundingClientRect(); if (r.width<24||r.height<24) bad.push([e.id||e.className||e.textContent.trim().slice(0,30), Math.round(r.width), Math.round(r.height)]); }
  return bad; }"""
async def axe(pg):
    await pg.add_script_tag(content=AXE)
    r = await pg.evaluate("(t)=>axe.run(document,{runOnly:{type:'tag',values:t}})", TAGS)
    return [{'id': v['id'], 'impact': v['impact'], 'nodes': [n['target'] for n in v['nodes']][:4]} for v in r['violations']]
async def run(p, name, vp, mob):
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport=vp, is_mobile=mob, has_touch=mob, service_workers='block', locale='es-ES')
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    out = {'checks': {}, 'axe': {}, 'targets': {}}
    C = out['checks']
    await pg.goto(BASE + 'index.html?intro=0&lang=es', wait_until='load')
    await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>60000 && document.querySelector('#countries button')", timeout=120000)
    await pg.wait_for_timeout(2500)
    C['no_overflow'] = await pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
    C['countries'] = await pg.evaluate("[...document.querySelectorAll('#countries button')].map(b=>b.textContent.trim())")
    C['home_shows_ireland'] = await pg.evaluate("(()=>{const b=map.getBounds(); return b.contains([-6.283,53.333]) && b.contains([13.4,52.5]) && b.contains([9.99,53.55]);})()")
    out['axe']['home'] = await axe(pg); out['targets']['home'] = await pg.evaluate(TARGETS)
    # Dublín a escala regional: el cuadro «6» se dibuja
    await pg.evaluate("void map.jumpTo({center:[-6.9,53.3], zoom:6.3, pitch:0, bearing:0})"); await pg.wait_for_timeout(3500)
    C['dublin_z6_badge'] = await pg.evaluate("map.queryRenderedFeatures({layers:['kl-clu','kl-one']}).filter(f=>Math.abs(f.geometry.coordinates[0]+6.28)<0.2).map(f=>f.properties.point_count||1)")
    await pg.evaluate("void map.jumpTo({center:[-6.28,53.333], zoom:11, pitch:0})"); await pg.wait_for_timeout(3000)
    C['dublin_z11_badge'] = await pg.evaluate("map.queryRenderedFeatures({layers:['kl-clu','kl-one']}).map(f=>f.properties.point_count||1)")
    # tocar el cuadro: acerca el mapa
    pt = await pg.evaluate("(()=>{const p=map.project([-6.2829,53.3332]); const r=map.getCanvas().getBoundingClientRect(); return [r.left+p.x, r.top+p.y];})()")
    z0 = await pg.evaluate("map.getZoom()")
    if mob: await pg.touchscreen.tap(pt[0], pt[1])
    else: await pg.mouse.click(pt[0], pt[1])
    await pg.wait_for_timeout(2500)
    C['badge_tap_zooms'] = [round(z0, 2), round(await pg.evaluate("map.getZoom()"), 2)]
    # países → Irlanda
    await pg.evaluate("void map.jumpTo({center:[10.4,51], zoom:5})")
    await pg.click('#countries button[data-cc=IE]'); await pg.wait_for_timeout(4000)
    C['country_ie'] = await pg.evaluate("(()=>{const c=map.getCenter(); return [+c.lng.toFixed(3), +c.lat.toFixed(3), +map.getZoom().toFixed(1)];})()")
    if mob:
        st = lambda: pg.evaluate("[document.querySelector('#side').dataset.sheet, Math.round(document.querySelector('#side').getBoundingClientRect().height), document.querySelector('#sheetHandle').getAttribute('aria-expanded')]")
        C['sheet_start'] = await st()
        # teclado: el asa es un botón; Enter abre, flecha arriba amplía, Escape cierra
        await pg.focus('#sheetHandle'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(400); a = await st()
        await pg.keyboard.press('ArrowUp'); await pg.wait_for_timeout(400); bb = await st()
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400); c = await st()
        C['sheet_keyboard'] = [a, bb, c]
        # arrastrar el asa hacia arriba con el dedo (eventos pointer de tipo touch)
        hb = await pg.locator('#sheetHandle').bounding_box()
        x, y = hb['x'] + hb['width'] / 2, hb['y'] + hb['height'] / 2
        cdp = await ctx.new_cdp_session(pg)
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y}]})
        for i in range(1, 13):
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x, 'y': y - i * 30}]}); await pg.wait_for_timeout(30)
        await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []}); await pg.wait_for_timeout(500)
        C['sheet_drag_up'] = await st()
        # escribir: la hoja sube y muestra resultados
        await pg.keyboard.press('Escape')
        await pg.evaluate("document.querySelector('#sheetHandle').click(); document.querySelector('#sheetHandle').click(); document.querySelector('#sheetHandle').click();")
        await pg.evaluate("KLUI.setSheet('peek')"); await pg.wait_for_timeout(300)
        await pg.click('#q'); await pg.fill('#q', 'Saks'); await pg.wait_for_timeout(1200)
        C['search_sheet'] = await st(); C['search_results'] = await pg.evaluate("document.querySelectorAll('#results button[data-id]').length")
        out['axe']['results'] = await axe(pg); out['targets']['results'] = await pg.evaluate(TARGETS)
        await pg.click('#results button[data-id]'); await pg.wait_for_timeout(4500)
        C['detail_open'] = await pg.evaluate("[!document.querySelector('#detail').hidden, document.querySelector('#detail h2').textContent, (()=>{const p=map.project([DATA.find(s=>s.id===selected)._dlo, DATA.find(s=>s.id===selected)._dla]); const top=document.querySelector('.top').getBoundingClientRect().bottom, sh=document.querySelector('#side').getBoundingClientRect().top; return p.y>top && p.y<sh;})()]")
        out['axe']['detail'] = await axe(pg); out['targets']['detail'] = await pg.evaluate(TARGETS)
        # capas
        await pg.click('#layersBtn'); await pg.wait_for_timeout(400)
        C['layers_open'] = await pg.evaluate("[document.querySelector('#layersBtn').getAttribute('aria-expanded'), document.activeElement.closest('#basemapsPanel')!==null, [...document.querySelectorAll('#basemapsPanel button')].map(b=>b.textContent.trim())]")
        out['axe']['layers'] = await axe(pg); out['targets']['layers'] = await pg.evaluate(TARGETS)
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
        C['layers_escape'] = await pg.evaluate("[document.querySelector('#layersBtn').getAttribute('aria-expanded'), document.activeElement.id]")
        # menú
        await pg.click('#menuBtn'); await pg.wait_for_timeout(400)
        C['menu_open'] = await pg.evaluate("[document.querySelector('#menuBtn').getAttribute('aria-expanded'), [...document.querySelectorAll('#topMenu a, #topMenu button')].filter(e=>e.getBoundingClientRect().height>0).map(e=>e.textContent.trim())]")
        out['axe']['menu'] = await axe(pg); out['targets']['menu'] = await pg.evaluate(TARGETS)
        await pg.click('#topMenu .lang button[data-lang=de]'); await pg.wait_for_timeout(500)
        C['menu_de'] = await pg.evaluate("[document.querySelector('#menuBtn').getAttribute('aria-label'), document.querySelector('#layersBtn').getAttribute('aria-label'), document.querySelector('#sheetHandle').getAttribute('aria-label'), document.querySelector('.countries-t').textContent]")
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
        C['menu_escape'] = await pg.evaluate("[document.querySelector('#menuBtn').getAttribute('aria-expanded'), document.activeElement.id]")
        C['no_overflow_end'] = await pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
    else:
        C['desktop_hidden_mobile_controls'] = await pg.evaluate("['#menuBtn','#layersBtn','#sheetHandle'].map(s=>getComputedStyle(document.querySelector(s)).display)")
        C['desktop_layout'] = await pg.evaluate("[Math.round(document.querySelector('#side').getBoundingClientRect().width), getComputedStyle(document.querySelector('.basemaps')).display, getComputedStyle(document.querySelector('body > .foot')).display]")
        await pg.fill('#q', 'Saks'); await pg.wait_for_timeout(1000)
        out['axe']['results'] = await axe(pg)
    out['pageerrors'] = errs
    await b.close()
    return out
async def main():
    res = {}
    async with async_playwright() as p:
        for name, vp, mob in (('p360', {'width': 360, 'height': 780}, True), ('p412', {'width': 412, 'height': 915}, True), ('desk', {'width': 1366, 'height': 800}, False)):
            res[name] = await run(p, name, vp, mob)
            print(name, json.dumps(res[name], ensure_ascii=False)[:3000])
    json.dump(res, open('shots/mobile-ui-check.json', 'w'), ensure_ascii=False, indent=1)
asyncio.run(main())
