"""v18: capturas de las piedras de Suecia en teléfono 412 (no publica nada; solo localhost, sin contador).
Uso: python3 tests/se-shots.py BASE_URL OUT_DIR → se-shots.json"""
import asyncio, sys, os, json
from playwright.async_api import async_playwright
BASE, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
async def main():
    R = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 412, 'height': 915}, is_mobile=True, has_touch=True, device_scale_factor=1, service_workers='block', locale='es-ES')
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(BASE + 'index.html?intro=0&lang=es', wait_until='load')
        await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>60000 && document.querySelector('#countries button')", timeout=120000)
        await pg.wait_for_timeout(3000)
        R['countries'] = await pg.evaluate("[...document.querySelectorAll('#countries button')].map(b=>b.textContent.trim())")
        await pg.screenshot(path=f'{OUT}/p412-se-0-inicio.png')
        R['inicio_bounds'] = await pg.evaluate("(()=>{const b=map.getBounds(); return {w:+b.getWest().toFixed(2),e:+b.getEast().toFixed(2),s:+b.getSouth().toFixed(2),n:+b.getNorth().toFixed(2), stockholm:b.contains([18.07,59.33]), malmo:b.contains([12.9979,55.6099]), dublin:b.contains([-6.28,53.33])};})()")
        # 1) botón «Suecia»
        await pg.click('#countries button[data-cc=SE]'); await pg.wait_for_timeout(5000)
        R['suecia_view'] = await pg.evaluate("(()=>{const c=map.getCenter(); return [+c.lng.toFixed(3), +c.lat.toFixed(3), +map.getZoom().toFixed(1)];})()")
        R['suecia_rendered'] = await pg.evaluate("map.queryRenderedFeatures({layers:['kl-clu','kl-one']}).map(f=>[f.properties.point_count||1, +f.geometry.coordinates[0].toFixed(3), +f.geometry.coordinates[1].toFixed(3)])")
        await pg.screenshot(path=f'{OUT}/p412-se-1-pais.png')
        R['suecia_bounds_contiene'] = await pg.evaluate("(()=>{const b=map.getBounds(); return {malmo:b.contains([12.9979,55.6099]), estocolmo:b.contains([18.07,59.33])};})()")
        # 2) Estocolmo y Malmö a escala de ciudad
        for name, c, z in (('2-estocolmo', [18.07, 59.33], 12.5), ('3-malmo', [12.9979, 55.6099], 17.5)):
            await pg.evaluate(f"void map.jumpTo({{center:{c}, zoom:{z}, pitch:0, bearing:0}})"); await pg.wait_for_timeout(4500)
            R[name] = await pg.evaluate("map.queryRenderedFeatures({layers:['kl-clu','kl-one']}).map(f=>[f.properties.point_count||1, +f.geometry.coordinates[0].toFixed(4), +f.geometry.coordinates[1].toFixed(4)])")
            await pg.screenshot(path=f'{OUT}/p412-se-{name}.png')
        # 3) búsqueda y ficha
        q = pg.locator('#q')
        if not await q.is_visible():
            for sel in ('#searchFab', '.searchbar'):
                if await pg.locator(sel).count() and await pg.locator(sel).first.is_visible(): await pg.locator(sel).first.click(); break
        for nm, sid in (('Holewa', 'n12247227671'), ('Gerson', 'n12212839192'), ('Moses', 'n12247228901')):
            await q.fill(nm); await pg.wait_for_timeout(1500)
            R['res_' + nm] = await pg.evaluate("[...document.querySelectorAll('#results button[data-id]')].filter(b=>/Skeppsbron|Kungsholmstorg|Gumshornsgatan|Apelbergsgatan/.test(b.textContent)).map(b=>b.textContent.trim().replace(/\\s+/g,' '))")
            await pg.locator('#results button[data-id="%s"]' % sid).first.click(); await pg.wait_for_timeout(5000)
            R['ficha_' + nm] = await pg.evaluate("document.querySelector('#side').innerText.replace(/\\s+/g,' ').slice(0,900)")
            R['ficha_links_' + nm] = await pg.evaluate("[...document.querySelectorAll('#side a[href]')].map(a=>a.href).filter(h=>/openstreetmap|wikidata|wikipedia|commons/.test(h))")
            await pg.screenshot(path=f'{OUT}/p412-se-4-ficha-{nm.lower()}.png')
            back = pg.locator('#back, .back, button:has-text("Volver")')
            if await back.count(): await back.first.click(); await pg.wait_for_timeout(500)
        R['overflow'] = await pg.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"); R['pageerrors'] = errs
        await b.close()
    json.dump(R, open(f'{OUT}/se-shots.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(R, ensure_ascii=False, indent=1))
asyncio.run(main())
