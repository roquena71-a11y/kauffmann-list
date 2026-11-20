#!/usr/bin/env python3
"""v20: construye los registros de UN país (OSM ODbL + Wikidata CC0) → V20_DATA/out/CC.json (no toca data/stones.json; eso lo hace merge_v20.py).
Entradas (V20_DATA): osm20_CC.json (Overpass, memorial=stolperstein…), wd_CC.json (SPARQL P31=Q26703203, P17), near/CC.json (edificios, vías, direcciones de OSM a <=100 m),
city/CC.json (municipio por límite administrativo de OSM, opcional).
Verificación de cada registro: nombre limpio, nombre ⊂ inscripción, dirección etiquetada ↔ objeto addr:* de OSM cercano, sin etiqueta fixme de posición sin comprobar,
fusión con Wikidata (≤50 m, nombre compatible). Lo dudoso va a «pendiente» con su motivo."""
import json, re, sys, os, math
from pathlib import Path
from urllib.parse import unquote
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import hav
from v20_common import *
D = Path(os.environ.get('V20_DATA', '/workspace/v20-data'))
CC = sys.argv[1]
J = lambda n: json.load(open(D / n, encoding='utf-8'))
osm = J('osm20_%s.json' % CC); els = osm['elements']
try: wdraw = J('wd_%s.json' % CC)['results']['bindings']
except FileNotFoundError: wdraw = []
near = J('near/%s.json' % CC) if (D / ('near/%s.json' % CC)).exists() else {'addr': {}, 'points': {}}
citymap = J('city/%s.json' % CC) if (D / ('city/%s.json' % CC)).exists() else {}
ADDR = list(near.get('addr', {}).values())
try: COMMONS = json.load(open(D / 'commons_coords20.json', encoding='utf-8'))
except FileNotFoundError: COMMONS = {}
def commons_check(la, lo, fname):
    """('ok' <=60 m | 'lejos' >150 m | 'medio' | 'sin_datos', distancia mínima a una coordenada del fichero de Commons)."""
    cs = COMMONS.get('File:' + fname) if fname else None
    if not cs: return 'sin_datos', None
    d = min(hav(la, lo, c[0], c[1]) for c in cs)
    return ('ok' if d <= 60 else 'lejos' if d > 150 else 'medio'), round(d)
MAXWD = 50.0       # m entre nodo OSM y ítem de Wikidata
ADDR_OK = 40.0     # m: objeto addr:* de OSM con la misma calle y número
SPLIT_RE = re.compile(r'\s*[;|]\s*')

def addr_check(la, lo, street, hn):
    """('ok'|'lejos'|'sin_coincidencia'|'sin_datos', distancia al objeto addr:* coincidente más cercano)."""
    if not street or not hn: return 'sin_datos', None
    cand = [x for x in ADDR if abs(x['la'] - la) < 0.0015 and abs(x['lo'] - lo) < 0.0025]
    if not cand: return 'sin_datos', None
    best = None; bestn = None
    for x in cand:
        t = x['t']
        if not hn_match(t.get('addr:housenumber', ''), hn): continue
        st = t.get('addr:street') or t.get('addr:place') or ''
        d = hav(la, lo, x['la'], x['lo'])
        if not st:   # objeto con número pero sin calle (la calle va en una relación associatedStreet): solo cuenta si está pegado (<= 25 m)
            if d <= 25 and (bestn is None or d < bestn): bestn = d
            continue
        if street_sim(st, street) < 0.8: continue
        if best is None or d < best: best = d
    if best is None and bestn is not None: best = bestn
    if best is None: return 'sin_coincidencia', None
    return ('ok' if best <= ADDR_OK else 'lejos'), round(best, 1)

# ---- Wikidata: una fila por ítem ----
wd = {}
for b in wdraw:
    q = b['s']['value'].rsplit('/', 1)[1]
    w = wd.setdefault(q, {'q': q, 'label': None, 'coord': set(), 'addr': set(), 'inscr': set(), 'p131': set(), 'subj': {}, 'img': set(), 'inc': set(), 'osm': set()})
    w['label'] = w['label'] or b.get('sLabel', {}).get('value')
    for k, f in (('coord', 'coord'), ('addr', 'addr'), ('inscr', 'inscr'), ('img', 'img'), ('inc', 'inc'), ('osm', 'osm')):
        if f in b: w[k].add(b[f]['value'])
    if 'p131' in b: w['p131'].add(b.get('p131Label', {}).get('value') or '')
    if 'subj' in b: w['subj'][b['subj']['value'].rsplit('/', 1)[1]] = b.get('subjLabel', {}).get('value')
