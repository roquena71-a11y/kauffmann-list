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
sel = [s for s in S if (s.get('cc') or 'DE') != 'DE'] + random.sample(de, 1500) + [s for s in de if s['id'] in legit]  # v20r5: IE/SE/JE/FI/RO también (ya hay near/)
# v20r3 (auditoría C ronda 2): los grupos que el auditor halló con el centro dentro de un edificio, las 4 placas en calzada y las 3 chinchetas 2D dentro de un edificio se comprueban SIEMPRE (todos los miembros de su grupo)
C_IDS = set('Q44067803 n6140555537 n7120057503 n7120057504 n7120057505 Q134694663 n13186250730 n2478709768 Q139713238 Q139713259 Q139713347 Q139713355 n14280924398 n13041383986 n13032352978 n13032352980 Q133230139 n1680242278 Q139713321 Q139713367'.split())
_fixed = {}
for g in SW.groups_of(de + [s for s in S if (s.get('cc') or 'DE') != 'DE']):
    if any(x['id'] in C_IDS for x in g):
        for x in g: _fixed[x['id']] = x
_have = {s['id'] for s in sel}; sel = sel + [x for i, x in _fixed.items() if i not in _have]
# v20r4 (auditoría C ronda 3, calzada): las 612 placas con el centro sobre la calzada que halló C, una muestra fija de las movidas por la regla de calzada y las documentadas en calzada-v20.csv se comprueban SIEMPRE
_road = set(open(R / 'tests/sidewalk/road-ids-v20.txt').read().split())
if (R / 'calzada-v20.csv').exists():
    import csv as _csv
    _road |= {r['id'] for r in _csv.DictReader(open(R / 'calzada-v20.csv', encoding='utf-8'))}
_rs = random.Random(20261120); _mv = sorted(s['id'] for s in S if s.get('dla') is not None)
_road |= set(_rs.sample(_mv, 600))
# v20r5 (auditoría C ronda 4): el test falló en Unna porque n12438845078/081 no estaban en la muestra del fixture
# (el fallo «centro dentro» ya era hard=True, sin exención por residuales). Se incluyen SIEMPRE residuales, excepciones,
# calzada, V19, el grupo de Unna (Mozartstraße) y Herrenstraße 22 (Karlsruhe).
import csv as _csv2
_always = set()
for _fn in ('residuales-acera-v20.csv', 'excepciones-25m-v20.csv', 'calzada-v20.csv'):
    if (R / _fn).exists():
        _always |= {r['id'] for r in _csv2.DictReader(open(R / _fn, encoding='utf-8'))}
_always |= {s['id'] for s in S if (s.get('cc') or 'DE') in SW.V19}
_always |= {'n2310732548', 'n2310732531', 'n2310732544', 'n12438845078', 'n12438845081'}
try:
    _sw = json.load(open(R / 'data/sidewalk-v20.json', encoding='utf-8'))['stones']
    _ug = {r.get('grupo_id') for r in _sw if r['id'] in ('n12438845078', 'n12438845081')}
    _always |= {r['id'] for r in _sw if r.get('grupo_id') in _ug}
except Exception:
    pass
_have = {s['id'] for s in sel}; sel = sel + [s for s in S if s['id'] in _road and s['id'] not in _have]
_have = {s['id'] for s in sel}; sel = sel + [s for s in S if s['id'] in _always and s['id'] not in _have]
byc = {}
for s in sel: byc.setdefault(s.get('cc') or 'DE', []).append(s)
near = {}; B = {}; ids = []
for cc, ss in byc.items():
    if not ((SW.D / ('near/%s.json' % cc)).exists() or (SW.D / ('near/%s.pkl' % cc)).exists()): print('omitido (sin near):', cc, len(ss)); continue
    N = SW.load_near(cc)
    for s in ss:
        la, lo = s['la'], s['lo']; ids.append(s['id']); near[s['id']] = []
        _pts = [(la, lo)] + ([(s['dla'], s['dlo'])] if s.get('dla') is not None else [])
        _bids = set()
        for _la, _lo in _pts:
            _bids.update(N.around(N.bi, _la, _lo, 1))
        for bid in _bids:
            outer, inner, tags = N.b[bid]
            if min(min(SW.hav(pla, plo, a, b) for r in outer for a, b in r) for pla, plo in _pts) > 70: continue
            near[s['id']].append(bid)
            if bid not in B: B[bid] = {'o': [[[round(a, 7), round(b, 7)] for a, b in r] for r in outer], 'i': [[[round(a, 7), round(b, 7)] for a, b in r] for r in inner]}
# v20r2 (auditoría C, F1): placas sin ningún edificio de OSM a <=50 m (tras volver a traer las huellas): lista explícita; el test falla si aparece alguna fuera de ella
def _d50(s, bids): return any(min(SW.hav(s['la'], s['lo'], a, b) for r in B[bid]['o'] for a, b in r) <= 50 for bid in bids)
sin_ed = sorted(i for i in ids if not _d50(next(s for s in sel if s['id'] == i), near.get(i, [])))
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
