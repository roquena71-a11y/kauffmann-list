#!/usr/bin/env python3
"""v19: posición de DIBUJO (dla/dlo) de las placas fuera de edificios, calle de por medio.
Las coordenadas de origen (la/lo) NO se tocan. Solo se añaden dla/dlo cuando la placa cae dentro de un edificio de OSM
o la columna cuadrada dibujada (1,2 m de lado, 0,85 m de media diagonal) tocaría la huella; el desplazamiento mira hacia la
calle (vía de OSM más cercana: acera, calle, plaza) y es el mínimo que deja la columna libre. Máximo 25 m; si hiciera falta más, se deja y se marca «revisar».
Uso: sidewalk.py [--extra GRUPO=metros ...]   → actualiza data/stones.json, data/sidewalk-v19.json y tests/sidewalk/footprints-v19.json"""
import json, math, sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import *
R = Path(__file__).resolve().parents[2]
D = Path(os.environ.get('V19_DATA', '/workspace/v19-data'))
CCS = ('IE', 'SE', 'JE', 'FI', 'RO')
COL_HALF, COL_STEP = 0.60, 1.85
DIAG = COL_HALF * math.sqrt(2)          # 0,849 m
MARGIN = 0.10
MAXMOVE = 25.0
ROADWAY = {'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential', 'living_street', 'service', 'road'}
NOT_STREET = {'proposed', 'construction', 'platform', 'bus_stop', 'corridor', 'elevator', 'razed', 'abandoned', 'services', 'rest_area'}

def spread(n):
    cols = math.ceil(math.sqrt(n)); rows = math.ceil(n / cols)
    return math.hypot((cols - 1) / 2, (rows - 1) / 2) * COL_STEP

def load():
    data = json.load(open(R / 'data/stones.json', encoding='utf-8'))
    near = json.load(open(D / 'near.json', encoding='utf-8'))
    return data, near

def groups_of(stones):
    sel = [s for s in stones if s.get('cc') in CCS]
    gs = []
    for s in sel:
        for g in gs:
            if g[0]['cc'] == s['cc'] and hav(g[0]['la'], g[0]['lo'], s['la'], s['lo']) <= 3.0: g.append(s); break
        else: gs.append([s])
    return gs

def prep_buildings(B, o, rad=80):
    out = []
    for bid, b in B.items():
        ro = [[to_xy(a, c, o) for a, c in r] for r in b['outer']]; ri = [[to_xy(a, c, o) for a, c in r] for r in b['inner']]
        if min(math.hypot(x, y) for r in ro for x, y in r) > rad + 60: continue
        out.append((bid, ro, ri, b['tags']))
    return out

def clearance(x, y, PB):
    """(distancia con signo al edificio más cercano: negativa si está dentro, id)."""
    best = (1e9, None)
    for bid, ro, ri, _ in PB:
        d, _p = dist_to_rings(x, y, ro + ri)
        if inside_poly(x, y, ro, ri): d = -d
        if abs(d) < abs(best[0]) or (d < 0 <= best[0]): best = (d, bid) if (d < 0 or best[0] >= 0) and abs(d) < abs(best[0]) or d < 0 else best
    return best

def clear_dist(x, y, PB):
    """Distancia al borde del edificio más cercano; 0 si está dentro."""
    m = 1e9; bid = None
    for b, ro, ri, _ in PB:
        if inside_poly(x, y, ro, ri): return 0.0, b
        d, _p = dist_to_rings(x, y, ro + ri)
        if d < m: m, bid = d, b
    return m, bid

def highways(H, o):
    out = []
    for hid, h in H.items():
        t = h.get('tags') or {}
        if t.get('highway') in NOT_STREET or t.get('tunnel') or t.get('indoor'): continue
        g = [to_xy(p['lat'], p['lon'], o) for p in h.get('geometry', [])]
        if len(g) >= 2: out.append((hid, g, t))
    return out

def nearest_highway(x, y, HW):
    best = (1e9, None, None, None)
    for hid, g, t in HW:
        for i in range(len(g) - 1):
            cx, cy, d = seg_closest(x, y, g[i][0], g[i][1], g[i + 1][0], g[i + 1][1])
            if d < best[0]: best = (d, (cx, cy), hid, t)
    return best

def solve(P, PB, HW, need):
    """Desplazamiento mínimo (dx,dy) hacia la calle que deja distancia >= need al edificio. None si pasa de MAXMOVE."""
    dH, H, hid, ht = nearest_highway(P[0], P[1], HW)
    if H is None: return None, None
    if dH > 0.3: hx, hy = (H[0] - P[0]) / dH, (H[1] - P[1]) / dH
    else:
        d0, b0 = clear_dist(P[0], P[1], PB); hx = hy = 0
    best = None
    for a in range(0, 360, 5):
        ux, uy = math.cos(math.radians(a)), math.sin(math.radians(a))
        dot = ux * hx + uy * hy if dH > 0.3 else 1.0
        if dot < 0.5: continue
        t = 0.05
        while t <= MAXMOVE:
            if dH > 0.3 and t * dot > dH + 0.5: break          # no pasar de la vía
            q = (P[0] + ux * t, P[1] + uy * t)
            d, _b = clear_dist(q[0], q[1], PB)
            if d >= need: 
                key = (round(t, 2), -dot)
                if best is None or key < best[0]: best = (key, (ux * t, uy * t), t)
                break
            t += 0.05
    if best is None: return None, (hid, ht, dH)
    return best[1], (hid, ht, dH)