for w in wd.values():
    cs = []
    for c in w['coord']:
        m = re.match(r'Point\(([-\d.]+) ([-\d.]+)\)', c)
        if m: cs.append((float(m.group(2)), float(m.group(1))))
    w['ll'] = cs[0] if len(cs) == 1 else None; w['multi_coord'] = len(cs) > 1

def wd_name(w):
    lb = (w['label'] or '').strip()
    m = re.match(r'^Stolperstein (?:dedicated to|for|für|pour|voor) (.+)$', lb, re.I)
    if not m: return None
    n = m.group(1).strip()
    n = re.sub(r',\s*f\.\s*', ' f. ', n)
    return n

added, pend, dups = [], [], []
def P(id_, reason, **kw): pend.append({'id': id_, 'cc': CC, 'reason': reason, **kw})

# ---- OSM ----
used_wd = set(); osm_recs = []
for e in sorted(els, key=lambda e: (e['type'], e['id'])):
    t = e['tags']; sid = ('n' if e['type'] == 'node' else 'w' if e['type'] == 'way' else 'r') + str(e['id'])
    base = {'id': sid, 'la': e['lat'], 'lo': e['lon']}
    kind = 'stolperschwelle' if 'stolperschwelle' in (t.get('memorial'), t.get('memorial:type')) else None
    if kind: P(sid, 'Stolperschwelle (placa colectiva, no se modela en v20)', **base); continue
    if t.get('proposed:historic') and not t.get('historic'): P(sid, 'propuesta (proposed:historic), aún no colocada', **base); continue
    allnotes = ' '.join(t.get(k, '') for k in ('note', 'fixme', 'description', 'check_date:note', 'survey:note'))
    if GONE_RE.search(allnotes): P(sid, 'nota de OSM: placa retirada, ausente o desaparecida (%s)' % allnotes[:80], **base); continue
    raw = t.get('name') or t.get('memorial:name') or t.get('person:name')
    name_from = 'name'
    if not raw and t.get('subject') and not re.fullmatch(r'Q\d+', t['subject'].strip()): raw = t['subject']; name_from = 'subject'
    if not raw:
        _i = split_insc(t.get('inscription') or t.get('memorial:text') or '')
        if _i and '\n' not in _i and 2 <= len(_i.split()) <= 5 and not re.search(r'\d', _i) and _i.upper() != _i.lower() and not GENERIC_RE.match(_i): raw = _i; name_from = 'inscription'
    raw, ly_b, ly_d = strip_years(raw)
    name, why = clean_name(raw)
    if not name: P(sid, why, **base); continue
    if COLLECTIVE_RE.search(name): P(sid, 'el nombre parece colectivo o de varias personas (%s)' % name[:60], **base); continue
    if len(toks(name)) < 2 and len(name.split()) < 2: P(sid, 'nombre de una sola palabra (%s)' % name, **base); continue
    insc_raw = t.get('inscription') or t.get('memorial:text') or ''
    insc = split_insc(insc_raw)
    # dirección
    street = t.get('addr:street') or t.get('object:street') or t.get('memorial:addr:street')
    hn = t.get('addr:housenumber') or t.get('object:housenumber') or t.get('memorial:addr:housenumber')
    maddr = (t.get('memorial:addr') or '').strip()
    a = None
    if street: a = compose_addr(street, hn, CC)
    elif maddr:
        _p = [x.strip() for x in maddr.split(',') if x.strip()]
        a = ', '.join(_p[:-1]) if len(_p) >= 2 and not re.search(r'\d', _p[-1]) else ', '.join(_p)   # quita solo la ciudad final
        a = re.sub(r'^(\d+[a-zA-Z]?),\s+', r'\1 ', a)                                              # «17, Rue X» → «17 Rue X»
    if street is None and maddr:
        ps, ph = parse_memorial_addr(maddr)
        if ps: street, hn = ps, ph
    city = t.get('addr:city') or t.get('object:city') or t.get('memorial:addr:city') or t.get('addr:place')
    if not city and maddr and ',' in maddr:
        city = maddr.split(',')[-1].strip() if not re.search(r'\d', maddr.split(',')[-1]) else None
    if not (a or insc): P(sid, 'sin dirección ni inscripción en OSM', n=name, **base); continue
    if not insc and not a: continue
    # nombre ⊂ inscripción
    if insc:
        fr = name_in_text(name, insc)
        if fr < 0.99:
            P(sid, 'el nombre de OSM no coincide con la inscripción (%.0f %% de las palabras del nombre están en la inscripción)' % (fr * 100), n=name, i=insc[:120], **base); continue
    # posición: dirección etiquetada ↔ objeto addr:* de OSM, y coordenada del fichero de Commons
    pos, dpos = addr_check(e['lat'], e['lon'], street, hn)
    fcom = (t.get('wikimedia_commons') or '')[5:] if (t.get('wikimedia_commons') or '').startswith('File:') else None
    cpos, cd = commons_check(e['lat'], e['lon'], fcom)
    fx = ' '.join(t.get(k, '') for k in ('fixme', 'FIXME', 'note') if t.get(k))
    posflag = bool(fx and POS_FIXME.search(fx))
    verified = pos == 'ok' or cpos == 'ok'
    if posflag and not verified: P(sid, 'OSM marca la posición como dudosa («%s») y ni una dirección de OSM ni la foto de Commons la confirman (dirección: %s, Commons: %s)' % (fx[:50], pos, cpos), n=name, **base); continue
    if pos == 'lejos' and cpos != 'ok': P(sid, 'la dirección etiquetada existe en OSM pero a %.0f m de la posición de la placa' % dpos, n=name, **base); continue
    if cpos == 'lejos' and pos != 'ok': P(sid, 'la foto de Commons está a %d m de la posición de la placa en OSM' % cd, n=name, **base); continue
    # fechas
    yrs = years_in(insc)
    b_ = (t.get('person:date_of_birth') or '').strip(); d_ = (t.get('person:date_of_death') or '').strip()
    notes = [] if name_from == 'name' else ['nombre tomado de la etiqueta %s' % name_from]
    if b_ and (not date_ok(b_) or (yrs and b_[:4] not in yrs)):
        notes.append('nacimiento %s de OSM descartado' % b_); b_ = ''
    if d_ and (not date_ok(d_) or int(d_[:4]) < 1930 or (b_ and int(d_[:4]) < int(b_[:4]))):
        notes.append('muerte %s de OSM descartada' % d_); d_ = ''
    if ly_b and not b_ and not d_: b_, d_ = ly_b, ly_d; notes.append('años (%s–%s) leídos del nombre de OSM' % (ly_b, ly_d))
    rec = {'id': sid, 'la': e['lat'], 'lo': e['lon'], 'src': 'osm'}
    q = t.get('wikidata') or t.get('memorial:wikidata')
    if q in wd:
        rec['_wdq'] = q
    pq = t.get('subject:wikidata')
    if pq and re.fullmatch(r'Q\d+', pq): rec['p'] = pq
    wp = parse_wp(t.get('subject:wikipedia') or t.get('memorial:wikipedia'))
    if wp: rec['wp'] = wp
    rec['n'] = name
    if insc: rec['i'] = insc
    if a: rec['a'] = a
    if city: rec['c'] = city.strip()
    cm = citymap.get(sid)
    if cm:
        if not rec.get('c') and cm.get('c'): rec['c'] = cm['c']
        if cm.get('sub') and cm.get('sub') != rec.get('c'): rec['sub'] = cm['sub']
    rec['cc'] = CC
    if b_: rec['b'] = b_
    if d_: rec['d'] = d_
    if t.get('start_date') and re.fullmatch(r'\d{4}(-\d{2}(-\d{2})?)?', t['start_date'].strip()): rec['laid'] = t['start_date'].strip()
    f = t.get('wikimedia_commons') or ''
    if f.startswith('File:'): rec['img'] = f[5:]
    rec['_v'] = {'pos': pos, 'dpos': dpos, 'commons': cpos, 'dcommons': cd, 'notes': notes, 'osm_version': e.get('version'), 'osm_time': e.get('timestamp')}
    osm_recs.append(rec)

