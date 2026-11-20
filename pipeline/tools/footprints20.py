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
out = {'ids': sorted(set(ids)), 'legit': sorted(legit & set(ids)), 'near': near, 'buildings': B}
p = R / 'tests/sidewalk/footprints-v20.json.gz'
with gzip.open(p, 'wt', encoding='utf-8', compresslevel=9) as f: json.dump(out, f, separators=(',', ':'))
print(len(out['ids']), 'placas', len(B), 'edificios', round(os.path.getsize(p) / 1e6, 2), 'MB')
