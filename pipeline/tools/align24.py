#!/usr/bin/env python3
"""v29 (paso 2 de la v24): cada grupo de columnas mira a SU calle y se coloca en 1–2 filas paralelas al bordillo.
Entrada: volcado del dibujo actual SIN alineación (dump_groups24.py --raw: grupos de la app, posiciones _dla/_dlo ya validadas en v20–v22).
Calle del grupo (OSM): 1) vía con el MISMO NOMBRE que la calle de la dirección a <=40 m; 2) vía rodada (residential…living_street) a <=30 m;
3) service a <=20 m; 4) peatonal/footway/path/cycleway a <=20 m (plazas). Sin ninguna → patio/parque: no se toca.
Rumbo = el del tramo OSM más cercano al centro FINAL de la fila (mismo tramo → mismo rumbo); si el tramo mide <6 m, la cuerda ±8 m a lo largo de la vía.
Disposición: n<=5 una fila; n<=16 dos filas; >16 bloques de 8 por fila; paso 1,85 m (igual que antes). Alternativas por orden: otra fila, cuadrícula actual girada.
Centro: el actual (ya en la acera) o el desplazamiento más pequeño (<=10 m a lo largo de la calle, <=3 m hacia/desde ella) que cumpla TODO:
  columna (1,2 m, girada) a >=0,53 m de cualquier edificio · centro fuera de la calzada de vías rodadas (semiancho+0,3 m; exento a <5,5 m de fachada)
  · cada placa a <=24,7 m de SU punto registrado · >=1,60 m de las columnas de otros grupos · mismo lado de la calle.
Si nada cumple, la placa está en excepciones-25m-v20/v21.csv o es «legítima» dentro de un edificio (sidewalk-v20.json), el grupo se queda como está (contado e informado en alineacion-v24.csv).
Salida: data/align-v24.json (solo dibujo; la/lo registrados no cambian) y alineacion-v24.csv.
Uso: align24.py DUMP_RAW.json [--out data/align-v24.json] [--report alineacion-v24.csv] [--stats stats.json]"""
import csv, json, math, re, sys, time, unicodedata
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Point
sys.path.insert(0, str(Path(__file__).resolve().parent))
import align24_geo as AG
import sidewalk20 as SW
import roadway20 as RWY
from geo import M_LAT

R = Path(__file__).resolve().parents[2]
STEP = 1.85; HALF = 0.60
B_CLEAR = 0.53; PIN_PX_HALF = 6; GAP = 1.60; MAXREC = 24.7; ROAD_M = 0.3; EXEMPT = 5.5
S_MAX, S_STEP, T_MAX, T_STEP = 10.0, 0.5, 3.0, 0.25
VEH_STREET = RWY.VEH | {'living_street', 'road'}
PED = {'pedestrian', 'footway', 'path', 'cycleway', 'steps', 'bridleway', 'track'}

def fold(s):
    s = (s or '').lower().replace('ß', 'ss')
    s = unicodedata.normalize('NFKD', s); s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'stra?sse\b|str\b\.?|straat\b', 'str', s)
    return re.sub(r'[^a-z0-9]', '', s)

def street_of(a):
    if not a: return ''
    part = a.split(',')[0]
    part = re.sub(r'\S*\d\S*', ' ', part)
    return fold(part)

def name_match(sa, t):
    if not sa or len(sa) < 3: return False
    for k in ('name', 'name:de', 'alt_name', 'old_name', 'official_name'):
        nm = fold(t.get(k))
        if nm and (nm == sa or (min(len(nm), len(sa)) >= 6 and (nm in sa or sa in nm))): return True
    return False

def bearing_at(ls, p):
    c = np.asarray(ls.coords); a, b = c[:-1], c[1:]; d = b - a
    L2 = (d ** 2).sum(1); L2[L2 == 0] = 1e-12
    t = np.clip(((p[0] - a[:, 0]) * d[:, 0] + (p[1] - a[:, 1]) * d[:, 1]) / L2, 0, 1)
    q = a + d * t[:, None]; k = int(np.argmin(((q - p) ** 2).sum(1)))
    v = d[k]; seglen = math.sqrt(L2[k]); how = 'tramo'
    if seglen < 6.0:
        s = ls.project(Point(p)); p1 = ls.interpolate(max(0, s - 8)); p2 = ls.interpolate(min(ls.length, s + 8))
        v = np.array([p2.x - p1.x, p2.y - p1.y]); how = 'cuerda'
    ang = math.atan2(v[1], v[0]) % math.pi
    # lado de la calle: signo del producto vectorial (tramo → punto)
    side = (d[k][0] * (p[1] - q[k][1]) - d[k][1] * (p[0] - q[k][0]))
    return ang, how, k, side, q[k], a[k], d[k]