# ---- fusión OSM–Wikidata ----
wd_by_osm = {}
for w in wd.values():
    for o in w['osm']:
        wd_by_osm[o.replace('node/', 'n').replace('way/', 'w')] = w['q']
for r in osm_recs:
    q = r.pop('_wdq', None)
    if not q:
        q = wd_by_osm.get(r['id'])
    if not q:   # sin etiqueta: por coordenadas (<=15 m) y nombre compatible
        for w in wd.values():
            if w['ll'] and hav(w['ll'][0], w['ll'][1], r['la'], r['lo']) <= 15:
                nm = wd_name(w)
                if nm and name_in_text(nm, r['n']) >= 0.99 and name_in_text(r['n'], nm) >= 0.99: q = w['q']; break
    if q and q in wd:
        w = wd[q]
        if w['ll'] and hav(w['ll'][0], w['ll'][1], r['la'], r['lo']) > MAXWD:
            P(r['id'], 'OSM y Wikidata (%s) sitúan la placa a %.0f m una de otra' % (q, hav(w['ll'][0], w['ll'][1], r['la'], r['lo'])), n=r['n'], la=r['la'], lo=r['lo']); r['_drop'] = True; used_wd.add(q); continue
        nm = wd_name(w)
        if nm and name_in_text(nm, r['n']) < 0.99 and name_in_text(r['n'], nm) < 0.99:
            P(r['id'], 'el nombre de OSM («%s») y el de Wikidata %s («%s») no coinciden' % (r['n'], q, nm), n=r['n'], la=r['la'], lo=r['lo']); r['_drop'] = True; used_wd.add(q); continue
        r['wd'] = q; r['src'] = 'osm+wd'; used_wd.add(q)
        if not r.get('p') and len(w['subj']) == 1:
            sq = next(iter(w['subj']))
            if re.fullmatch(r'Q\d+', sq): r['p'] = sq
        if not r.get('img') and w['img']:
            from urllib.parse import unquote
            r['img'] = unquote(sorted(w['img'])[0].rsplit('/', 1)[-1]).replace('_', ' ')
        if not r.get('c') and len(w['p131']) == 1: r['c'] = next(iter(w['p131']))
