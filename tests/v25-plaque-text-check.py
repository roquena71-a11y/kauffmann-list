#!/usr/bin/env python3
"""v25 (paso 3): la inscripción escrita en la placa de latón de cada columna (capa WebGL 'plaque-text', plaquetext.js).
Comprueba en el navegador:
  1. Carga perezosa: plaquetext.js NO se pide en la carga inicial ni a zoom 19; sí al pasar de 19,5.
  2. Umbrales por tamaño de la placa en pantalla (escritorio 1280x800): z20,2 (≈35 px) → nada; z20,8 (≈85 px) → solo el nombre;
     z21,2 (≈170 px) → la inscripción entera; z21,6 → la cámara queda a la altura de las placas (16 m) → nada, surcos de vuelta.
  3. Solo placas en vista (± 15 %), como mucho 60; nunca la ficha abierta.
  4. Nada inventado: cada placa escrita tiene campo i, y sus palabras son exactamente las de i en mayúsculas (texto completo)
     o un trozo literal de i (nombre). Las placas sin i nunca se escriben (comprobado sobre TODAS las placas cargadas).
  5. Orientación: el cuadro de texto gira con la placa (_ang de align-v24, múltiplos de 90°), cabe dentro de la cara,
     y queda «derecho» en pantalla (también con el mapa girado).
  6. Los surcos finos se ocultan solo donde hay texto (filtro de 'stones-grooves').
  7. Se ve: captura con la capa visible ≠ oculta; las letras son oscuras (contraste WCAG >= 4,5 con la cara #d6b25a).
  8. 0 peticiones al contador (bloqueadas) y 0 errores de página.
Uso: python3 tests/v25-plaque-text-check.py BASE_URL"""
import asyncio, base64, math, os, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8899/'
CHROME = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
SPOT = ['Q131924672', 'Q131924669', 'Q131924674', 'Q131924675']   # Westendstraße 82 (Frankfurt), 4 placas con inscripción

