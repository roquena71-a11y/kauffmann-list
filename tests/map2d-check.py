"""v19 ronda 2: el mapa clásico 2D (2d/app.js) dibuja las placas de IE/SE/JE/FI/RO en su posición de DIBUJO (dla/dlo si existe)
y ninguna chincheta toca un edificio de OSM (huellas de tests/sidewalk/footprints-v19.json), con la chincheta a su tamaño real a zoom 19 + 0,5 m de holgura.
También comprueba que flyTo/ficha usan la posición de dibujo. Solo localhost; teselas y contador bloqueados; stones.json se sustituye por las 41 placas
(con las 65.861 chinchetas el agrupador tarda minutos en un Chrome sin pantalla). Uso: python3 tests/map2d-check.py BASE_URL"""
import asyncio, sys, json, math
from pathlib import Path
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'pipeline/tools'))
from geo import *
from playwright.async_api import async_playwright
BASE = sys.argv[1]
CCS = ('IE', 'SE', 'JE', 'FI', 'RO'); MARGIN = 0.5
FP = json.load(open(R / 'tests/sidewalk/footprints-v19.json'))
ALL = json.load(open(R / 'data/stones.json', encoding='utf-8'))
SUB = dict(ALL, stones=[s for s in ALL['stones'] if s.get('cc') in CCS])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True)
        ctx = await b.new_context(viewport={'width': 1100, 'height': 800}, service_workers='block', locale='es-ES')
        pg = await ctx.new_page(); errs = []; reqs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('request', lambda r: reqs.append(r.url))
        await pg.route('**/data/stones.json', lambda r: r.fulfill(status=200, content_type='application/json', body=json.dumps(SUB, ensure_ascii=False)))
        # v21: el mapa 2D también carga las listas municipales; en este fixture no hacen falta (solo IE/SE/JE/FI/RO).
        empty_added = json.dumps({'meta': {}, 'stones': []})
        await pg.route('**/data/*-added-*.json', lambda r: r.fulfill(status=200, content_type='application/json', body=empty_added))
        await pg.route('**/tile.openstreetmap.org/**', lambda r: r.abort())
        await pg.route('**/*.workers.dev/**', lambda r: r.abort())
        await pg.goto(BASE + '2d/index.html', wait_until='load')
        await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length===41 && cluster.getLayers().length===41", timeout=60000)
        rows = await pg.evaluate("""() => { const L_ = cluster.getLayers(); const out = []; const m = new Map(DATA.map(s => [s.la.toFixed(7)+','+s.lo.toFixed(7), s]));
          for (const mk of L_) { const ll = mk.getLatLng(); out.push([ll.lat, ll.lng]); }
          return out; }""")
        # chincheta a tamaño real a zoom 19: se mide el elemento del icono
        px = await pg.evaluate("""() => { map.setView([50, 10], 19, {animate:false}); const m = L.marker([50, 10], {icon}).addTo(map); const r = m.getElement().firstElementChild.getBoundingClientRect(); m.remove(); return [r.width, r.height]; }""")
        stones = await pg.evaluate("() => DATA.map(s => ({id: s.id, n: s.n, cc: s.cc, la: s.la, lo: s.lo, dla: s.dla ?? null, dlo: s.dlo ?? null}))")
        # el marcador de cada placa está en la posición de dibujo: se busca por id mediante show()
        fly = []
        for s in stones:
            if s['dla'] is None: continue
            c = await pg.evaluate("""(id) => { show(byId.get(id)); map.stop(); const mk = cluster.getLayers().find(l => Math.abs(l.getLatLng().lat - (byId.get(id).dla)) < 1e-9 && Math.abs(l.getLatLng().lng - (byId.get(id).dlo)) < 1e-9); return !!mk; }""", s['id'])
            fly.append((s['id'], c))
        await b.close()
    bad = []; res = []
    drawn = {}
    # emparejar marcadores con placas: la posición de cada placa es dla/dlo o la de origen
    pts = set((round(a, 7), round(c, 7)) for a, c in rows)
    for s in stones:
        la, lo = (s['dla'], s['dlo']) if s['dla'] is not None else (s['la'], s['lo'])
        if (round(la, 7), round(lo, 7)) not in pts: bad.append({'id': s['id'], 'motivo': 'el mapa 2D no dibuja la placa en la posición de dibujo'})
        mpp = 40075016.686 * math.cos(math.radians(la)) / (256 * 2 ** 19)
        half = max(px) / 2 * mpp + MARGIN
        o = (la, lo); sq = square_corners(0, 0, half, 0.0); hit = None; dmin = 1e9
        for bid in FP['near'].get(s['id'], []):
            bd = FP['buildings'][bid]
            ro = [[to_xy(a, c, o) for a, c in ring] for ring in bd['o']]; ri = [[to_xy(a, c, o) for a, c in ring] for ring in bd['i']]
            if square_hits_poly(sq, ro, ri): hit = bid
            d, _ = dist_to_rings(0, 0, ro)
            dmin = min(dmin, 0 if inside_poly(0, 0, ro, ri) else d)
        res.append({'id': s['id'], 'n': s['n'], 'chincheta_m': round(2 * (half - MARGIN), 2), 'centro_a_edificio_m': round(dmin, 2), 'toca': hit})
        if hit: bad.append(res[-1])
    for i, ok in fly:
        if not ok: bad.append({'id': i, 'motivo': 'show()/flyTo no usa la posición de dibujo'})
    workers = [u for u in reqs if 'workers.dev' in u]
    print('chincheta 2D a zoom 19:', px, 'px | placas', len(stones), '| con posición de dibujo propia', len(fly), '| tocan edificio:', len([x for x in res if x['toca']]), '| errores de página:', errs, '| peticiones workers.dev:', len(workers))
    for x in sorted(res, key=lambda x: x['centro_a_edificio_m'])[:5]: print('  ', x)
    if bad or errs or workers or len(stones) != 41: print('FALLO', bad[:5]); sys.exit(1)
    print('OK: el mapa 2D dibuja las 41 chinchetas fuera de los edificios (zoom 19, +0,5 m)')
asyncio.run(main())
