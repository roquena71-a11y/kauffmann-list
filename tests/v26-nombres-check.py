#!/usr/bin/env python3
"""v35 (C1–C3): visibilidad de nombres en la placa.
  C1: al seleccionar, se queda la columna de oro con placa y texto; no hay fuste pálido #fff3c4 de 34/400 m;
      el resalte es un marco de oro (~16,5 m) + resplandor; a z<14,6 un halo (que pulsa).
  C2: en teléfono 412×915, inclinación 42°, los nombres salen hacia z20,2 (cara ≈ 31 px).
  C3: en el mismo viewport, z21,6 a 42° (cámara ~0,7 m sobre la cara) el texto se ve; no solo surcos.
Uso: python3 tests/v26-nombres-check.py BASE_URL   (V26_SHOTS=dir guarda capturas pequeñas JPEG)"""
import asyncio, os, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8899/'
CHROME = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
SHOTS = os.environ.get('V26_SHOTS')
SONABEND = ['n12825380212', 'n12825380213', 'n12825380214', 'n12825380215']
MASACCIO = ['fi-324267_1', 'fi-324267_2', 'fi-324267_3', 'fi-324267_4']
PALMERO, SARA = 'n12848781720', 'Q133289206'

async def boot(ctx, base, lang='es'):
    pg = await ctx.new_page()
    blocked, errs, reqs = [], [], []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('request', lambda r: reqs.append(r.url))
    async def rh(r): blocked.append(r.request.url); await r.abort()
    await pg.route('**/*.workers.dev/**', rh); await pg.route('**/*kl-contador*', rh)
    await pg.goto(BASE + f'index.html?intro=0&lang={lang}&base={base}', wait_until='domcontentloaded', timeout=180000)
    await pg.wait_for_function("typeof VISIBLE!=='undefined' && VISIBLE.length>70000 && window.map && map.loaded && map.loaded() && (!window.KLAlign || KLAlign.ready)", timeout=300000)
    if await pg.evaluate("typeof KLUI!=='undefined' && KLUI.setSheet"):
        await pg.evaluate("KLUI.setSheet('collapsed')")
    return pg, blocked, errs, reqs

async def go(pg, ids, z, pitch=0, bearing=0, select=None, lift=False, fly=True):
    return await pg.evaluate("""async ([ids, z, pi, br, sel, lift, fly]) => {
      const ss = ids.map(id => byId.get(id)).filter(Boolean);
      if (!ss.length) return {n: 0};
      const la = ss.reduce((a,s)=>a+s._dla,0)/ss.length, lo = ss.reduce((a,s)=>a+s._dlo,0)/ss.length;
      let cla = la, clo = lo;
      if (lift){ const d = 16.42 * Math.tan(pi * Math.PI / 180), b = br * Math.PI / 180;
        cla = la + d * Math.cos(b) / 111320; clo = lo + d * Math.sin(b) / (111320 * Math.cos(la * Math.PI / 180)); }
      map.jumpTo({center:[clo, cla], zoom:z, pitch:pi, bearing:br});
      if (window.KLCols && KLCols.finish) KLCols.finish();
      if (window.KLUI && KLUI.setSheet) KLUI.setSheet('collapsed');
      if (sel){ if (fly) openStone(sel, true); else { selected = sel; refreshSel(); } }
      else if (typeof closeDetail === 'function') closeDetail();
      if (window.KLUI && KLUI.setSheet) KLUI.setSheet('collapsed');
      await new Promise(r => { map.once('idle', r); setTimeout(r, 8000); });
      for (let k = 0; k < 50 && window.KLPlaqueText === undefined && map.getZoom() >= 19; k++) await new Promise(r => setTimeout(r, 100));
      if (window.KLPlaqueText){ KLPlaqueText.refresh(); map.triggerRepaint(); await new Promise(r => { map.once('idle', r); setTimeout(r, 6000); }); }
      const st = window.KLPlaqueText ? KLPlaqueText.state() : {drawn:0, ids:[], skipped:'no-layer', mode:null};
      const src = map.getSource('sel'); const data = (src && src.serialize && src.serialize().data) || {features:[]};
      const polys = (data.features || []).filter(f => f.geometry && f.geometry.type === 'Polygon');
      const hs = polys.map(f => f.properties && f.properties.h);
      const paint = map.getLayer('sel') && map.getPaintProperty('sel', 'fill-extrusion-color');
      const flt = map.getFilter('stones') || (window.KLCols && KLCols.state && 'see-cols');
      const hidden = window.KLCols && map.getFilter('stones-2');
      return {n: ss.length, st, hs, paint, sel: selected, hidden, glow: !!map.getLayer('sel-glow'),
              camAlt: st.camAlt, facePx: st.facePx, backend: st.backend};
    }""", [ids, z, pitch, bearing, select, lift, fly])

