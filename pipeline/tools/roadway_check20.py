#!/usr/bin/env python3
"""v20r4 (auditoría C ronda 3, §2): comprueba con la posición REAL de dibujo (volcado de la app) que ningún centro de columna cae sobre la calzada de una vía rodada de OSM (ver roadway20.py).
Uso: roadway_check20.py select DUMP.json   → V20_DATA/road_groups.json (grupos a recolocar: ids de grupo) y resumen
     roadway_check20.py csv DUMP.json      → calzada-v20.csv (las placas con el centro sobre la calzada que quedan documentadas, con motivo) y resumen
Independiente del solver: distancia del centro dibujado a los ejes de OSM (shapely) y a los edificios (huellas de near/CC)."""
import json, math, sys, os, csv
from pathlib import Path
from collections import defaultdict, Counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sidewalk20 as SW, roadway20 as RWY
from shapely.geometry import Point, LineString, Polygon
from geo import to_xy
R = SW.R; D = SW.D
mode, dump_f = sys.argv[1], sys.argv[2]
dump = json.load(open(dump_f))['rows']
S = json.load(open(R / 'data/stones.json', encoding='utf-8'))['stones']; byid = {s['id']: s for s in S}
legit = set(json.load(open(D / 'legit_inside.json'))) if (D / 'legit_inside.json').exists() else set()
rows_cc = defaultdict(list)
for r in dump:
    _cc = byid[r[0]].get('cc') or 'DE'
    if not r[7] and _cc not in SW.V19: rows_cc[_cc].append(r)
def bdist(N, la, lo, rc=1):
    o = (la, lo); db = 1e9
    for bid in N.around(N.bi, la, lo, rc):
        outer, inner, tags = N.b[bid]
        for ring in outer:
            try: db = min(db, Polygon([to_xy(a, c, o) for a, c in ring]).distance(Point(0, 0)))
            except Exception: pass
    return db
gid_all = {}
sel_groups = set(); out = []; summ = Counter(); ginfo = {}; gsz = Counter()
for cc, rows in rows_cc.items():
    N = SW.load_near(cc); gs = SW.groups_of([s for s in S if (s.get('cc') or 'DE') == cc]); gid = {}; g0 = {}
    for g in gs:
        gsz[g[0]['id']] = len(g)
        for s in g: gid[s['id']] = g[0]['id']; gid_all[s['id']] = g[0]['id']
        g0[g[0]['id']] = (sum(s['la'] for s in g) / len(g), sum(s['lo'] for s in g) / len(g))
    gb = {}
    for r in rows:
        la, lo = r[4], r[5]; o = (la, lo); best = None
        for hid in N.around(N.hi, la, lo, 1):
            pts, t = N.h[hid]
            if not RWY.is_vehicular(t): continue
            d = LineString([to_xy(a, c, o) for a, c in pts]).distance(Point(0, 0)); hw = RWY.semiwidth(t)
            if d < hw and (best is None or d - hw < best[0]): best = (d - hw, d, hw, t, hid)
        if best is None: continue
        db = bdist(N, la, lo)
        if db < RWY.BLD_EXEMPT_NEAR: summ['exenta_fachada<6m'] += 1; continue
        if r[0] in legit: continue
        g_ = gid[r[0]]
        if g_ not in gb: gb[g_] = bdist(N, g0[g_][0], g0[g_][1], 2)
        t = best[3]
        if RWY.no_sidewalk(t): why = 'sin acera en OSM (sidewalk=no): la placa está donde la fuente la pone, en una calle sin acera'; k = 'sin_acera_osm'
        elif gb[g_] > RWY.BLD_NEAR_MAX: why = 'sin ningún edificio de OSM a <=25 m del grupo: no hay línea de fachada ni acera que deducir; no se mueve'; k = 'sin_edificio_25m'
        else: why = 'VIOLACION'; k = 'violacion'
        summ[k] += 1
        if k == 'violacion': sel_groups.add(g_)
        s = byid[r[0]]; mv = SW.hav(s['la'], s['lo'], la, lo); ginfo[r[0]] = (g_, gsz[g_], cc)
        out.append([r[0], cc, s.get('n'), s.get('a') or '', (t.get('name') or '') + ' (' + t['highway'] + ')', t['highway'], round(best[1], 2), best[2], round(db, 1), round(mv, 1), why, k])
    print(cc, len(rows), flush=True)
print(dict(summ), 'grupos con violación:', len(sel_groups))
if mode == 'select':
    json.dump(sorted(sel_groups), open(D / 'road_groups.json', 'w'))
else:
    keep = []
    swr = {r['id']: r for r in json.load(open(R / 'data/sidewalk-v20.json', encoding='utf-8'))['stones']}
    drawn = {r[0]: r for r in dump if not r[7]}
    # placas de OTROS grupos del solver con la misma clave de dirección que la app (addrKey) a <=15 m (8 m sin número) de la posición DIBUJADA: la app las une en una sola cuadrícula (agrupa por posición dibujada)
    bykey = defaultdict(list)
    for r in dump:
        if not r[7]: bykey[SW.addr_key(byid[r[0]].get('a'))].append(r)
    for x in out:
        if x[-1] == 'violacion':
            g_, n_, cc_ = ginfo[x[0]]; sr = swr.get(x[0], {}); lvl = sr.get('nivel')
            k = SW.addr_key(byid[x[0]].get('a')); me = drawn[x[0]]; lim = 15.0 if (k and any(ch.isdigit() for ch in k)) else 8.0
            others = [o for o in bykey.get(k, []) if o[0] != x[0] and gid_all.get(o[0]) != g_ and SW.hav(me[4], me[5], o[4], o[5]) <= lim] if k else []
            if others:
                x[10] = 'la app une este grupo (%d placa/s) con otro de la misma dirección del solver (%d placa/s a <=%d m de la posición dibujada): agrupa por posición dibujada, no por origen, y recoloca una cuadrícula conjunta; el solver no puede fijar ambos a la vez. Documentado (centro a %.2f m del eje, semiancho %.2f m)' % (n_, len(others), lim, x[6], x[7])
            elif n_ >= 7:
                x[10] = 'grupo de %d placas con la misma dirección (cuadrícula %dx%d): sin hueco a <=25 m del origen con todos los edificios a >=0,5 m y todos los centros fuera de la calzada; el solver lo deja en la mejor posición con holguras relajadas (nivel %s de data/sidewalk-v20.json). Documentado' % (n_, math.ceil(math.sqrt(n_)), math.ceil(n_ / math.ceil(math.sqrt(n_))), lvl if lvl is not None else 'sin movimiento: no hay hueco')
            else:
                x[10] = 'sin hueco a <=25 m del origen que cumpla a la vez edificios (>=0,5 m) y calzada para este grupo de %d placa/s (nivel %s de data/sidewalk-v20.json); queda en el mejor sitio del solver. Documentado' % (n_, lvl if lvl is not None else 'sin movimiento')
        keep.append(x[:-1])
    keep.sort(key=lambda x: (x[1], x[0]))
    with open(R / 'calzada-v20.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['id', 'pais', 'nombre', 'direccion', 'via', 'clase', 'dist_eje_m', 'semiancho_m', 'edificio_mas_cercano_m', 'dibujo_vs_origen_m', 'motivo']); w.writerows(keep)
    print('calzada-v20.csv', len(keep), Counter(x[10][:30] for x in keep))
