"""v19: capturas en teléfono 412×915 de cada país (botón del país) y primeros planos de placas sobre la acera.
Solo localhost, sin contador. Uso: python3 tests/v19-shots.py BASE_URL OUT_DIR → v19-shots.json"""
import asyncio, sys, os, json
from playwright.async_api import async_playwright
BASE, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
CLOSE = [  # (archivo, id, zoom, inclinación)
    ('se-moses-2d', 'n12247228901', 20, 0), ('se-moses-3d', 'n12247228901', 19, 60),
    ('ro-bloch-2d', 'Q44101523', 20, 0), ('ro-bloch-3d', 'Q44101523', 19, 60),
    ('je-bercu-2d', 'n13021664959', 20, 0), ('je-bercu-3d', 'n13021664959', 19, 60),
    ('je-anchorage-2d', 'n13021292775', 20, 0),
    ('fi-kollmann-2d', 'n5666091193', 20, 0), ('fi-kollmann-3d', 'n5666091193', 19, 60),
    ('fi-huppert-2d', 'n11716782880', 20, 0), ('ie-donore-2d', 'n13067653175', 20, 0), ('se-szybilski-2d', 'n12228264289', 20, 0),
]
async def main():
    R = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 412, 'height': 915}, is_mobile=True, has_touch=True, device_scale_factor=1, service_workers='block', locale='es-ES')
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(BASE + 'index.html?intro=0&lang=es', wait_until='load')
        await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>60000 && document.querySelector('#countries button')", timeout=180000)
        await pg.wait_for_timeout(3000)
        R['countries'] = await pg.evaluate("[...document.querySelectorAll('#countries button')].map(b=>b.textContent.trim())")
        await pg.screenshot(path=f'{OUT}/p412-v19-0-inicio.png')
        for cc in ('JE', 'FI', 'RO', 'SE', 'IE'):
            await pg.click(f'#countries button[data-cc={cc}]'); await pg.wait_for_timeout(6000)
            R['vista_' + cc] = await pg.evaluate("(()=>{const c=map.getCenter(); return [+c.lng.toFixed(3), +c.lat.toFixed(3), +map.getZoom().toFixed(1), Math.round(map.getPitch())];})()")
            R['visibles_' + cc] = await pg.evaluate("(cc)=>{const b=map.getBounds(); const l=DATA.filter(s=>s.cc===cc&&!s._aliasOf); return [l.filter(s=>b.contains([s.lo,s.la])).length, l.length];}", cc)
            await pg.screenshot(path=f'{OUT}/p412-v19-{cc.lower()}-pais.png')
        for name, sid, z, pitch in CLOSE:
            await pg.evaluate("([id,z,pitch])=>{const s=byId.get(id); map.jumpTo({center:[s._dlo,s._dla], zoom:z, pitch:pitch, bearing:0});}", [sid, z, pitch])
            await pg.wait_for_timeout(5500)
            await pg.screenshot(path=f'{OUT}/p412-v19-cerca-{name}.png')
        R['errores'] = errs
        await b.close()
    json.dump(R, open(f'{OUT}/v19-shots.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(R, ensure_ascii=False)[:1500])
asyncio.run(main())
