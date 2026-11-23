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
import csv
RESID = {r['id'] for r in csv.DictReader(open(R / 'residuales-acera-v20.csv', encoding='utf-8'))}   # excepciones documentadas (grupos sin hueco en la acera a <=25 m)
IDS = set(FP['ids']); LEGIT = set(FP['legit']); MARGIN = 0.5
# v20r2 (auditoría C, F1): ninguna placa sin datos de edificios (el test antiguo recorría listas vacías y daba OK); solo la lista explícita (campo/costa sin edificio a <=50 m en OSM)
SIN = set(FP.get('sin_edificios_50m', []))
# v20r5 (auditoría C ronda 4): el test ya trataba «centro dentro de un edificio» como hard=True
# (residuales-acera NO exime: solo LEGIT n12461266505/6/7). Falló Unna porque esos ids no estaban en
# footprints-v20.json.gz (muestra + listas fijas). Exigir que residuales, excepciones, calzada, V19 y
# las placas de Unna/Karlsruhe del fallo estén en el fixture; si faltan, el test FALLA (cobertura).
_V19 = {'IE', 'SE', 'JE', 'FI', 'RO'}
_req = set()
if (R / 'residuales-acera-v20.csv').exists():
    _req |= {r['id'] for r in csv.DictReader(open(R / 'residuales-acera-v20.csv', encoding='utf-8'))}
if (R / 'excepciones-25m-v20.csv').exists():
    _req |= {r['id'] for r in csv.DictReader(open(R / 'excepciones-25m-v20.csv', encoding='utf-8'))}
if (R / 'calzada-v20.csv').exists():
    _req |= {r['id'] for r in csv.DictReader(open(R / 'calzada-v20.csv', encoding='utf-8'))}
if (R / 'data/stones.json').exists():
    _req |= {s['id'] for s in json.load(open(R / 'data/stones.json', encoding='utf-8'))['stones'] if (s.get('cc') or 'DE') in _V19}
_req |= {'n12438845078', 'n12438845081', 'n2310732548', 'n13021249318'}
_missing = sorted(_req - IDS)
if _missing:
    print('FALLO de cobertura del fixture: %d ids documentados o V19 no están en footprints-v20.json.gz (así se escapó Unna en ronda 4):' % len(_missing), _missing[:20])
    raise SystemExit(1)

