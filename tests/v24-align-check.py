#!/usr/bin/env python3
"""v29 (paso 2 de la v24): cada grupo de columnas DIBUJADO mira a su calle de OSM y TODAS las reglas de colocación se cumplen.
Abre la web local dos veces (contador y *.workers.dev bloqueados): sin alineación (?alignoff=1, = v28) y con data/align-v24.json.
Comprueba, sobre las 74 979 placas visibles:
  · cifras 75 122 / 74 979; KLAlign aplicó TODAS las placas del archivo (0 entradas omitidas); la/lo registrados idénticos con y sin alineación y al archivo;
  · posición dibujada = la del archivo (misma fórmula que layout()); las placas que no están en el archivo, idénticas a v28;
  · reglas: ninguna apilada; >=1,55 m entre dos columnas cualesquiera; columna (1,2 m girada) a >=0,5 m de todo edificio de OSM;
    chincheta 2D (12 px a z19) con centro a >=semilado+0,5 m de todo edificio si la alineación la movió; centro fuera de la calzada (vía rodada, semiancho; exento con edificio a <6 m); <=25 m de su punto registrado; cuadrícula de 1,85 m en filas;
    las excepciones documentadas (residuales-acera-v20.csv, calzada-v20/21.csv, excepciones-25m-v20/21.csv) solo valen si la placa NO se movió;
  · paralelismo: histograma del error de ángulo entre la fila dibujada y el tramo OSM de su calle (elección de calle propia de esta prueba),
    comparado con v28 (ángulo PCA); mismo tramo → mismo rumbo.
Uso: v24-align-check.py BASE_URL [--json salida.json]   (geometría OSM: ver pipeline/tools/align24_geo.py; variables V24_V20_NEAR, V24_V21_NEAR, V24_V22_NEAR)"""
import asyncio, csv, json, math, os, re, sys, time, unicodedata
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Point, Polygon, LineString
from playwright.async_api import async_playwright
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / 'pipeline' / 'tools'))
import align24_geo as AG
import roadway20 as RWY
from geo import hav, M_LAT

BLOCK = ('kl-contador', 'workers.dev')
N_DATA, N_VIS = 75122, 74979
COL_HALF, MARGIN, GAP, STEP, MAXMOVE = 0.60, 0.50, 1.55, 1.85, 25.0
QTOL = 0.015   # «no más cerca que en v28»: el centro del archivo va en grados·1e7 (±0,6 cm por eje), así que se admite 1,5 cm
EPS = 1e-6

async def dump(base, off):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get('CHROME_BIN', '/usr/bin/google-chrome'), headless=True,
                                    args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--disable-dev-shm-usage'])
        ctx = await b.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block', locale='es-ES')
        pg = await ctx.new_page(); errs = []; blocked = []; hosts = set()
        pg.on('pageerror', lambda e: errs.append(str(e)))
        async def rh(route):
            u = route.request.url; h = u.split('/')[2] if '://' in u else ''
            if any(x in u for x in BLOCK): blocked.append(u); await route.abort(); return
            hosts.add(h); await route.continue_()
        await pg.route('**/*', rh)
        await pg.goto(base.rstrip('/') + '/index.html?intro=0&lang=es' + ('&alignoff=1' if off else ''), wait_until='load', timeout=120000)
        await pg.wait_for_function("typeof DATA!=='undefined' && DATA.length>75000 && window.KLGroups && window.KLAlign && KLAlign.ready && DATA.every(s=>s._dla!==undefined || s._aliasOf)", timeout=600000)
        d = await pg.evaluate("""() => ({
          n: DATA.length, vis: VISIBLE.length, meta_count: META.count,
          align: {ready: KLAlign.ready, applied: KLAlign.applied, entries: KLAlign.entries, skipped: KLAlign.skipped, off: KLAlign.off, error: KLAlign.error || null},
          groups: KLGroups.map(pg => pg.g.map(s => String(s.id))),
          stones: DATA.map(s => [String(s.id), s.src || null, s.cc || null, s.a || null, s.sla ?? s.la, s.slo ?? s.lo, s._dla, s._dlo, s._ang || 0, s._aliasOf || null, !!s._added])
        })""")
        await b.close()
    assert not any('kl-contador' in h or 'workers.dev' in h for h in hosts), hosts
    d['errs'] = errs; d['blocked'] = len(blocked)
    return d

