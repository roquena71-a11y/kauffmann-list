# Comprobación en navegador del sitio local (no publica nada). Uso: python3 tests/site-check.py [port]
import asyncio, json, sys, re
from playwright.async_api import async_playwright
PORT = sys.argv[1] if len(sys.argv) > 1 else '8817'
BASE = f'http://127.0.0.1:{PORT}/'
LIVE = 'https://roquena71-a11y.github.io/kauffmann-list/'
SHOTS = 'shots/'
IDS = json.load(open('tests/visible-ids.json'))
out = {'runs': []}

async def one(p, name, vp, mobile):
    b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport=vp, is_mobile=mobile, has_touch=mobile, device_scale_factor=2 if mobile else 1, service_workers='block', locale='es-ES')
    errors, pageerrors, failed = [], [], []
    # /api/ no existe en local (lo genera la pipeline al publicar): se lee del sitio en línea, solo GET.
    async def api(route):
        url = route.request.url.replace(BASE, LIVE)
        try:
            r = await route.fetch(url=url)
            await route.fulfill(response=r)
        except Exception:
            await route.abort()
    await ctx.route(re.compile(r'.*/api/v1/.*'), api)
    pg = await ctx.new_page()
    pg.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
    pg.on('pageerror', lambda e: pageerrors.append(str(e)))
    pg.on('requestfailed', lambda r: failed.append(r.url))
    run = {'name': name}
    # 1) enlace directo al Alexander de 1904 (carga nueva)
    await pg.goto(BASE + '?intro=0&lang=es#s=n1794209827', wait_until='load')
    await pg.wait_for_function('window.KLMerge && document.querySelector("#detail:not([hidden]) h2")', timeout=120000)
    await pg.wait_for_timeout(4000)
    run['KLMerge'] = await pg.evaluate('({groups:KLMerge.groups, extra:KLMerge.extra, visible:KLMerge.visible, source:KLMerge.source, isestr69:KLMerge.isestr69, doubtful:KLMerge.doubtful.length})')
    run['deeplink_1904'] = await pg.evaluate('({h2:document.querySelector("#detail h2").textContent, insc:[...document.querySelectorAll("#detail .brassplate")].map(x=>x.textContent), hash:location.hash})')
    await pg.screenshot(path=f'{SHOTS}{name}_alexander_freiwald_1904.png')
    # 2) los 47 registros de la auditoría C: cada uno abre su propia ficha
    res = []
    for id_, nm, jg in IDS:
        r = await pg.evaluate('''([id]) => { openStone(id, true); const d=document.querySelector('#detail');
            return {hash:location.hash, h2:d.querySelector('h2').textContent, insc:[...d.querySelectorAll('.brassplate')].map(x=>x.textContent).join(' || ')}; }''', [id_])
        ok = r['hash'] == '#s=' + id_ and (nm.split(' ')[0] in r['insc'] or nm.split(' ')[0] in r['h2']) and (not jg or jg in r['insc'])
        res.append({'id': id_, 'expect': nm + ' ' + jg, 'ok': ok, **r})
    run['audit_records_ok'] = sum(1 for r in res if r['ok']); run['audit_records'] = len(res)
    run['audit_records_bad'] = [r for r in res if not r['ok']]
    # 3) ficha con fuentes: Elfriede Löpert (Isestraße 69)
    await pg.evaluate('openStone("n676133185", false)')
    await pg.wait_for_timeout(5000)
    src = await pg.evaluate('''() => { const box=document.querySelector('#sourceSearch'); const a=[...box.querySelectorAll('a')];
        return {links:a.map(x=>[x.textContent, x.href, x.target, x.rel]), note:box.querySelector('.note').textContent,
                osmwd:a.filter(x=>/openstreetmap|wikidata/.test(x.href)).length, dup:a.length-new Set(a.map(x=>x.href)).size,
                sources:[...document.querySelectorAll('#detail ul.links')].pop().textContent}; }''')
    run['loepert_sources'] = src
    await pg.evaluate('document.querySelector("#detail .section-t:nth-of-type(n)")')
    await pg.evaluate('''() => { const t=[...document.querySelectorAll('#detail .section-t')].find(x=>/Buscar en las fuentes/.test(x.textContent)); t && t.scrollIntoView({block:'start'}); }''')
    await pg.wait_for_timeout(600)
    await pg.screenshot(path=f'{SHOTS}{name}_ficha_fuentes_loepert.png')
    # 4) nombres difíciles en la ficha real
    hard = {}
    for id_ in ['n676009557']:  # Gertrud Böhm geb. Cohn
        await pg.evaluate(f'openStone("{id_}", true)'); await pg.wait_for_timeout(1500)
        hard[id_] = await pg.evaluate('[...document.querySelectorAll("#sourceSearch a")].map(a=>a.textContent)')
    run['hard_names'] = hard
    # 5) vista de persona con registros directos (API leída del sitio en línea)
    pv = {}
    for pid in ['wd-Q105457315', 'wd-Q104421307']:
        ok = await pg.evaluate(f'KLPeople && KLPeople.open ? KLPeople.open("{pid}") : (typeof openPerson==="function" ? openPerson("{pid}") : null)')
        await pg.wait_for_timeout(2500)
        pv[pid] = await pg.evaluate('''() => { const d=document.querySelector('#detail'); const a=[...d.querySelectorAll('a')];
            return {h2:d.querySelector('h2')?.textContent, wikidataLinks:a.filter(x=>/wikidata\\.org\\/wiki\\/Q/.test(x.href)).map(x=>x.href),
                    search:[...d.querySelectorAll('#sourceSearch a')].map(x=>x.textContent), records:a.filter(x=>/bundesarchiv|yadvashem|ushmm/.test(x.href)).map(x=>x.href)}; }''')
        pv[pid]['opened'] = ok
    run['person_view'] = pv
    # 6) Acerca de: nota de privacidad
    await pg.evaluate('closeDetail(true)')
    if await pg.locator('#menuBtn').is_visible():   # v17: en el teléfono, «Acerca de los datos» está en el menú
        await pg.click('#menuBtn'); await pg.wait_for_timeout(300)
    await pg.click('#aboutLink'); await pg.wait_for_timeout(500)
    run['privacy'] = await pg.evaluate('document.querySelector("#aboutBody").innerText.split("\\n").filter(l=>/Privacidad/.test(l))')
    await pg.keyboard.press('Escape')
    # 7) foco visible
    await pg.evaluate('openStone("n676133185", true)'); await pg.wait_for_timeout(800)
    await pg.focus('#detail #sourceSearch a'); await pg.keyboard.press('Shift+Tab'); await pg.keyboard.press('Tab')
    run['focus'] = await pg.evaluate('(() => { const e=document.activeElement, s=getComputedStyle(e); return {tag:e.tagName, outline:s.outlineColor+" "+s.outlineStyle+" "+s.outlineWidth, shadow:s.boxShadow}; })()')
    await pg.screenshot(path=f'{SHOTS}{name}_focus.png')
    await pg.wait_for_timeout(1500)
    run['console_errors'] = errors; run['pageerrors'] = pageerrors
    run['failed_requests'] = [u for u in failed if 'tiles.openfreemap' not in u][:20]
    run['counter_requests'] = [u for u in failed if 'workers.dev' in u]
    out['runs'].append(run)
    await b.close()

async def main():
    async with async_playwright() as p:
        await one(p, 'desktop1366', {'width': 1366, 'height': 900}, False)
        await one(p, 'phone430', {'width': 430, 'height': 932}, True)
    json.dump(out, open('shots/site-check.json', 'w'), ensure_ascii=False, indent=1)
    for r in out['runs']:
        print(r['name'], json.dumps({k: r[k] for k in ['KLMerge', 'deeplink_1904', 'audit_records_ok', 'audit_records', 'console_errors', 'pageerrors', 'privacy', 'focus']}, ensure_ascii=False))
        print('  loepert osm/wd in search:', r['loepert_sources']['osmwd'], 'dup:', r['loepert_sources']['dup'], 'note:', r['loepert_sources']['note'])
        print('  bad:', r['audit_records_bad'][:3])
asyncio.run(main())