_vac = []
# v20r4 (auditoría C ronda 3, calzada): el centro dibujado no puede caer sobre la calzada de una vía rodada de OSM (ejes: tests/sidewalk/roads-v20.json.gz; semiancho por clase o width) salvo que haya un edificio a <6 m
# (acera pegada a la fachada) o la placa esté documentada con motivo en calzada-v20.csv
RD = json.load(gzip.open(R / 'tests/sidewalk/roads-v20.json.gz', 'rt', encoding='utf-8'))
CAL = {}
for _r in csv.DictReader(open(R / 'calzada-v20.csv', encoding='utf-8')): CAL[_r['id']] = _r['motivo']
EXEMPT_BLD = 6.0
def road_hit(rid_list, o):
    best = None
    for rid in rid_list:
        rd = RD['roads'][rid]
        if not rd['c']: continue
        pts = [to_xy(a, c, o) for a, c in rd['p']]
        d = min(_pseg(0, 0, pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        if d < rd['hw'] and (best is None or d - rd['hw'] < best[0]): best = (d - rd['hw'], d, rd['hw'], rd['n'])
    return best
EXC25 = {r['id'] for r in csv.DictReader(open(R / 'excepciones-25m-v20.csv', encoding='utf-8'))} if (R / 'excepciones-25m-v20.csv').exists() else set()

def _pseg(px, py, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    u = 0 if L == 0 else max(0, min(1, ((px - a[0]) * dx + (py - a[1]) * dy) / L))
    return math.hypot(px - a[0] - u * dx, py - a[1] - u * dy)
def _psq(px, py, h, ang):
    c, s = math.cos(ang), math.sin(ang); x = c * px + s * py; y = -s * px + c * py
    return math.hypot(max(abs(x) - h, 0), max(abs(y) - h, 0))
def square_dist(h, ang, ro, ri):
    """Distancia euclídea (m) del cuadrado de lado 2h centrado en el origen y girado ang al edificio (0 si lo toca): como las auditorías, no un cuadrado ensanchado."""
    sq = square_corners(0, 0, h, ang)
    if square_hits_poly(sq, ro, ri): return 0.0
    best = 1e9
    for ring in ro + ri:
        for i in range(len(ring) - 1):
            a, b = ring[i], ring[i + 1]
            best = min(best, _psq(a[0], a[1], h, ang), _psq(b[0], b[1], h, ang), *[_pseg(cx, cy, a, b) for cx, cy in sq[:4]])
    return best
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True, args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block', locale='es-ES')
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*.workers.dev/**', lambda r: r.abort())
        await pg.goto(BASE + 'index.html?intro=0&lang=es', wait_until='load')
        await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>60000 && DATA.every(s=>s._dla!==undefined || s._aliasOf) && (!window.KLAlign || KLAlign.ready)", timeout=300000)
        rows = await pg.evaluate("(ids) => { const S = new Set(ids); return {half: COL_HALF, rows: DATA.filter(s => S.has(s.id)).map(s => ({id: s.id, n: s.n, cc: s.cc || 'DE', la: s.sla ?? s.la, lo: s.slo ?? s.lo, dla: s._dla, dlo: s._dlo, pla: s.la, plo: s.lo, ang: s._ang, alias: s._aliasOf || null}))} }", sorted(IDS))
        await b.close()
    half = rows['half']; bad = []; res = []; nroad = []
    for r in rows['rows']:
        if r['alias']: continue
        o = (r['dla'], r['dlo']); ang = r['ang'] or 0
        ih = 6 * 40075016.686 / (256 * 2 ** 19) * math.cos(math.radians(r['dla']))   # chincheta 2D: 12 px a zoom 19
        worst = 1e9; hit = None; inside = False; pin_inside = False; d3 = 1e9; dsrc = 1e9; osrc = (r['la'], r['lo'])
        for bid in FP['near'].get(r['id'], []):
            bd = FP['buildings'][bid]
            ro = [[to_xy(a, c, o) for a, c in ring] for ring in bd['o']]; ri = [[to_xy(a, c, o) for a, c in ring] for ring in bd['i']]
            dd3 = square_dist(half, ang, ro, ri); d3 = min(d3, dd3)
            if dd3 < MARGIN - 1e-6: hit = bid
            dsrc = min(dsrc, dist_to_rings(0, 0, [[to_xy(a, c, osrc) for a, c in ring] for ring in bd['o']])[0])   # distancia desde la coordenada de ORIGEN de la placa
            d, _ = dist_to_rings(0, 0, ro)
            if inside_poly(0, 0, ro, ri): d = 0; inside = True
            pp = to_xy(r['pla'], r['plo'], o)   # chincheta 2D (v20r3, C): centro en s.la/s.lo tras aplicar dla/dlo
            if inside_poly(pp[0], pp[1], ro, ri): pin_inside = True
            worst = min(worst, d)
        mv = hav(r['la'], r['lo'], r['dla'], r['dlo'])
        rh = road_hit(RD['near'].get(r['id'], []), o)
        if rh and worst >= EXEMPT_BLD and r['id'] not in LEGIT and r['id'] not in CAL: bad.append({'id': r['id'], 'n': r['n'], 'cc': r['cc'], 'motivo': 'centro sobre la calzada: %.2f m del eje de %s (semiancho %.2f m), sin edificio a <6 m y sin documentar en calzada-v20.csv' % (rh[1], rh[3], rh[2]), 'hard': True})
        if rh and worst >= EXEMPT_BLD: nroad.append(r['id'])
        x = {'id': r['id'], 'n': r['n'], 'cc': r['cc'], 'centro_a_edificio_m': round(worst, 2), 'toca': hit, 'dibujo_vs_origen_m': round(mv, 2)}
        res.append(x)
        if r['id'] in LEGIT: continue
        # v20r3 (auditoría C ronda 2): el CENTRO de la columna 3D o de la chincheta 2D dentro de un edificio es un fallo SIN excepción (ni residuales-acera): solo las placas legítimamente dentro (LEGIT)
        if inside: bad.append(dict(x, motivo='centro de la columna 3D dentro de un edificio', hard=True))
        if pin_inside: bad.append(dict(x, motivo='centro de la chincheta 2D dentro de un edificio', hard=True))
        if hit and not inside: bad.append(x)
        elif worst - ih < MARGIN - 1e-6: bad.append(dict(x, motivo='chincheta 2D a menos de 0,5 m de una huella'))
        if mv > 25.0 and r['id'] not in EXC25: bad.append(dict(x, motivo='dibujo a más de 25 m del origen (y no está en excepciones-25m-v20.csv)'))
        if dsrc > 50 and r['id'] not in SIN: bad.append(dict(x, motivo='sin ningún edificio de OSM a <=50 m en los datos (footprints): geometría no comprobable'))
    print('placas con el centro en la calzada y sin edificio a <6 m (todas documentadas en calzada-v20.csv):', len(nroad), '| placas con vía en el fixture:', sum(1 for i in RD['near'] if RD['near'][i]))
    if [i for i, m in CAL.items() if not m.strip()]: print('FALLO: calzada-v20.csv con motivo vacío'); sys.exit(1)
    print('placas comprobadas', len(res), '| fallos:', len(bad), '| errores de página:', errs)
    for x in sorted(res, key=lambda x: x['centro_a_edificio_m'])[:5]: print('  ', x)
    exc = [x for x in bad if x['id'] in RESID and not x.get('hard')]; bad = [x for x in bad if x['id'] not in RESID or x.get('hard')]
    if exc: print('excepciones documentadas en residuales-acera-v20.csv:', len(exc), [x['id'] for x in exc])
    if OUT: json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
    if len(SIN) > 70: print('FALLO: demasiadas placas sin edificio a <=50 m en la lista explícita', len(SIN)); sys.exit(1)
    if bad or errs or len(res) < len(IDS) - 200: print('FALLO', bad[:5], 'n=', len(res)); sys.exit(1)
    print('OK: ninguna columna ni chincheta dibujada (holgura >= 0,5 m) toca un edificio en %d placas (países nuevos + muestra de Alemania)' % len(res))
asyncio.run(main())
