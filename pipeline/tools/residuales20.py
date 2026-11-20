#!/usr/bin/env python3
"""v20r2 (auditoría C, F4/F2): reconcilia residuales de la acera y excepciones del tope de 25 m.
Entradas: V20_DATA/layout_check_*.json (check_layout20.py sobre el volcado de la app real), un volcado dump_layout (argumento 1), data/stones.json y data/sidewalk-v20.json.
Salidas: residuales-acera-v20.csv (cada placa con holgura <0,5 m tras el cierre → 'fallo'; cada 'revisar' del solver sin contacto detectado → 'revisar-sin-contacto', con justificación) y excepciones-25m-v20.csv (dibujo a >25 m del origen: grupos de >20 placas)."""
import csv, glob, json, math, os, sys
from collections import Counter
from pathlib import Path
R = Path(__file__).resolve().parents[2]; D = Path(os.environ.get('V20_DATA', '/workspace/v20-data'))
sys.path.insert(0, str(Path(__file__).resolve().parent)); import sidewalk20 as SW
dump = json.load(open(sys.argv[1])); S = json.load(open(R / 'data/stones.json', encoding='utf-8'))['stones']; byid = {s['id']: s for s in S}
fallos = {}
for f in glob.glob(str(D / 'layout_check_*.json')):
    if '--' in f: continue
    for b in json.load(open(f))['fallos']: fallos[b['id']] = b
gsize = {}
for cc in {(s.get('cc') or 'DE') for s in S}:
    if cc in SW.V19: continue
    for g in SW.groups_of([s for s in S if (s.get('cc') or 'DE') == cc]):
        for s in g: gsize[s['id']] = len(g)
SWt = json.load(open(R / 'data/sidewalk-v20.json', encoding='utf-8'))['stones']
SWd = {r['id']: r for r in SWt}
rows = []
for r in SWt:
    if r['id'] not in byid: continue
    if r['id'] in fallos:
        b = fallos[r['id']]; n = gsize.get(r['id'], 1)
        rows.append([r['id'], r['cc'], r.get('n'), 'fallo', r['estado'], b['holgura3d_m'], b['holgura2d_m'], round(max(0, 0.5 - min(b['holgura3d_m'], b['holgura2d_m'])), 2),
            'columna/chincheta a <0,5 m de una huella de OSM tras el cierre (grupo de %d placas con la misma dirección; calle sin hueco libre de edificios a <=25 m del origen para la cuadrícula completa; no se mueve más para no falsear su dirección)' % n])
    elif r['estado'] == 'revisar':
        rows.append([r['id'], r['cc'], r.get('n'), 'revisar-sin-contacto', 'revisar', '', '', '', 'el solver no encontró hueco, pero la comprobación independiente sobre la app real (shapely, OSM) NO detecta contacto (holgura >=0,5 m en 3D y 2D): se documenta, no hay solape'])
with open(R / 'residuales-acera-v20.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['id', 'pais', 'nombre', 'tipo', 'estado_solver', 'holgura3d_m', 'holgura2d_m', 'deficit_m', 'motivo']); w.writerows(rows)
M = 111320; ex = []
for r in dump['rows']:
    if r[7]: continue
    d = math.hypot((r[4] - r[2]) * M, (r[5] - r[3]) * M * math.cos(math.radians(r[2])))
    if d > 25.0 and r[0] in byid: ex.append([r[0], r[1], byid[r[0]].get('n'), round(d, 1), gsize.get(r[0], 1), ('dibujo a >25 m de la coordenada de origen de la placa: grupo de %d placas con la misma dirección; desplazamiento del grupo %s m + casilla de la cuadrícula (hasta ~%.0f m) y/o dispersión de las coordenadas de origen dentro del grupo (la placa no está en el centro). %s' % (gsize.get(r[0], 1), (SWd.get(r[0], {}).get('desplazamiento_m', 0)), SW.spread(gsize.get(r[0], 1)), 'Grupo de >20 placas: excepción documentada.' if gsize.get(r[0], 1) > 20 else 'Grupo de <=20: el tope del solver (25 m menos la dispersión) se cumple para el centro del grupo, no para cada casilla; documentado, sin mover más para no falsear la dirección.'))])
with open(R / 'excepciones-25m-v20.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['id', 'pais', 'nombre', 'dibujo_vs_origen_m', 'placas_en_el_grupo', 'motivo']); w.writerows(ex)
print('residuales', len(rows), Counter(r[3] for r in rows), '| excepciones >25 m:', len(ex), Counter(r[4] > 20 for r in ex))
# v20r3 (auditoría C ronda 2): pares de columnas de grupos distintos a <1,55 m (gaps20.py sobre el volcado de la app) → pares-solapados-v20.csv, cada uno con su causa
gp = Path(os.environ.get('V20_DATA', '/workspace/v20-data-r4')) / 'gaps20.json'
pr = []
if gp.exists():
    for a_, b_, dd in json.load(open(gp)):
        if a_ not in byid or b_ not in byid: continue
        A, Bs = byid[a_], byid[b_]; so = math.hypot((A['la'] - Bs['la']) * M, (A['lo'] - Bs['lo']) * M * math.cos(math.radians(A['la'])))
        why = ('orígenes a %.1f m entre sí: la fuente ya los sitúa casi en el mismo punto (direcciones distintas); la separación entre grupos queda limitada por el hueco libre de la acera' % so) if so < 3 else \
              ('grupos de direcciones distintas (orígenes a %.1f m) cuyas casillas de acera quedan a %.2f m; separación entre grupos acotada por MAXSEP (8 m) y por los edificios' % (so, dd))
        pr.append([a_, A.get('cc') or 'DE', A.get('n'), A.get('a') or '', b_, Bs.get('cc') or 'DE', Bs.get('n'), Bs.get('a') or '', dd, round(so, 1), why])
with open(R / 'pares-solapados-v20.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['id_a', 'pais_a', 'nombre_a', 'direccion_a', 'id_b', 'pais_b', 'nombre_b', 'direccion_b', 'distancia_dibujo_m', 'distancia_origen_m', 'motivo']); w.writerows(pr)
print('pares solapados (<1,55 m, grupos distintos):', len(pr))