def dist_eq(la1, lo1, la2, lo2):
    return math.hypot((la1 - la2) * M_LAT, (lo1 - lo2) * M_LAT * math.cos(math.radians((la1 + la2) / 2)))

def fold(s):
    s = (s or '').lower().replace('ß', 'ss'); s = unicodedata.normalize('NFKD', s); s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]', '', re.sub(r'stra?sse\b|str\b\.?|straat\b', 'str', s))

def addr_street(a):
    return fold(re.sub(r'\S*\d\S*', ' ', (a or '').split(',')[0])) if a else ''

STREETISH = RWY.VEH | {'living_street', 'road', 'service', 'pedestrian', 'footway', 'path', 'cycleway', 'steps', 'bridleway', 'track'}
VEHS = RWY.VEH | {'living_street', 'road'}
PEDS = {'pedestrian', 'footway', 'path', 'cycleway', 'steps', 'bridleway', 'track'}

def street_bearing(geo, la0, lo0, addr, mode='calle'):
    """Calle de la prueba (implementación propia de la regla documentada en align24.py): 'calle' = la vía con el nombre de la dirección a <=40 m
    (de cualquier tipo, p. ej. *_link); si no, la vía rodada más cercana a <=30 m; si no, service a <=20 m; si no, peatonal a <=20 m.
    'cercana' = la vía de cualquier tipo más cercana a <=30 m (informativo, esquinas).
    Rumbo local = el del tramo más cercano; si el tramo mide <6 m, la cuerda ±8 m a lo largo de la vía.
    Empates (<=5 cm, p. ej. el nodo donde se unen dos tramos de la misma calle): vale cualquiera de los tramos empatados.
    Devuelve ([rumbos en rad [0,π) de los tramos empatados], (índice de vía, índice de tramo) si no hay empate, longitud del tramo) o None."""
    kx = M_LAT * math.cos(math.radians(la0))
    q = shapely.box(lo0 - 45 / kx, la0 - 45 / M_LAT, lo0 + 45 / kx, la0 + 45 / M_LAT)
    sa = addr_street(addr); cands = []
    for hi in geo.htree.query(q):
        t = geo.HT[hi]; hw = t.get('highway')
        c = np.asarray(geo.H[hi].coords); x = (c[:, 0] - lo0) * kx; y = (c[:, 1] - la0) * M_LAT
        ax, ay, dx, dy = x[:-1], y[:-1], np.diff(x), np.diff(y); L2 = dx * dx + dy * dy; L2[L2 == 0] = 1e-12
        tt = np.clip(-(ax * dx + ay * dy) / L2, 0, 1); dd = np.hypot(ax + tt * dx, ay + tt * dy); k = int(np.argmin(dd)); dist = float(dd[k])
        if mode == 'cercana':
            cat = 0 if (dist <= 30 and hw in STREETISH) else 9
        else:
            names = [fold(t.get(f)) for f in ('name', 'name:de', 'alt_name', 'old_name', 'official_name')]
            named = bool(sa) and len(sa) >= 3 and any(n and (n == sa or (min(len(n), len(sa)) >= 6 and (n in sa or sa in n))) for n in names)
            cat = 0 if (named and dist <= 40) else 1 if (hw in VEHS and dist <= 30) else 2 if (hw == 'service' and dist <= 20) else 3 if (hw in PEDS and dist <= 20) else 9
        if cat == 9: continue
        for kk in np.nonzero(dd <= dist + 0.05)[0]:
            kk = int(kk); seglen = math.sqrt(L2[kk]); vx, vy = dx[kk], dy[kk]
            if seglen < 6.0:
                ls = LineString(np.column_stack([x, y])); s0 = ls.project(Point(0, 0))
                p1 = ls.interpolate(max(0.0, s0 - 8)); p2 = ls.interpolate(min(ls.length, s0 + 8)); vx, vy = p2.x - p1.x, p2.y - p1.y
            cands.append((cat, float(dd[kk]), math.atan2(vy, vx) % math.pi, (int(hi), kk), seglen))
    if not cands: return None
    cands.sort(key=lambda c: (c[0], c[1])); b = cands[0]
    tied = [c for c in cands if c[0] == b[0] and c[1] <= b[1] + 0.05]
    return [c[2] for c in tied], (b[3] if len(tied) == 1 else None), b[4]