async def main():
    fails = []
    def ok(c, m):
        if not c: fails.append(m)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        pg = await (await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block', locale='es-ES')).new_page()
        blocked, errs, reqs = [], [], []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('request', lambda r: reqs.append(r.url))
        async def rh(r): blocked.append(r.request.url); await r.abort()
        await pg.route('**/*.workers.dev/**', rh); await pg.route('**/*kl-contador*', rh)
        await pg.goto(BASE + 'index.html?intro=0&lang=es&base=day', wait_until='domcontentloaded', timeout=180000)
        await pg.wait_for_function("typeof VISIBLE!=='undefined' && VISIBLE.length>70000 && window.map && map.loaded && map.loaded() && (!window.KLAlign || KLAlign.ready)", timeout=300000)
        await pg.wait_for_timeout(1500)
        pt = lambda: [u for u in reqs if 'plaquetext.js' in u]
        ok(not pt(), f'plaquetext.js pedido en la carga inicial: {pt()}')
        ok(await pg.evaluate("!window.KLPlaqueText"), 'KLPlaqueText presente en la carga inicial')

        async def go(z, bearing=0, pitch=0, lift=False):
            return await pg.evaluate("""async ([ids, z, br, pi, lift]) => {
              const ss = ids.map(id => byId.get(id)).filter(Boolean);
              const la = ss.reduce((a,s)=>a+s._dla,0)/ss.length, lo = ss.reduce((a,s)=>a+s._dlo,0)/ss.length;
              // lift: centrar la vista en las CARAS (16,42 m), no en el pie: con inclinación p el rayo central toca el suelo
              // 16,42·tan(p) m más allá de la columna, en la dirección del rumbo.
              let cla = la, clo = lo;
              if (lift){ const d = 16.42 * Math.tan(pi * Math.PI / 180), b = br * Math.PI / 180;
                cla = la + d * Math.cos(b) / 111320; clo = lo + d * Math.sin(b) / (111320 * Math.cos(la * Math.PI / 180)); }
              map.jumpTo({center:[clo, cla], zoom:z, pitch:pi, bearing:br});
              if (window.KLCols && KLCols.finish) KLCols.finish();
              await new Promise(r => { map.once('idle', r); setTimeout(r, 8000); });
              for (let k = 0; k < 60 && window.KLPlaqueText === undefined && map.getZoom() >= 19.5; k++) await new Promise(r => setTimeout(r, 100));
              if (window.KLPlaqueText){ KLPlaqueText.refresh(); map.triggerRepaint(); await new Promise(r => { map.once('idle', r); setTimeout(r, 8000); }); }
              return ss.length;
            }""", [SPOT, z, bearing, pitch, lift])

        n = await go(19.0)
        ok(n == 4, f'placas de prueba no encontradas ({n}/4)')
        ok(not pt(), 'plaquetext.js pedido a zoom 19 (< 19,5)')
        await go(20.2)
        ok(len(pt()) == 1, f'plaquetext.js no pedido (o pedido {len(pt())} veces) a zoom 20,2')
        ok('?v=' in (pt() or [''])[0], 'plaquetext.js sin ?v= (caché del service worker)')
        s0 = await pg.evaluate("KLPlaqueText.state()")
        ok(s0['drawn'] == 0 and s0['skipped'] == 'pequena', f'a zoom 20,2 no debe escribirse nada: {s0["drawn"]} {s0["skipped"]} {s0.get("facePx")} px')

        CHECK = """(mode) => {
          const st = KLPlaqueText.state(), P = KLPlaqueText, K = KLCols.state(), b = map.getBounds(), out = [];
          const pl = (b.getEast()-b.getWest())*0.16, pa = (b.getNorth()-b.getSouth())*0.16;
          const up = t => String(t).toLocaleUpperCase('de-DE'), W = t => up(t).split(/[\\s|]+/).filter(Boolean).join(' ');
          const flt = JSON.stringify(map.getFilter('stones-grooves') || []);
          for (const q of st.quads){
            const s = byId.get(q.id), i = P.inscOf(s);
            if (!i){ out.push(q.id + ': escrita sin campo i'); continue; }
            if (q.id === selected) out.push(q.id + ': escrita la ficha abierta');
            if (s._dla < b.getSouth()-pa || s._dla > b.getNorth()+pa || s._dlo < b.getWest()-pl || s._dlo > b.getEast()+pl) out.push(q.id + ': fuera de vista');
            const txt = q.lines.join(' ').split(/\\s+/).filter(Boolean).join(' ');
            if (mode === 'full' && txt !== W(i)) out.push(q.id + ': texto ≠ i en mayúsculas: ' + txt.slice(0, 80));
            if (mode === 'name'){ const n = P.nameLine(s); if (!n || !String(i).includes(n) || txt !== W(n)) out.push(q.id + ': nombre no literal de i: ' + txt); }
            const d = ((q.a - (s._ang || 0)) / (Math.PI / 2)); if (Math.abs(d - Math.round(d)) > 1e-6) out.push(q.id + ': no gira con la placa');
            if (q.half * Math.SQRT2 > K.faceHalf * Math.SQRT2 - 0.01 || q.half > K.faceHalf - 0.02) out.push(q.id + ': el texto se sale de la cara');
            if (q.up < Math.SQRT1_2 - 1e-6) out.push(q.id + ': texto torcido en pantalla (' + q.up.toFixed(2) + ')');
            if (Math.abs(q.z - (K.faceTop + 0.005)) > 0.002) out.push(q.id + ': altura ' + q.z);
            if (!flt.includes(q.id)) out.push(q.id + ': surcos no ocultos bajo el texto');
          }
          for (const id of KLCols.state().textIds || []) if (!st.ids.includes(id)) out.push(id + ': surcos ocultos sin texto');
          return {st: {drawn: st.drawn, mode: st.mode, skipped: st.skipped, inView: st.inView.length, textures: st.textures, facePx: st.facePx}, out, flt: flt.length};
        }"""
        async def seen(z, br, pi, tag):
            await go(z, br, pi, lift=pi > 0)
            st = await pg.evaluate("KLPlaqueText.state()")
            on = await pg.screenshot(type='png')
            if os.environ.get('V25_TEXT_SHOTS'): open(os.path.join(os.environ['V25_TEXT_SHOTS'], f'check-{tag}.png'), 'wb').write(on)
            await pg.evaluate("() => { map.setLayoutProperty('plaque-text', 'visibility', 'none'); map.triggerRepaint(); }")
            await pg.wait_for_timeout(1200)
            off = await pg.screenshot(type='png')
            await pg.evaluate("() => { map.setLayoutProperty('plaque-text', 'visibility', 'visible'); map.triggerRepaint(); }")
            px = await pg.evaluate("""async ([a, b]) => {
              const load = u => new Promise(r => { const im = new Image(); im.onload = () => r(im); im.src = u; });
              const [A, B] = await Promise.all([load(a), load(b)]); const cv = document.createElement('canvas'); cv.width = A.width; cv.height = A.height;
              const g = cv.getContext('2d'); g.drawImage(A, 0, 0); const da = g.getImageData(0, 0, cv.width, cv.height).data; g.drawImage(B, 0, 0); const db = g.getImageData(0, 0, cv.width, cv.height).data;
              let diff = 0, dark = 0, x0 = 1e9, y0 = 1e9, x1 = -1, y1 = -1; const W = cv.width;
              for (let k = 0; k < da.length; k += 4){ const d = Math.abs(da[k]-db[k]) + Math.abs(da[k+1]-db[k+1]) + Math.abs(da[k+2]-db[k+2]);
                if (d > 30){ diff++; const q = k / 4, x = q % W, y = (q - x) / W; x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); if (da[k] + da[k+1] + da[k+2] < db[k] + db[k+1] + db[k+2]) dark++; } }
              return {diff, dark, x0, y0, x1, y1};
            }""", ['data:image/png;base64,' + base64.b64encode(on).decode(), 'data:image/png;base64,' + base64.b64encode(off).decode()])
            box = await pg.evaluate("(() => { const r = map.getCanvas().getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; })()")
            inside = px['x0'] >= box[0] - 1 and px['y0'] >= box[1] - 1 and px['x1'] <= box[2] + 1 and px['y1'] <= box[3] + 1
            ok(st['drawn'] >= 3, f'{tag}: solo {st["drawn"]} placas escritas')
            ok(px['diff'] > 500, f'{tag}: la capa no cambia la imagen ({px["diff"]} píxeles): el texto no se ve')
            ok(px['dark'] > 0.6 * max(1, px['diff']), f'{tag}: las letras no son más oscuras que la cara ({px["dark"]}/{px["diff"]})')
            ok(inside, f'{tag}: cambios fuera del mapa {px}')
            px['mode'] = st['mode']; px['drawn'] = st['drawn']; px['facePx'] = st.get('facePx')
            return px
        res = {}
        for z, mode, br, pi in [(20.8, 'name', 0, 0), (21.2, 'full', 0, 0), (21.2, 'full', 100, 0), (20.6, 'name', 30, 35)]:
            await go(z, br, pi, lift=pi > 0)
            r = await pg.evaluate(CHECK, mode)
            res[(z, br, pi)] = r['st']
            ok(r['st']['mode'] == mode, f'z{z}: modo {r["st"]["mode"]} ≠ {mode}')
            ok(r['st']['drawn'] >= 3, f'z{z} rumbo {br}: solo {r["st"]["drawn"]} placas escritas')
            ok(r['st']['inView'] <= 60, f'z{z}: {r["st"]["inView"]} placas en vista (> 60)')
            fails.extend(f'z{z} rumbo {br}: {m}' for m in r['out'][:10])

        # v32: inscripciones con marcado (<br />, '''…''', [[…|…]], &#…;, <b> como separador): limpias en la ficha y en la placa
        mk = await pg.evaluate("""async (ids) => { const out = [];
          for (const id of ids){ openStone(id); await new Promise(r => setTimeout(r, 400));
            const bp = [...document.querySelectorAll('.brassplate')], txt = bp.map(e => e.innerText).join('\\n'), html = bp.map(e => e.innerHTML).join('');
            const plate = (KLPlaqueText.linesFor(byId.get(id), 'full') || []).join(' / ');
            const bad = /<|\'\'\'|\\[\\[|\\]\\]|&#|&nbsp;/;
            out.push({id, ok: bp.length > 0 && !bad.test(txt) && !/&lt;|&amp;#/.test(html) && !bad.test(plate), lines: txt.split('\\n').filter(Boolean).length, txt: txt.slice(0, 90), plate: plate.slice(0, 90)});
            if (typeof closeDetail === 'function') closeDetail(); }
          return out; }""", ['n2432838644', 'n8572696652', 'Q73391789', 'Q132183676'])
        for m in mk: ok(m['ok'], f"marcado visible en {m['id']}: ficha «{m['txt']}» placa «{m['plate']}»")
        ok(mk[0]['lines'] >= 5 and mk[1]['lines'] >= 4, f"<br>/<b> no son saltos de línea en la ficha: {[(m['id'], m['lines']) for m in mk[:2]]}")
        # ficha abierta: esa placa no se escribe (la ficha muestra la placa grande)
        await pg.evaluate("(id) => { const s = byId.get(id); openStone(id); map.triggerRepaint(); }", SPOT[0])
        await pg.wait_for_timeout(800)
        sel_ids = await pg.evaluate("KLPlaqueText.state().ids")
        ok(SPOT[0] in sel_ids, 'la placa de la ficha abierta no se escribe (v35 C1: el seleccionado también lleva texto)')
        await pg.evaluate("() => { if (typeof closeDetail === 'function') closeDetail(); else selected = null; map.triggerRepaint(); }")
        await go(21.6, 0, 0)
        cb = await pg.evaluate("[KLPlaqueText.state(), KLCols.state().textIds]")
        ok(cb[0]['drawn'] == 0 and cb[0]['skipped'] == 'camara' and not cb[1], f'z21,6 (cámara a la altura de las placas): {cb[0]["drawn"]} {cb[0]["skipped"]} {cb[0].get("camAlt")} m; surcos ocultos {len(cb[1])}')

        # nada inventado en TODAS las placas cargadas: sin i → no hay textura
        blank = await pg.evaluate("""() => { let n = 0, bad = []; for (const s of DATA){ if (KLPlaqueText.inscOf(s)) continue; n++;
            for (const m of ['name','full']) if (KLPlaqueText._paint(s, m) !== null) bad.push(s.id); } return {n, bad: bad.slice(0,5)}; }""")
        ok(blank['n'] > 1000 and not blank['bad'], f'placas sin i con texto: {blank}')

        # se ve: visible vs oculta, y letras oscuras — en planta (z21,2) y con el mapa INCLINADO 35° y girado 30° (z20,6),
        # con la vista centrada en las caras para que las placas estén dentro de la imagen
        px = await seen(21.2, 0, 0, 'planta')
        pxt = await seen(20.6, 30, 35, 'inclinado')
        cr = await pg.evaluate("KLPlaqueText.contrast(KLPlaqueText.INK, KLPlaqueText.FACE)")
        ok(cr >= 4.5, f'contraste {cr:.2f} < 4,5')
        ok(not errs, f'errores de página: {errs[:3]}')
        ok(not [u for u in reqs if ('workers.dev' in u or 'kl-contador' in u) and u not in blocked], 'petición al contador no bloqueada')
        await b.close()
    if fails:
        print('FAIL v25-plaque-text:'); [print('  -', f) for f in fails]; sys.exit(1)
    print(f'OK v25-plaque-text: perezoso (no en la carga ni a z19); z20,2 nada; z20,8 nombre ({res[(20.8,0,0)]["drawn"]} placas); '
          f'z21,2 inscripción ({res[(21.2,0,0)]["drawn"]}; girado 100°: {res[(21.2,100,0)]["drawn"]}; inclinado 35°/girado 30° a z20,6: {res[(20.6,30,35)]["drawn"]}); z21,6 cámara a la altura de las placas → nada; texto = i en mayúsculas, '
          f'gira con la placa y cabe en la cara; surcos ocultos solo bajo texto; {blank["n"]} placas sin i siempre lisas; '
          f'se ve en planta ({px["diff"]} píxeles cambian, {px["dark"]} más oscuros) e inclinado 35° ({pxt["diff"]} / {pxt["dark"]}, modo {pxt["mode"]}, cara {pxt["facePx"]} px); marcado HTML/wiki limpio en ficha y placa ({len(mk)} casos); contraste {cr:.2f}:1; contador bloqueado ({len(blocked)})')

asyncio.run(main())
