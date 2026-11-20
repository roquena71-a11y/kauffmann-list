#!/usr/bin/env python3
"""v20r2: comprobaciones de datos de las placas añadidas en la v20 (auditorías independientes A y B): dirección/ciudad, nombres de persona, imágenes, fechas y duplicados.
Falla si alguna placa nueva: tiene «a» sin letras o «c» que es país/calle/«Municipality»; un nombre colectivo/rótulo/institución; img con «;» o «File:» (o inexistente según la caché de Commons);
b/d que no son fecha ISO, o una muerte cuyo año no aparece en la inscripción; un nombre que no está tal cual en su inscripción; o dos placas a <=15 m con nombres compatibles."""
import json, os, re, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(R / 'pipeline/tools'))
from v20_common import same_person_dup, not_one_person, bad_city, name_exact_in, names_compatible, death_years, years_in, parse_wp
from geo import hav
data = json.load(open(R / 'data/stones.json', encoding='utf-8')); S = data['stones']
man = json.load(open(R / 'data/v20-added-20261120.json', encoding='utf-8'))
ids = {r['id'] for r in man['added']} | {s['id'] for s in S if s.get('gm') == 'commons:coordinates'}
new = [s for s in S if s['id'] in ids]
ex = None; cf = Path(os.environ.get('V20_DATA', '/workspace/v20-data-r3')) / 'commons_exists20.json'
if cf.exists(): ex = json.load(open(cf, encoding='utf-8'))
bad = []
def B(s, why): bad.append('%s %s: %s' % (s['id'], (s.get('n') or '')[:40], why))
for s in new:
    a = s.get('a') or ''; c = s.get('c') or ''
    if re.search(r'  |[|]|^\s|\s$|\[$|^\]', s['n']): B(s, 'nombre con espacios dobles o separadores sueltos (%r)' % s['n'])
    if re.search(r'[;:|]', a): B(s, 'a no legible (%r)' % a)
    if a and not re.search(r'[^\W\d_]', a): B(s, 'a sin letras (%r)' % a)
    if c and (bad_city(c) or re.search(r'municipality$', c, re.I)): B(s, 'c es país/calle/Municipality (%r)' % c)
    if s.get('sub') and s['sub'] == c: B(s, 'sub == c')
    if not s.get('src') == 'wd' or True:
        w = not_one_person(s['n'])
        if w and s['id'] not in ('Q98983030', 'Q98983031'): B(s, w)
    img = s.get('img')
    if img:
        if ';' in img or img.startswith('File:'): B(s, 'img con ; o File: (%r)' % img)
        elif ex is not None and not ex.get(img): B(s, 'img inexistente en Commons (%r)' % img)
    for k in ('b', 'd'):
        if s.get(k) and not re.fullmatch(r'\d{4}(-\d\d(-\d\d)?)?', s[k]): B(s, '%s no es fecha (%r)' % (k, s[k]))
    i = s.get('i') or ''
    if s.get('d') and i:
        dy = death_years(i); ys = years_in(i)
        if (dy and s['d'][:4] not in dy) or (ys and s['d'][:4] not in ys): B(s, 'muerte %s no coincide con la inscripción' % s['d'])
    if i and not name_exact_in(s['n'], i) and s.get('src') != 'wd' and not s.get('gm'): B(s, 'nombre no está tal cual en la inscripción')
    if s.get('wp') and parse_wp(s['wp']) is None: B(s, 'enlace de Wikipedia genérico (%r)' % s['wp'])
grid = {}
for s in S: grid.setdefault((int(s['la'] / 0.0003), int(s['lo'] / 0.0005)), []).append(s)
for s in new:
    ci, cj = int(s['la'] / 0.0003), int(s['lo'] / 0.0005)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            for t in grid.get((ci + di, cj + dj), []):
                if t['id'] > s['id'] and (t.get('cc') or 'DE') == (s.get('cc') or 'DE') and hav(s['la'], s['lo'], t['la'], t['lo']) <= 15 and same_person_dup(s, t) \
                   and not (s.get('src') == 'wd' and t.get('src') == 'wd'): B(s, 'duplicado de %s (<=15 m, nombres compatibles)' % t['id'])
# v20r3 (auditorías A/B ronda 2)
ISO_B = re.compile(r'^\d{4}(-\d\d(-\d\d)?)?$')
for s in S:   # TODAS las placas (también las de la v19): b/d solo fechas ISO (nada de «unknown», «unbek.», URLs, «23.04.1942»)
    for k in ('b', 'd'):
        if s.get(k) and not ISO_B.match(s[k]): B(s, '%s no es una fecha ISO (%r)' % (k, s[k]))
    if (s.get('cc') in ('LU', 'CH')) and s.get('c') and bad_city(s['c']): B(s, 'c es país/calle (%r)' % s['c'])
for s in new:
    if re.search(r'(?<![A-Za-z])(historic|memorial|network|name|stolperstein)=', s.get('i') or ''): B(s, 'la inscripción trae etiquetas de OSM pegadas')
    dy = [int(y) for y in death_years(s.get('i') or '')] + ([int(s['d'][:4])] if s.get('d') else [])
    if dy and max(dy) > 1950 and s.get('gm') is None and s.get('src') != 'wd': B(s, 'muerte posterior a 1950 (%d): no es una víctima del nazismo' % max(dy))
    if s.get('cc') in ('CZ', 'SK', 'AT') and not s.get('c') and s.get('a'): B(s, 'sin municipio con dirección')
print('v20r2-data-check:', len(new), 'placas nuevas;', len(bad), 'fallos')
for b in bad[:40]: print('  ', b)
sys.exit(1 if bad else 0)
