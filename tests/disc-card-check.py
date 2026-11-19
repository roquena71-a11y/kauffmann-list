"""v19 ronda 2: la ficha de Peter Denis Hassall (Jersey) muestra el aviso «Las fuentes no coinciden» con enlaces a ambos lados (es/de/en),
la dirección sigue siendo la de OpenStreetMap, «Cómo llegar» usa la coordenada de origen y axe (WCAG 2.2 AA) no da fallos. Solo localhost.
Uso: python3 tests/disc-card-check.py BASE_URL [OUT_DIR]"""
import asyncio, sys, json, os
from playwright.async_api import async_playwright
BASE = sys.argv[1]; OUT = sys.argv[2] if len(sys.argv) > 2 else None
AXE = open('/workspace/tools-ai/node_modules/axe-core/axe.min.js').read()
TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']
ID = 'n13021664958'
async def main():
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        for lang, w, h in (('es', 412, 915), ('de', 412, 915), ('en', 1280, 800)):
            ctx = await b.new_context(viewport={'width': w, 'height': h}, is_mobile=w < 600, has_touch=w < 600, service_workers='block', locale=lang)
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(BASE + f'index.html?intro=0&lang={lang}#s={ID}', wait_until='load')
            await pg.wait_for_selector('#detail .disc', timeout=180000)
            await pg.wait_for_timeout(1500)
            r = await pg.evaluate("""()=>{const d=document.querySelector('#detail .disc'); const links=[...d.querySelectorAll('a')].map(a=>[a.hostname,a.target,a.rel]);
              const dirs=[...document.querySelectorAll('#detail .actions a')].map(a=>a.href);
              return {text:d.textContent, links, dirs, addr:document.querySelector('#detail .place').textContent, h2:document.querySelector('#detail h2').textContent}}""")
            await pg.add_script_tag(content=AXE)
            ax = await pg.evaluate("(t)=>axe.run(document.querySelector('#detail'),{runOnly:{type:'tag',values:t}}).then(r=>r.violations.map(v=>[v.id,v.nodes.length,v.nodes[0].target]))", TAGS)
            hosts = {l[0] for l in r['links']}
            print(lang, w, r['h2'], '|', r['addr'], '|', sorted(hosts), '| axe', ax, '| errores', errs)
            if not {'www.bbc.co.uk', 'jerseyeveningpost.com', 'www.bailiwickexpress.com', 'de.wikipedia.org', 'www.frankfallaarchive.org', 'www.liberationroute.com', 'www.openstreetmap.org'} <= hosts: bad.append((lang, 'faltan enlaces', sorted(hosts)))
            if 'Byron Lane' not in r['text'] or 'Winchester' not in r['text']: bad.append((lang, 'el aviso no nombra ambas direcciones'))
            if 'Winchester House, Winchester Street' not in r['addr']: bad.append((lang, 'la dirección mostrada no es la de OSM'))
            if not all(l[1] == '_blank' and 'noopener' in (l[2] or '') for l in r['links']): bad.append((lang, 'enlaces sin noopener'))
            if not any('49.1884118' in d and '-2.1048038' in d for d in r['dirs']): bad.append((lang, 'Cómo llegar no usa la coordenada de origen', r['dirs']))
            if ax or errs: bad.append((lang, 'axe/errores', ax, errs))
            if OUT: os.makedirs(OUT, exist_ok=True); await pg.screenshot(path=f'{OUT}/p{w}-v19-hassall-{lang}.png')
            await ctx.close()
        await b.close()
    if bad: print('FALLO', bad); sys.exit(1)
    print('OK: ficha de Hassall con aviso «las fuentes no coinciden» (es/de/en), enlaces a ambos lados, ruta con la coordenada de origen, axe 0')
asyncio.run(main())
