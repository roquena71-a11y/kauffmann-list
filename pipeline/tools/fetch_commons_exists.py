#!/usr/bin/env python3
"""v20r2: ¿existen hoy en Wikimedia Commons los ficheros de imagen de las placas? → V20_DATA/commons_exists20.json {nombre: true|false}.
Lee los nombres (campo wikimedia_commons de OSM, P18 de Wikidata) de osm20_CC.json y wd_CC.json; consulta la API de Commons (info, 40 títulos por petición).
Uso: fetch_commons_exists.py [CC...]"""
import json, os, re, sys, time, glob, urllib.request, urllib.parse
from pathlib import Path
D = Path(os.environ.get('V20_DATA', '/workspace/v20-data'))
names = set()
def add(f):
    for x in re.split(r'\s*;\s*', f or ''):
        x = x.strip()
        if x.startswith('File:'): x = x[5:]
        if x: names.add(x.replace('_', ' '))
for p in glob.glob(str(D / 'osm20_*.json')):
    for e in json.load(open(p, encoding='utf-8'))['elements']: add((e.get('tags') or {}).get('wikimedia_commons'))
for p in glob.glob(str(D / 'wd_*.json')):
    for b in json.load(open(p, encoding='utf-8'))['results']['bindings']:
        if 'img' in b: add(urllib.parse.unquote(b['img']['value'].rsplit('/', 1)[-1]))
for p in glob.glob(str(D / 'out/D1480.json')):
    for r in json.load(open(p, encoding='utf-8'))['added']: add(r.get('img'))
cf = D / 'commons_exists20.json'; cache = json.load(open(cf)) if cf.exists() else {}
todo = sorted(n for n in names if n not in cache); print(len(names), 'nombres;', len(todo), 'por consultar')
for i in range(0, len(todo), 40):
    batch = todo[i:i + 40]
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'titles': '|'.join('File:' + n for n in batch), 'prop': 'info', 'format': 'json', 'formatversion': 2, 'redirects': 1})
    for k in range(4):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'ListaKauffmann/1.0 (https://github.com/roquena71-a11y/kauffmann-list; audit-fix)'}), timeout=60)); break
        except Exception as ex: time.sleep(3 * (k + 1)); d = None
    if d is None: print('fallo en el lote', i); continue
    q = d['query']; norm_ = {x['from']: x['to'] for x in q.get('normalized', [])}; red = {x['from']: x['to'] for x in q.get('redirects', [])}
    miss = {p['title']: bool(p.get('missing')) for p in q['pages']}
    for n in batch:
        t = 'File:' + n; t = norm_.get(t, t); t = red.get(t, t)
        cache[n] = (not miss[t]) if t in miss else False
    time.sleep(0.2)
json.dump(cache, open(cf, 'w'), ensure_ascii=False, indent=0)
print('existen', sum(1 for v in cache.values() if v), 'no existen', sum(1 for v in cache.values() if not v))
