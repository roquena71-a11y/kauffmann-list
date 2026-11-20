#!/usr/bin/env python3
"""v20r4 (auditoría B ronda 3, R3-1): corrige el país de las placas fronterizas cuyo país salió del respaldo de Natural Earth (sin límite admin_level=2 de OSM en el extracto `adm2`).
Entrada: V20_DATA/border_isin_r4.json = {id: [ISO3166-1...]} (Overpass `is_in` sobre cada candidato a <~10 km de otra frontera: límite administrativo admin_level=2 de OSM, ODbL, 2026-11-20).
Hace: (1) osm_all_cc.json: cc = país del límite (cc_src='osm_admin2_isin'); (2) mueve los elementos de osm20_<viejo>.json a osm20_<nuevo>.json si existe; (3) escribe data/v20-border-cc.json
(id → país por límite OSM) que usa tests/v20r4-border-test.py. Idempotente. merge_v20.py relabela con osm_all_cc.json las placas v19 que no eran Alemania."""
import json, os
from pathlib import Path
R = Path(__file__).resolve().parents[2]; D = Path(os.environ.get('V20_DATA', '/workspace/v20-data'))
isin = json.load(open(D / 'border_isin_r4.json', encoding='utf-8'))
allc = json.load(open(D / 'osm_all_cc.json', encoding='utf-8'))
by = {('%s%d' % (e['type'][0], e['id'])): e for e in allc}
moved = {}
for k, v in isin.items():
    e = by[k]
    if len(set(v)) != 1: continue
    new = v[0]
    if e['cc'] == new: continue
    old = e['cc']; e['cc'] = new; e['cc_src'] = 'osm_admin2_isin'; e['cc_ne'] = e.get('cc_ne', old)
    moved[k] = (old, new)
json.dump(allc, open(D / 'osm_all_cc.json', 'w', encoding='utf-8'), ensure_ascii=False)
for old in {o for o, _ in moved.values() if o}:
    fo = D / ('osm20_%s.json' % old)
    if not fo.exists(): continue
    jo = json.load(open(fo, encoding='utf-8'))
    for new in {n for k, (o, n) in moved.items() if o == old}:
        fn = D / ('osm20_%s.json' % new)
        if not fn.exists(): continue
        ids = {k for k, (o, n) in moved.items() if o == old and n == new}
        mv = [x for x in jo['elements'] if ('%s%d' % (x['type'][0], x['id'])) in ids]
        jn = json.load(open(fn, encoding='utf-8')); have = {('%s%d' % (x['type'][0], x['id'])) for x in jn['elements']}
        jn['elements'] += [x for x in mv if ('%s%d' % (x['type'][0], x['id'])) not in have]
        jo['elements'] = [x for x in jo['elements'] if ('%s%d' % (x['type'][0], x['id'])) not in ids]
        json.dump(jn, open(fn, 'w', encoding='utf-8'), ensure_ascii=False); print('movidos', len(mv), old, '→', new)
    json.dump(jo, open(fo, 'w', encoding='utf-8'), ensure_ascii=False)
chg = {('%s%d' % (e['type'][0], e['id'])): [e.get('cc_ne'), e['cc']] for e in json.load(open(D / 'osm_all_cc.json', encoding='utf-8')) if e.get('cc_src') == 'osm_admin2_isin' and e.get('cc_ne') != e['cc']}
fx = {'meta': {'method': 'país por límite administrativo admin_level=2 de OSM (Overpass is_in), 2026-11-20, para las placas que estaban a <~10 km de otra frontera y cuyo país salió del respaldo de Natural Earth', 'source': 'OpenStreetMap contributors, ODbL 1.0'},
      'cambiados': dict(sorted(chg.items())),
      'cc': {k: (v[0] if len(set(v)) == 1 else None) for k, v in sorted(isin.items())}}
(R / 'data/v20-border-cc.json').write_text(json.dumps(fx, ensure_ascii=False, indent=0), encoding='utf-8')
from collections import Counter
print('placas con país corregido:', len(moved), Counter(moved.values()))

# (4) near/ (edificios, vías, direcciones, puntos) y city/ (municipio) del país viejo → país nuevo, para las placas movidas entre ficheros osm20_*.json (idempotente)
pairs = {}
for e in json.load(open(D / 'osm_all_cc.json', encoding='utf-8')):
    if e.get('cc_src') == 'osm_admin2_isin' and e.get('cc_ne') and e['cc_ne'] != e['cc'] and (D / ('osm20_%s.json' % e['cc'])).exists() and (D / ('osm20_%s.json' % e['cc_ne'])).exists():
        pairs.setdefault((e['cc_ne'], e['cc']), []).append('%s%d' % (e['type'][0], e['id']))
for (old, new), ids in pairs.items():
    no, nn = D / ('near/%s.json' % old), D / ('near/%s.json' % new)
    if no.exists() and nn.exists():
        jo, jn = json.load(open(no, encoding='utf-8')), json.load(open(nn, encoding='utf-8'))
        for k in ('buildings', 'highways', 'addr'):
            for kk, vv in jo.get(k, {}).items(): jn[k].setdefault(kk, vv)
        for i in ids:
            if 'osm' + i in jo.get('points', {}): jn['points'].setdefault('osm' + i, jo['points']['osm' + i])
        json.dump(jn, open(nn, 'w', encoding='utf-8'), ensure_ascii=False)
    co, cn = D / ('city/%s.json' % old), D / ('city/%s.json' % new)
    if co.exists() and cn.exists():
        jo, jn = json.load(open(co, encoding='utf-8')), json.load(open(cn, encoding='utf-8'))
        for i in ids:
            if i in jo: jn.setdefault(i, jo[i])
        json.dump(jn, open(cn, 'w', encoding='utf-8'), ensure_ascii=False)
    print('near/city', old, '→', new, len(ids))
