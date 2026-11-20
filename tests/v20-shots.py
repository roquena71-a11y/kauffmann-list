"""v20: capturas en teléfono 412×915: inicio, fila de países plegada y abierta, vista de cada país nuevo grande y primeros planos (2D y 3D) de placas movidas a la acera (países nuevos y Alemania).
Solo localhost, sin contador. Uso: python3 tests/v20-shots.py BASE_URL OUT_DIR → v20-shots.json"""
import asyncio, sys, os, json
from playwright.async_api import async_playwright
BASE, OUT = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
async def main():
    R = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 412, 'height': 915}, is_mobile=True, has_touch=True, device_scale_factor=1, service_workers='block', locale='es-ES')
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*.workers.dev/**', lambda r: r.abort())
        await pg.goto(BASE + 'index.html?intro=0&lang=es', wait_until='load')
        await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>60000 && DATA.every(s=>s._dla!==undefined || s._aliasOf) && document.querySelector('#countries button')", timeout=300000)
        await pg.wait_for_timeout(3000)
        R['paises'] = await pg.evaluate("[...document.querySelectorAll('#countries button')].map(b=>b.textContent.trim())")
        await pg.screenshot(path=f'{OUT}/p412-v20-0-inicio-fila-plegada.png')
        await pg.click('#countries button.more'); await pg.wait_for_timeout(500)
        await pg.screenshot(path=f'{OUT}/p412-v20-1-fila-abierta.png')
        await pg.click('#countries button.more'); await pg.wait_for_timeout(300)
        for cc in ('NL', 'FR', 'AT', 'NO', 'CZ'):
            await pg.click(f'#countries button[data-cc={cc}]'); await pg.wait_for_timeout(6000)
            R['visibles_' + cc] = await pg.evaluate("(cc)=>{const b=map.getBounds(); const l=DATA.filter(s=>s.cc===cc&&!s._aliasOf); return [l.filter(s=>b.contains([s.lo,s.la])).length, l.length];}", cc)
            await pg.screenshot(path=f'{OUT}/p412-v20-pais-{cc.lower()}.png')
            await pg.evaluate("()=>{ if (typeof closeCountriesIfOpen==='function') closeCountriesIfOpen(); }")
        picks = await pg.evaluate("""()=>{const out=[]; for (const cc of ['NL','FR','NO','AT','DE']){ const s=DATA.find(x=>(x.cc||'DE')===cc && x.dla!==undefined && !x._aliasOf && x.sla!==undefined); if(s) out.push([cc, s.id, s.n]); } return out;}""")
        R['cerca'] = picks
        for cc, sid, n in picks:
            for mode, z, pitch in (('2d', 20, 0), ('3d', 19.5, 60)):
                await pg.evaluate("([id,z,pitch])=>{const s=byId.get(id); map.jumpTo({center:[s._dlo,s._dla], zoom:z, pitch:pitch, bearing:0});}", [sid, z, pitch])
                await pg.wait_for_timeout(5500)
                await pg.screenshot(path=f'{OUT}/p412-v20-cerca-{cc.lower()}-{mode}.png')
        R['errores'] = errs
        await b.close()
    json.dump(R, open(f'{OUT}/v20-shots.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(R, ensure_ascii=False)[:1500])
asyncio.run(main())
