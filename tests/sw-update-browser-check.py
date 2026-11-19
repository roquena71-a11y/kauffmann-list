"""Auditoría 2 (v17): actualización real en Chrome con service worker (no publica nada).
Sirve /tmp/swt/cur (enlace que cambiamos de versión) con Cache-Control: max-age=600 como GitHub Pages.
1) visita con v16 (la publicada) → 2) se publica v17 → al abrir de nuevo, ¿llega v17 sin que el usuario haga nada?
3) pestaña abierta con v17 → se publica «v18» → al volver a la pestaña (visibilitychange), ¿se recarga sola con v18?"""
import asyncio, os, time, json
from playwright.async_api import async_playwright
URL = 'http://localhost:8850/index.html?intro=0&lang=es'
def swap(t): os.system(f'ln -sfn {t} /tmp/swt/cur')
async def state(pg):
    try:
        return await asyncio.wait_for(pg.evaluate("""async()=>({sw: navigator.serviceWorker.controller ? (await caches.keys()).join(',') : 'none',
          v17: !!document.querySelector('#layersBtn'), v18: !!document.querySelector('meta[name=kl-test]'),
          status: (document.querySelector('#status')||{}).textContent})"""), 6)
    except Exception as e: return {'err': (str(e) or type(e).__name__)[:80]}  # p. ej. la página se está recargando sola
async def wait_for(pg, js, t=120):
    t0 = time.time()
    while time.time() - t0 < t:
        try:
            if await asyncio.wait_for(pg.evaluate(js), 6): return round(time.time() - t0, 1)
        except Exception: pass
        await asyncio.sleep(1)
    return None
async def main():
    out = {}
    swap('old')
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context('/tmp/swt/profile', executable_path='/usr/bin/google-chrome', headless=True,
              args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'], viewport={'width': 412, 'height': 915}, is_mobile=True, has_touch=True)
        pg = ctx.pages[0] if ctx.pages else await ctx.new_page()
        T0 = time.time(); navs = []
        pg.on('framenavigated', lambda f: f == pg.main_frame and navs.append([round(time.time() - T0, 1), f.url[-40:]]))
        await pg.goto(URL); await wait_for(pg, "navigator.serviceWorker.controller && DATA.length>60000", 120)
        await asyncio.sleep(3); out['1_v16_visit'] = await state(pg)
        await pg.goto('about:blank')
        swap('new')                                   # se publica v17
        await pg.goto(URL)
        out['2_first_paint_after_publish'] = await state(pg)
        t0 = time.time(); trace = []
        while time.time() - t0 < 300:
            st = await state(pg); trace.append([round(time.time() - t0), st.get('sw'), st.get('v17'), (st.get('status') or '')[:12]])
            if st.get('v17') and 'placas en' in (st.get('status') or ''): break
            await asyncio.sleep(3)
        out['2_trace'] = trace
        out['2_seconds_until_v17'] = trace[-1][0] if trace[-1][2] else None
        await asyncio.sleep(3); out['2_after'] = await state(pg)
        swap('new2')                                  # se publica «v18» con la pestaña abierta
        await asyncio.sleep(8)                         # deja terminar cualquier recarga pendiente
        out['2_navs'] = list(navs)
        for _ in range(3):
            try: await pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))"); break
            except Exception: await asyncio.sleep(3)
        out['3_seconds_until_v18'] = await wait_for(pg, "!!document.querySelector('meta[name=kl-test]') && DATA.length>60000", 150)
        await asyncio.sleep(3); out['3_after'] = await state(pg)
        # sin conexión: la última versión sigue abriendo
        await ctx.set_offline(True); await pg.reload()
        out['4_offline_seconds'] = await wait_for(pg, "DATA.length>60000", 90)
        out['4_offline'] = await state(pg)
        await ctx.close()
    swap('old')
    out['navs'] = navs
    print(json.dumps(out, ensure_ascii=False, indent=1))
    ok = out['2_seconds_until_v17'] is not None and out['3_seconds_until_v18'] is not None and out['4_offline_seconds'] is not None and 'v18' in out['3_after'].get('sw', '')
    print('sw-update-browser-check:', 'OK' if ok else 'FALLO')
asyncio.run(main())
