#!/usr/bin/env python3
"""v20r2 (auditoría C, F1): vuelve a traer de Overpass (ODbL) edificios/vías/direcciones para las placas sin ningún edificio a <=50 m en V20_DATA/near.
Uso: refetch_near20.py CC [CC...]   → V20_DATA/near-extra/CC.json (mismo formato que near/CC.json); sidewalk20.load_near lo añade a lo que ya hay."""
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, '/workspace/v20-data')
from ovp import overpass
R_ = Path(__file__).resolve().parents[2]; D = Path(os.environ.get('V20_DATA', '/workspace/v20-data'))
S = json.load(open(R_ / 'data/stones.json', encoding='utf-8'))['stones']
(D / 'near-extra').mkdir(exist_ok=True)
for cc in sys.argv[1:]:
    ids = json.load(open(D / ('nobuild_%s.json' % cc)))[cc]
    byid = {s['id']: s for s in S}; P = [(byid[i]['la'], byid[i]['lo']) for i in ids if i in byid]
    out = {'buildings': {}, 'highways': {}, 'addr': {}}; ts = None; R = 120
    for i in range(0, len(P), 8):
        pts = P[i:i + 8]
        a = ''.join('way(around:%d,%.7f,%.7f)["building"];rel(around:%d,%.7f,%.7f)["building"];' % (R, la, lo, R, la, lo) for la, lo in pts)
        h = ''.join('way(around:%d,%.7f,%.7f)["highway"];' % (R, la, lo) for la, lo in pts)
        o = overpass('[out:json][timeout:240];(%s);out geom tags;' % a); ts = o['osm3s'].get('timestamp_osm_base')
        for e in o['elements']: out['buildings']['%s%d' % (e['type'][0], e['id'])] = e
        o = overpass('[out:json][timeout:240];(%s);out geom tags;' % h)
        for e in o['elements']: out['highways']['%s%d' % (e['type'][0], e['id'])] = e
        time.sleep(0.5)
    out['osm_timestamp'] = ts; out['radius_m'] = R
    json.dump(out, open(D / ('near-extra/%s.json' % cc), 'w'), ensure_ascii=False)
    print(cc, len(P), 'placas; edificios', len(out['buildings']), 'vías', len(out['highways']), ts, flush=True)
