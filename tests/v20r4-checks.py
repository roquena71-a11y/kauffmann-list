#!/usr/bin/env python3
"""v20r4 (auditorías A/B ronda 3): (1) ninguna placa fuera de la caja de Viena/Praga/Bratislava lleva ese municipio; (2) país de las placas fronterizas = país por límite administrativo de OSM
(data/v20-border-cc.json: Overpass is_in, 2026-11-20) y ninguna placa de Audun-le-Tiche/Mondorff es de Luxemburgo; (3) fechas de las placas añadidas en v20: ISO válida, sin «-00», día existente;
(4) el «Acerca de» (app3d.js es/de/en) y el INFORME dicen lo mismo que excepciones-25m-v20.csv (nº de placas a >25 m y distancia máxima); (5) sin «inscription=» pegado."""
import json, re, csv, calendar, sys
from pathlib import Path
R = Path(__file__).resolve().parents[1]
S = json.load(open(R / 'data/stones.json', encoding='utf-8'))['stones']; by = {s['id']: s for s in S}
man = json.load(open(R / 'data/v20-added-20261120.json', encoding='utf-8'))
fails = []
def F(m): fails.append(m); print('FALLO:', m)
BOX = {('AT', 'Wien'): (48.10, 16.18, 48.33, 16.58), ('CZ', 'Praha'): (49.94, 14.22, 50.18, 14.71), ('SK', 'Bratislava'): (48.05, 16.95, 48.25, 17.30)}
n1 = 0
for s in S:
    b = BOX.get(((s.get('cc') or 'DE'), s.get('c')))
    if b:
        n1 += 1
        if not (b[0] <= s['la'] <= b[2] and b[1] <= s['lo'] <= b[3]): F('%s (%s) c=%s fuera de la caja de la ciudad (%s, %s)' % (s['id'], s['cc'], s['c'], s['la'], s['lo']))
if by['n2975306671'].get('c') == 'Wien': F('n2975306671 (Josef Logar, Klagenfurt) sigue con c=Wien')
print('(1) placas con c = Wien/Praha/Bratislava dentro de su caja:', n1)
fx = json.load(open(R / 'data/v20-border-cc.json', encoding='utf-8'))['cc']; n2 = 0
for i, iso in fx.items():
    if iso and i in by:
        n2 += 1
        if (by[i].get('cc') or 'DE') != iso: F('%s: cc=%s pero el límite administrativo de OSM dice %s' % (i, by[i].get('cc') or 'DE', iso))
for s in S:
    if (s.get('cc') or 'DE') == 'LU' and s.get('c') in ('Audun-le-Tiche', 'Mondorff'): F('%s en %s marcada Luxemburgo (es Francia)' % (s['id'], s['c']))
    if (s.get('cc') or 'DE') == 'DE' and s.get('c') == 'Vaals': F('%s en Vaals marcada Alemania (es Países Bajos)' % s['id'])
print('(2) placas fronterizas comprobadas contra el límite OSM:', n2, '| LU', sum(1 for s in S if s.get('cc') == 'LU'), 'FR', sum(1 for s in S if s.get('cc') == 'FR'))
ids = {a['id'] for a in man['added']}; n3 = 0
for s in S:
    if s['id'] not in ids: continue
    for k in ('b', 'd'):
        v = s.get(k)
        if not v: continue
        n3 += 1; m = re.fullmatch(r'(\d{4})(?:-(\d\d)(?:-(\d\d))?)?', v)
        if not m: F('%s %s=%r no es ISO' % (s['id'], k, v)); continue
        y, mo, d = int(m[1]), m[2], m[3]
        if mo and not 1 <= int(mo) <= 12: F('%s %s=%r mes imposible' % (s['id'], k, v))
        elif d and not 1 <= int(d) <= calendar.monthrange(y, int(mo))[1]: F('%s %s=%r día inexistente' % (s['id'], k, v))
print('(3) fechas b/d de las placas v20 comprobadas:', n3)
if by['n4585454893'].get('d') != '1943-02-28': F('n4585454893 d=%r (OSM description: 28 February 1943)' % by['n4585454893'].get('d'))
if by['n8494515395'].get('d') != '1945-02': F('n8494515395 d=%r (29-02-1945 no existe: año-mes)' % by['n8494515395'].get('d'))
ex = list(csv.DictReader(open(R / 'excepciones-25m-v20.csv', encoding='utf-8'))); nex = len(ex); mx = max(float(x['dibujo_vs_origen_m']) for x in ex)
app = (R / 'app3d.js').read_text(encoding='utf-8')
for pat, lang in ((r'en %d placas', 'es'), (r'bei %d Steinen', 'de'), (r'for %d stones', 'en')):
    if (pat % nex) not in app: F('«Acerca de» (%s): no dice «%s» (filas de excepciones-25m-v20.csv = %d)' % (lang, pat % nex, nex))
for pat in ('nunca más de 25', 'höchstens 25 m', 'never more than 25'):
    if pat in app: F('«Acerca de» conserva la frase falsa «%s»' % pat)
if ('hasta unos %d m' % round(mx)) not in app: F('«Acerca de» (es): distancia máxima distinta de %.1f m' % mx)
inf = (R / 'INFORME-v20.md').read_text(encoding='utf-8')
for m in re.finditer(r'(\d+) dibujos a >25 m|\*\*(\d+) placas dibujadas a >25 m\*\*', inf):
    if int(m[1] or m[2]) != nex: F('INFORME dice %s a >25 m, el CSV tiene %d' % (m[0], nex))
print('(4) excepciones >25 m: CSV %d, máximo %.1f m' % (nex, mx))
for s in S:
    if re.match(r'(?i)inscription\s*=', s.get('i') or ''): F('%s: inscripción con «inscription=» pegado' % s['id'])
print('v20r4-checks:', 'FALLA (%d)' % len(fails) if fails else 'OK'); sys.exit(1 if fails else 0)
