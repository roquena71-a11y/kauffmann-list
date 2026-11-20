#!/usr/bin/env python3
"""v20: añade a data/stones.json los registros de out/CC.json de los países indicados (los que pasaron auditoría) y escribe el manifiesto data/v20-added-20261120.json.
Uso: merge_v20.py CC [CC ...] | --all.  Idempotente: quita antes cualquier registro v20 previo de esos países (los de v19 y Alemania no se tocan)."""
import json, sys, os, hashlib, csv
from pathlib import Path
R = Path(__file__).resolve().parents[2]
D = Path(os.environ.get('V20_DATA', '/workspace/v20-data'))
V19 = ('IE', 'SE', 'JE', 'FI', 'RO')
args = [a for a in sys.argv[1:] if not a.startswith('--')]
ccs = sorted(p.stem for p in (D / 'out').glob('??.json')) if '--all' in sys.argv else args
data = json.load(open(R / 'data/stones.json', encoding='utf-8')); S = data['stones']
import subprocess
V19IDS = {r['id'] for r in json.loads(subprocess.run(['git', 'show', '49e7725:data/stones.json'], cwd=R, capture_output=True, text=True, check=True).stdout)['stones']}   # registros publicados en la v19
S = [s for s in S if s['id'] in V19IDS and s.get('gm') != 'commons:coordinates']
# v20: 15 placas que la v19 contó como Alemania caen, según el límite administrativo (admin_level=2) de OSM, en LU/AT/PL/CH: se corrige su país (el contenido no cambia)
TRUE = {('%s%d' % (e['type'][0], e['id'])): e['cc'] for e in json.load(open(D / 'osm_all_cc.json', encoding='utf-8'))}
relabel = 0
for s in S:
    if not s.get('cc') and TRUE.get(s['id'], 'DE') != 'DE': s['cc'] = TRUE[s['id']]; relabel += 1
n0 = len(S); ids = {s['id'] for s in S}
added = []; man = {'countries': {}, 'pending': [], 'duplicates': []}
for cc in ccs:
    o = json.load(open(D / ('out/%s.json' % cc), encoding='utf-8'))
    recs = [{k: v for k, v in r.items() if k != '_v'} for r in o['added'] if r['id'] not in ids]
    for r in recs: ids.add(r['id'])
    added += recs
    man['countries'][cc] = {'anadidas': len(recs), 'pendientes': len(o['pending']), 'duplicados': len(o['duplicates']), 'osm_snapshot': o['osm_snapshot'], 'stats': o['stats']}
    man['pending'] += o['pending']; man['duplicates'] += [{'cc': cc, **x} for x in o['duplicates']]
d1480 = []
if (D / 'out/D1480.json').exists() and '--no1480' not in sys.argv:
    o = json.load(open(D / 'out/D1480.json', encoding='utf-8'))
    d1480 = [{k: v for k, v in r.items() if k != '_v'} for r in o['added'] if r['id'] not in ids]
    for r in d1480: ids.add(r['id'])
# v20r2: placas solo-Wikidata que son la misma persona que una placa ya presente (v19 reasignada, otra de OSM) a <=15 m con nombre compatible → duplicado, no se añade
sys.path.insert(0, str(Path(__file__).resolve().parent)); from v20_common import names_compatible; from geo import hav
_grid = {}
for s in S + d1480 + [r for r in added if r.get('src') != 'wd']: _grid.setdefault((int(s['la'] / 0.0003), int(s['lo'] / 0.0005)), []).append(s)
_keep = []
for r in added:
    if r.get('src') == 'wd':
        ci, cj = int(r['la'] / 0.0003), int(r['lo'] / 0.0005)
        d = next((s for di in (-1, 0, 1) for dj in (-1, 0, 1) for s in _grid.get((ci + di, cj + dj), []) if s['id'] != r['id'] and (s.get('cc') or 'DE') == (r.get('cc') or 'DE') and hav(s['la'], s['lo'], r['la'], r['lo']) <= 15 and names_compatible(s['n'], r['n'])), None)
        if d: man['duplicates'].append({'cc': r['cc'], 'id': r['id'], 'dup_de': d['id'], 'n': r['n'], 'regla': 'merge: <=15 m y nombres compatibles'}); man['countries'][r['cc']]['anadidas'] -= 1; man['countries'][r['cc']]['duplicados'] += 1; continue
    _keep.append(r)
added = _keep
data['stones'] = S + d1480 + added; data['meta']['count'] = len(data['stones']); data['meta']['v20_wd1480_added'] = len(d1480)
data['meta']['layout_pinned'] = True   # v20: la app no separa grupos (lo hace sidewalk20): dibujo = dla/dlo exacto
data['meta']['v20_added'] = {'records': len(added), 'countries': {cc: man['countries'][cc]['anadidas'] for cc in ccs},
    'snapshot_osm': '2026-11-18T21:21:02Z (Geofabrik europe-latest) refrescado por id con Overpass el 2026-11-20', 'snapshot_wikidata': '2026-11-20',
    'method': 'OSM memorial=stolperstein (ODbL) y Wikidata P31=Q26703203 (CC0). Cada placa: nombre limpio, nombre contenido en la inscripción, dirección etiquetada contrastada con objetos addr:* de OSM o con la foto de Commons, '
              'fusión con Wikidata (<=50 m, nombre compatible); lo dudoso va a pendiente con su motivo. Municipio: límites administrativos de OSM. Posición de dibujo (dla/dlo): ver data/sidewalk-v20.json.'}
(R / 'data/stones.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
(R / 'data/v20-added-20261120.json').write_text(json.dumps({'meta': {'records': len(added), 'previous_records': n0, 'countries': man['countries']},
    'added': [{k: r.get(k) for k in ('id', 'wd', 'p', 'n', 'c', 'cc', 'la', 'lo', 'src')} for r in added], 'excluded': man['pending'], 'duplicates': man['duplicates']}, ensure_ascii=False, indent=1), encoding='utf-8')
with open(R / 'pendiente-v20.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['cc', 'id', 'nombre', 'motivo', 'lat', 'lon'])
    for p in man['pending']: w.writerow([p['cc'], p['id'], p.get('n') or '', p['reason'], p.get('la', ''), p.get('lo', '')])
print('relabel', relabel, 'añadidas', len(added), '+1480:', len(d1480), 'total', len(data['stones']), {cc: man['countries'][cc]['anadidas'] for cc in ccs})
