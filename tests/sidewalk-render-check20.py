"""v20: ninguna columna DIBUJADA (3D, 1,2 m) ni chincheta 2D (12 px a zoom 19) de los países nuevos y de una muestra fija de 1.500 placas de Alemania toca un edificio de OSM (huellas de tests/sidewalk/footprints-v20.json.gz)
con >= 0,5 m de holgura, salvo las que la fuente sitúa legítimamente dentro (OSM level -1, Stolperschwellen). Lee la posición real de dibujo (_dla/_dlo/_ang) de la app. Solo localhost, sin contador.
Uso: python3 tests/sidewalk-render-check20.py BASE_URL [--json salida.json]"""
import asyncio, sys, json, math, gzip
from pathlib import Path
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'pipeline/tools'))
from geo import *
from playwright.async_api import async_playwright
BASE = sys.argv[1]; OUT = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
FP = json.load(gzip.open(R / 'tests/sidewalk/footprints-v20.json.gz', 'rt', encoding='utf-8'))
IDS = set(FP['ids']); LEGIT = set(FP['legit']); MARGIN = 0.5
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block', locale='es-ES')
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*.workers.dev/**', lambda r: r.abort())
        await pg.goto(BASE + 'index.html?intro=0&lang=es', wait_until='load')
        await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>60000 && DATA.every(s=>s._dla!==undefined || s._aliasOf)", timeout=300000)
        rows = await pg.evaluate("(ids) => { const S = new Set(ids); return {half: COL_HALF, rows: DATA.filter(s => S.has(s.id)).map(s => ({id: s.id, n: s.n, cc: s.cc || 'DE', la: s.sla ?? s.la, lo: s.slo ?? s.lo, dla: s._dla, dlo: s._dlo, ang: s._ang, alias: s._aliasOf || null}))} }", sorted(IDS))
        await b.close()
    half = rows['half']; bad = []; res = []
    for r in rows['rows']:
        if r['alias']: continue
        o = (r['dla'], r['dlo']); sq = square_corners(0, 0, half + MARGIN, r['ang'] or 0)
        ih = 6 * 40075016.686 / (256 * 2 ** 19) * math.cos(math.radians(r['dla']))   # chincheta 2D: 12 px a zoom 19
        worst = 1e9; hit = None; inside = False
        for bid in FP['near'].get(r['id'], []):
            bd = FP['buildings'][bid]
            ro = [[to_xy(a, c, o) for a, c in ring] for ring in bd['o']]; ri = [[to_xy(a, c, o) for a, c in ring] for ring in bd['i']]
            if square_hits_poly(sq, ro, ri): hit = bid
            d, _ = dist_to_rings(0, 0, ro)
            if inside_poly(0, 0, ro, ri): d = 0; inside = True
            worst = min(worst, d)
        mv = hav(r['la'], r['lo'], r['dla'], r['dlo'])
        x = {'id': r['id'], 'n': r['n'], 'cc': r['cc'], 'centro_a_edificio_m': round(worst, 2), 'toca': hit, 'dibujo_vs_origen_m': round(mv, 2)}
        res.append(x)
        if r['id'] in LEGIT: continue
        if hit or inside: bad.append(x)
        elif worst - ih < MARGIN - 1e-6: bad.append(dict(x, motivo='chincheta 2D a menos de 0,5 m de una huella'))
        if mv > 45: bad.append(dict(x, motivo='dibujo a más de 45 m del origen'))
    print('placas comprobadas', len(res), '| fallos:', len(bad), '| errores de página:', errs)
    for x in sorted(res, key=lambda x: x['centro_a_edificio_m'])[:5]: print('  ', x)
    if OUT: json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
    if bad or errs or len(res) < len(IDS) - 200: print('FALLO', bad[:5], 'n=', len(res)); sys.exit(1)
    print('OK: ninguna columna ni chincheta dibujada (holgura >= 0,5 m) toca un edificio en %d placas (países nuevos + muestra de Alemania)' % len(res))
asyncio.run(main())
