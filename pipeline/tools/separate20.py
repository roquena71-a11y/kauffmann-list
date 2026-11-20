#!/usr/bin/env python3
"""v20: separación entre grupos (la app no separa los grupos fijos): columnas DIBUJADAS de grupos distintos a < 1,8 m se separan moviendo el grupo menor
(<= 8 m, mismo criterio exacto de edificios que sidewalk20). Lee el volcado de la app real; escribe sidewalk-comp20.json {grupo: [x, y]} (desplazamiento total) y changed_groups.json.
Uso: separate20.py DUMP.json CC [CC...]"""
import json, math, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sidewalk20 as SW
from shapely.geometry import Point
R = SW.R; D = SW.D
GAP = 1.8; MAXSEP = 8.0
dump = json.load(open(sys.argv[1])); ccs = sys.argv[2:]
S = json.load(open(R / 'data/stones.json', encoding='utf-8'))['stones']; byid = {s['id']: s for s in S}
rows = {r[0]: r for r in dump['rows']}
cf = Path(__file__).with_name('sidewalk-comp20.json'); comp = json.load(open(cf)) if cf.exists() else {}
legit = set(json.load(open(D / 'legit_inside.json')))
xf = Path(__file__).with_name('sidewalk-extra20.json'); EXTRA = json.load(open(xf)) if xf.exists() else {}   # holgura extra del grupo (si no, sidewalk20 descarta el desplazamiento por no caber)
A_ = json.load(open(D / 'ang20.json')); angs = A_['ang']; alias = set(A_['alias'])
changed = set(); total_pairs = 0; unresolved = 0
for cc in ccs:
    sel = [s for s in S if (s.get('cc') or 'DE') == cc]
    gs = SW.groups_of(sel); gid = {}
    for g in gs:
        for s in g: gid[s['id']] = g[0]['id']
    gmap = {g[0]['id']: g for g in gs}
    NN = None
    # columnas dibujadas (no alias) por celda
    M = 111320.0; cell = 4.0; grid = defaultdict(list); pts = {}
    for g in gs:
        for s in g:
            r = rows.get(s['id'])
            if r is None or r[7]: continue
            y = r[4] * M; x = r[5] * M * math.cos(math.radians(r[4])); pts[s['id']] = (y, x, gid[s['id']])
            grid[(int(y // cell), int(x // cell))].append(s['id'])
    def near_pts(y, x, own, rad=GAP):
        out = []
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for sid in grid.get((int(y // cell) + di, int(x // cell) + dj), ()):
                    y2, x2, g2 = pts[sid]
                    if g2 != own and math.hypot(y - y2, x - x2) < rad: out.append(sid)
        return out
    colliding = defaultdict(set)
    for sid, (y, x, g) in pts.items():
        for o in near_pts(y, x, g): colliding[g].add(gid[o])
    pairs = sum(len(v) for v in colliding.values()) // 2; total_pairs += pairs
    done = set()
    for g_, others in sorted(colliding.items(), key=lambda kv: (len(gmap[kv[0]]), kv[0])):
        if g_ in done: continue
        # se mueve el menor del conjunto en colisión (empate: id menor); los demás se quedan
        if any(o not in done and (len(gmap[o]), o) < (len(gmap[g_]), g_) for o in others): continue
        if any(o in done for o in others): continue
        g = gmap[g_]
        if all(s['id'] in legit for s in g): continue
        la0 = sum(s['la'] for s in g) / len(g); lo0 = sum(s['lo'] for s in g) / len(g); o = (la0, lo0)
        if NN is None: NN = SW.load_near(cc)
        PB, polys, ids, lines, RW = SW.local_geom(NN, la0, lo0)
        pins = [SW.to_xy(s['la'], s['lo'], o) for s in g]
        vis = [s for s in g if s['id'] not in alias] or g; ang = angs.get(vis[0]['id'])
        okf = SW.make_okf(PB, pins, SW.slots(len(vis), ang or 0.0), ang, SW.icon_half(la0), EXTRA.get(g_, 0.0))
        cur = [(s['dla'], s['dlo']) for s in g if 'dla' in s]
        q0 = SW.to_xy(sum(a for a, b in cur) / len(cur), sum(b for a, b in cur) / len(cur), o) if cur else (0.0, 0.0)
        mem = [(sid, pts[sid]) for sid in (s['id'] for s in g) if sid in pts]
        best = None
        for a in range(0, 360, 10):
            ux, uy = math.cos(math.radians(a)), math.sin(math.radians(a)); t = 0.2
            while t <= MAXSEP:
                q = (q0[0] + ux * t, q0[1] + uy * t)
                if math.hypot(*q) <= SW.MAXMOVE - (SW.spread(len(g)) if 1 < len(g) <= 20 else 0.0) and okf(q) and not any(near_pts(py + uy * t, px + ux * t, g_, GAP) for _, (py, px, _) in mem):
                    if best is None or t < best[0]: best = (t, q)
                    break
                t += 0.2
        if best: comp[g_] = [round(best[1][0], 2), round(best[1][1], 2)]; changed.add(g_); done.add(g_)
        else: unresolved += 1
    print(cc, 'pares', pairs, 'grupos movidos', len([1 for x in changed if x in gmap]))
json.dump(comp, open(cf, 'w'), indent=0)
old = set(json.load(open(D / 'changed_groups.json'))) if (D / 'changed_groups.json').exists() else set()
json.dump(sorted(changed | old), open(D / 'changed_groups.json', 'w'))
print('TOTAL pares', total_pairs, 'movidos', len(changed), 'sin solución', unresolved)
