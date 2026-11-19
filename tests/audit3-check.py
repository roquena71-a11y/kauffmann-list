"""Auditoría 3 (v17): comparación v16 (publicada) ↔ v17 y casos no cubiertos por las otras pruebas (no publica nada).
· escritorio sin regresión: mismas posiciones de cabecera, panel, botones de mapa base y pie;
· dominios externos pedidos (sin rastreadores nuevos);
· introducción en el teléfono → mapa con todos los países;
· movimiento reducido; vigilia «Recordar a todos» en el teléfono; ficha por enlace #s= en el teléfono.
Uso: python3 tests/audit3-check.py http://127.0.0.1:8841/ http://127.0.0.1:8842/"""
import asyncio, json, sys
from urllib.parse import urlparse
from playwright.async_api import async_playwright
OLD, NEW = sys.argv[1], sys.argv[2]
ARGS = ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']
GEOM = """() => { const r = s => { const e = document.querySelector(s); if (!e) return null; const b = e.getBoundingClientRect(); return [Math.round(b.x), Math.round(b.y), Math.round(b.width), Math.round(b.height), getComputedStyle(e).display]; };
  return {top: r('.top'), side: r('#side'), q: r('#q'), city: r('#city'), map: r('#map'), basemaps: r('.basemaps'), foot: r('body > .foot'), remember: r('#remember'), lang: r('.lang'), rot: r('#rotBtns'), nav: r('.maplibregl-ctrl-top-right')}; }"""
async def page(p, base, vp, mob, url, reduce=False):
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=ARGS)
    ctx = await b.new_context(viewport=vp, is_mobile=mob, has_touch=mob, service_workers='block', locale='es-ES', reduced_motion='reduce' if reduce else 'no-preference')
    pg = await ctx.new_page(); hosts = set(); errs = []
    pg.on('request', lambda r: hosts.add(urlparse(r.url).hostname))
    pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(base + url, wait_until='load')
    await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>60000", timeout=120000); await pg.wait_for_timeout(3000)
    return b, pg, hosts, errs
async def main():
    R = {}
    async with async_playwright() as p:
        # 1) escritorio: geometría
        for tag, base in (('v16', OLD), ('v17', NEW)):
            b, pg, hosts, errs = await page(p, base, {'width': 1366, 'height': 800}, False, 'index.html?intro=0&lang=es')
            R['desk_' + tag] = await pg.evaluate(GEOM); R['hosts_' + tag] = sorted(h for h in hosts if h and h != '127.0.0.1'); R['err_' + tag] = errs
            await b.close()
        diff = {k: (R['desk_v16'][k], R['desk_v17'][k]) for k in R['desk_v16'] if R['desk_v16'][k] != R['desk_v17'][k]}
        R['desk_diff'] = diff
        R['new_hosts'] = sorted(set(R['hosts_v17']) - set(R['hosts_v16']))
        # 2) introducción en el teléfono
        b, pg, hosts, errs = await page(p, NEW, {'width': 360, 'height': 780}, True, 'index.html?intro=1&lang=es')
        R['intro_visible'] = await pg.evaluate("getComputedStyle(document.querySelector('#intro')).display")
        R['intro_hides_mobile_ui'] = await pg.evaluate("['#layersBtn','.top','#side'].map(s=>getComputedStyle(document.querySelector(s)).display)")
        for _ in range(3): await pg.click('#introNext'); await pg.wait_for_timeout(400)
        await pg.wait_for_timeout(7000)
        R['after_intro'] = await pg.evaluate("[document.documentElement.classList.contains('intro-skip'), map.getBounds().contains([-6.283,53.333]) && map.getBounds().contains([13.4,52.5]), getComputedStyle(document.querySelector('#layersBtn')).display, document.querySelector('#side').dataset.sheet]")
        # 3) vigilia en el teléfono (menú → Recordar a todos)
        await pg.click('#menuBtn'); await pg.click('#remember'); await pg.wait_for_timeout(1500)
        R['vigil'] = await pg.evaluate("[document.body.classList.contains('vigil-on'), !document.querySelector('#vigil').hidden, document.querySelector('#menuBtn').getAttribute('aria-expanded'), (()=>{const v=document.querySelector('#vigil').getBoundingClientRect(), t=document.querySelector('.top').getBoundingClientRect(); return v.top>=t.bottom-1;})()]")
        await pg.screenshot(path='shots/after/p360-9-recordar.png')
        R['err_intro'] = errs; await b.close()
        # 4) movimiento reducido + enlace directo a una ficha (Dublín) en el teléfono
        b, pg, hosts, errs = await page(p, NEW, {'width': 412, 'height': 915}, True, 'index.html?lang=es#s=n13067653175', reduce=True)
        await pg.wait_for_timeout(2000)
        R['deeplink'] = await pg.evaluate("[document.querySelector('#detail h2')?.textContent, document.querySelector('#side').dataset.sheet, getComputedStyle(document.querySelector('#side')).transitionDuration, Math.abs(map.getCenter().lng+6.283)<0.01]")
        await pg.screenshot(path='shots/after/p412-10-enlace-ficha-dublin.png')
        R['err_deeplink'] = errs; await b.close()
    print(json.dumps(R, ensure_ascii=False, indent=1))
    json.dump(R, open('shots/audit3-check.json', 'w'), ensure_ascii=False, indent=1)
asyncio.run(main())
