#!/usr/bin/env python3
"""v20r4: tras corregir el país de placas fronterizas (apply_border_cc.py), alinea data/sidewalk-v20.json (cc de cada placa y recuentos por país) y los CSV de acera/pares con data/stones.json.
La posición (dla/dlo) no cambia. Uso: patch_sidewalk_cc.py <stones.json del estado anterior>. Idempotente."""
import json, sys, csv
from pathlib import Path
from collections import Counter
R = Path(__file__).resolve().parents[2]
old = {s['id']: (s.get('cc') or 'DE') for s in json.load(open(sys.argv[1], encoding='utf-8'))['stones']}
new = {s['id']: (s.get('cc') or 'DE') for s in json.load(open(R / 'data/stones.json', encoding='utf-8'))['stones']}
ch = {i: (old[i], new[i]) for i in new if i in old and old[i] != new[i]}
p = R / 'data/sidewalk-v20.json'; d = json.load(open(p, encoding='utf-8')); tab = {s['id']: s for s in d['stones']}
for i, (o, n) in ch.items():
    if i in tab and tab[i]['cc'] == o:
        tab[i]['cc'] = n; e = tab[i]['estado']
        d['counts'][o][e] -= 1; d['counts'].setdefault(n, {'ok': 0})[e] = d['counts'].get(n, {}).get(e, 0) + 1
    elif i not in tab:
        d['counts'][o]['ok'] -= 1; d['counts'].setdefault(n, {'ok': 0})['ok'] += 1
for cc, c in list(d['counts'].items()):
    for k in [k for k, v in c.items() if v == 0 and k != 'ok']: del c[k]
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding='utf-8')
for f, col in (('residuales-acera-v20.csv', 'pais'), ('excepciones-25m-v20.csv', 'pais'), ('pares-solapados-v20.csv', None), ('sin-edificios-v20.csv', None)):
    q = R / f
    if not q.exists(): continue
    rows = list(csv.reader(open(q, encoding='utf-8'))); h = rows[0]
    ci = [j for j, x in enumerate(h) if x in ('pais', 'cc', 'pais_a')]; ii = [j for j, x in enumerate(h) if x in ('id', 'id_a', 'id_b', 'a')]
    n = 0
    for r in rows[1:]:
        for j in ii:
            if j < len(r) and r[j] in ch:
                for cj in ci:
                    if r[cj] == ch[r[j]][0]: r[cj] = ch[r[j]][1]; n += 1
    csv.writer(open(q, 'w', encoding='utf-8', newline='')).writerows(rows); print(f, 'filas con país cambiado:', n, '| cabecera', h)
print('placas con país distinto:', len(ch), Counter(ch.values()))
