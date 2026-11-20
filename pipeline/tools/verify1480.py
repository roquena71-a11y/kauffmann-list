#!/usr/bin/env python3
"""v20: verificación de las 1.480 piedras de Wikidata sin coordenadas (v14, pendiente-sin-coordenadas.csv) con FUENTES ABIERTAS:
se añade una piedra solo si
  R1 el ítem de Wikidata tiene nombre de persona limpio (etiqueta «Stolperstein für X») y, si tiene inscripción, el nombre está en ella;
  R2 el fichero de imagen del PROPIO ítem (P18) en Wikimedia Commons tiene coordenadas y su título/descripción contiene el nombre (descarta fotos de otra persona);
  R3 la coordenada de la foto cae a <= 40 m de un objeto addr:* de OpenStreetMap cuya «calle + número» aparece en el título/descripción de la foto o en la dirección del ítem;
  R4 no hay ya una placa del mismo nombre a <= 60 m en el mapa;
  R5 la ubicación no es un caso «dudoso» (varios ficheros con coordenadas lejanas entre sí).
La posición es la de la foto (aproximada; se marca gm='commons:coordinates'); el municipio sale del objeto addr de OSM.
Salida: V20_DATA/out/D1480.json (added/pending, con motivo) y pendiente-1480-v20.csv (los 1.480 con resultado)."""
import json, re, sys, os, csv
from pathlib import Path
from urllib.parse import unquote
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import hav
from v20_common import norm, clean_name, name_in_text, split_insc
R = Path(__file__).resolve().parents[2]; D = Path(os.environ.get('V20_DATA', '/workspace/v20-data'))
W = json.load(open(D / 'p1480/wd1480.json', encoding='utf-8')); C = json.load(open(D / 'p1480/commons1480.json', encoding='utf-8')); INFO = C['info']
NEAR = json.load(open(D / 'near/D1480.json', encoding='utf-8')); ADDR = list(NEAR['addr'].values())
S = json.load(open(R / 'data/stones.json', encoding='utf-8'))['stones']
OLD = {r['qid']: r for r in csv.DictReader(open('/workspace/wd-stones-proto/pendiente-sin-coordenadas.csv', encoding='utf-8'))}
def sn(s):
    s = norm(s); s = re.sub(r'\bstr\b', 'strasse', s); s = re.sub(r'strasse\b', 'strasse', s)
    return re.sub(r'\s+', ' ', s)
def stones_near(la, lo, r=0.0012):
    return [s for s in S if abs(s['la'] - la) < r and abs(s['lo'] - lo) < r * 1.6]
added, pend = [], []
def P(q, why, d=''): pend.append({'qid': q, 'reason': why, 'detail': d})
for q, bs in W.items():
    b = bs[0]; lab = b.get('sLabel', {}).get('value', ''); m = re.sub(r'\s*\([^)]*\)\s*$', '', lab).strip()
    if lab == q or not lab: P(q, 'sin nombre en Wikidata'); continue
    nm, why = clean_name(m)
    if not nm: P(q, 'nombre no válido: %s' % why); continue
    insc = split_insc(b.get('inscr', {}).get('value', '')) if b.get('inscr') else ''
    if insc and name_in_text(nm, insc) < 1.0 and name_in_text(nm, re.sub(r"'''", '', insc)) < 1.0: P(q, 'el nombre no está en la inscripción de Wikidata', insc[:80]); continue
    fs = C['files'].get(q, [])
    if not fs: P(q, 'el ítem no tiene imagen (P18): ninguna fuente abierta de posición'); continue
    cands = [f for f in fs if INFO.get(f, {}).get('coords')]
    if not cands: P(q, 'la imagen de Commons no tiene coordenadas'); continue
    ok = None; reasons = []
    for f in cands:
        i = INFO[f]; txt = f[5:] + ' ' + i['desc']
        if name_in_text(nm, txt) < 1.0: reasons.append('la foto «%s» no menciona a %s' % (f[5:][:60], nm)); continue
        la, lo = i['coords'][0]
        T = sn(txt + ' ' + ' '.join(x.get('addr', {}).get('value', '') for x in bs))
        hit = None
        for a in ADDR:
            t = a['t']; st = t.get('addr:street'); hn = t.get('addr:housenumber')
            if not st or not hn or hav(la, lo, a['la'], a['lo']) > 40: continue
            if re.search(r'(?<![0-9a-z])%s %s(?![0-9a-z])' % (re.escape(sn(st)), re.escape(sn(hn))), T): hit = (a, hav(la, lo, a['la'], a['lo'])); break
        if not hit: reasons.append('ningún objeto addr:* de OSM a ≤40 m coincide con la calle y número de la foto/ítem'); continue
        ok = (f, la, lo, hit); break
    if not ok: P(q, '; '.join(sorted(set(reasons)))[:200]); continue
    f, la, lo, (a, dd) = ok
    dup = [s for s in stones_near(la, lo) if norm(s['n']) == norm(nm) and hav(la, lo, s['la'], s['lo']) <= 60]
    if dup: P(q, 'ya hay una placa del mismo nombre a ≤60 m en el mapa (%s)' % dup[0]['id']); continue
    if len({(round(INFO[x]['coords'][0][0], 3), round(INFO[x]['coords'][0][1], 3)) for x in cands}) > 1: P(q, 'varias fotos con coordenadas distintas'); continue
    t = a['t']; city = t.get('addr:city') or (b.get('p131Label', {}).get('value') or '')
    rec = {'id': q, 'la': round(la, 7), 'lo': round(lo, 7), 'src': 'wd', 'wd': q, 'n': nm}
    if insc: rec['i'] = insc
    rec['a'] = '%s %s, %s' % (t['addr:street'], t['addr:housenumber'], city) if city else '%s %s' % (t['addr:street'], t['addr:housenumber'])
    if city: rec['c'] = city
    p131 = b.get('p131Label', {}).get('value')
    if p131 and p131 != city: rec['sub'] = p131
    rec['gm'] = 'commons:coordinates'; rec['img'] = f[5:]
    rec['_v'] = {'foto': f, 'dist_addr_m': round(dd), 'addr_obj': next(k for k, v in NEAR['addr'].items() if v is a)}
    added.append(rec)
res = {'cc': 'D1480', 'osm_snapshot': NEAR.get('osm_timestamp'), 'stats': {'total': len(W), 'anadidas': len(added), 'pendientes': len(pend)}, 'added': added, 'pending': pend}
json.dump(res, open(D / 'out/D1480.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
pm = {p['qid']: p for p in pend}; am = {r['id']: r for r in added}
with open(R / 'pendiente-1480-v20.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['qid', 'resultado', 'nombre', 'municipio_P131', 'motivo_v14', 'motivo_v20', 'url'])
    for q in W:
        o = OLD.get(q, {}); w.writerow([q, 'añadida' if q in am else 'pendiente', (am[q]['n'] if q in am else o.get('nombre', '')), o.get('municipio_P131', ''), o.get('motivo', ''), '' if q in am else pm[q]['reason'], 'https://www.wikidata.org/wiki/' + q])
from collections import Counter
print(res['stats'], Counter(re.sub(r'[«(].*', '', p['reason'])[:60] for p in pend).most_common(8))