def choose_street(lines, sa, p=(0.0, 0.0)):
    P0 = Point(float(p[0]), float(p[1])); best = {}
    for ls, t in lines:
        hw = t.get('highway'); dd = ls.distance(P0)
        if name_match(sa, t) and dd <= 40: cat = 0
        elif hw in VEH_STREET and dd <= 30: cat = 1
        elif hw == 'service' and dd <= 20: cat = 2
        elif hw in PED and dd <= 20: cat = 3
        else: continue
        if cat not in best or dd < best[cat][0]: best[cat] = (dd, ls, t)
    for cat in (0, 1, 2, 3):
        if cat in best: return cat, best[cat]
    return None, None

def layouts(n, cur_cols):
    sq = math.ceil(math.sqrt(n)) or 1
    if n == 1: L = [1]
    elif n <= 5: L = [n, math.ceil(n / 2)]
    elif n <= 16: L = [math.ceil(n / 2), math.ceil(n / 3)]
    else: L = [8, sq]
    out = []
    for c in L + [cur_cols]:
        if c not in out: out.append(c)
    return out

def main():
    a = sys.argv[1:]; dump = a[0]
    out = R / (a[a.index('--out') + 1] if '--out' in a else 'data/align-v24.json')
    rep = R / (a[a.index('--report') + 1] if '--report' in a else 'alineacion-v24.csv')
    stats_f = a[a.index('--stats') + 1] if '--stats' in a else None
    t0 = time.time()
    D = json.load(open(dump))
    assert not D.get('align') or not D['align'].get('applied'), 'el volcado debe ser el dibujo SIN alineación (--raw)'
    S = {}
    for r in D['stones']:
        sid, src, cc, ad, sla, slo, dla, dlo, ang, alias, added = r
        S[sid] = dict(id=sid, src=src, cc=cc or 'DE', a=ad, sla=sla, slo=slo, dla=dla, dlo=dlo, ang=ang, alias=alias, added=added)
    legit = {r['id'] for r in json.load(open(R / 'data' / 'sidewalk-v20.json', encoding='utf-8'))['stones'] if r.get('estado') == 'legitima'}
    exc25 = set()
    for f in ('excepciones-25m-v20.csv', 'excepciones-25m-v21.csv'):
        exc25 |= {row['id'] for row in csv.DictReader(open(R / f, encoding='utf-8'))}
    # grupos: los de la app (base) + placas municipales visibles agrupadas como en las pruebas v22 (SW.groups_of sobre la posición dibujada)
    G = []
    for g in D['groups']:
        if g['ids']: G.append({'ids': g['ids'], 'kind': 'base', 'old_ang': g['ang']})
    add_vis = [dict(s, la=s['dla'], lo=s['dlo']) for s in S.values() if s['added'] and not s['alias']]
    for g in SW.groups_of(add_vis):
        G.append({'ids': [s['id'] for s in g], 'kind': 'added', 'old_ang': 0.0})
    for g in G:
        ss = [S[i] for i in g['ids']]
        g['key'] = AG.source_key(ss[0]['cc'], ss[0]['src'] if ss[0]['added'] else None)
        g['c0'] = (sum(s['dla'] for s in ss) / len(ss), sum(s['dlo'] for s in ss) / len(ss))
        g['n'] = len(ss)
    vis_n = sum(1 for s in S.values() if not s['alias'])
    assert sum(g['n'] for g in G) == vis_n, (sum(g['n'] for g in G), vis_n)
    print('placas', len(S), 'visibles', vis_n, 'grupos', len(G), 'base', sum(g['kind'] == 'base' for g in G), flush=True)

    # índice global de posiciones de columnas (se actualiza al recolocar cada grupo)
    CELL = 0.00003
    pos = {sid: (s['dla'], s['dlo']) for sid, s in S.items() if not s['alias']}
    grid = defaultdict(set)
    ck = lambda la, lo: (math.floor(la / CELL), math.floor(lo / CELL))
    for sid, (la, lo) in pos.items(): grid[ck(la, lo)].add(sid)
    def others_near(la0, lo0, rad, own):
        r_la = rad / M_LAT; r_lo = rad / (M_LAT * math.cos(math.radians(la0)))
        i0, i1 = math.floor((la0 - r_la) / CELL), math.floor((la0 + r_la) / CELL)
        j0, j1 = math.floor((lo0 - r_lo) / CELL), math.floor((lo0 + r_lo) / CELL)
        out = []
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                for sid in grid.get((i, j), ()):
                    if sid not in own: out.append(pos[sid])
        return out

    cands = sorted(((float(s_), float(t_)) for s_ in np.arange(-S_MAX, S_MAX + 1e-9, S_STEP) for t_ in np.arange(-T_MAX, T_MAX + 1e-9, T_STEP)), key=lambda c: (abs(c[0]) + 2 * abs(c[1]), abs(c[1]), c))
    only = a[a.index('--only') + 1].split(',') if '--only' in a else None
    n_noconv = 0
    res = []; entries = []; n_changed_ang = 0; n_changed_layout = 0; cats = Counter(); cats_pin = Counter(); how_c = Counter(); errs_deg = []
    bykey = defaultdict(list)
    for gi, g in enumerate(G): bykey[g['key']].append(gi)
    for key in sorted(bykey, key=lambda k: -len(bykey[k])):
        if only and key not in only: continue
        tk = time.time(); geo = AG.Geo(key)
        print('geometría %s: %d edificios, %d vías (%.0fs) · %d grupos' % (key, geo.nb, geo.nh, time.time() - tk, len(bykey[key])), flush=True)
        order = sorted(bykey[key], key=lambda gi: -G[gi]['n'])
        for cnt, gi in enumerate(order):
            g = G[gi]; ids = g['ids']; n = g['n']; la0, lo0 = g['c0']; own = set(ids)
            ss = [S[i] for i in ids]
            r = {'gi': gi, 'id0': ids[0], 'n': n, 'kind': g['kind'], 'key': key, 'a': ss[0]['a'] or ''}
            cur_xy = np.array([AG.to_local(s['dla'], s['dlo'], la0, lo0) for s in ss])
            ext = float(np.max(np.hypot(cur_xy[:, 0], cur_xy[:, 1]))) if n > 1 else 0.0
            cur_cols = math.ceil(math.sqrt(n)) or 1
            if any(i in exc25 for i in ids):
                r.update(estado='sin_cambio', motivo='excepción 25 m documentada (excepciones-25m-v20/v21.csv): no se mueve'); res.append(r); cats['excepcion25'] += 1; continue
            if any(i in legit for i in ids):
                r.update(estado='sin_cambio', motivo='placa legítimamente dentro de un edificio (sidewalk-v20.json estado=legitima, p. ej. en un vestíbulo): no se mueve'); res.append(r); cats['legitima_interior'] += 1; continue
            rad = ext + 8 * STEP + S_MAX + 45
            B, btree, lines = geo.local(la0, lo0, rad)
            cat, st = choose_street(lines, street_of(ss[0]['a']))
            if cat is None:
                r.update(estado='sin_cambio', motivo='sin calle OSM a <=30 m (ni peatonal a <=20 m): patio, parque o cementerio; se deja como estaba'); res.append(r); cats['sin_calle'] += 1; continue
            dist_st, ls, tags = st
            _, how, segk, side0, q, a0, d0 = bearing_at(ls, np.array([0.0, 0.0]))
            sa = street_of(ss[0]['a'])
            rec = np.array([AG.to_local(s['sla'], s['slo'], la0, lo0) for s in ss])
            oth = others_near(la0, lo0, ext + 8 * STEP + S_MAX + 4, own)
            oth = np.array([AG.to_local(p[0], p[1], la0, lo0) for p in oth]) if oth else np.zeros((0, 2))
            # chincheta 2D (12 px a zoom 19, como sidewalk-render-check20): su centro (= el de la columna) a >= semilado + 0,5 m de todo edificio
            pin_r = PIN_PX_HALF * 40075016.686 / (256 * 2 ** 19) * math.cos(math.radians(la0)) + B_CLEAR
            # umbral por placa: semilado+0,53 m; si en v28 ya estaba más cerca (geometría OSM más nueva que la de v20 o residual documentado), no más cerca que en v28
            pin_thr = np.full(n, pin_r)
            if btree is not None:
                p0 = shapely.points(cur_xy); hh = btree.query(p0, predicate='dwithin', distance=pin_r)
                for k, bi in zip(hh[0], hh[1]): pin_thr[k] = min(pin_thr[k], float(shapely.distance(p0[k], B[bi])))
            n_pin_rel = int(np.sum(pin_thr < pin_r - 1e-9))
            if n_pin_rel: cats_pin['grupos_con_umbral_v28'] += 1; cats_pin['placas_con_umbral_v28'] += n_pin_rel
            veh = [(l, RWY.semiwidth(t)) for l, t in lines if RWY.is_vehicular(t)]
            vtree = shapely.STRtree([l for l, _ in veh]) if veh else None
            sl = lambda x, y: d0[0] * (y - q[1]) - d0[1] * (x - q[0])
            def search(a10, coherent=True):
                angq = a10 * math.pi / 1800
                ux, uy = math.cos(angq), math.sin(angq); nx, ny = -uy, ux
                for li, cols in enumerate(layouts(n, cur_cols)):
                    off = np.array(AG.grid_offsets(n, cols, angq, STEP))
                    for s_, t_ in cands:
                        cx, cy = s_ * ux + t_ * nx, s_ * uy + t_ * ny
                        C = off + np.array([cx, cy])
                        if np.max(np.hypot(C[:, 0] - rec[:, 0], C[:, 1] - rec[:, 1])) > MAXREC: continue
                        if len(oth):
                            dmin = np.min(np.hypot(C[:, None, 0] - oth[None, :, 0], C[:, None, 1] - oth[None, :, 1]))
                            if dmin < GAP: continue
                        if abs(side0) > 1.0 and sl(cx, cy) * side0 <= 0: continue
                        if btree is not None:
                            sq = AG.squares(C[:, 0], C[:, 1], angq, HALF)
                            hit = btree.query(sq, predicate='dwithin', distance=B_CLEAR)
                            if hit.shape[1]: continue
                            pc = shapely.points(C); hh = btree.query(pc, predicate='dwithin', distance=pin_r)
                            if hh.shape[1] and any(float(shapely.distance(pc[k], B[bi])) < pin_thr[k] - 1e-9 for k, bi in zip(hh[0], hh[1])): continue
                        bad_road = False
                        if vtree is not None:
                            pts = shapely.points(C)
                            for k in range(n):
                                for j in vtree.query(pts[k], predicate='dwithin', distance=8.0):
                                    l, sw = veh[j]
                                    if l.distance(pts[k]) < sw + ROAD_M:
                                        near_b = btree is not None and btree.query(pts[k], predicate='dwithin', distance=EXEMPT).size > 0
                                        if not near_b: bad_road = True; break
                                if bad_road: break
                        if bad_road: continue
                        if not coherent: return (li, cols, cx, cy)
                        # coherencia: el centro final de la fila queda frente al tramo cuyo rumbo se usa (mismo tramo → mismo rumbo)
                        c2, st2 = choose_street(lines, sa, (cx, cy))
                        if c2 is None or int(round(math.degrees(bearing_at(st2[1], np.array([cx, cy]))[0]) * 10)) % 1800 != a10: continue
                        return (li, cols, cx, cy)
                return None
            # rumbo = el del tramo más cercano al CENTRO FINAL de la fila: primero el del centro actual; si ninguna posición válida queda frente a ese
            # tramo, el del tramo que queda delante de la posición válida más cercana (<=3 rumbos distintos)
            pt = np.array([0.0, 0.0]); found = None; tried_a = set(); had_free = False
            for it in range(3):
                c_, st_it = choose_street(lines, sa, pt)
                if c_ is None: break
                a10_it = int(round(math.degrees(bearing_at(st_it[1], pt)[0]) * 10)) % 1800
                if a10_it in tried_a: break
                tried_a.add(a10_it)
                f = search(a10_it)
                if f is not None:
                    fc = np.array([f[2], f[3]]); c3, st3 = choose_street(lines, sa, fc)
                    found = f + (a10_it, c3, st3, bearing_at(st3[1], fc)[1]); break
                f = search(a10_it, False)
                if f is None: break
                had_free = True; pt = np.array([f[2], f[3]])
            if not found and had_free:
                n_noconv += 1
                r.update(estado='sin_cambio', motivo='esquina: toda posición válida deja el centro de la fila frente a otro tramo con otro rumbo; se deja como estaba', calle=tags.get('name') or tags.get('highway'), cat=cat)
                res.append(r); cats['esquina_sin_posicion_coherente'] += 1; continue
            if not found:
                r.update(estado='sin_cambio', motivo='ninguna disposición en 1–2 filas (ni la cuadrícula girada) cabe junto a la calle cumpliendo edificios ≥0,5 m, calzada, 25 m y 1,55 m: se deja como estaba', calle=tags.get('name') or tags.get('highway'), cat=cat)
                res.append(r); cats['sin_hueco'] += 1; continue
            li, cols, cx, cy, a10, cat, st, how = found
            dist_st, ls, tags = st
            angq = a10 * math.pi / 1800
            cla, clo = la0 + cy / M_LAT, lo0 + cx / (M_LAT * math.cos(math.radians(la0)))
            la7, lo7 = int(round(cla * 1e7)), int(round(clo * 1e7))
            P = AG.place_ll(la7 / 1e7, lo7 / 1e7, n, cols, angq, STEP)
            for sid, (pla, plo) in zip(ids, P):
                grid[ck(*pos[sid])].discard(sid); pos[sid] = (pla, plo); grid[ck(pla, plo)].add(sid)
            entries.append([la7, lo7, a10, cols] + ids)
            dang = abs((math.degrees(angq - (g['old_ang'] or 0)) + 90) % 180 - 90)
            shift = math.hypot(cx, cy)
            moved = max(math.hypot(*(np.array(AG.to_local(p[0], p[1], la0, lo0)) - cur_xy[k])) for k, p in enumerate(P))
            ch_ang = dang > 2.0; ch_lay = moved > 0.10
            n_changed_ang += ch_ang; n_changed_layout += ch_lay
            st_ = 'alineado' if li == 0 else ('alineado_cuadricula_girada' if cols == cur_cols else 'alineado_fila_alternativa')
            cats[st_] += 1; how_c[('nombre', 'via', 'service', 'peatonal')[cat] + '/' + how] += 1
            r.update(estado=st_, cat=cat, calle=tags.get('name') or tags.get('highway'), dist_calle=round(dist_st, 1), ang_old=round(math.degrees(g['old_ang'] or 0), 1), ang_new=a10 / 10, dang=round(dang, 1), cols=cols, rows=math.ceil(n / cols), shift=round(shift, 2), max_move=round(moved, 2), how=how)
            res.append(r)
            if cnt % 2000 == 0: print('  %s %d/%d (%.0fs)' % (key, cnt, len(order), time.time() - t0), flush=True)
        del geo
    entries.sort(key=lambda e: e[4])
    outj = {'v': 1, 'about': 'v29: posición de DIBUJO de las columnas alineada con la calle de OSM (solo dibujo; la/lo registrados no cambian). Cada entrada: [lat·1e7, lon·1e7, rumbo·10 (grados, 0–179.9), columnas, ids…]; casilla i → como layout() de app3d.js con paso 1,85 m.', 'step': STEP, 'g': entries}
    json.dump(outj, open(out, 'w'), separators=(',', ':'), ensure_ascii=False)
    with open(rep, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['id_primera_placa', 'placas', 'tipo', 'direccion', 'estado', 'motivo'])
        for r in sorted(res, key=lambda r: r['id0']):
            if r['estado'] == 'sin_cambio': w.writerow([r['id0'], r['n'], r['kind'], r['a'], r['estado'], r['motivo']])
    st = {'grupos': len(G), 'placas_visibles': vis_n, 'categorias': dict(cats), 'chincheta_2d': dict(cats_pin), 'calle_y_rumbo': {k: v for k, v in how_c.items()},
          'cambian_angulo_gt2': n_changed_ang, 'esquina_sin_posicion_coherente': n_noconv, 'cambian_disposicion_gt0_1m': n_changed_layout, 'entradas': len(entries),
          'placas_alineadas': sum(len(e) - 4 for e in entries), 'tiempo_s': round(time.time() - t0)}
    print(json.dumps(st, ensure_ascii=False, indent=1))
    if stats_f: json.dump({'stats': st, 'grupos': res}, open(stats_f, 'w'), ensure_ascii=False)

if __name__ == '__main__':
    main()