def main():
    extra = {}
    for a in sys.argv[1:]:
        if '=' in a: k, v = a.split('='); extra[k] = float(v)
    data, near = load()
    S = data['stones']
    B = building_polygons(near['buildings'])
    table = []; snap = {}
    gs = groups_of(S)
    for g in gs:
        for s in g: s.pop('dla', None); s.pop('dlo', None)
        la0 = sum(s['la'] for s in g) / len(g); lo0 = sum(s['lo'] for s in g) / len(g); o = (la0, lo0)
        PB = prep_buildings(B, o); HW = highways(near['highways'], o)
        need = DIAG + MARGIN + (spread(len(g)) if len(g) > 1 else 0) + extra.get(g[0]['id'], 0)
        d0, b0 = clear_dist(0, 0, PB)
        insd = any(inside_poly(0, 0, ro, ri) for _, ro, ri, _t in PB)
        status, shift, info = 'ok', None, nearest_highway(0, 0, HW)
        if insd or d0 < need:
            shift, info2 = solve((0, 0), PB, HW, need)
            if shift is None: status = 'revisar'
            else: status = 'ajustada'
        for s in g:
            r = {'id': s['id'], 'n': s.get('n'), 'cc': s['cc'], 'la': s['la'], 'lo': s['lo'], 'grupo': len(g),
                 'dentro_edificio': insd, 'borde_m': round(d0, 2), 'edificio': b0, 'necesita_m': round(need, 2), 'estado': status,
                 'via_mas_cercana': {'id': info[2], 'highway': (info[3] or {}).get('highway'), 'name': (info[3] or {}).get('name'), 'm': round(info[0], 1)}}
            if shift:
                x, y = to_xy(s['la'], s['lo'], o)
                la, lo = to_ll(x + shift[0], y + shift[1], o)
                s['dla'] = round(la, 7); s['dlo'] = round(lo, 7)
                r['dla'], r['dlo'] = s['dla'], s['dlo']; r['desplazamiento_m'] = round(math.hypot(*shift), 2)
                dd, _ = clear_dist(x + shift[0] - 0, y + shift[1], PB); r['borde_despues_m'] = round(dd, 2)
            av = []
            if (info[3] or {}).get('highway') in ROADWAY and info[0] < 1.5: av.append('sobre el eje de la calzada (%s, a %.1f m): posible desvío de la fuente o calle sin acera' % (info[3].get('highway'), info[0]))
            if d0 > 20: av.append('ningún edificio de OSM a menos de 20 m (%s): no se puede comprobar la fachada' % ('sin edificios en 110 m' if d0 > 1000 else '%.0f m' % d0))
            if av: r['avisos'] = av
            table.append(r)
        # instantánea de edificios cercanos (<=60 m) para la prueba automática
        for s in g:
            so = (s['la'], s['lo']); k = s['id']
            near_b = {}
            for bid, b in B.items():
                ro = [[to_xy(a, c, so) for a, c in r] for r in b['outer']]
                if min(math.hypot(x, y) for r in ro for x, y in r) > 90: continue
                dd, _p = dist_to_rings(0, 0, ro)
                if dd <= 60: near_b[bid] = {'o': [[[round(a, 7), round(c, 7)] for a, c in r] for r in b['outer']], 'i': [[[round(a, 7), round(c, 7)] for a, c in r] for r in b['inner']]}
            snap[k] = near_b
    (R / 'data/stones.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    # edificios únicos
    uniq = {}
    for k, bs in snap.items():
        for bid, b in bs.items(): uniq[bid] = b
    fp = {'attribution': '© colaboradores de OpenStreetMap (ODbL 1.0)', 'osm_timestamp': near['osm_timestamp'], 'radius_m': 60,
          'note': 'Huellas de edificios (building=*) de OSM a <=60 m de cada placa de IE/SE/JE/FI/RO; solo para la prueba automática tests/sidewalk-test.cjs',
          'near': {k: sorted(v) for k, v in snap.items()}, 'buildings': uniq}
    (R / 'tests/sidewalk').mkdir(exist_ok=True)
    (R / 'tests/sidewalk/footprints-v19.json').write_text(json.dumps(fp, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    (R / 'data/sidewalk-v19.json').write_text(json.dumps({'meta': {'osm_timestamp': near['osm_timestamp'], 'clear_m': round(DIAG + MARGIN, 2), 'max_move_m': MAXMOVE,
        'method': 'Si la placa cae dentro de un edificio de OSM o la columna dibujada (1,2 m) tocaría su huella, la posición de dibujo (dla/dlo) se desplaza el mínimo hacia la vía de OSM más cercana hasta dejar la columna libre; la coordenada de origen (la/lo) no cambia.'},
        'stones': table}, ensure_ascii=False, indent=1), encoding='utf-8')
    from collections import Counter
    print(Counter((r['cc'], r['estado']) for r in table))
    for r in table:
        if r['estado'] != 'ok': print(r['cc'], r['id'], r['n'], r['estado'], 'dentro' if r['dentro_edificio'] else '', 'borde', r['borde_m'], '-> mover', r.get('desplazamiento_m'), 'borde despues', r.get('borde_despues_m'), r['via_mas_cercana'])
if __name__ == '__main__': main()
