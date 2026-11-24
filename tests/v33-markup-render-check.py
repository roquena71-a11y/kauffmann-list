#!/usr/bin/env python3
"""v33: ningún texto de datos se PINTA con marcado HTML/wiki literal (<br />, <b>, '''…''', [[…|…]], «]]» suelto, &#8218; &shy; …).
Auditoría C, ronda 2 (F1): la línea «según la inscripción» (#inscDates) pintaba trozos de data/bio/*.json con <br />.
Comprueba en el navegador, con el texto que de verdad queda en pantalla (innerText):
  1. Mapa 3D: abre la ficha de CADA placa cuyo texto de origen lleva marcado (campo i y registros fusionados, dirección,
     descripción, aviso de dirección, trozos de fecha de data/bio, historia de data/bio/text) y espera a la historia:
     la ficha entera (cabecera, placa de latón, línea de fechas, datos, historia) no muestra marcado.
     Walter Rosenbaum (Dorsten, n2432838644): la línea de fechas dice «… deportiert 1942 · ermordet 1943 in Auschwitz».
  2. Lista de resultados 3D para esas placas (búsqueda por id → nombre) sin marcado.
  3. Mapa 2D: la ventana (popup) de TODAS las placas y la lista de resultados, sin marcado.
  4. Los datos no cambian (data/ se lee tal cual; el campo i de origen sigue con su marcado).
  5. 0 peticiones al contador (bloqueadas) y 0 errores de página.
Uso: python3 tests/v33-markup-render-check.py BASE_URL   (V25_TEXT_SHOTS=dir guarda la ficha de Rosenbaum)"""
import asyncio, glob, json, os, re, sys
from playwright.async_api import async_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8899/'
CHROME = os.environ.get('CHROME_BIN', '/usr/bin/google-chrome')
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
MK = re.compile(r"<\/?[a-z][a-z0-9]*(?:\s[^<>]*)?\/?>|'''|\[\[|\]\]|&(#x?[0-9a-f]+|[a-z]+);", re.I)
ROSEN = 'n2432838644'

def marked_ids():
    ids = set()
    files = [os.path.join(ROOT, 'data', 'stones.json')] + sorted(glob.glob(os.path.join(ROOT, 'data', '*-added-2026112*.json')))
    for f in files:
        for s in json.load(open(f, encoding='utf-8')).get('stones', []):
            recs = [s] + list(s.get('_also') or [])
            vals = [r.get('i') for r in recs] + [s.get(k) for k in ('n', 'a', 'b', 'd', 'desc', 'sub', 'laid')] + [(s.get('disc') or {}).get('alt')]
            if any(isinstance(v, str) and MK.search(v) for v in vals): ids.add(s['id'])
    for f in glob.glob(os.path.join(ROOT, 'data', 'bio', '*.json')):
        for sid, rec in (json.load(open(f, encoding='utf-8')) or {}).items():
            ins = (rec or {}).get('insc') if isinstance(rec, dict) else None
            if isinstance(ins, dict) and any(isinstance(v, str) and MK.search(v) for v in ins.values()): ids.add(sid)
    for f in glob.glob(os.path.join(ROOT, 'data', 'bio', 'text', '*.json')):
        t = (json.load(open(f, encoding='utf-8')) or {}).get('text')
        if isinstance(t, str) and MK.search(t): ids.add(os.path.basename(f)[:-5])
    return sorted(ids)

