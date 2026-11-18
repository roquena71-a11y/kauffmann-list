"""Los enlaces citables abren de verdad a la persona en el mapa (Chrome sin pantalla). No publica nada.
Uso: python3 tests/permalink-browser-check.py <url_base_local> <informe_ai-sim.json>
   p. ej. python3 tests/permalink-browser-check.py http://127.0.0.1:8830/ work-ia/ai-sim-seed11.json
Las llamadas a /api/v1/cc0/ se leen del sitio en línea (solo GET) si no existen en local."""
import asyncio, json, re, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1]
LIVE = 'https://roquena71-a11y.github.io/kauffmann-list/'
rep = json.load(open(sys.argv[2], encoding='utf-8'))
cases = []
for r in rep['results']:
    m = re.search(r'(#[sp]=\S+?)\. Fuente', r['citation'])
    cases.append((r['family'], r['citation'].split(' (')[0], m.group(1)))
async def main():
    bad = 0
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block', locale='es-ES')
        async def api(route):
            try:
                r = await route.fetch(url=route.request.url.replace(BASE, LIVE)); await route.fulfill(response=r)
            except Exception:
                await route.continue_()
        await ctx.route(re.compile(r'.*/api/v1/cc0/.*'), api)
        for fam, name, frag in cases[:10] + [c for c in cases if c[0] == 'cc0'][:5]:
            pg = await ctx.new_page()
            await pg.goto(BASE + 'index.html?intro=0&lang=es' + frag, wait_until='load')
            ok = False
            for _ in range(40):
                await pg.wait_for_timeout(500)
                txt = await pg.evaluate("document.querySelector('#detail')?.hidden===false ? document.querySelector('#detail').innerText : ''")
                if txt and name.split()[-1].lower() in txt.lower():
                    ok = True; break
            print(('OK    ' if ok else 'FALLO ') + fam, frag, name)
            bad += 0 if ok else 1
            await pg.close()
        await b.close()
    print('permalink-browser-check: %d fallos' % bad)
    return 1 if bad else 0
sys.exit(asyncio.run(main()))
