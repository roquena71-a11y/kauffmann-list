#!/usr/bin/env python3
"""v20: huellas de edificios de OSM (ODbL) para tests/sidewalk-render-check.py: todas las placas de los países nuevos + una muestra fija de 1.500 de Alemania (semilla 20261120).
Salida: tests/sidewalk/footprints-v20.json.gz  {ids, legit, near:{id:[bid]}, buildings:{bid:{o:[anillos],i:[anillos]}}}"""
import json, gzip, random, sys, math, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sidewalk20 as SW
R = SW.R
S = json.load(open(R / 'data/stones.json', encoding='utf-8'))['stones']
legit = set(json.load(open(SW.D / 'legit_inside.json')))
random.seed(20261120)
de = [s for s in S if (s.get('cc') or 'DE') == 'DE']
sel = [s for s in S if (s.get('cc') or 'DE') not in ('DE',) + SW.V19] + random.sample(de, 1500) + [s for s in de if s['id'] in legit]
byc = {}
for s in sel: byc.setdefault(s.get('cc') or 'DE', []).append(s)
near = {}; B = {}; ids = []
for cc, ss in byc.items():
    N = SW.load_near(cc)
    for s in ss:
        la, lo = s['la'], s['lo']; ids.append(s['id']); near[s['id']] = []
        for bid in N.around(N.bi, la, lo, 1):
            outer, inner, tags = N.b[bid]
            if min(SW.hav(la, lo, a, b) for r in outer for a, b in r) > 70: continue
            near[s['id']].append(bid)
            if bid not in B: B[bid] = {'o': [[[round(a, 7), round(b, 7)] for a, b in r] for r in outer], 'i': [[[round(a, 7), round(b, 7)] for a, b in r] for r in inner]}
# v20r2 (auditoría C, F1): placas sin ningún edificio de OSM a <=50 m (tras volver a traer las huellas): lista explícita; el test falla si aparece alguna fuera de ella
def _d50(s, bids): return any(min(SW.hav(s['la'], s['lo'], a, b) for r in B[bid]['o'] for a, b in r) <= 50 for bid in bids)
sin_ed = sorted(i for i in ids if not _d50(next(s for s in sel if s['id'] == i), near[i])) if False else sorted(s['id'] for s in sel if not _d50(s, near[s['id']]))
# CSV con la distancia al edificio más cercano (los datos incluyen edificios hasta 120 m: más lejos = ninguno en OSM)
import csv
def _dmin(s):
    N = _N.setdefault(s.get('cc') or 'DE', SW.load_near(s.get('cc') or 'DE')); best = None
    for bid in N.around(N.bi, s['la'], s['lo'], 2):
        o, i, t_ = N.b[bid]; d_ = min(SW.hav(s['la'], s['lo'], a, b) for r in o for a, b in r); best = d_ if best is None else min(best, d_)
    return best
_N = {}; _sin = {s['id']: s for s in sel if s['id'] in set(sin_ed)}
with open(R / 'sin-edificios-v20.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['id', 'pais', 'nombre', 'direccion', 'ciudad', 'edificio_mas_cercano_m'])
    for i in sin_ed:
        s = _sin[i]; d_ = _dmin(s); w.writerow([i, s.get('cc') or 'DE', s.get('n'), s.get('a'), s.get('c'), ('%.0f' % d_) if d_ is not None and d_ <= 150 else '>150 (ninguno en OSM)'])
out = {'ids': sorted(set(ids)), 'legit': sorted(legit & set(ids)), 'sin_edificios_50m': sin_ed, 'near': near, 'buildings': B}
p = R / 'tests/sidewalk/footprints-v20.json.gz'
with gzip.open(p, 'wt', encoding='utf-8', compresslevel=9) as f: json.dump(out, f, separators=(',', ':'))
print(len(sin_ed), 'placas sin edificio a <=50 m:', sin_ed[:12]); print(len(out['ids']), 'placas', len(B), 'edificios', round(os.path.getsize(p) / 1e6, 2), 'MB')
