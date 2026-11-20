#!/usr/bin/env python3
"""v20: posición de DIBUJO (dla/dlo) de TODAS las placas (Alemania incluida) fuera de los edificios de OSM, con shapely.
Mismo criterio que v19 (sidewalk.py): columna 3D de 1,2 m (media diagonal 0,849 m) + chincheta 2D (12 px a zoom 19) con >= 0,5 m de holgura a toda fachada;
el desplazamiento mira hacia la calle y es el mínimo; máximo 25 m, si no «revisar». La coordenada de origen (la/lo) NO se toca.
Excepción: placas que la fuente sitúa legítimamente dentro de un edificio (OSM indoor=yes, location=indoor/inside, level distinto de 0): no se mueven.
Las placas de IE/SE/JE/FI/RO conservan su cálculo de la v19 (data/sidewalk-v19.json).
Entradas (V20_DATA): near/CC.json (Overpass: edificios y vías de OSM a <=100 m de cada candidato; ODbL) o near/DE.pkl (extraído del PBF de Geofabrik).
Uso: sidewalk20.py [CC ...]   (por defecto todos los países con datos)  → data/stones.json (dla/dlo), data/sidewalk-v20.json"""
import json, math, sys, os, pickle, glob
from pathlib import Path
from collections import defaultdict
import shapely
from shapely.geometry import Point, Polygon, LineString, MultiPolygon, box
from shapely.ops import unary_union, nearest_points
from shapely.prepared import prep
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import to_xy, to_ll, hav, building_polygons
R = Path(__file__).resolve().parents[2]
D = Path(os.environ.get('V20_DATA', '/workspace/v20-data'))
V19 = ('IE', 'SE', 'JE', 'FI', 'RO')
COL_HALF = 0.60; DIAG = COL_HALF * math.sqrt(2); MARGIN = 0.50; ICON_PX = 12
MPP19 = 40075016.686 / (256 * 2 ** 19); MAXMOVE = 25.0; COL_STEP = 1.85
ROADWAY = {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'living_street', 'service', 'road'}
NOT_STREET = {'proposed', 'construction', 'platform', 'bus_stop', 'corridor', 'elevator', 'razed', 'abandoned', 'services', 'rest_area'}
CELL = 0.001

def icon_half(lat): return ICON_PX / 2 * MPP19 * math.cos(math.radians(lat))
def spread(n):
    cols = math.ceil(math.sqrt(n)); rows = math.ceil(n / cols)
    return math.hypot((cols - 1) / 2, (rows - 1) / 2) * COL_STEP
def cell(la, lo): return (math.floor(la / CELL), math.floor(lo / (CELL * 1.6)))

class Near:
    """Edificios y vías de un país, indexados por celdas de ~110 m."""
    def __init__(self):
        self.b = {}; self.h = {}; self.bi = defaultdict(list); self.hi = defaultdict(list); self.ts = None
    def add_b(self, bid, outer, inner, tags):
        if bid in self.b: return
        self.b[bid] = (outer, inner, tags)
        las = [p[0] for r in outer for p in r]; los = [p[1] for r in outer for p in r]
        for i in range(cell(min(las), min(los))[0], cell(max(las), max(los))[0] + 1):
            for j in range(cell(min(las), min(los))[1], cell(max(las), max(los))[1] + 1): self.bi[(i, j)].append(bid)
    def add_h(self, hid, pts, tags):
        if hid in self.h: return
        self.h[hid] = (pts, tags)
        las = [p[0] for p in pts]; los = [p[1] for p in pts]
        for i in range(cell(min(las), min(los))[0], cell(max(las), max(los))[0] + 1):
            for j in range(cell(min(las), min(los))[1], cell(max(las), max(los))[1] + 1): self.hi[(i, j)].append(hid)
    def around(self, idx, la, lo, rc=1):
        i, j = cell(la, lo); out = set()
        for di in range(-rc, rc + 1):
            for dj in range(-rc, rc + 1): out.update(idx.get((i + di, j + dj), ()))
        return out

def load_near(cc):
    N = Near(); pk = D / ('near/%s.pkl' % cc); jf = D / ('near/%s.json' % cc)
    if pk.exists():
        d = pickle.load(open(pk, 'rb')); N.ts = d.get('osm_timestamp')
        for bid, (o, i, t) in d['buildings'].items(): N.add_b(bid, o, i, t)
        for hid, (p, t) in d['highways'].items(): N.add_h(hid, p, t)
        return N
    d = json.load(open(jf, encoding='utf-8')); N.ts = d.get('osm_timestamp')
    for bid, b in building_polygons(d['buildings']).items(): N.add_b(bid, b['outer'], b['inner'], b['tags'])
    for hid, h in d['highways'].items():
        g = [(p['lat'], p['lon']) for p in h.get('geometry', [])]
        if len(g) >= 2: N.add_h(hid, g, h.get('tags') or {})
    return N

