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
# cobertura real de la confirmación de posición (auditoría A, C6b): A dirección independiente ≤40 m, B foto independiente, C foto con la coordenada copiada de OSM, D solo la coordenada de la fuente
vid = {s['id'] for s in S}; cov = {}; covt = Counter()
for cc_, o_ in list(outs.items()) + [('D1480', d1480)]:
    for r in o_['added']:
        if r['id'] not in vid or r['id'] in V19: continue
        v = r.get('_v') or {}
        k = 'A' if (v.get('pos_indep', v.get('pos')) == 'ok') else ('B' if v.get('commons') == 'ok' and (v.get('dcommons') or 0) > 1 else ('C' if v.get('commons') == 'ok' else 'D'))
        cov.setdefault(r.get('cc') or 'DE', Counter())[k] += 1; covt[k] += 1
ntot = sum(covt.values())
relab = Counter(s['cc'] for s in S if s['id'] in V19 and s.get('cc') and s['cc'] not in ('JE', 'FI', 'IE', 'SE', 'RO'))   # JE/FI/IE/SE/RO (41) ya iban con país en la v19 publicada
_rr = list(csv.DictReader(open(R / 'residuales-acera-v20.csv', encoding='utf-8'))); n_fallo = sum(1 for r in _rr if r['tipo'] == 'fallo'); n_rev = sum(1 for r in _rr if r['tipo'] == 'revisar-sin-contacto'); n_man = sum(1 for r in _rr if r['tipo'] == 'manzana-dudosa')
_fb = Counter(r['pais'] for r in _rr if r['tipo'] == 'fallo')
_ex = list(csv.DictReader(open(R / 'excepciones-25m-v20.csv', encoding='utf-8'))); n_ex = len(_ex)
_fpj = json.load(__import__('gzip').open(R / 'tests/sidewalk/footprints-v20.json.gz', 'rt', encoding='utf-8')); n_sin = len(_fpj.get('sin_edificios_50m', []))
now = datetime.now().strftime('%Y-%m-%d %H:%M')
L = []; a = L.append
tot_new = sum(new.values())
a('# INFORME v20 — países nuevos, colocación en la acera (Alemania incluida) y las 1.480 de Wikidata\n')
a('Generado %s (hora de Berlín). Prototipo local sobre la v19 publicada (commit 49e7725). **Nada publicado, sin push.**\n' % now)
a('## 1. Resumen\n')
a('- Total de placas en el mapa: **{:,}** (v19: {:,}; **+{:,}**). {} países con placas.'.format(len(S), len(V19), len(S) - len(V19), len(cnt)).replace(',', '.'))
a('- Nuevas por país (países nuevos + las %d de las 1.480 en Alemania): ' % new.get('DE', 0) + ' · '.join('%s %d' % (NAMES[c][0], n) for c, n in sorted(new.items(), key=lambda x: -x[1]) if n))
a('- Datos abiertos únicamente: OpenStreetMap (ODbL; Geofabrik europe 2026-11-18 ~21:21 UTC, refrescado por id con Overpass el 2026-11-20) y Wikidata (CC0, consulta del 2026-11-20). Sin nombres de archivos cerrados.')
a('- Las coordenadas de origen (`la`/`lo`) no se tocan nunca; la posición de dibujo va en `dla`/`dlo`.')
a('- Controles aplicados a cada placa nueva (no todas tienen la misma confirmación de posición; ver cobertura abajo): nombre limpio (solo se quitan prefijos literales como «Stolperstein für»), nombre (palabras completas) tal cual en la inscripción cuando ésta existe, un solo nombre de persona (los registros con varias personas, rótulos o instituciones van a pendiente), año de muerte coherente con la inscripción, imagen de Commons existente, sin duplicado a ≤15 m (mismo nombre o subconjunto y mismo nacimiento), y, si OSM marca la posición como dudosa (`fixme`), solo con un objeto `addr:*` ajeno a la placa a ≤15 m o una foto cuya coordenada no sea copia de OSM; fusión OSM–Wikidata solo si ≤50 m y nombre compatible. Lo dudoso va a `pendiente-v20.csv` con su motivo.')
a(('- **Cobertura real de la confirmación de posición** de las %d placas nuevas: **A** objeto `addr:*` de OSM ajeno a la placa, misma calle y número, ≤40 m: **%d (%.0f %%)** · **B** foto de Commons con coordenada independiente: %d · **C** foto de Commons cuya coordenada coincide con la de OSM al metro (no es independiente): %d · **D** solo la coordenada de la fuente (sin dirección ni foto que la contraste): **%d (%.0f %%)**. La dirección o la inscripción de cada ficha viene de la fuente, pero la posición solo está contrastada de forma independiente en A+B. Por país (A/B/C/D): ' % (ntot, covt['A'], 100 * covt['A'] / ntot, covt['B'], covt['C'], covt['D'], 100 * covt['D'] / ntot)) + '; '.join('%s %d/%d/%d/%d' % (c_, v_['A'], v_['B'], v_['C'], v_['D']) for c_, v_ in sorted(cov.items(), key=lambda x: -sum(x[1].values()))) + '.')
a('- Regla de «posible superviviente / vivo»: igual que en la v19 (`policy.py`, 110 años; marcadores multilingües de superviviente en `pipeline/inscription.py`).\n')
a('## Notas de la versión v20 (para publicar)\n')
a(('- **Corrección de país de %d placas de la v19** (contadas como Alemania; el límite administrativo admin_level=2 de OSM las sitúa fuera): ' % sum(relab.values())) + ', '.join('%s %d' % (NAMES[c_][0], n_) for c_, n_ in relab.most_common()) + '. El contenido no cambia (Jersey 20, Finlandia 7, Irlanda 6, Suecia 6 y Rumanía 2 ya llevaban su país en la v19 publicada). Alemania: 65.820 (v19) − %d + %d de las 1.480 (Wikidata) = %d.' % (sum(relab.values()), cnt['DE'] - (65820 - sum(relab.values())), cnt['DE']))
a('- **27 países**: Alemania y 26 más de Europa (Países Bajos, Austria, Francia, Chequia, Noruega, Italia, España, Bélgica, Luxemburgo, Hungría, Lituania, Suiza, Polonia, Eslovaquia, Jersey, Croacia, Dinamarca, Guernsey, Finlandia, Andorra, Irlanda, Suecia, Letonia, Reino Unido, Rumanía y Liechtenstein). Botones de país y búsqueda en español, alemán e inglés; la fila de países se pliega en «Más países (N)».')
a(('- **+%s placas** verificables' % '{:,}'.format(len(S) - len(V19)).replace(',', '.')) + ' con datos abiertos (OSM ODbL + Wikidata CC0), cada una con enlace a su fuente; los casos dudosos quedan en pendiente con su motivo.')
a('- **Todas las placas fuera de los edificios**: Alemania incluida, la posición de dibujo (`dla`/`dlo`) va a la acera con ≥0,5 m de holgura (salvo %d placas residuales con holgura <0,5 m y %d «revisar» sin contacto detectado y %d con el dibujo junto a otra calle, todas documentadas una a una en `residuales-acera-v20.csv`; 25 dibujos a >25 m en `excepciones-25m-v20.csv`; 57 placas sin edificio de OSM a ≤50 m en `sin-edificios-v20.csv`)' % (n_fallo, n_rev, n_man) + '; la coordenada de origen no se toca y es la que usan «Cómo llegar» y las descargas.')
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
_man = json.load(open(R / 'data/v20-added-20261120.json', encoding='utf-8')); _d14 = [d for d in _man['duplicates'] if d.get('regla', '').endswith('(las 1.480)')]
_ad14 = sum(1 for s in S if s.get('gm') == 'commons:coordinates')
a('- **Añadidas al mapa: %d** · **pendientes: %d** (de %d). El verificador aceptó %d, pero %d eran la misma persona que una placa ya presente a ≤15 m y se fusionaron con ella, sin añadir otra: %s (en `pendiente-1480-v20.csv` figuran como «duplicado»).' % (_ad14, st['total'] - _ad14, st['total'], st['anadidas'], len(_d14), '; '.join('%s → %s' % (d['id'], d['dup_de']) for d in _d14)))
for k, v in rs.most_common(): a('  - %s: %d' % (k, v))
a('\nDetalle por ítem: `pendiente-1480-v20.csv` (resultado, motivo v14 y motivo v20).\n')
a('## 5. Colocación en la acera (Alemania y países nuevos)\n')
ge = swc.get('DE', {})
a('- Alemania: %s placas ya bien, **%s con posición de dibujo ajustada**, %s dentro de un edificio por indicación de la fuente (nivel −1, Stolperschwellen), %s para revisar.' % (ge.get('ok'), ge.get('ajustada'), ge.get('legitima', 0), ge.get('revisar', 0)))
a('- Regla: columna 3D de 1,2 m + chincheta 2D de 12 px (zoom 19) a ≥0,5 m de toda huella de OSM; desplazamiento mínimo hacia la calle, máximo 25 m (+ cuadrícula del grupo); el bucle con la **disposición real de la app** (`_dla/_dlo/_ang` en Chrome) comprueba cada columna y añade holgura por grupo; el bucle se cerró con %d residuales con holgura <0,5 m (no con 0; ver abajo).' % n_fallo + ' Las coordenadas de «Cómo llegar», GeoJSON y KML son las de origen.')
a('- Detalle de las placas movidas o por revisar: `data/sidewalk-v20.json`.\n')
a('- **Grupos fijos (cambio de la app en v20):** con `meta.layout_pinned` la app ya no empuja ni encoge los grupos de columnas (en la v19 los empujaba hasta 8 m y podía devolver una columna a un edificio). La separación entre grupos la calcula ahora `pipeline/tools/separate20.py` (columnas de grupos distintos a ≥1,8 m salvo casos sin hueco): pares de columnas dibujadas a <1,55 m: de 845 (v19) a 35 tras v20r2 (los 35 restantes son grupos contiguos sin hueco libre para separarlos ≤8 m; los 7 casos «sin solución» de `separate20` están entre ellos).')
a('- **Solver exacto** (`sidewalk20.py`): cada chincheta 2D en su coordenada y cada columna 3D en su casilla de la cuadrícula real (ángulo tomado de la app) a ≥0,5 m de toda huella de OSM; la chincheta 2D se exige además en la casilla de la columna (así miden las auditorías).')
a(('- **Comprobación independiente** (`check_layout20.py`, shapely, sobre el volcado de la app real): tras el cierre quedan **%d placas con holgura <0,5 m (%s)**; el CSV `residuales-acera-v20.csv` tiene **%d filas = %d de esas + %d «revisar»** (el solver no halló hueco, pero la comprobación independiente no detecta contacto con ninguna huella) **+ %d «manzana-dudosa»** (FR `n13041383986`, `n13032352978`, `n13032352980`, DE `Q133230139`: el dibujo queda más cerca de otra calle que la de su dirección; comprobado, sin corregir). Cada fila lleva su motivo. Son grupos grandes en calles sin hueco libre de edificios a ≤25 m; no se mueven más para no falsear su dirección. **Estas placas siguen pendientes de decisión de Carlos** (no se afirma que estén bien colocadas).' % (n_fallo, ', '.join('%s %d' % (k, v) for k, v in _fb.most_common()) or 'ninguna', len(_rr), n_fallo, n_rev, n_man)))
a(('- **Tope de 25 m de lo dibujado** (auditoría C): el solver reduce el desplazamiento máximo del grupo en la dispersión de su cuadrícula (grupos de hasta 20 placas); los grupos de más de 20 placas con la misma dirección (campos de Stolpersteine, p. ej. Brahmsallee y Grindelallee en Hamburgo) no caben en 25 m: **%d placas dibujadas a >25 m**, listadas en `excepciones-25m-v20.csv`.' % n_ex))
a(('- **Placas sin ningún edificio de OSM a ≤50 m** (tras volver a traer de Overpass las huellas en 120 m de radio para LU, IT, ES, GG, CZ, NL y FR): **%d placas** (sobre todo Sabadell/Terrassa y Trieste: edificios no mapeados o coordenada en calle ancha; GG y CZ rurales); la lista explícita y la distancia al edificio más cercano están en `sin-edificios-v20.csv` (y `sin_edificios_50m` en `tests/sidewalk/footprints-v20.json.gz`). Para ellas la comprobación se hace contra el edificio más cercano que existe en OSM; el test falla si aparece cualquier otra placa sin edificio a ≤50 m. Es una carencia de datos de OSM, no una verificación.' % n_sin))
a('- Las placas «legítimas» según la fuente (solo las 3 con `level=-1`/`location=indoor` en OSM: `n12461266505/6/7`, museo) no se mueven; las otras 57 Stolperschwellen que la v20 inicial eximía **ya se colocan en la acera como cualquier placa** (solo el dibujo; las coordenadas de origen no cambian).\n')

