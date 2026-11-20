#!/usr/bin/env python3
"""v20: genera INFORME-v20.md y INFORME-v20-personas.csv a partir de data/stones.json, data/sidewalk-v20.json, V20_DATA/out/*.json y D1480.json."""
import json, csv, os, re, sys
from pathlib import Path
from collections import Counter
from datetime import datetime
R = Path(__file__).resolve().parents[2]; D = Path(os.environ.get('V20_DATA', '/workspace/v20-data'))
sys.path.insert(0, str(Path(__file__).resolve().parent)); from ui20 import NAMES
S = json.load(open(R / 'data/stones.json', encoding='utf-8')); M = S['meta']; S = S['stones']
SW = json.load(open(R / 'data/sidewalk-v20.json', encoding='utf-8'))
V19 = {r['id'] for r in json.loads(os.popen('cd %s && git show 49e7725:data/stones.json' % R).read())['stones']}
cnt = Counter((s.get('cc') or 'DE') for s in S); new = Counter((s.get('cc') or 'DE') for s in S if s['id'] not in V19)
outs = {p.stem: json.load(open(p, encoding='utf-8')) for p in sorted((D / 'out').glob('??.json'))}
d1480 = json.load(open(D / 'out/D1480.json', encoding='utf-8'))
swc = SW['counts']; tbl = SW['stones']
mv = {}
for r in tbl:
    if 'desplazamiento_m' in r: mv.setdefault(r['cc'], []).append(r['desplazamiento_m'])
now = datetime.now().strftime('%Y-%m-%d %H:%M')
L = []; a = L.append
tot_new = sum(new.values())
a('# INFORME v20 — países nuevos, colocación en la acera (Alemania incluida) y las 1.480 de Wikidata\n')
a('Generado %s (hora de Berlín). Prototipo local sobre la v19 publicada (commit 49e7725). **Nada publicado, sin push.**\n' % now)
a('## 1. Resumen\n')
a('- Total de placas en el mapa: **{:,}** (v19: {:,}; **+{:,}**). {} países con placas.'.format(len(S), len(V19), len(S) - len(V19), len(cnt)).replace(',', '.'))
a('- Nuevas por país (países nuevos + las 32 de las 1.480 en Alemania): ' + ' · '.join('%s %d' % (NAMES[c][0], n) for c, n in sorted(new.items(), key=lambda x: -x[1]) if n))
a('- Datos abiertos únicamente: OpenStreetMap (ODbL; Geofabrik europe 2026-11-18 ~21:21 UTC, refrescado por id con Overpass el 2026-11-20) y Wikidata (CC0, consulta del 2026-11-20). Sin nombres de archivos cerrados.')
a('- Las coordenadas de origen (`la`/`lo`) no se tocan nunca; la posición de dibujo va en `dla`/`dlo`.')
a('- Cada placa nueva cumple: nombre limpio (solo se quitan prefijos literales como «Stolperstein für»), nombre contenido en la inscripción, dirección etiquetada contrastada con objetos `addr:*` de OSM (≤40 m; sin calle ≤25 m) o con la coordenada de la foto de Commons, sin `fixme` de posición sin comprobar, fusión OSM–Wikidata solo si ≤50 m y nombre compatible. Lo dudoso va a `pendiente-v20.csv` con su motivo.')
a('- Regla de «posible superviviente / vivo»: igual que en la v19 (`policy.py`, 110 años; marcadores multilingües de superviviente en `pipeline/inscription.py`).\n')
a('## Notas de la versión v20 (para publicar)\n')
a('- **27 países**: Alemania y 26 más de Europa (Países Bajos, Austria, Francia, Chequia, Noruega, Italia, España, Bélgica, Luxemburgo, Hungría, Lituania, Suiza, Polonia, Eslovaquia, Jersey, Croacia, Dinamarca, Guernsey, Finlandia, Andorra, Irlanda, Suecia, Letonia, Reino Unido, Rumanía y Liechtenstein). Botones de país y búsqueda en español, alemán e inglés; la fila de países se pliega en «Más países (N)».')
a('- **+6.412 placas** verificables con datos abiertos (OSM ODbL + Wikidata CC0), cada una con enlace a su fuente; los casos dudosos quedan en pendiente con su motivo.')
a('- **Todas las placas fuera de los edificios**: Alemania incluida, la posición de dibujo (`dla`/`dlo`) va a la acera con ≥0,5 m de holgura; la coordenada de origen no se toca y es la que usan «Cómo llegar» y las descargas.')
a('- Piedras con posición deducida de la foto de Commons: aviso «posición aproximada» propio. Regla de «posible superviviente» sin cambios.')
a('- Caché del navegador: `kauffmann-v20-pages`.\n')
a('## 2. Placas por país\n')
a('| País | En el mapa | Nuevas v20 | Objetos OSM | Ítems WD | Pendientes (motivo en CSV) | Acera: ya bien | Acera: ajustadas | Dentro legítimo | Para revisar | Mayor desplazamiento (m) |')
a('|--|--|--|--|--|--|--|--|--|--|--|')
for c, n in sorted(cnt.items(), key=lambda x: -x[1]):
    o = outs.get(c); sc = swc.get(c, {}); m_ = mv.get(c)
    a('| %s (%s) | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (NAMES[c][0], c, n, new[c], o['stats']['osm_objetos'] if o else '—', o['stats']['wd_items'] if o else '—', o['stats']['pendientes'] if o else '—',
        sc.get('ok', '—'), sc.get('ajustada', '—'), sc.get('legitima', 0) if sc else '—', sc.get('revisar', 0) if sc else '—', max(m_) if m_ else '—'))
