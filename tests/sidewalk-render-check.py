"""v19: ninguna columna DIBUJADA de IE/SE/JE/FI/RO toca un edificio de OSM (huellas de tests/sidewalk/footprints-v19.json).
Abre la web local, lee la posición real de dibujo (_dla/_dlo/_ang, ya con la distribución en cuadrícula de la app) y comprueba el cuadrado de 1,2 m.
Solo localhost, sin contador. Uso: python3 tests/sidewalk-render-check.py BASE_URL [--json salida.json]"""
import asyncio, sys, json, math, os
from pathlib import Path
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'pipeline/tools'))
from geo import *
from playwright.async_api import async_playwright
BASE = sys.argv[1]; OUT = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
FP = json.load(open(R / 'tests/sidewalk/footprints-v19.json'))
CCS = ('IE', 'SE', 'JE', 'FI', 'RO')
MARGIN = 0.5   # holgura mínima columna–fachada (m), ronda 2 de la v19
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block', locale='es-ES')
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(BASE + 'index.html?intro=0&lang=es', wait_until='load')
        await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>60000 && DATA.every(s=>s._dla!==undefined || s._aliasOf)", timeout=180000)
        rows = await pg.evaluate("(ccs) => ({half: COL_HALF, rows: DATA.filter(s => ccs.includes(s.cc)).map(s => ({id: s.id, n: s.n, cc: s.cc, la: s.sla ?? s.la, lo: s.slo ?? s.lo, dla: s._dla, dlo: s._dlo, ang: s._ang, alias: s._aliasOf || null, disp: s.dla ?? null}))})", list(CCS))
        await b.close()
    half = rows['half']; bad = []; res = []
    for r in rows['rows']:
        if r['alias']: continue
        o = (r['dla'], r['dlo']); sq = square_corners(0, 0, half + MARGIN, r['ang'] or 0)   # columna de 1,2 m ensanchada 0,5 m por lado: no toca ningún edificio
        worst = 1e9; hit = None
        for bid in FP['near'].get(r['id'], []):
            bd = FP['buildings'][bid]
            ro = [[to_xy(a, c, o) for a, c in ring] for ring in bd['o']]; ri = [[to_xy(a, c, o) for a, c in ring] for ring in bd['i']]
            if square_hits_poly(sq, ro, ri): hit = bid
            d, _ = dist_to_rings(0, 0, ro)
            if inside_poly(0, 0, ro, ri): d = 0
            worst = min(worst, d)
        mv = hav(r['la'], r['lo'], r['dla'], r['dlo'])
        res.append({'id': r['id'], 'n': r['n'], 'cc': r['cc'], 'centro_a_edificio_m': round(worst, 2), 'toca': hit, 'dibujo_vs_origen_m': round(mv, 2)})
        if hit: bad.append(res[-1])
        if mv > 30: bad.append(dict(res[-1], motivo='movida más de 30 m (25 m de ajuste + cuadrícula)'))
    print('piedras comprobadas', len(res), '| tocan edificio:', len([x for x in res if x['toca']]), '| errores de página:', errs)
    for x in sorted(res, key=lambda x: x['centro_a_edificio_m'])[:8]: print('  ', x)
    if OUT: json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
    if bad or errs or len(res) != 41: print('FALLO', bad[:5], 'n=', len(res)); sys.exit(1)
    print('OK: ninguna columna dibujada (1,2 m + 0,5 m de holgura) toca un edificio')
asyncio.run(main())