async def main():
    ids = marked_ids(); fails = []
    def ok(c, m):
        if not c: fails.append(m)
    ok(len(ids) >= 116, f'solo {len(ids)} placas con marcado en los datos (¿datos cambiados?)')
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block', locale='es-ES')
        blocked, errs = [], []
        async def rh(r): blocked.append(r.request.url); await r.abort()
        pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*.workers.dev/**', rh); await pg.route('**/*kl-contador*', rh)
        await pg.goto(BASE + 'index.html?intro=0&lang=es&base=day', wait_until='domcontentloaded', timeout=180000)
        await pg.wait_for_function("typeof VISIBLE!=='undefined' && VISIBLE.length>70000 && window.map && map.loaded && map.loaded()", timeout=300000)
        r3 = await pg.evaluate(r"""async (ids) => {
          const BAD = /<\/?[a-z][a-z0-9]*(?:\s[^<>]*)?\/?>|'''|\[\[|\]\]|&(#x?[0-9a-f]+|[a-z]+);/i;
          const out = {opened: 0, missing: [], bad: [], dates: {}, raw: null, results: 0};
          window.reduceMotion = true;
          for (const id of ids){
            const s = byId.get(id); if (!s){ out.missing.push(id); continue; }
            openStone(id); out.opened++;
            for (let k = 0; k < 40; k++){ const sl = document.getElementById('storySlot'); if (sl && !sl.querySelector('.story-wait')) break; await new Promise(r => setTimeout(r, 75)); }
            const d = document.getElementById('detail'), txt = d ? d.innerText : '';
            const m = txt.match(BAD); if (m) out.bad.push([id, m[0], txt.slice(Math.max(0, txt.indexOf(m[0]) - 40), txt.indexOf(m[0]) + 40)]);
            const dt = document.getElementById('inscDates'); if (dt && !dt.hidden) out.dates[id] = dt.innerText;
          }
          // lista de resultados 3D: buscar por el nombre de cada placa (primeras 40)
          for (const id of ids.slice(0, 40)){
            const s = byId.get(id); if (!s || !s.n) continue; const q = document.getElementById('q');
            q.value = s.n; search(); const t = document.getElementById('results').innerText; out.results++;
            const m = t.match(BAD); if (m) out.bad.push(['resultados:' + id, m[0], t.slice(0, 80)]);
          }
          const r = byId.get('""" + ROSEN + r"""'); out.raw = r ? r.i : null;
          return out; }""", ids)
        ok(not r3['missing'], f'placas no encontradas: {r3["missing"][:5]}')
        for bid, m, ctxt in r3['bad'][:10]: fails.append(f'3D {bid}: «{m}» en «{ctxt}»')
        rd = r3['dates'].get(ROSEN, '')
        ok('deportiert 1942 · ermordet 1943 in Auschwitz' in rd, f'Rosenbaum: línea de fechas «{rd}»')
        ok(r3['raw'] and '<br />' in r3['raw'], 'Rosenbaum: el campo i de origen ya no tiene su <br /> (¿datos cambiados?)')
        if os.environ.get('V25_TEXT_SHOTS'):
            await pg.evaluate("(id) => { openStone(id); }", ROSEN)
            await pg.wait_for_timeout(1500)
            await pg.screenshot(path=os.path.join(os.environ['V25_TEXT_SHOTS'], 'v33-rosenbaum-ficha-1280x800.png'))
        # 2D
        p2 = await ctx.new_page(); p2.on('pageerror', lambda e: errs.append('2D: ' + str(e)))
        await p2.route('**/*.workers.dev/**', rh); await p2.route('**/*kl-contador*', rh)
        await p2.goto(BASE + '2d/index.html', wait_until='domcontentloaded', timeout=180000)
        await p2.wait_for_function("typeof DATA!=='undefined' && DATA.length>70000", timeout=300000)
        r2 = await p2.evaluate(r"""(ids) => {
          const BAD = /<\/?[a-z][a-z0-9]*(?:\s[^<>]*)?\/?>|'''|\[\[|\]\]|&(#x?[0-9a-f]+|[a-z]+);/i;
          const el = document.createElement('div'); let n = 0; const bad = [];
          for (const s of DATA){ el.innerHTML = popup(s); n++; const t = el.textContent, m = t.match(BAD); if (m) bad.push([s.id, m[0], t.slice(0, 80)]); }
          let lists = 0;
          for (const id of ids.slice(0, 40)){ const s = byId.get(id); if (!s || !s.n) continue; document.getElementById('q').value = s.n; search(); lists++;
            const t = document.getElementById('results').innerText, m = t.match(BAD); if (m) bad.push(['lista2D:' + id, m[0], t.slice(0, 80)]); }
          return {n, bad, lists}; }""", ids)
        for bid, m, ctxt in r2['bad'][:10]: fails.append(f'2D {bid}: «{m}» en «{ctxt}»')
        ok(r2['n'] > 70000, f'2D: solo {r2["n"]} ventanas comprobadas')
        ok(not errs, f'errores de página: {errs[:3]}')
        await b.close()
    if fails:
        print('FAIL v33-markup-render:'); [print('  -', f) for f in fails]; sys.exit(1)
    print(f'OK v33-markup-render: {len(ids)} placas con marcado en los datos; {r3["opened"]} fichas 3D abiertas (cabecera, placa, línea de fechas, '
          f'datos, historia) sin marcado; {r3["results"]} listas 3D y {r2["lists"]} listas 2D sin marcado; {r2["n"]} ventanas 2D sin marcado; '
          f'Rosenbaum: «{rd[:80]}»; datos de origen sin cambiar; contador bloqueado ({len(blocked)})')
asyncio.run(main())