osm_recs = [r for r in osm_recs if not r.get('_drop')]

# ---- duplicados OSM–OSM (mismo nombre normalizado a <=25 m) ----
seen = []
for r in sorted(osm_recs, key=lambda r: r['id']):
    dup = next((s for s in seen if norm(s['n']) == norm(r['n']) and hav(s['la'], s['lo'], r['la'], r['lo']) <= 25), None)
    if dup: dups.append({'id': r['id'], 'dup_de': dup['id'], 'n': r['n']}); continue
    seen.append(r)
osm_recs = seen

# ---- Wikidata sin OSM ----
for q, w in sorted(wd.items()):
    if q in used_wd: continue
    nm = wd_name(w)
    base = {'n': nm or w['label']}
    if not nm: P(q, 'el ítem de Wikidata no es una piedra de una persona con nombre (etiqueta: «%s»)' % (w['label'] or '')[:70], **base); continue
    nm, wy_b, wy_d = strip_years(nm)
    nm, why = clean_name(nm)
    if not nm or COLLECTIVE_RE.search(nm): P(q, why or 'nombre colectivo en Wikidata', **base); continue
    if not w['ll'] or w['multi_coord']: P(q, 'sin coordenadas P625 únicas en Wikidata', **base); continue
    la, lo = w['ll']
    ins = sorted(w['inscr']); ad = sorted(w['addr'])
    if len(ad) > 1 or len(ins) > 1:
        P(q, 'Wikidata trae varias direcciones o inscripciones distintas', **base, la=la, lo=lo); continue
    if not (ad or ins): P(q, 'sin dirección P6375 ni inscripción P1684 en Wikidata', **base, la=la, lo=lo); continue
    insc = split_insc(re.sub(r'^"|"$', '', ins[0])) if ins else ''
    if insc and name_in_text(nm, insc) < 0.99: P(q, 'el nombre de Wikidata no coincide con su inscripción', **base, la=la, lo=lo); continue
    street = hn = None; a = None
    if ad:
        ps, ph = parse_memorial_addr(ad[0].split(',')[0] if CC not in ('FR',) else ad[0])
        if CC == 'FR':
            m = re.match(r'^(\d+\w?)\s+(.*?)\s+\d{5}\s+(.*)$', ad[0])
            if m: ph, ps = m.group(1), m.group(2)
        if ps: street, hn = ps, ph
        a = compose_addr(street, hn, CC) if street else ad[0].split(',')[0].strip()
    if not street or not hn:
        P(q, 'la dirección de Wikidata no tiene calle y número legibles; sin comprobar contra OSM', **base, la=la, lo=lo); continue
    pos, dpos = addr_check(la, lo, street, hn)
    fimg = unquote(sorted(w['img'])[0].rsplit('/', 1)[-1]).replace('_', ' ') if w['img'] else None
    cpos, cd = commons_check(la, lo, fimg)
    if not (pos == 'ok' or cpos == 'ok') or cpos == 'lejos' and pos != 'ok':
        P(q, 'la coordenada de Wikidata no se confirma con una dirección de OSM ni con la foto de Commons (%s %s: dirección %s%s; Commons %s)' % (street, hn, pos, ' a %.0f m' % dpos if dpos else '', cpos), **base, la=la, lo=lo); continue
    c = next(iter(w['p131'])) if len(w['p131']) == 1 else None
    if len(w['subj']) > 1: P(q, 'varios sujetos (P547) en Wikidata', **base, la=la, lo=lo); continue
    rec = {'id': q, 'la': round(la, 6), 'lo': round(lo, 6), 'src': 'wd', 'wd': q}
    if len(w['subj']) == 1 and re.fullmatch(r'Q\d+', next(iter(w['subj']))): rec['p'] = next(iter(w['subj']))
    rec['n'] = nm
    if wy_b: rec['b'] = wy_b; rec['d'] = wy_d
    if insc: rec['i'] = insc
    rec['a'] = a
    if c: rec['c'] = c
    cm = citymap.get(q)
    if cm:
        if not rec.get('c') and cm.get('c'): rec['c'] = cm['c']
        if cm.get('sub') and cm.get('sub') != rec.get('c'): rec['sub'] = cm['sub']
    rec['cc'] = CC
    if w['inc']:
        y = sorted(w['inc'])[0][:10]
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}', y): rec['laid'] = y[:4] if y.endswith('-01-01') else y
    if w['img']:
        from urllib.parse import unquote
        rec['img'] = unquote(sorted(w['img'])[0].rsplit('/', 1)[-1]).replace('_', ' ')
    rec['_v'] = {'pos': pos, 'dpos': dpos, 'commons': cpos, 'dcommons': cd, 'notes': []}
    osm_recs.append(rec)