a('\nPaíses con datos abiertos pero **sin ninguna placa verificable** (todo en pendiente): ' + ', '.join('%s (%d objetos/ítems)' % (NAMES[c][0], o['stats']['osm_objetos'] + o['stats']['wd_items']) for c, o in outs.items() if c not in cnt) + '.\n')
a('## 3. Motivos de pendiente por país (resumen)\n')
for c, o in outs.items():
    mo = o['stats']['motivos_pendiente']
    if mo: a('- **%s**: ' % NAMES[c][0] + '; '.join('%s: %d' % (k, v) for k, v in sorted(mo.items(), key=lambda x: -x[1])[:6]))
a('\nLista completa (id, nombre, motivo, coordenada): `pendiente-v20.csv`.\n')
a('## 4. Las 1.480 piedras de Wikidata sin coordenadas (v14)\n')
st = d1480['stats']; rs = Counter(re.sub(r'[«(].*', '', p['reason']).strip()[:90] for p in d1480['pending'])
a('Regla: se añade solo si el ítem tiene nombre limpio (y está en su inscripción), su propia imagen (P18) de Commons tiene coordenadas y menciona el nombre, y esa coordenada cae a ≤40 m de un objeto `addr:*` de OSM cuya calle y número aparecen en la foto o en el ítem; sin duplicado a ≤60 m. La posición es la de la foto (aproximada; marcada `gm=commons:coordinates`, con aviso en la ficha).\n')
a('- **Añadidas: %d** · **pendientes: %d** (de %d).' % (st['anadidas'], st['pendientes'], st['total']))
for k, v in rs.most_common(): a('  - %s: %d' % (k, v))
a('\nDetalle por ítem: `pendiente-1480-v20.csv` (resultado, motivo v14 y motivo v20).\n')
a('## 5. Colocación en la acera (Alemania y países nuevos)\n')
ge = swc.get('DE', {})
a('- Alemania: %s placas ya bien, **%s con posición de dibujo ajustada**, %s dentro de un edificio por indicación de la fuente (nivel −1, Stolperschwellen), %s para revisar.' % (ge.get('ok'), ge.get('ajustada'), ge.get('legitima', 0), ge.get('revisar', 0)))
a('- Regla: columna 3D de 1,2 m + chincheta 2D de 12 px (zoom 19) a ≥0,5 m de toda huella de OSM; desplazamiento mínimo hacia la calle, máximo 25 m (+ cuadrícula del grupo); el bucle con la **disposición real de la app** (`_dla/_dlo/_ang` en Chrome) comprueba cada columna y añade holgura por grupo hasta 0 fallos. Las coordenadas de «Cómo llegar», GeoJSON y KML son las de origen.')
a('- Detalle de las placas movidas o por revisar: `data/sidewalk-v20.json`.\n')
a('- **Grupos fijos (cambio de la app en v20):** con `meta.layout_pinned` la app ya no empuja ni encoge los grupos de columnas (en la v19 los empujaba hasta 8 m y podía devolver una columna a un edificio). La separación entre grupos la calcula ahora `pipeline/tools/separate20.py` (columnas de grupos distintos a ≥1,8 m salvo casos sin hueco): pares de columnas a <1,55 m pasaron de 845 a 68.')
a('- **Solver exacto** (`sidewalk20.py`): cada chincheta 2D en su coordenada y cada columna 3D en su casilla de la cuadrícula real (ángulo tomado de la app) a ≥0,5 m de toda huella de OSM; la chincheta 2D se exige además en la casilla de la columna (así miden las auditorías).')
a('- **Comprobación independiente** (`/workspace/v20-data/tools/check_layout20.py`, shapely, sobre el volcado de la app real): tras el cierre quedan **36 placas con holgura <0,5 m (33 Alemania, 3 Países Bajos)** y 26 «revisar» sin solape detectado; todas listadas con motivo y déficit en `residuales-acera-v20.csv` (grupos grandes sin hueco en la acera a ≤25 m, p. ej. 10 placas en una calle estrecha). No se ha movido ninguna de ellas más allá de 25 m para no falsear su dirección.')
a('- Las 60 placas «legítimas» (OSM nivel −1 / Stolperschwellen) no se mueven; el resto de Alemania, 100 % de las placas comprobadas salvo los residuales anteriores.\n')