def angerr(a, b):
    return abs((math.degrees(a - b) + 90) % 180 - 90)

def main():
    base = sys.argv[1]; out = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
    t0 = time.time(); FAIL = []
    raw = asyncio.run(dump(base, True)); ali = asyncio.run(dump(base, False))
    print('volcados: v28=%d/%d v29=%d/%d KLAlign=%s errores=%s bloqueadas=%d+%d (%.0fs)' % (raw['n'], raw['vis'], ali['n'], ali['vis'], ali['align'], raw['errs'] + ali['errs'], raw['blocked'], ali['blocked'], time.time() - t0), flush=True)
    if raw['errs'] or ali['errs']: FAIL.append('errores de página %s' % (raw['errs'] + ali['errs'])[:3])
    for d in (raw, ali):
        if d['n'] != N_DATA or d['vis'] != N_VIS or d['meta_count'] != N_DATA: FAIL.append('cifras %d/%d/%d' % (d['n'], d['vis'], d['meta_count']))
    A = json.load(open(R / 'data' / 'align-v24.json'))
    n_file = sum(len(e) - 4 for e in A['g'])
    if not raw['align']['off'] or raw['align']['applied'] != 0: FAIL.append('alignoff no desactiva la alineación')
    if ali['align']['skipped'] != 0 or ali['align']['applied'] != n_file or ali['align']['entries'] != len(A['g']) or ali['align']['error']: FAIL.append('KLAlign %s (archivo: %d placas)' % (ali['align'], n_file))
    S0 = {r[0]: r for r in raw['stones']}; S1 = {r[0]: r for r in ali['stones']}
    # coordenadas registradas: idénticas con y sin alineación y a los archivos de datos
    filerec = {}
    for s in json.load(open(R / 'data' / 'stones.json'))['stones']: filerec[str(s['id'])] = (s['la'], s['lo'])
    for f in sorted((R / 'data').glob('*-added-20261121.json')):
        for s in json.load(open(f))['stones']: filerec[str(s['id'])] = (s['la'], s['lo'])
    bad_rec = [i for i in S1 if (S1[i][4], S1[i][5]) != (S0[i][4], S0[i][5]) or (S1[i][4], S1[i][5]) != filerec.get(i)]
    if bad_rec or len(filerec) != N_DATA: FAIL.append('coordenadas registradas cambiadas: %d (archivos %d)' % (len(bad_rec), len(filerec)))
    # posición = archivo; fuera del archivo = v28
    listed = {}; ent_of = {}
    for ei, e in enumerate(A['g']):
        P = AG.place_ll(e[0] / 1e7, e[1] / 1e7, len(e) - 4, e[3], e[2] * math.pi / 1800, A['step'])
        for sid, p in zip(e[4:], P): listed[sid] = (p[0], p[1], e[2] * math.pi / 1800); ent_of[sid] = ei
    vis = [i for i, r in S1.items() if not r[9]]
    pos_bad = [i for i in vis if i in listed and (abs(S1[i][6] - listed[i][0]) > 1e-9 or abs(S1[i][7] - listed[i][1]) > 1e-9 or abs(S1[i][8] - listed[i][2]) > 1e-9)]
    same_bad = [i for i in vis if i not in listed and (S1[i][6], S1[i][7], S1[i][8]) != (S0[i][6], S0[i][7], S0[i][8])]
    alias_bad = [i for i, r in S1.items() if r[9] and (r[6], r[7]) != (S1[r[9]][6], S1[r[9]][7])]
    if pos_bad or same_bad or alias_bad: FAIL.append('posición ≠ archivo %d · fuera del archivo ≠ v28 %d · alias ≠ principal %d' % (len(pos_bad), len(same_bad), len(alias_bad)))
    moved = {i for i in vis if (S1[i][6], S1[i][7]) != (S0[i][6], S0[i][7])}
    changed = {i for i in vis if i in moved or abs(S1[i][8] - S0[i][8]) > 1e-12}
    print('placas en el archivo %d · movidas %d · solo giradas %d · sin cambio %d' % (len(listed), len(moved), len(changed - moved), len(vis) - len(changed)), flush=True)
    exc = {}
    for f, k in (('residuales-acera-v20.csv', 'edif'), ('calzada-v20.csv', 'calzada'), ('calzada-v21.csv', 'calzada'), ('excepciones-25m-v20.csv', '25m'), ('excepciones-25m-v21.csv', '25m')):
        for row in csv.DictReader(open(R / f, encoding='utf-8')): exc.setdefault(k, set()).add(row['id'])
    exc['edif'] |= {r['id'] for r in json.load(open(R / 'data' / 'sidewalk-v20.json', encoding='utf-8'))['stones'] if r.get('estado') == 'legitima'}   # dentro de un edificio por diseño
    def documented(kind, sid): return sid in exc.get(kind, set()) and sid not in changed
    # 1) apiladas y separación global
    cell = 0.00003; grid = defaultdict(list)
    for i in vis: grid[(math.floor(S1[i][6] / cell), math.floor(S1[i][7] / cell))].append(i)
    stacked, gap = [], []
    for i in vis:
        la, lo = S1[i][6], S1[i][7]; a0, b0 = math.floor(la / cell), math.floor(lo / cell)
        for da in (-1, 0, 1):
            for db in (-2, -1, 0, 1, 2):
                for j in grid.get((a0 + da, b0 + db), ()):
                    if j <= i: continue
                    dd = dist_eq(la, lo, S1[j][6], S1[j][7])
                    if dd < 0.01: stacked.append((i, j))
                    elif dd < GAP - EPS: gap.append((i, j, round(dd, 3)))
    # 2) cuadrícula y filas paralelas al rumbo
    grid_bad, row_bad = [], []
    for e in A['g']:
        ids = e[4:]; n = len(ids); cols = e[3]; ang = e[2] * math.pi / 1800
        if n < 2: continue
        P = [(S1[i][6], S1[i][7]) for i in ids]
        for k in range(n):
            ds = [dist_eq(*P[k], *P[m]) for m in range(n) if m != k]
            if min(ds) < STEP - 0.02 or min(abs(x - STEP) for x in ds) > 0.02: grid_bad.append((ids[0], k)); break
        if cols >= 2:
            la0 = P[0][0]; dx = (P[1][1] - P[0][1]) * M_LAT * math.cos(math.radians(la0)); dy = (P[1][0] - P[0][0]) * M_LAT
            if angerr(math.atan2(dy, dx), ang) > 0.2: row_bad.append(ids[0])
    # 3) edificios, calzada, 25 m — por grupo de geometría
    bykey = defaultdict(list)
    for i in vis: bykey[AG.source_key(S1[i][2] or 'DE', S1[i][1] if S1[i][10] else None)].append(i)
    bld, road, far, pin, doc_used = [], [], [], [], Counter()
    hist = {'v29': Counter(), 'v28': Counter(), 'v29_cercana': Counter()}; seg_angles = defaultdict(set); nostreet = 0; errs_list = []
    BINS = [1, 2, 5, 10, 20, 45, 91]
    binof = lambda x: next(b for b in BINS if x < b)
    for key in sorted(bykey, key=lambda k: -len(bykey[k])):
        tk = time.time(); geo = AG.Geo(key)
        ids = bykey[key]
        cl = defaultdict(list)
        for i in ids: cl[(math.floor(S1[i][6] / 0.0003), math.floor(S1[i][7] / 0.0005))].append(i)
        for (ca, cb), members in cl.items():
            la0 = (ca + 0.5) * 0.0003; lo0 = (cb + 0.5) * 0.0005
            B, btree, lines = geo.local(la0, lo0, 120)
            veh = [(l, RWY.semiwidth(t)) for l, t in lines if RWY.is_vehicular(t)]
            for i in members:
                r = S1[i]; x, y = AG.to_local(r[6], r[7], la0, lo0); x, y = float(x), float(y)
                sq = AG.squares([x], [y], r[8], COL_HALF)[0]; pt = Point(x, y)
                dsq = min((float(shapely.distance(sq, B[k])) for k in btree.query(sq, predicate='dwithin', distance=6.5)), default=99.0) if btree is not None else 99.0
                dc = min((float(shapely.distance(pt, B[k])) for k in btree.query(pt, predicate='dwithin', distance=6.5)), default=99.0) if btree is not None else 99.0
                if dsq < MARGIN - EPS:
                    if documented('edif', i): doc_used['edif'] += 1
                    else: bld.append((i, round(dsq, 3), i in changed))
                ih = 6 * 40075016.686 / (256 * 2 ** 19) * math.cos(math.radians(r[6]))   # chincheta 2D: 12 px a zoom 19 (como sidewalk-render-check20)
                if dc - ih < MARGIN - EPS and i in changed:
                    # solo es fallo si la alineación la movió: en v28 la chincheta debía cumplirlo ya (o está documentada y entonces no se mueve)
                    x0, y0 = AG.to_local(S0[i][6], S0[i][7], la0, lo0); p0 = Point(float(x0), float(y0))
                    dc0 = min((float(shapely.distance(p0, B[k])) for k in btree.query(p0, predicate='dwithin', distance=6.5)), default=99.0) if btree is not None else 99.0
                    if dc0 - ih >= MARGIN - EPS or dc - ih < dc0 - ih - QTOL: pin.append((i, round(dc - ih, 3), round(dc0 - ih, 3)))
                if dc >= RWY.BLD_EXEMPT_NEAR:
                    rc = min((l.distance(pt) - sw for l, sw in veh), default=99.0)
                    if rc < -EPS:
                        if documented('calzada', i): doc_used['calzada'] += 1
                        else: road.append((i, round(rc, 3), i in changed))
                mv = max(hav(r[4], r[5], r[6], r[7]), dist_eq(r[4], r[5], r[6], r[7]))
                if mv > MAXMOVE + EPS:
                    if documented('25m', i): doc_used['25m'] += 1
                    else: far.append((i, round(mv, 2), i in changed))
        # paralelismo por grupo dibujado (entradas del archivo con placas de esta fuente)
        ents = sorted({ent_of[i] for i in ids if i in ent_of})
        for ei in ents:
            e = A['g'][ei]; cla, clo = e[0] / 1e7, e[1] / 1e7   # centro de la fila/cuadrícula dibujada
            sbn = street_bearing(geo, cla, clo, S1[e[4]][3], 'cercana')
            if sbn: hist['v29_cercana'][binof(min(angerr(e[2] * math.pi / 1800, b) for b in sbn[0]))] += 1
            sb = street_bearing(geo, cla, clo, S1[e[4]][3])
            if sb is None: nostreet += 1; continue
            br, segid, seglen = sb
            e1 = min(angerr(e[2] * math.pi / 1800, b) for b in br); e0 = min(angerr(S0[e[4]][8], b) for b in br)
            hist['v29'][binof(e1)] += 1; hist['v28'][binof(e0)] += 1
            if e1 >= 10: errs_list.append((e[4], round(e1, 1), S1[e[4]][3]))
            if segid is not None and seglen >= 6.0: seg_angles[(key, segid)].add(e[2])
        print('  %s: %d placas, %d entradas (%.0fs)' % (key, len(ids), len(ents), time.time() - tk), flush=True)
        del geo
    incons = {k: v for k, v in seg_angles.items() if len(v) > 1 and (max(v) - min(v)) > 1 and (max(v) - min(v)) < 1799}
    tot = sum(hist['v29'].values())
    pct = lambda h, lim: 100.0 * sum(v for b, v in h.items() if b <= lim) / max(1, sum(h.values()))
    print('histograma del error de ángulo fila↔tramo OSM de su calle (%d grupos alineados con calle; %d sin calle a <=30 m para la prueba):' % (tot, nostreet))
    for b in BINS:
        lo_ = ([0] + BINS)[BINS.index(b)]
        print('   %2d–%2d°  v29 %6d   v28 %6d   (v29 frente a la vía más cercana de cualquier tipo: %6d)' % (lo_, b, hist['v29'][b], hist['v28'][b], hist['v29_cercana'][b]))
    print('   v29 <2°: %.2f %%  <5°: %.2f %%  <10°: %.2f %%   ·   v28 <2°: %.2f %%  <5°: %.2f %%' % (pct(hist['v29'], 2), pct(hist['v29'], 5), pct(hist['v29'], 10), pct(hist['v28'], 2), pct(hist['v28'], 5)))
    print('tramos OSM con varios grupos: %d · con rumbos distintos: %d' % (sum(1 for v in seg_angles.values()), len(incons)))
    print('reglas: apiladas=%d separación<1,55=%d edificio<0,5=%d calzada=%d >25m=%d cuadrícula=%d filas_no_paralelas=%d chincheta2D<0,5=%d · excepciones documentadas usadas (placas sin mover): %s' % (len(stacked), len(gap), len(bld), len(road), len(far), len(grid_bad), len(row_bad), len(pin), dict(doc_used)))
    for nm, L in (('apiladas', stacked), ('separación', gap), ('edificio', bld), ('calzada', road), ('25 m', far), ('cuadrícula', grid_bad), ('filas', row_bad), ('chincheta 2D', pin)):
        if L: FAIL.append('%s: %d %s' % (nm, len(L), L[:4]))
    print('   informativo (vía más cercana de cualquier tipo, p. ej. en esquinas): v29 <2° %.2f %%  <10° %.2f %%' % (pct(hist['v29_cercana'], 2), pct(hist['v29_cercana'], 10)))
    if pct(hist['v29'], 2) < 99.0 or pct(hist['v29'], 10) < 99.5: FAIL.append('paralelismo insuficiente: <2° %.2f %%, <10° %.2f %%' % (pct(hist['v29'], 2), pct(hist['v29'], 10)))
    if incons: FAIL.append('mismo tramo con rumbos distintos: %d %s' % (len(incons), list(incons.items())[:3]))
    if out:
        json.dump({'hist': {k: dict(v) for k, v in hist.items()}, 'err_ge10': errs_list, 'moved': len(moved), 'changed': len(changed), 'doc_used': dict(doc_used)}, open(out, 'w'), ensure_ascii=False, indent=1)
    if errs_list: print('grupos con error >=10° (primeros):', errs_list[:8])
    if FAIL:
        print('FALLO v24-align-check:'); [print('  -', f) for f in FAIL]; sys.exit(1)
    print('OK v24-align-check: %d placas visibles, %d alineadas en %d grupos, 0 reglas incumplidas (%.0fs)' % (len(vis), len(listed), len(A['g']), time.time() - t0))

if __name__ == '__main__':
    main()