# duplicados Wikidata sin OSM contra OSM
fin = []
for r in osm_recs:
    if r['src'] == 'wd':
        dup = next((s for s in fin if s['src'] != 'wd' and norm(s['n']) == norm(r['n']) and hav(s['la'], s['lo'], r['la'], r['lo']) <= 100), None)
        if dup: dups.append({'id': r['id'], 'dup_de': dup['id'], 'n': r['n']}); continue
    fin.append(r)
ORDER = ['id', 'la', 'lo', 'src', 'wd', 'p', 'wp', 'n', 'i', 'a', 'c', 'sub', 'cc', 'b', 'd', 'laid', 'img']
added = [{k: r[k] for k in ORDER if k in r} | {'_v': r['_v']} for r in fin]
from collections import Counter
stats = {'osm_objetos': len(els), 'wd_items': len(wd), 'anadidas': len(added), 'pendientes': len(pend), 'duplicados': len(dups),
         'src': dict(Counter(r['src'] for r in added)), 'posicion': dict(Counter(r['_v']['pos'] for r in added)), 'commons': dict(Counter(r['_v']['commons'] for r in added)),
         'motivos_pendiente': dict(Counter(re.sub(r'[\(«].*', '', p['reason']).strip()[:70] for p in pend))}
out = {'cc': CC, 'osm_snapshot': osm.get('osm_timestamp'), 'near_snapshot': near.get('osm_timestamp'), 'stats': stats, 'added': added, 'pending': pend, 'duplicates': dups}
(D / 'out').mkdir(exist_ok=True)
json.dump(out, open(D / ('out/%s.json' % CC), 'w'), ensure_ascii=False, indent=1)
print(CC, json.dumps(stats, ensure_ascii=False))