async def shot(pg, name):
    if not SHOTS: return
    os.makedirs(SHOTS, exist_ok=True)
    await pg.screenshot(path=os.path.join(SHOTS, name), type='jpeg', quality=78)

async def main():
    fails = []
    def ok(c, m):
        if not c: fails.append(m)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        # --- escritorio ---
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block', locale='es-ES')
        pg, blocked, errs, reqs = await boot(ctx, 'day')
        # C1: z20,8 seleccionado — texto en Simon, sin fuste de 34 m, color no #fff3c4
        r = await go(pg, SONABEND, 20.8, 0, 0, 'n12825380212')
        ok(r['n'] == 4, f'Sonabend no encontrado ({r["n"]})')
        ok('n12825380212' in (r['st'].get('ids') or []), f'C1: Simon seleccionado sin texto: {r["st"]}')
        ok(r['st'].get('drawn', 0) >= 3, f'C1: solo {r["st"].get("drawn")} placas escritas')
        ok(r['hs'] and max(r['hs']) <= 17 and min(r['hs']) >= 15, f'C1: altura del resalte {r["hs"]} (se esperaba ~16,5 m, no 34/400)')
        col = r['paint'] if isinstance(r['paint'], str) else (r['paint'][-1] if isinstance(r['paint'], list) else r['paint'])
        ok(col and 'fff3c4' not in str(col).lower() and 'fff3c4' not in str(r['paint']).lower(), f'C1: color pálido aún presente: {r["paint"]}')
        ok(r['hidden'] in (None, False) or r['hidden'] == [], f'C1: la placa sigue filtrada: {r["hidden"]}')
        await shot(pg, 'despues-sonabend-z208-sel-1280x800.jpg')
        # z18 seleccionado: columna real, marco ≤17 m (no palo de 34 m)
        r18 = await go(pg, SONABEND, 18, 50, 0, 'n12825380212')
        ok((not r18['hs']) or max(r18['hs']) <= 17, f'C1 z18: fuste alto {r18["hs"]}')
        await shot(pg, 'despues-sonabend-z18-sel-1280x800.jpg')
        # zoom bajo: halo, sin fuste de 400 m
        r13 = await go(pg, SONABEND, 13, 0, 0, 'n12825380212', fly=False)
        ok(not r13['hs'], f'C1 z13: aún hay polígono de resalte {r13["hs"]}')
        ok(r13['glow'], 'C1 z13: falta el halo sel-glow')
        # inscripción completa cenital
        rfull = await go(pg, SONABEND, 21.2, 0, 0, None)
        ok(rfull['st'].get('mode') == 'full' and rfull['st'].get('drawn', 0) >= 3, f'inscripción completa: {rfull["st"]}')
        await shot(pg, 'despues-sonabend-z212-full-1280x800.jpg')
        # Masaccio + Palmero: seleccionado con texto, sin fuste alto
        rm = await go(pg, MASACCIO, 20.8, 0, 0, 'fi-324267_4')
        ok('fi-324267_4' in (rm['st'].get('ids') or []) and (not rm['hs'] or max(rm['hs']) <= 17), f'Masaccio: {rm["st"]} h={rm["hs"]}')
        await shot(pg, 'despues-masaccio-z208-sel-1280x800.jpg')
        rp = await go(pg, [PALMERO], 20.8, 0, 0, PALMERO)
        ok(PALMERO in (rp['st'].get('ids') or []) and (not rp['hs'] or max(rp['hs']) <= 17), f'Palmero: {rp["st"]} h={rp["hs"]}')
        await shot(pg, 'despues-palmero-z208-sel-1280x800.jpg')
        # C3 escritorio z21,6 cenital: cámara a la altura de las placas → nada
        cb = await go(pg, SONABEND, 21.6, 0, 0, None)
        # already took full at 21.6 pitch 0 — on desktop 1280, z21.6 is at plaque height (camara). Recheck:
        # (the full shot above may have been 'full' or 'camara' depending on exact altitude)
        # C3 is about tilted close-ups; desktop nadir z21.6 historically is 'camara'. Don't fail if full shows — CAM_CLEAR only hides when <=0.25m
        await ctx.close()

        # --- teléfono 412×915 (como el diagnóstico) ---
        ctxp = await b.new_context(viewport={'width': 412, 'height': 915}, is_mobile=True, has_touch=True, device_scale_factor=2, service_workers='block', locale='es-ES')
        pp, blocked2, errs2, reqs2 = await boot(ctxp, 'day')
        blocked += blocked2; errs += errs2; reqs += reqs2
        # C2: z20,2 pitch 42 → nombres
        c2 = await go(pp, SONABEND, 20.2, 42, 0, None, lift=True)
        ok(c2['st'].get('mode') == 'name' and c2['st'].get('drawn', 0) >= 3, f'C2 teléfono z20,2 p42: {c2["st"]}')
        await shot(pp, 'despues-sonabend-z202-p42-412x915.jpg')
        # C1 + C2: seleccionado a z20,8 p42 con nombre
        c1p = await go(pp, SONABEND, 20.8, 42, 0, 'n12825380212', lift=True)
        ok('n12825380212' in (c1p['st'].get('ids') or []), f'C1 teléfono: Simon sin texto {c1p["st"]}')
        ok((not c1p['hs']) or max(c1p['hs']) <= 17, f'C1 teléfono: fuste alto {c1p["hs"]}')
        await shot(pp, 'despues-sonabend-z208-sel-412x915.jpg')
        # C3: z21,6 p42 — texto visible (antes CAM_CLEAR 1 m lo apagaba a 0,68 m)
        c3 = await go(pp, SONABEND, 21.6, 42, 0, 'n12825380212', lift=True)
        ok(c3['st'].get('drawn', 0) >= 1 and c3['st'].get('skipped') != 'camara', f'C3 teléfono z21,6 p42: {c3["st"]}')
        await shot(pp, 'despues-sonabend-z216-p42-sel-412x915.jpg')
        rm = await go(pp, MASACCIO, 20.8, 42, 0, 'fi-324267_4', lift=True)
        ok(rm['st'].get('drawn', 0) >= 2, f'Masaccio teléfono: {rm["st"]}')
        await shot(pp, 'despues-masaccio-z208-sel-412x915.jpg')
        await ctxp.close()

        # Sara Franco noche (como la foto de Carlos)
        ctxn = await b.new_context(viewport={'width': 412, 'height': 915}, is_mobile=True, has_touch=True, device_scale_factor=2, service_workers='block', locale='es-ES')
        pn, b3, e3, r3 = await boot(ctxn, 'night')
        blocked += b3; errs += e3; reqs += r3
        rs = await go(pn, [SARA], 21.2, 0, 0, SARA)
        ok(SARA in (rs['st'].get('ids') or []), f'Sara noche seleccionada sin texto: {rs["st"]}')
        ok((not rs['hs']) or max(rs['hs']) <= 17, f'Sara noche: fuste alto {rs["hs"]}')
        await shot(pn, 'despues-sara-noche-z212-sel-412x915.jpg')
        await ctxn.close()
        ok(not errs, f'errores de página: {errs[:3]}')
        ok(not [u for u in reqs if ('workers.dev' in u or 'kl-contador' in u) and u not in blocked], 'petición al contador no bloqueada')
        await b.close()
    if fails:
        print('FAIL v26-nombres:'); [print('  -', f) for f in fails]; sys.exit(1)
    print('OK v26-nombres: C1 seleccionado con texto y marco de oro ~16,5 m (0 fustes 34/400 m, color no #fff3c4) en Sonabend, Masaccio y Palmero; '
          'halo a z13; C2 teléfono 412×915 p42 z20,2 modo nombre; C3 z21,6 p42 texto visible; Sara noche seleccionada con nombre; '
          f'contador bloqueado ({len(blocked)})')

asyncio.run(main())