a('## 6. Auditoría\n')
a('Los scripts de auditoría y los datos están en `/workspace/audits/countries/v20-indep/` (A: fuente cruda; B: contraste en vivo; C: geometría en vivo + interfaz) y `/workspace/v20-data/`. **Las auditorías independientes las ejecutan auditores distintos del constructor**; sus informes irán a `/workspace/audits/countries/v20-indep/{A,B,C}/`.\n')
a('## 7. Archivos\n')
a('- `data/stones.json` (con `dla`/`dlo`), `data/v20-added-20261120.json` (manifiesto), `data/sidewalk-v20.json`, `pendiente-v20.csv`, `pendiente-1480-v20.csv`, `INFORME-v20-personas.csv`.')
a('- Código: `pipeline/tools/{v20_common,build_v20,merge_v20,verify1480,sidewalk20,ui20,make_informe20}.py`.')
(R / 'INFORME-v20.md').write_text('\n'.join(L) + '\n', encoding='utf-8')
with open(R / 'INFORME-v20-personas.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['pais', 'id', 'nombre', 'direccion', 'localidad', 'inscripcion', 'fuente', 'enlace'])
    for s in S:
        if s['id'] in V19: continue
        i = s['id']; link = 'https://www.openstreetmap.org/%s/%s' % ({'n': 'node', 'w': 'way', 'r': 'relation'}[i[0]], i[1:]) if re.match(r'^[nwr]\d+$', i) else 'https://www.wikidata.org/wiki/' + i
        w.writerow([s.get('cc') or 'DE', i, s['n'], s.get('a', ''), s.get('c', ''), (s.get('i') or '').replace('\n', ' / '), s['src'], link])
print('INFORME-v20.md', len(L), 'líneas')
