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
        k = 'E' if cc_ == 'D1480' else 'A' if (v.get('pos_indep', v.get('pos')) == 'ok') else ('B' if v.get('commons') == 'ok' and (v.get('dcommons') or 0) > 1 else ('C' if v.get('commons') == 'ok' else 'D'))
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
a('- Controles aplicados a cada placa nueva (no todas tienen la misma confirmación de posición; ver cobertura abajo): nombre limpio (solo se quitan prefijos literales como «Stolperstein für»), nombre (palabras completas) tal cual en la inscripción cuando ésta existe, un solo nombre de persona (los registros con varias personas, rótulos o instituciones van a pendiente), año de muerte coherente con la inscripción, imagen de Commons existente, sin duplicado a ≤15 m (mismo nombre o subconjunto y mismo nacimiento), y, si OSM marca la posición como dudosa (`fixme`), solo con un objeto `addr:*` ajeno a la placa a ≤15 m o una foto cuya coordenada no sea copia de OSM; fusión OSM–Wikidata: por la etiqueta `wikidata=` del nodo (solo si ≤50 m y nombre compatible), por nombre idéntico a ≤100 m o por nombre compatible a ≤15 m; **dos fusiones por nombre idéntico superan 50 m** (n3787363171 «Hildegard Stiegler», 58 m; n13037621384 «Raymond Rabeaux», 99 m; mismo nombre y mismo municipio; se conserva la posición del nodo de OSM y no se crea una segunda placa). Lo dudoso va a `pendiente-v20.csv` con su motivo.')
a(('- **Cobertura real de la confirmación de posición** de las %d placas nuevas: **A** objeto `addr:*` de OSM ajeno a la placa, misma calle y número, ≤40 m: **%d (%.0f %%)** · **B** foto de Commons con coordenada independiente: %d · **C** foto de Commons cuya coordenada coincide con la de OSM al metro (no es independiente): %d · **D** solo la coordenada de la fuente (sin dirección ni foto que la contraste): **%d (%.0f %%)** · **E** (las %d de Wikidata en Alemania) la posición ES la coordenada de la foto de Commons del propio ítem, sin segunda fuente. La dirección o la inscripción de cada ficha viene de la fuente, pero la posición solo está contrastada de forma independiente en A+B (criterio estricto: misma calle con similitud ≥0,8 y mismo número, objeto ajeno a la placa, ≤40 m; una medición manual con un criterio más laxo da algo más de A). Por país (A/B/C/D[/E]): ' % (ntot, covt['A'], 100 * covt['A'] / ntot, covt['B'], covt['C'], covt['D'], 100 * covt['D'] / ntot, covt['E'])) + '; '.join('%s %d/%d/%d/%d' % (c_, v_['A'], v_['B'], v_['C'], v_['D']) + ('/%d' % v_['E'] if v_['E'] else '') for c_, v_ in sorted(cov.items(), key=lambda x: -sum(x[1].values()))) + '.')
a('- Regla de «posible superviviente / vivo»: igual que en la v19 (`policy.py`, 110 años; marcadores multilingües de superviviente en `pipeline/inscription.py`).\n')
a('## Notas de la versión v20 (para publicar)\n')
a(('- **Corrección de país de %d placas de la v19** (contadas como Alemania; el límite administrativo admin_level=2 de OSM las sitúa fuera): ' % sum(relab.values())) + ', '.join('%s %d' % (NAMES[c_][0], n_) for c_, n_ in relab.most_common()) + '. El contenido no cambia (Jersey 20, Finlandia 7, Irlanda 6, Suecia 6 y Rumanía 2 ya llevaban su país en la v19 publicada). Alemania: 65.820 (v19) − %d + %d de las 1.480 (Wikidata) = %d.' % (sum(relab.values()), cnt['DE'] - (65820 - sum(relab.values())), cnt['DE']))
a('- **27 países**: Alemania y 26 más de Europa (Países Bajos, Austria, Francia, Chequia, Noruega, Italia, España, Bélgica, Luxemburgo, Hungría, Lituania, Suiza, Polonia, Eslovaquia, Jersey, Croacia, Dinamarca, Guernsey, Finlandia, Andorra, Irlanda, Suecia, Letonia, Reino Unido, Rumanía y Liechtenstein). Botones de país y búsqueda en español, alemán e inglés; la fila de países se pliega en «Más países (N)».')
a(('- **+%s placas** verificables' % '{:,}'.format(len(S) - len(V19)).replace(',', '.')) + ' con datos abiertos (OSM ODbL + Wikidata CC0), cada una con enlace a su fuente; los casos dudosos quedan en pendiente con su motivo.')
a('- **Todas las placas fuera de los edificios**: Alemania incluida, la posición de dibujo (`dla`/`dlo`) va a la acera con ≥0,5 m de holgura (salvo %d placas residuales con holgura <0,5 m y %d «revisar» sin contacto detectado y %d con el dibujo junto a otra calle, todas documentadas una a una en `residuales-acera-v20.csv`; %d dibujos a >25 m (hasta %.1f m) en `excepciones-25m-v20.csv`; 57 placas sin edificio de OSM a ≤50 m en `sin-edificios-v20.csv`)' % (n_fallo, n_rev, n_man, n_ex, max(float(x['dibujo_vs_origen_m']) for x in _ex)) + '; la coordenada de origen no se toca y es la que usan «Cómo llegar» y las descargas.')
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
st = d1480['stats']; rs = Counter(('la foto de Commons no menciona el nombre' if p['reason'].startswith('la foto «') else re.sub(r'[«(].*', '', p['reason']).strip()[:90]) for p in d1480['pending'])   # v20r4 (B ronda 3, R3-3): la frase estaba cortada
a('Regla: se añade solo si el ítem tiene nombre limpio (y está en su inscripción), su propia imagen (P18) de Commons tiene coordenadas y menciona el nombre, y esa coordenada cae a ≤40 m de un objeto `addr:*` de OSM cuya calle y número aparecen en la foto o en el ítem; sin duplicado a ≤60 m. La posición es la de la foto (aproximada; marcada `gm=commons:coordinates`, con aviso en la ficha).\n')
_man = json.load(open(R / 'data/v20-added-20261120.json', encoding='utf-8')); _d14 = [d for d in _man['duplicates'] if d.get('regla', '').endswith('(las 1.480)')]
_ad14 = sum(1 for s in S if s.get('gm') == 'commons:coordinates')
a('- **Añadidas al mapa: %d** · **pendientes: %d** (de %d). El verificador aceptó %d, pero %d eran la misma persona que una placa ya presente a ≤15 m y se fusionaron con ella, sin añadir otra: %s (en `pendiente-1480-v20.csv` figuran como «duplicado»).' % (_ad14, st['total'] - _ad14, st['total'], st['anadidas'], len(_d14), '; '.join('%s → %s' % (d['id'], d['dup_de']) for d in _d14)))
for k, v in rs.most_common(): a('  - %s: %d' % (k, v))
a('  - (duplicados: %d, fusionados con una placa ya presente; ver arriba)' % len(_d14))   # v20r4 (B ronda 3, R3-3): los puntos suman 1.448 pendientes + 3 duplicados + 29 añadidas = 1.480
a('\nDetalle por ítem: `pendiente-1480-v20.csv` (resultado, motivo v14 y motivo v20).\n')
a('## 5. Colocación en la acera (Alemania y países nuevos)\n')
ge = swc.get('DE', {})
a('- Alemania: %s placas ya bien, **%s con posición de dibujo ajustada**, %s dentro de un edificio por indicación de la fuente (nivel −1, Stolperschwellen), %s para revisar.' % (ge.get('ok'), ge.get('ajustada'), ge.get('legitima', 0), ge.get('revisar', 0)))
a('- Regla: columna 3D de 1,2 m + chincheta 2D de 12 px (zoom 19) a ≥0,5 m de toda huella de OSM; desplazamiento mínimo hacia la calle, máximo 25 m (+ cuadrícula del grupo); el bucle con la **disposición real de la app** (`_dla/_dlo/_ang` en Chrome) comprueba cada columna y añade holgura por grupo; el bucle se cerró con %d residuales con holgura <0,5 m (no con 0; ver abajo).' % n_fallo + ' Las coordenadas de «Cómo llegar», GeoJSON y KML son las de origen.')
a('- Detalle de las placas movidas o por revisar: `data/sidewalk-v20.json`.\n')
a('- **Grupos fijos (cambio de la app en v20):** con `meta.layout_pinned` la app ya no empuja ni encoge los grupos de columnas (en la v19 los empujaba hasta 8 m y podía devolver una columna a un edificio). La separación entre grupos la calcula ahora `pipeline/tools/separate20.py` (columnas de grupos distintos a ≥1,8 m salvo casos sin hueco): pares de columnas dibujadas a <1,55 m: de 845 (v19) a 35 tras v20r2 (los 35 restantes son grupos contiguos sin hueco libre para separarlos ≤8 m; los 7 casos «sin solución» de `separate20` están entre ellos).')
a('- **Solver exacto** (`sidewalk20.py`): cada chincheta 2D en su coordenada y cada columna 3D en su casilla de la cuadrícula real (ángulo tomado de la app) a ≥0,5 m de toda huella de OSM; la chincheta 2D se exige además en la casilla de la columna (así miden las auditorías).')
a('- **v20r3 (auditoría C, ronda 2):** (1) los grupos sin hueco con holgura completa (13 con el centro de la columna dentro de un edificio en la v20r2) se colocan con `solve_relaxed`: la posición más cercana al origen en la que el CENTRO de cada columna 3D y de cada chincheta 2D queda fuera de todo edificio con holgura decreciente (1,5 → 0,1 m; fila pegada a la fachada, la columna puede rozar la pared) y a ≥2 m de toda vía rodada; solo si no existe se renuncia, por este orden, a la calzada, a la calle de la dirección y al tope de 25 m (hasta 40 m); (2) las 4 placas que se dibujaban en la calzada (FR `n13041383986`, `n13032352978`, `n13032352980`; DE `Q133230139`) van en fila pegada a la fachada de la calle de su dirección (`sidewalk-facade20.json`); (3) la app ya no agrupa por calle sin número de casa salvo orígenes a ≤8 m (con número, 15 m): no se juntan Brahmsallee/Grindelallee a >25 m; (4) `tests/sidewalk-render-check20.py` FALLA si el centro de una columna 3D o de una chincheta 2D está dentro de un edificio, sin excepción alguna (solo las 3 placas realmente en interior); `residuales-acera-v20.csv` y `pares-solapados-v20.csv` listan lo que queda.')
# v20r4 (auditoría C ronda 3, calzada)
_cal = list(csv.DictReader(open(R / 'calzada-v20.csv', encoding='utf-8'))) if (R / 'calzada-v20.csv').exists() else []
_calk = {}
for _r in _cal: _calk[_r['motivo'][:22]] = _calk.get(_r['motivo'][:22], 0) + 1
_mv_road = sum(1 for r in json.load(open(R / 'data/sidewalk-v20.json', encoding='utf-8'))['stones'] if r.get('nivel') == 5)
a(('- **v20r4 (auditoría C, ronda 3): la placa ya no se dibuja sobre la calzada.** Reglas (`roadway20.py`, solver `sidewalk20.py`): vía rodada = highway motorway/trunk/primary/secondary/tertiary/unclassified/residential (sin túnel ni puente); semiancho = mitad de `width` de OSM si existe (1,5–8 m), si no por clase (residential/unclassified 2,5 m, tertiary 2,75, secondary 3,0, primary/trunk 3,5, motorway 7,0); el CENTRO de cada columna dibujada debe quedar a ≥ semiancho del eje (el solver deja 0,3 m más) salvo que haya un edificio a <6 m (acera pegada a la fachada, mismo criterio que la auditoría C); el desplazamiento mínimo (≤25 m, ≥0,5 m de todo edificio, grupos fijos) elige entre las soluciones a ≤1,5 m del mínimo la más cercana a la línea de fachada. Sin acera donde no se puede deducir una (sin ningún edificio de OSM a ≤25 m del grupo, `sidewalk=no`) la placa no se mueve y se documenta una a una en `calzada-v20.csv` (**%d placas**: %s). Con la regla se reubicaron %s placas (nivel 5 de `data/sidewalk-v20.json`). Causa raíz de las falsas violaciones iniciales: el solver agrupaba las placas por la cadena exacta de la dirección y la app por `addrKey` (calle + número, sin código postal ni ciudad; además une grupos con el centroide a <0,8 m); ahora `sidewalk20.addr_key` es la misma función y se reagruparon %d grupos. Test: `tests/sidewalk-render-check20.py` falla si el centro dibujado de una placa de la muestra (las 612 de C + 600 movidas + países nuevos + 1.500 de Alemania) cae a menos del semiancho del eje de una vía rodada sin edificio a <6 m y sin documentar en `calzada-v20.csv`.' % (len(_cal), '; '.join('%d «%s…»' % (v, k) for k, v in sorted(_calk.items())) or 'ninguna', '{:,}'.format(_mv_road).replace(',', '.'), 503)))
a(('- **Comprobación independiente** (`check_layout20.py`, shapely, sobre el volcado de la app real): tras el cierre quedan **%d placas con holgura <0,5 m (%s)**; el CSV `residuales-acera-v20.csv` tiene **%d filas = %d de esas + %d «revisar»** (el solver no halló hueco, pero la comprobación independiente no detecta contacto con ninguna huella) **+ %d «manzana-dudosa»** (FR `n13041383986`, `n13032352978`, `n13032352980`, DE `Q133230139`: el dibujo queda más cerca de otra calle que la de su dirección; comprobado, sin corregir). Cada fila lleva su motivo. Son grupos grandes en calles sin hueco libre de edificios a ≤25 m; no se mueven más para no falsear su dirección. **Estas placas siguen pendientes de decisión de Carlos** (no se afirma que estén bien colocadas).' % (n_fallo, ', '.join('%s %d' % (k, v) for k, v in _fb.most_common()) or 'ninguna', len(_rr), n_fallo, n_rev, n_man)))
a(('- **Tope de 25 m de lo dibujado** (auditoría C): el solver reduce el desplazamiento máximo del grupo en la dispersión de su cuadrícula (grupos de hasta 20 placas); los grupos de más de 20 placas con la misma dirección (campos de Stolpersteine, p. ej. Brahmsallee y Grindelallee en Hamburgo) no caben en 25 m: **%d placas dibujadas a >25 m**, listadas en `excepciones-25m-v20.csv`.' % n_ex))
a(('- **Placas sin ningún edificio de OSM a ≤50 m** (tras volver a traer de Overpass las huellas en 120 m de radio para LU, IT, ES, GG, CZ, NL y FR): **%d placas** (sobre todo Sabadell/Terrassa y Trieste: edificios no mapeados o coordenada en calle ancha; GG y CZ rurales); la lista explícita y la distancia al edificio más cercano están en `sin-edificios-v20.csv` (y `sin_edificios_50m` en `tests/sidewalk/footprints-v20.json.gz`). Para ellas la comprobación se hace contra el edificio más cercano que existe en OSM; el test falla si aparece cualquier otra placa sin edificio a ≤50 m. Es una carencia de datos de OSM, no una verificación.' % n_sin))
a('- Las placas «legítimas» según la fuente (solo las 3 con `level=-1`/`location=indoor` en OSM: `n12461266505/6/7`, museo) no se mueven; las otras 57 Stolperschwellen que la v20 inicial eximía **ya se colocan en la acera como cualquier placa** (solo el dibujo; las coordenadas de origen no cambian).\n')

