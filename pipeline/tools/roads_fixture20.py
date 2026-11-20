#!/usr/bin/env python3
"""v20r4: ejes de las vías rodadas de OSM (ODbL) cerca de las placas de tests/sidewalk/footprints-v20.json.gz, para el test de calzada (tests/sidewalk-render-check20.py).
Salida: tests/sidewalk/roads-v20.json.gz {roads:{rid:{p:[[lat,lon]..], hw:semiancho, c:1 si obliga (hay acera), n:nombre/clase}}, near:{id:[rid]}}. Ejecutar DESPUÉS de footprints20.py."""
import json, gzip, sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sidewalk20 as SW, roadway20 as RWY
from shapely.geometry import Point, LineString
from geo import to_xy
R = SW.R
FP = json.load(gzip.open(R / 'tests/sidewalk/footprints-v20.json.gz', 'rt', encoding='utf-8'))
S = {s['id']: s for s in json.load(open(R / 'data/stones.json', encoding='utf-8'))['stones']}
byc = {}
for i in FP['ids']: byc.setdefault(S[i].get('cc') or 'DE', []).append(S[i])
roads = {}; near = {}
for cc, ss in byc.items():
    N = SW.load_near(cc)
    for s in ss:
        near[s['id']] = []
        for hid in N.around(N.hi, s['la'], s['lo'], 1):
            pts, t = N.h[hid]
            if not RWY.is_vehicular(t): continue
            o = (s['la'], s['lo'])
            if LineString([to_xy(a, c, o) for a, c in pts]).distance(Point(0, 0)) > 45: continue   # el dibujo se mueve <= 25 m del origen
            near[s['id']].append(hid)
            if hid not in roads:
                roads[hid] = {'p': [[round(a, 7), round(b, 7)] for a, b in pts], 'hw': RWY.semiwidth(t), 'c': 1 if RWY.constrained(t) else 0, 'n': '%s (%s)' % (t.get('name') or '', t['highway'])}
out = {'roads': roads, 'near': near}
p = R / 'tests/sidewalk/roads-v20.json.gz'
with gzip.open(p, 'wt', encoding='utf-8', compresslevel=9) as f: json.dump(out, f, separators=(',', ':'))
print(len(near), 'placas', len(roads), 'vías', round(os.path.getsize(p) / 1e6, 2), 'MB')
