"""Pares de columnas DIBUJADAS a menos de COL_GAP_MIN (1,55 m) entre sí (grupos distintos: dentro de un grupo la rejilla es de 1,85 m). Uso: gaps20.py DUMP.json
v20r5: la distancia usa el coseno de la latitud media (como el resto de herramientas y las auditorías). La versión anterior medía x con el coseno de cada punto por separado y sobreestimaba ~0,08–0,10 m, dejando fuera pares de 1,45–1,53 m.
"""
import json, sys, math
from collections import defaultdict
d = json.load(open(sys.argv[1])); rows = [r for r in d['rows'] if not r[7]]
M = 111320.0; cell = 3.0
COS0 = math.cos(math.radians(50.0))
g = defaultdict(list)
for i, r in enumerate(rows):
    y = r[4] * M; x = r[5] * M * COS0
    g[(int(math.floor(y / cell)), int(math.floor(x / cell)))].append(i)

def dist_m(a, b):
    la, lo, lb, lonb = a[4], a[5], b[4], b[5]
    return math.hypot((la - lb) * M, (lo - lonb) * M * math.cos(math.radians((la + lb) / 2)))

pairs = []
seen = set()
for (cy, cx), L in g.items():
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            for i in L:
                for j in g.get((cy + di, cx + dj), []):
                    if j <= i: continue
                    dd = dist_m(rows[i], rows[j])
                    if dd < 1.55:
                        key = tuple(sorted((rows[i][0], rows[j][0])))
                        if key in seen: continue
                        seen.add(key)
                        pairs.append((rows[i][0], rows[j][0], round(dd, 2)))
print(len(pairs), 'pares <1,55 m')
for p in pairs[:15]: print(p)
json.dump(pairs, open('/workspace/v20-data-r4/gaps20.json', 'w'))
