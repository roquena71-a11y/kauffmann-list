#!/usr/bin/env python3
"""v34 (v25-data sobre v33): fechas en conflicto y fotos añadidas, en el navegador.
  1. Carga: los sidecars (data/date-conflicts-v25.json, data/photos-added-v25.json) no retrasan el mapa; los créditos
     (data/photo-credits-v25.json) NO se piden hasta abrir una ficha con foto.
  2. Fechas: en cada choque del sidecar la ficha muestra la fecha de la INSCRIPCIÓN como principal y la otra como «otra fuente»
     (nunca se elige en silencio). Caso de Carlos: Anna Mayer (n13186756540) «1870» + «otra fuente: 1876-01-09 (…)».
  3. Fotos: las 1.621 del sidecar solo van a placas SIN img; ninguna img publicada cambia; la/lo de origen sin cambiar.
  4. Aviso visible SOLO en las 299 fotos añadidas cuyo nombre no habla de la placa (no en las 53.587 ya publicadas);
     contraste del aviso >= 4,5:1. Ejemplo: Carla Moses (Essen, n4176766678).
  5. Créditos CC: tras abrir la ficha, el pie de foto lleva autor y licencia del archivo de créditos (Commons).
  6. Las 680 fotos publicadas cuyo archivo ya no está en Commons se muestran igual que antes (sin «Sin foto todavía»).
  7. 0 peticiones al contador y 0 errores de página.
Uso: python3 tests/v34-photos-dates-check.py BASE_URL   (V34_SHOTS=dir guarda capturas de escritorio y teléfono)"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8899/'
CHROME = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
ANNA, WARNED = 'n13186756540', 'n4176766678'
SHOTS = os.environ.get('V34_SHOTS')

async def open_detail(pg, sid):
    await pg.evaluate("(id) => openStone(id)", sid)
    await pg.wait_for_function("(id) => selected === id && document.querySelector('#detail') && !document.querySelector('#detail').hidden", arg=sid, timeout=30000)
    await pg.wait_for_timeout(600)

async def main():
    fails = []
    def ok(c, m):
        if not c: fails.append(m)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        blocked, errs, reqs = [], [], []
        async def rh(r): blocked.append(r.request.url); await r.abort()
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block', locale='es-ES')
        pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('request', lambda r: reqs.append(r.url))
        await pg.route('**/*.workers.dev/**', rh); await pg.route('**/*kl-contador*', rh)
        await pg.goto(BASE + 'index.html?intro=0&lang=es&base=day', wait_until='domcontentloaded', timeout=180000)
        await pg.wait_for_function("typeof VISIBLE!=='undefined' && VISIBLE.length>70000 && window.map && map.loaded && map.loaded()", timeout=300000)
        await pg.wait_for_function("typeof SIDECARS_READY!=='undefined' && SIDECARS_READY", timeout=60000)
        ok(not [u for u in reqs if 'photo-credits' in u], 'créditos pedidos sin abrir ninguna ficha')
        r = await pg.evaluate(r"""async () => {
          const raw = await (await fetch('data/stones.json')).json();
          const orig = new Map(raw.stones.map(s => [s.id, s]));
          const ph = (await (await fetch('data/photos-added-v25.json')).json()).photos;
          const dc = (await (await fetch('data/date-conflicts-v25.json')).json()).conflicts;
          const out = {added: 0, addedIds: 0, replaced: [], moved: [], warned: new Set(), warnedExisting: [], notes: 0, noteStones: 0, silent: [], primaryNotInsc: []};
          for (const s of DATA){
            const o = orig.get(s.id);
            if (o){
              if (o.img && s.img !== o.img) out.replaced.push(s.id);
              const la = s.sla ?? s.la, lo = s.slo ?? s.lo;
              if (Math.abs(la - o.la) > 1e-12 || Math.abs(lo - o.lo) > 1e-12) out.moved.push(s.id);
            }
            if (s._imgAdded && ph[s.id] === s.img) out.addedIds++;
            const h = photoHtml(s);
            if (h.includes('photo-warn')){ if (s._imgAdded) out.warned.add(s.img + '|' + s.id); else out.warnedExisting.push(s.id); }
          }
          out.added = Object.keys(ph).filter(id => { const s = byId.get(id); return s && s.img === ph[id]; }).length;
          // ids del sidecar cuyo registro tenía foto antes: nunca se sustituye
          out.preHad = Object.keys(ph).filter(id => orig.get(id) && orig.get(id).img).length;
          // fechas: cada choque con valor de inscripción → principal = inscripción y nota «otra fuente»
          for (const [id, c] of Object.entries(dc)){
            const s = byId.get(id); if (!s) continue; let any = false;
            for (const f of ['birth', 'death']){
              const x = c[f]; if (!x || !x.insc) continue;
              const v = dateFactValue(s, f, f === 'birth' ? s.b : s.d);
              if (String(v.primary) !== String(x.insc)) out.primaryNotInsc.push(id + '.' + f);
              if (x.other && x.other_src){ if (!v.note) out.silent.push(id + '.' + f); else { out.notes++; any = true; } }
            }
            if (any) out.noteStones++;
          }
          out.warnedIds = [...out.warned].length; out.warnedFiles = new Set([...out.warned].map(x => x.split('|')[0])).size;
          out.warnedPhotoIds = Object.entries(ph).filter(([id, f]) => !looksLikeStonePhoto(f)).length;
          delete out.warned; out.replaced = out.replaced.slice(0, 5); out.moved = out.moved.slice(0, 5); out.warnedExisting = out.warnedExisting.slice(0, 5);
          out.silent = out.silent.slice(0, 5); out.primaryNotInsc = out.primaryNotInsc.slice(0, 5);
          return out; }""")
        ok(r['added'] == 1621, f'fotos añadidas visibles: {r["added"]} ≠ 1621')
        ok(r['preHad'] == 0 and not r['replaced'], f'se sustituyó una foto publicada: {r["replaced"]} (sidecar con img previa: {r["preHad"]})')
        ok(not r['moved'], f'la/lo de origen cambiados: {r["moved"]}')
        ok(r['warnedPhotoIds'] == 299, f'fotos añadidas con aviso según el nombre: {r["warnedPhotoIds"]} ≠ 299')
        ok(r['warnedIds'] >= 299 and not r['warnedExisting'], f'aviso: {r["warnedIds"]} registros; en fotos ya publicadas: {r["warnedExisting"]}')
        ok(not r['silent'] and not r['primaryNotInsc'], f'fecha elegida en silencio: {r["silent"]} / principal ≠ inscripción: {r["primaryNotInsc"]}')
        ok(r['notes'] > 1900, f'solo {r["notes"]} fechas con «otra fuente»')

        # Anna Mayer
        await open_detail(pg, ANNA)
        dd = await pg.evaluate("[...document.querySelectorAll('#detail dt')].map(d => [d.innerText, d.nextElementSibling ? d.nextElementSibling.innerText : ''])")
        born = [v for k, v in dd if k.strip().lower().startswith('nacim')]
        ok(born and born[0].startswith('1870') and 'otra fuente: 1876-01-09' in born[0].lower(), f'Anna Mayer: nacimiento «{born}»')
        if SHOTS:
            await pg.evaluate("() => { const e = document.querySelector('#detail dl'); if (e) e.scrollIntoView({block: 'center'}); }")
            await pg.wait_for_timeout(500)
            await pg.screenshot(path=os.path.join(SHOTS, 'v34-fecha-anna-mayer-1280x800.png'))
        # Carla Moses: aviso + crédito
        await open_detail(pg, WARNED)
        await pg.wait_for_function("document.querySelector('#detail figure.photo figcaption') && document.querySelector('#detail figure.photo figcaption').innerText.startsWith('Foto:')", timeout=60000)
        w = await pg.evaluate(r"""() => { const e = document.querySelector('#detail .photo-warn'); if (!e) return null;
          const cs = getComputedStyle(e), r = e.getBoundingClientRect();
          const rgb = t => t.match(/\d+(\.\d+)?/g).slice(0, 3).map(Number);
          const L = c => { const v = c.map(x => x / 255).map(x => x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4)); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
          const a = L(rgb(cs.color)), b2 = L(rgb(cs.backgroundColor));
          return {text: e.innerText, visible: r.width > 50 && r.height > 10 && cs.display !== 'none' && cs.visibility !== 'hidden', cr: (Math.max(a, b2) + 0.05) / (Math.min(a, b2) + 0.05),
                  cap: document.querySelector('#detail figure.photo figcaption').innerText, img: byId.get('""" + WARNED + r"""').img}; }""")
        ok(w and w['visible'] and 'puede que esta foto no muestre la placa' in w['text'], f'Carla Moses: aviso {w}')
        ok(w and w['cr'] >= 4.5, f'contraste del aviso {w and w["cr"]:.2f} < 4,5')
        cred = await pg.evaluate("async (f) => { const c = (await (await fetch('data/photo-credits-v25.json')).json()).credits; return c[f] || c[f.replace(/_/g, ' ')] || null; }", w['img'] if w else '')
        ok(cred and cred.get('a') and cred['a'] in w['cap'] and cred.get('l') and cred['l'] in w['cap'], f'Carla Moses: crédito «{w and w["cap"]}» ≠ {cred}')
        if SHOTS:
            await pg.evaluate("() => { const e = document.querySelector('#detail figure.photo'); if (e) e.scrollIntoView({block: 'center'}); }")
            await pg.wait_for_timeout(2500)
            await pg.screenshot(path=os.path.join(SHOTS, 'v34-aviso-carla-moses-1280x800.png'))
        # una foto publicada sin aviso, con crédito; y una de las 680 (archivo ya no en Commons) igual que antes
        r680 = await pg.evaluate("""async () => { const c = (await (await fetch('data/photo-credits-v25.json')).json()).credits;
          let gone = 0, goneShown = 0, ex = null, pub = null;
          for (const s of VISIBLE){ if (!s.img || s._imgAdded) continue; const rec = c[s.img] || c[s.img.replace(/_/g, ' ')], has = rec && (rec.a || rec.l);
            if (!has){ gone++; const h = photoHtml(s); if (h.includes('<figure') && !h.includes('photo-warn') && !/Sin foto/.test(h)) goneShown++; if (!ex) ex = s.id; }
            else if (!pub && /stolperstein/i.test(s.img)) pub = s.id; }
          return {gone, goneShown, ex, pub}; }""")
        ok(r680['gone'] >= 600 and r680['gone'] == r680['goneShown'], f'fotos publicadas sin archivo en Commons: {r680}')
        await open_detail(pg, r680['pub'])
        cap = await pg.evaluate("async () => { for (let k = 0; k < 50; k++){ const f = document.querySelector('#detail figure.photo figcaption'); if (f && !f.innerText.startsWith('Foto de la placa')) return [f.innerText, !!document.querySelector('#detail .photo-warn')]; await new Promise(r => setTimeout(r, 100)); } return null; }")
        ok(cap and 'Foto:' in cap[0] and not cap[1], f'foto publicada: pie «{cap}» (sin aviso)')
        # teléfono
        if SHOTS:
            ph = await (await b.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True, device_scale_factor=2, service_workers='block', locale='es-ES')).new_page()
            await ph.route('**/*.workers.dev/**', rh); await ph.route('**/*kl-contador*', rh)
            await ph.goto(BASE + 'index.html?intro=0&lang=es&base=day', wait_until='domcontentloaded', timeout=180000)
            await ph.wait_for_function("typeof VISIBLE!=='undefined' && VISIBLE.length>70000 && window.map && map.loaded && map.loaded()", timeout=300000)
            for sid, name in [(ANNA, 'fecha-anna-mayer'), (WARNED, 'aviso-carla-moses')]:
                await open_detail(ph, sid)
                await ph.evaluate("() => { if (window.KLUI && KLUI.setSheet) KLUI.setSheet('full'); }")
                await ph.wait_for_timeout(2500)
                sel = '#detail dl' if sid == ANNA else '#detail figure.photo'
                await ph.evaluate("(s) => { const e = document.querySelector(s); if (e) e.scrollIntoView({block: 'center'}); }", sel)
                await ph.wait_for_timeout(1500)
                await ph.screenshot(path=os.path.join(SHOTS, f'v34-{name}-390x844.png'))
        ok(not errs, f'errores de página: {errs[:3]}')
        await b.close()
    if fails:
        print('FAIL v34-photos-dates:'); [print('  -', f) for f in fails]; sys.exit(1)
    print(f'OK v34-photos-dates: {r["added"]} fotos añadidas (solo donde no había img; 0 sustituidas; la/lo sin cambiar); aviso en {r["warnedPhotoIds"]} fotos '
          f'nuevas ({r["warnedIds"]} registros, {r["warnedFiles"]} archivos), 0 en fotos ya publicadas, contraste {w["cr"]:.2f}:1; '
          f'{r["notes"]} fechas con «otra fuente» en {r["noteStones"]} placas, 0 en silencio; Anna Mayer «{born[0][:60]}»; '
          f'crédito «{w["cap"][:70]}»; {r680["gone"]} fotos publicadas sin archivo en Commons, igual que antes; contador bloqueado ({len(blocked)})')
asyncio.run(main())