a('## 6. Auditoría\n')
a('Los scripts de auditoría y los datos están en `/workspace/audits/countries/v20-indep/` (A: fuente cruda; B: contraste en vivo; C: geometría en vivo + interfaz) y `/workspace/v20-data/`. **Las auditorías independientes las ejecutan auditores distintos del constructor**; sus informes irán a `/workspace/audits/countries/v20-indep/{A,B,C}/`.\n')
a('## 6b. Pruebas ejecutadas (por el constructor, no son auditorías independientes)\n')
a('- `tests/run-all.sh` con `REQUIRE_OAV=1` en un venv nuevo (`tests/requirements-ci.txt`, **sin** `SKIP_COUNTRY_BUTTONS`): unitarias del pipeline (58 de inscripción), `v20-added-test`, `v20r2-data-check` (nuevo: 6.177 placas añadidas; ciudad ≠ país/calle, sin multipersonas ni rótulos, imágenes existentes en Commons, fechas frente a la inscripción, nombre exacto en la inscripción, duplicados ≤15 m), ai-door-check, ai-sim, sidewalk-render-check y sidewalk-render-check20 (placas de los países nuevos + 1.500 de Alemania; falla si falta edificio a ≤50 m fuera de `sin-edificios-v20.csv` o si el dibujo está a >25 m fuera de `excepciones-25m-v20.csv`), map2d, fila de países, ficha de Hassall, atribución + axe, y `country-buttons-check` en los 10 tamaños (incl. 844×390, 667×375, 320×568, 360×640, 412×915) para los 27 países. El resultado de la pasada final está en `ESTADO-v20r2.md`.')
a('- Capturas a 412 px: `shots/p412-v20-*.png` (inicio con la fila plegada, fila abierta, vista de NL/FR/AT/NO/CZ, primeros planos 2D y 3D en acera de NL/FR/NO/AT/DE), `shots/v20-shots.json`.\n')
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