def groups_of(stones):
    """Agrupación como la de la app (clusterByDist): enlace simple; 15 m entre placas con la misma dirección (addrKey), 3,5 m sin dirección."""
    par = list(range(len(stones)))
    def find(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    byk = defaultdict(list)
    for i, s in enumerate(stones):
        a = s.get('a'); k = ('A', (s.get('c') or '').strip().lower(), a.strip().lower()) if a else ('N',)
        byk[k].append(i)
    for k, idx in byk.items():
        lim = 15.0 if k[0] == 'A' else 3.5
        grid = defaultdict(list)
        for i in idx:
            s = stones[i]; grid[(math.floor(s['la'] / 0.0003), math.floor(s['lo'] / 0.0005))].append(i)
        for i in idx:
            s = stones[i]; ci, cj = math.floor(s['la'] / 0.0003), math.floor(s['lo'] / 0.0005)
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    for j in grid.get((ci + di, cj + dj), ()):
                        if j > i and hav(s['la'], s['lo'], stones[j]['la'], stones[j]['lo']) <= lim: par[find(i)] = find(j)
    gs = defaultdict(list)
    for i in range(len(stones)): gs[find(i)].append(stones[i])
    return [sorted(g, key=lambda s: s['id']) for g in gs.values()]

def local_geom(N, la0, lo0, rad=70):
    o = (la0, lo0); polys = []; ids = []
    for bid in N.around(N.bi, la0, lo0, 1):
        outer, inner, tags = N.b[bid]
        ro = [[to_xy(a, c, o) for a, c in r] for r in outer]
        if min(math.hypot(x, y) for r in ro for x, y in r) > rad + 40: continue
        ri = [[to_xy(a, c, o) for a, c in r] for r in inner]
        try:
            ps = [Polygon(r) for r in ro]; ps = [p if p.is_valid else p.buffer(0) for p in ps]
            u = unary_union(ps)
            if ri: u = u.difference(unary_union([Polygon(r).buffer(0) for r in ri]))
            polys.append(u); ids.append(bid)
        except Exception: continue
    PB = unary_union(polys) if polys else None
    lines = []; roads = []
    for hid in N.around(N.hi, la0, lo0, 1):
        pts, t = N.h[hid]
        if t.get('highway') in NOT_STREET or t.get('tunnel') or t.get('indoor'): continue
        ls = LineString([to_xy(a, c, o) for a, c in pts]); lines.append((ls, t))
        if t.get('highway') in ROADWAY: roads.append(ls)
    return PB, polys, ids, lines, (unary_union(roads) if roads else None)

def ok_at(q, PB, need, h2):
    if PB is None: return True
    if PB.distance(Point(q)) < need: return False
    c, s = 1.0, 0.0; hh = h2 + MARGIN
    return not Polygon([(q[0] - hh, q[1] - hh), (q[0] + hh, q[1] - hh), (q[0] + hh, q[1] + hh), (q[0] - hh, q[1] + hh)]).intersects(PB)

def solve(PB, lines, RW, need, h2, inside, keep_min=1.5, min_dot=0.5):
    P = Point(0, 0)
    best_h = None
    for ls, t in lines:
        d = ls.distance(P)
        if best_h is None or d < best_h[0]: best_h = (d, ls, t)
    if best_h is None: return None, None
    dH, hl, ht = best_h
    if inside or PB is None:
        hp = nearest_points(P, hl)[1]
        if dH > 0.3: hx, hy = (hp.x) / dH, (hp.y) / dH
        else: hx = hy = 0.0
        use = dH > 0.3
    else:
        cp = nearest_points(PB, P)[0]; dd = P.distance(cp)
        if dd < 1e-6: hx = hy = 0.0; use = False
        else: hx, hy = (0 - cp.x) / dd, (0 - cp.y) / dd; use = True
    rd0 = RW.distance(P) if RW is not None else 1e9; keep = min(rd0, keep_min) - 0.01
    best = None
    for a in range(0, 360, 5):
        ux, uy = math.cos(math.radians(a)), math.sin(math.radians(a))
        dot = ux * hx + uy * hy if use else 1.0
        if dot < min_dot: continue
        t = 0.05
        while t <= MAXMOVE:
            q = (ux * t, uy * t)
            if (inside and use and min_dot > 0 and t * dot > dH + 0.5) or (RW is not None and RW.distance(Point(q)) < keep): break
            if ok_at(q, PB, need, h2):
                key = (round(t, 2), -dot)
                if best is None or key < best[0]: best = (key, (q[0], q[1]), t)
                break
            t += 0.05
    if best is None: return None, (dH, ht)
    return best[1], (dH, ht)

def process_cc(cc, stones, N, extra, legit, only=None):
    sel = [s for s in stones if (s.get('cc') or 'DE') == cc]
    if only is None:
        for s in sel: s.pop('dla', None); s.pop('dlo', None)
    table = []; n_ok = 0
    for g in groups_of(sel):
        if only is not None:
            if g[0]['id'] not in only: continue
            for s in g: s.pop('dla', None); s.pop('dlo', None)
        la0 = sum(s['la'] for s in g) / len(g); lo0 = sum(s['lo'] for s in g) / len(g); o = (la0, lo0)
        PB, polys, ids, lines, RW = local_geom(N, la0, lo0)
        need = DIAG + MARGIN + (spread(len(g)) if len(g) > 1 else 0) + extra.get(g[0]['id'], 0)
        h2 = icon_half(la0); P0 = Point(0, 0)
        insd = bool(PB is not None and PB.contains(P0)); d0 = 0.0 if insd else (PB.distance(P0) if PB is not None else 1e9)
        status, shift, tier = 'ok', None, 0
        if all(s['id'] in legit for s in g) and (insd or not ok_at((0, 0), PB, need, h2)):
            status = 'legitima'
        elif insd or not ok_at((0, 0), PB, need, h2):
            shift, info = solve(PB, lines, RW, need, h2, insd); tier = 1
            need1 = DIAG + MARGIN + extra.get(g[0]['id'], 0)
            if shift is None and len(g) > 1: shift, info = solve(PB, lines, RW, need1, h2, insd); tier = 2      # grupo grande en acera estrecha: sitio para una columna; la comprobación con la cuadrícula real de la app (bucle) añade lo que falte
            if shift is None: shift, info = solve(PB, lines, RW, need1, h2, insd, keep_min=0.4); tier = 3          # acera muy estrecha: se permite acercarse más al eje de la calzada
            if shift is None: shift, info = solve(PB, lines, RW, need1, h2, insd, keep_min=0.4, min_dot=-1.01); tier = 4   # sin sitio hacia la calle (patio, esquina): cualquier dirección, sin cruzar la calzada
            status = 'revisar' if shift is None else 'ajustada'
        if status == 'ok': n_ok += len(g); continue
        for s in g:
            r = {'id': s['id'], 'n': s.get('n'), 'cc': cc, 'la': s['la'], 'lo': s['lo'], 'grupo': len(g), 'grupo_id': g[0]['id'], 'extra_m': round(extra.get(g[0]['id'], 0), 2),
                 'dentro_edificio': insd, 'borde_m': round(d0, 2), 'necesita_m': round(need, 2), 'estado': status, 'nivel': (tier if shift else 0) if status != 'legitima' else 0}
            if shift:
                x, y = to_xy(s['la'], s['lo'], o); la, lo = to_ll(x + shift[0], y + shift[1], o)
                s['dla'] = round(la, 7); s['dlo'] = round(lo, 7); r['dla'], r['dlo'] = s['dla'], s['dlo']; r['desplazamiento_m'] = round(math.hypot(*shift), 2)
                r['borde_despues_m'] = round(PB.distance(Point(shift)) if PB is not None else 1e9, 2)
            table.append(r)
    return table, n_ok

def main():
    ccs = [a for a in sys.argv[1:] if not a.startswith('-')]
    data = json.load(open(R / 'data/stones.json', encoding='utf-8')); S = data['stones']
    extra = {}
    xf = Path(__file__).with_name('sidewalk-extra20.json')
    if xf.exists(): extra.update(json.load(open(xf)))
    legit = set(json.load(open(D / 'legit_inside.json'))) if (D / 'legit_inside.json').exists() else set()
    have = sorted({(s.get('cc') or 'DE') for s in S} - set(V19))
    if ccs: have = [c for c in have if c in ccs]
    table = []; counts = {}; ts = {}
    for cc in have:
        if not ((D / ('near/%s.json' % cc)).exists() or (D / ('near/%s.pkl' % cc)).exists()): print('sin datos de edificios:', cc); continue
        N = load_near(cc); ts[cc] = N.ts
        only = set(json.load(open(D / 'changed_groups.json'))) if '--only' in sys.argv else None
        t, nok = process_cc(cc, S, N, extra, legit, only)
        if only is not None:
            pv = json.load(open(R / 'data/sidewalk-v20.json', encoding='utf-8'))
            t = [r for r in pv['stones'] if r['cc'] == cc and r['grupo_id'] not in only] + t
            nok = sum(1 for x in S if (x.get('cc') or 'DE') == cc) - len(t)
        table += t
        from collections import Counter
        c = Counter(r['estado'] for r in t); counts[cc] = {'ok': nok, **{k: v for k, v in c.items()}}
        print(cc, counts[cc], flush=True)
    (R / 'data/stones.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    prev = {}
    p = R / 'data/sidewalk-v20.json'
    if p.exists() and (ccs or True): prev = json.load(open(p, encoding='utf-8'))
    tb = [r for r in prev.get('stones', []) if r['cc'] not in have] + table
    cn = {**prev.get('counts', {}), **counts}
    p.write_text(json.dumps({'meta': {'osm_timestamp': ts, 'clear_m': round(DIAG + MARGIN, 2), 'margin_m': MARGIN, 'icon2d_px': ICON_PX, 'max_move_m': MAXMOVE,
        'method': 'Misma regla que v19 con shapely: si la placa cae dentro de un edificio de OSM o la columna 3D (1,2 m) o la chincheta 2D (12 px a zoom 19) quedaría a menos de 0,5 m de una huella, la posición de dibujo (dla/dlo) se desplaza el mínimo hacia la calle, máximo 25 m; la coordenada de origen no se toca. Solo se listan las placas no «ok».'},
        'counts': cn, 'stones': tb}, ensure_ascii=False, indent=1), encoding='utf-8')
if __name__ == '__main__': main()
