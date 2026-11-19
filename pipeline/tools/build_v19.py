#!/usr/bin/env python3
"""v19: añade Jersey (JE), Finlandia (FI) y Rumanía (RO) a data/stones.json (OSM ODbL + Wikidata CC0).
Entradas (consultas del 19-11-2026, carpeta DATA): osm_je/fi/ro.json, wd_fi/ro.json, is_in.json.
No inventa nada: copia campos de OSM/Wikidata o lee literalmente de la inscripción. Cada exclusión lleva su motivo."""
import json, re, hashlib, sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import hav
R = Path(__file__).resolve().parents[2]
D = Path(os.environ.get('V19_DATA', '/workspace/v19-data'))
J = lambda n: json.load(open(D / n, encoding='utf-8'))

raw = (R / 'data/stones.json').read_text(encoding='utf-8')
data = json.loads(raw); S = data['stones']
assert len(S) == 65832 and data['meta']['count'] == 65832, len(S)
for s in S: assert 'dla' not in s
base_hash = hashlib.sha256(json.dumps(S, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
is_in = J('is_in.json')

def level(k, al):
    return next((x['name'] for x in is_in['is_in'].get(k, []) if x['al'] == str(al)), None)

def lines(txt):
    """Saltos de línea de la placa: JE usa «/», FI usa «\\\\» o « / ». Solo se cambia el separador."""
    t = txt.strip()
    t = re.sub(r'\s*\\\\+\s*', '\n', t)
    t = re.sub(r'\s*/\s*', '\n', t)
    return re.sub(r'\n+', '\n', t).strip()

added, excluded = [], []
# ---------------- Jersey ----------------
osm_je = J('osm_je.json')
for e in sorted(osm_je['elements'], key=lambda e: e['id']):
    t = e['tags']; sid = 'n%d' % e['id']
    if not (t.get('name') and t.get('inscription') and t.get('memorial:addr')):
        excluded.append({'id': sid, 'cc': 'JE', 'la': e['lat'], 'lo': e['lon'], 'reason': 'sin nombre, inscripción o dirección en OSM'}); continue
    insc = lines(t['inscription'])
    rec = {'id': sid, 'la': e['lat'], 'lo': e['lon'], 'src': 'osm'}
    if t.get('subject:wikidata'): rec['p'] = t['subject:wikidata']
    if t.get('subject:wikipedia'): rec['wp'] = t['subject:wikipedia']
    rec.update({'n': t['name'].strip(), 'i': insc, 'a': t['memorial:addr'].strip(), 'c': level(sid, 8), 'cc': 'JE'})
    assert rec['c'], sid
    mb = re.search(r'BORN(?: [A-ZÀ-Ý ]+?)? (\d{4})\b', insc.replace('\n', ' '))
    pb = (t.get('person:date_of_birth') or '').strip()
    assert mb and mb.group(1) == pb, (sid, mb and mb.group(1), pb)       # año de OSM = año de la placa
    rec['b'] = pb
    if t.get('person:date_of_death'): rec['d'] = t['person:date_of_death']
    if t.get('start_date'): rec['laid'] = t['start_date']
    f = t.get('wikimedia_commons')
    if f: rec['img'] = re.sub(r'^File:', '', f)
    added.append(rec)

# ---------------- Finlandia ----------------
osm_fi = J('osm_fi.json'); wd_fi = J('wd_fi.json')
wds = {}
for b in wd_fi['results']['bindings']:
    q = b['s']['value'].rsplit('/', 1)[1]; m = re.match(r'Point\(([-\d.]+) ([-\d.]+)\)', b['coord']['value'])
    wds[q] = (float(m.group(2)), float(m.group(1)))
matched = set()
for e in sorted(osm_fi['elements'], key=lambda e: e['id']):
    t = e['tags']; sid = 'n%d' % e['id']
    if not (t.get('name') and t.get('inscription')):
        excluded.append({'id': sid, 'cc': 'FI', 'la': e['lat'], 'lo': e['lon'],
                         'reason': 'nodo OSM memorial=stolperstein que solo tiene dirección (Pekanraitti 15, Helsinki); sin nombre ni inscripción'}); continue
    q = t.get('wikidata'); assert q in wds, (sid, q)
    assert hav(wds[q][0], wds[q][1], e['lat'], e['lon']) < 25, ('coordenadas WD lejos', sid)
    matched.add(q)
    insc = lines(t['inscription'])
    mb = re.search(r'\bs\. (\d{4})\b', insc.replace('\n', ' '))
    rec = {'id': sid, 'la': e['lat'], 'lo': e['lon'], 'src': 'osm+wd', 'wd': q}
    if t.get('subject:wikipedia'):
        m = re.match(r'https?://([a-z\-]+)\.wikipedia\.org/wiki/(.+)$', t['subject:wikipedia'])
        rec['wp'] = '%s:%s' % (m.group(1), m.group(2).replace('_', ' '))
    rec.update({'n': t['name'].strip(), 'i': insc, 'c': level(sid, 8), 'sub': level(sid, 10), 'cc': 'FI'})
    assert rec['c'] == 'Helsinki', sid
    if mb: rec['b'] = mb.group(1)
    f = t.get('wikimedia_commons')
    if f: rec['img'] = re.sub(r'^File:', '', f)
    added.append(rec)
assert matched == set(wds), set(wds) - matched

# ---------------- Rumanía (solo Wikidata: OSM no tiene ninguna) ----------------
wd_ro = J('wd_ro.json')
for b in sorted(wd_ro['results']['bindings'], key=lambda b: b['s']['value']):
    q = b['s']['value'].rsplit('/', 1)[1]; m = re.match(r'Point\(([-\d.]+) ([-\d.]+)\)', b['coord']['value'])
    la, lo = float(m.group(2)), float(m.group(1))
    cc_ = {'Q44103124': 'Marca', 'Q44101523': 'Timișoara', 'Q44068923': 'Marca'}[q]
    assert b['p131Label']['value'] == cc_
    if q == 'Q44068923':
        excluded.append({'id': q, 'cc': 'RO', 'la': la, 'lo': lo, 'reason': 'Wikidata (Eva Kor Mozes, Marca): sin inscripción ni dirección; no cumple datos completos'}); continue
    img = b['img']['value'].rsplit('/', 1)[1]
    from urllib.parse import unquote
    rec = {'id': q, 'la': round(la, 6), 'lo': round(lo, 6), 'src': 'wd', 'wd': q}
    if q == 'Q44103124':
        rec['p'] = 'Q37819936'; rec['wp'] = 'es:Miriam Mozes Zeiger'        # P547 de la piedra y sitelink eswiki del ítem de la persona
        rec.update({'n': 'Miriam Zeiger Mozes',
                    'i': 'Aici locuia Miriam Zeiger Mozes născuta 1934 arestata Martie 1944 deportata 1944 Auschwitz-Birkenau eliberată/supravietuit',   # P1684 de Wikidata, literal
                    'c': 'Marca', 'sub': 'Porț', 'cc': 'RO', 'b': '1934'})   # sub: P276 de la piedra = Q731068 (Porț, pueblo de la comuna de Marca)
    else:
        rec.update({'n': 'Bloch Lorand', 'a': b['addr']['value'].split(',')[0].strip(), 'c': 'Timișoara', 'cc': 'RO'})   # P6375: «Piața Romanilor 8, 307200 Timișoara»
    rec['img'] = unquote(img)
    added.append(rec)

# orden de claves como en el resto del fichero
ORDER = ['id', 'la', 'lo', 'src', 'wd', 'p', 'wp', 'n', 'i', 'a', 'c', 'sub', 'cc', 'b', 'd', 'laid', 'img']
added = [{k: r[k] for k in ORDER if k in r} for r in added]
from collections import Counter
cnt = Counter(r['cc'] for r in added); print(cnt, len(added), 'excluidas', len(excluded))
assert cnt == {'JE': 20, 'FI': 7, 'RO': 2}, cnt
snap = {'osm': osm_je['osm3s'].get('timestamp_osm_base'), 'wd': '2026-11-19'}
data['stones'] = S + added; data['meta']['count'] = len(data['stones'])
data['meta']['v19_added'] = {'snapshot_osm': snap['osm'], 'snapshot_wikidata': snap['wd'], 'records': len(added), 'countries': dict(cnt),
    'method': 'JE/FI: OSM memorial=stolperstein (ODbL) con nombre e inscripción; FI fusionado con Wikidata P31 Q26703203 P17 Finland (CC0) por la etiqueta wikidata de OSM y por coordenadas (<25 m); '
              'RO: OSM no tiene ninguna; solo Wikidata (CC0) con coordenadas precisas, nombre y dirección o inscripción. Ciudad/parroquia/barrio: límites administrativos de OSM (is_in). '
              'Fechas de nacimiento y muerte: etiquetas person:date_of_* de OSM solo si coinciden con la inscripción, o leídas de la inscripción; no se geocodificó.'}
(R / 'data/stones.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
man = {'meta': {'countries': dict(cnt), 'added': len(added), 'excluded': len(excluded), 'osm_snapshot': snap['osm'], 'wikidata_queried_at': snap['wd'],
                'previous_records': 65832, 'previous_sha256_json_list': base_hash,
                'sources': {'JE': 'OSM ODbL (nodos memorial=stolperstein; área ISO3166-1=JE)', 'FI': 'OSM ODbL + Wikidata CC0', 'RO': 'Wikidata CC0 (OSM: 0 nodos)'}},
       'added': [{k: r.get(k) for k in ('id', 'wd', 'p', 'n', 'c', 'cc', 'la', 'lo', 'src')} for r in added], 'excluded': excluded}
(R / 'data/v19-added-20261119.json').write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps(added[:3], ensure_ascii=False, indent=1)); print('base', base_hash)