a('## 6. Auditoría\n')
a('Los scripts de auditoría y los datos están en `/workspace/audits/countries/v20-indep/` (A: fuente cruda; B: contraste en vivo; C: geometría en vivo + interfaz) y `/workspace/v20-data/`. **Las auditorías independientes las ejecutan auditores distintos del constructor**; sus informes irán a `/workspace/audits/countries/v20-indep/{A,B,C}/`.\n')
a('## 6b. Pruebas ejecutadas (por el constructor, no son auditorías independientes)\n')
a('- `tests/run-all.sh` con `REQUIRE_OAV=1` en un venv nuevo (`tests/requirements-ci.txt`, **sin** `SKIP_COUNTRY_BUTTONS`): unitarias del pipeline (58 de inscripción), `v20-added-test`, `v20r2-data-check` (nuevo: 6.177 placas añadidas; ciudad ≠ país/calle, sin multipersonas ni rótulos, imágenes existentes en Commons, fechas frente a la inscripción, nombre exacto en la inscripción, duplicados ≤15 m), ai-door-check, ai-sim, sidewalk-render-check y sidewalk-render-check20 (placas de los países nuevos + 1.500 de Alemania; falla si falta edificio a ≤50 m fuera de `sin-edificios-v20.csv` o si el dibujo está a >25 m fuera de `excepciones-25m-v20.csv`), map2d, fila de países, ficha de Hassall, atribución + axe, y `country-buttons-check` en los 10 tamaños (incl. 844×390, 667×375, 320×568, 360×640, 412×915) para los 27 países. El resultado de la pasada final está en `ESTADO-v20r2.md`.')
a('- Capturas a 412 px: `shots/p412-v20-*.png` (inicio con la fila plegada, fila abierta, vista de NL/FR/AT/NO/CZ, primeros planos 2D y 3D en acera de NL/FR/NO/AT/DE), `shots/v20-shots.json`.\n')
a('## 6c. Problemas conocidos heredados de la v19 (datos de Alemania), NO corregidos en v20\n')
a('Las auditorías A y B (ronda 3) los encontraron en la base v19 ya publicada; no son regresiones de v20 y no se tocó la base en bloque (solo los 926 `base_fixes` documentados). Quedan para una ronda posterior:\n')
_base = [x for x in S if x['id'] in V19]
_gen = sum(1 for x in _base if 'genid' in (x.get('n') or '') or (x.get('n') or '').startswith('http'))
_db = sum(1 for x in _base if x.get('b') and x.get('d') and x['b'][:4].isdigit() and x['d'][:4].isdigit() and int(x['d'][:4]) < int(x['b'][:4]))
_b45 = sum(1 for x in _base if x.get('b') and x['b'][:4].isdigit() and int(x['b'][:4]) > 1945)
_z = sum(1 for x in _base for k in ('b', 'd') if x.get(k) and re.search(r'-00', x[k]))
_laid = sum(1 for x in _base if x.get('laid') and not re.fullmatch(r'\d{4}(-\d\d(-\d\d)?)?', x['laid']))
_cnum = sum(1 for x in _base if (x.get('cc') or 'DE') == 'DE' and x.get('c') and re.fullmatch(r'[\d\W]*\d[\w\W]{0,2}|.*umbenannt.*', x['c']))
a('- Nombres que no son un nombre limpio: 163 con URL de Wikidata (`…/.well-known/genid/…`) y unos 469 con prefijo («Stolperstein Albert Meyer»), «Familie …», varias personas separadas por «;»/«und» o texto genérico (recuentos de la auditoría A; el nuestro con el criterio estricto «genid»/«http» da %d).' % _gen)
a('- Fechas imposibles o parciales: %d registros con nacimiento posterior a la muerte, %d con nacimiento posterior a 1945, %d campos `b`/`d` con «-00» (fecha parcial de OSM, p. ej. `1910-00-00`).' % (_db, _b45, _z))
a('- `laid` (fecha de colocación) que no es ISO: %d; municipio (`c`) de Alemania con basura numérica («1a», «16», «1946 umbenannt)»): unos 111 (recuento de la auditoría A).' % _laid)
a('- Se vaciaron en v20 (base_fixes) fechas basura, pero también ~150 con el año legible en la inscripción («Jg. 1908»): pérdida conservadora, no error.')
a('- Luxemburgo: «Déifferdeng» (luxemburgués) y «Differdange» (francés) para la misma ciudad; ciudades en inglés (IT «Turin», DK «Copenhagen», CH «Zurich») frente al endónimo de otros países.')
_bc = json.load(open(R / 'data/v20-border-cc.json', encoding='utf-8'))['cambiados']
_pend = {r['id'] for r in csv.DictReader(open(R / 'pendiente-v20.csv', encoding='utf-8'))}
_sid = {x['id'] for x in S}
_fuera = sorted(i for i in _bc if i not in _sid and i not in _pend)
a('- **Placas fronterizas que ninguna versión incluye (hallazgo de v20r4, no añadidas):** al corregir el país por el límite administrativo de OSM (`apply_border_cc.py`, `data/v20-border-cc.json`) se vio que %d nodos `memorial=stolperstein` de OSM (%s; todos a <10 km de otra frontera o fuera de todo país en el respaldo de Natural Earth) no están ni en la v19 ni en el mapa v20: el país que se les asignó (Alemania o ninguno) no coincidía con su fichero de país. **No se han añadido** (no pasaron por las rondas de verificación): %s.' % (len(_fuera), ', '.join('%s %d' % (NAMES[c_][0], n_) for c_, n_ in Counter(_bc[i][1] for i in _fuera).most_common()), ', '.join('`%s`' % i for i in _fuera)))
a('- Corrección de país de v20r4: %d placas del mapa por el límite OSM (22 de Audun-le-Tiche y Mondorff: Luxemburgo → Francia; 4 de Vaals: Alemania → Países Bajos); `tests/v20r4-checks.py` lo comprueba contra el límite OSM para %d placas fronterizas.\n' % (sum(1 for i in _bc if i in _sid), sum(1 for i, v in json.load(open(R / 'data/v20-border-cc.json', encoding='utf-8'))['cc'].items() if v and i in _sid)))
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
