# ESTADO v20r4 (rama v20r4 desde 3f425ee8; datos V20_DATA=/workspace/v20-data-r4)
Tareas: A R3-1 Wien/Klagenfurt, B R3-1 22 LU→FR, B R3-2 texto 25 m, menores (A R3-2/3/4/6, B R3-3/4/5), listar problemas heredados DE en INFORME. Luego rebuild, textos/PDF, stats, bump, API offline, run-all REQUIRE_OAV=1. Sin push, sin auditorías.

## 15:37 worktree + datos r4 creados (cp de r3, rutas reescritas)

## código hecho (sin rebuild aún)
- build_v20.py: cajas Wien/Praha/Bratislava (in_box), CITY_MANUAL n2975306671=Klagenfurt am Wörthersee (Nominatim zoom18), CZ Prague→Praha, strip 'inscription=' , fix_osm_date (v20_common: 1943-20-28 solo con descripción OSM; día inexistente→año-mes; -00 recortado).
- merge_v20.py: Q134877719 a='Eichbergstraße 16, Darmstadt'.
- app3d.js: 'Acerca de' 25 m (es/de/en) reescrito (26 excepciones, hasta ~42 m, ~54 residuales); fecha Wikidata = wikidata_added.snapshot (ui20.py igual).
- make_informe20.py: n_ex en notas, 'la foto de Commons no menciona…', bullet duplicados, sección 6c heredados v19.
- texts20_r4.py (NUEVO; correr DESPUÉS de ui20): 65.820 medido el 18-nov; sitemap lastmod 2026-11-20.
- v20-data-r4/border_isin_r4.py (Overpass is_in, 660 candidatos; salida border_isin_r4.json) → luego assign cc corregido (osm_all_cc.json + osm20_*.json mover LU→FR) + test de frontera.
## Pendiente: aplicar cc, rebuild (rebuild_r3.sh → renombrar r4), sidewalk solo cambiados, texts20.py, ui20, texts20_r4, PDFs, footprints, INFORME, API offline (+10 ficheros), tests nuevos (Wien bbox, frontera, texto 25 m), run-all.
export GIT_AUTHOR_NAME="Carlos Kauffmann" GIT_AUTHOR_EMAIL=roquena71-a11y@users.noreply.github.com GIT_COMMITTER_NAME="Carlos Kauffmann" GIT_COMMITTER_EMAIL=roquena71-a11y@users.noreply.github.com  # para commits

## 16:42 C ronda 3 (calzada): roadway20.py + road_zone/solve_road en sidewalk20.py (separate20 también), roadway_check20.py (select/csv). 1150 grupos con violación (layout_final_r3). Siguiente: sidewalk20.py --only (changed_groups=road_groups.json), dump app (server 8935), select de nuevo, csv, finalize/separate, tests (render-check calzada), pendiente C: n13032352978/80, 3 residuales (n2310732548,Q132934563,Q132934701), 3 pares 1,50-1,53, Tepfer motivo, INFORME.

## 17:20 groups_of une centroides <0,8 m como la app (los pares con dirección distinta se dibujaban como 2 col. desplazadas ~0,9 m: causa de falsas violaciones). rd.sh (ang→sidewalk --only→dump→select) iteraciones r4a→r4b→r4c: 168→89→87 violaciones (45 grupos). Siguiente: analizar esos 45 (niveles 9-13 comp/relajada).

## 17:50 CAUSA RAIZ del desajuste solver/app: groups_of agrupaba por cadena de dirección exacta; la app por addrKey (calle+nº, sin CP/ciudad). Ahora sidewalk20.addr_key = addrKey JS; 503 grupos (2938 placas) cambian de agrupado → regroup_ids.json re-resueltos. _RES evita filas duplicadas en sidewalk-v20.json. fr4.sh (ronda: ang→separate→sidewalk --only→dump→select/gaps/check). Tests: tests/sidewalk-render-check20.py (calzada, requiere roads-v20.json.gz = roads_fixture20.py tras footprints20.py) y road-ids-v20.txt (612 ids de C).

## 18:40 fr4.sh rondas r4h..r4j en curso. Fix Tepfer: extra reset + intento estricto FACADE (tier 6, centros fuera de TODA calzada, <=25 m). near-extra/DE.json (OSM de hoy para Karlsruhe w108964401 y Bergen w146861667) para C-extras. force_groups.json. Quedan ~20 grupos con violación de calzada (grupos grandes sin hueco; 4 pares/1 par app-vs-solver por agrupar distinto según distancia de posiciones DIBUJADAS) → calzada-v20.csv con motivo.

## 18:56 Tepfer FACADE estricto (tier 6) → 18–20 m (ya no >25 m). C-extras n2310732548/Q132934563/Q132934701 corregidos con near-extra/DE.json (OSM de hoy). calzada-v20.csv 109. residuales 147 / excepciones 250 / pares 46 (incl. 1,51–1,54). About actualizado. PDFs regenerados. footprints+roads fixture en curso → INFORME, API, run-all.

## 19:08 footprints20 OK (8934 placas, 168800 edificios, 57 sin edificio ≤50 m, 1 JE omitido sin near). roads_fixture20 OK (14303 vías, 1,04 MB). INFORME regenerado (250 excepciones = 29 grupos, justificado: regla de calzada + addrKey, no artefacto; residuales 147, 102 solo chincheta 2D). Siguiente: bump, API offline, run-all.

## 19:51 run-all REQUIRE_OAV=1 en segundo plano (nohup).
PID: 691051  log: /workspace/v20-data-r4/runall_r4.log
Bump ya en v20 (--sync). API offline ya generada (2026-11-20, 9399 archivos, validate 0 errores). Tras run-all: git add -f api data/search llms, commit final (sin push).

## 20:22 run-all REQUIRE_OAV=1: OK (log /workspace/v20-data-r4/runall_r4.log; PID 691051 terminó).
FALLOS country-buttons: ninguno. sidewalk-render-check20 OK en 8928 placas (incluye regla de calzada). v20r4-checks OK. API offline generated=2026-11-20, 9399 archivos, validate 0 errores 4 avisos (archivos grandes, iguales que r3). Versión 20. Commit final, sin push.
Cuentas: 72.110 total. DE 65.830, NL 1.284, FR 1.177, AT 1.119, NO 611, CZ 600, IT 474, ES 328, BE 172, LU 146, HU 87, LT 70, CH 51, PL 33, SK 33, JE 20, HR 17, DK 14, GG 8, FI 7, AD 7, IE 6, SE 6, LV 4, RO 2, GB 2, LI 2.
Calzada 109, residuales 147, excepciones >25 m 250 (29 grupos), pares <1,55 m 46 (incl. 1,51 1,52 1,54). Tepfer corregido a 18,2 m (tier 6). C-extras n2310732548 / Q132934563 / Q132934701 corregidos (near-extra/DE.json). 22 LU→FR, 4 Vaals DE→NL, Wien/Klagenfurt n2975306671.

## 21:20 r5 (auditoría C ronda 4 FAIL / B menor) — WIP (reaplicado tras un reset del worktree a ea5fba73; near/ V19 y near-extra/DE del Overpass 20-nov 21:13 UTC se conservaron)
Causa del test que no pilló Unna: `sidewalk-render-check20.py` ya marca «centro dentro» como hard=True (residuales no eximen; solo LEGIT n12461266505/6/7), pero n12438845078/081 no estaban en `footprints-v20.json.gz`.
- Unna Mozartstraße (162): dla/dlo +2,3 m N +2,3 m E (3,25 m NE). `layout_nudge20.json`.
- Karlsruhe Herrenstraße 22: grupo 0,50 m más lejos de w108964401 (holgura de columna era 0,08 m).
- near/ IE SE JE FI RO; roadway_check y footprints ya no omiten V19. n13021249318 (JE): 0,72 m del eje, sin acera ni edificio ≤25 m → calzada al regenerar.
- excepciones: unión columna>25 m o chincheta dla>25 m. Osterfeldstraße 12: motivo específico (no se cambia la regla global de 15 m).
- gaps20: distancia con latitud media (antes sobreestimaba y dejaba fuera los 3 pares de C).
- INFORME: cuenta exacta «solo chincheta 2D» del CSV. n5885430141 c=Vaals.
Pendiente: volcado, check_layout_r5, residuales/pares/calzada, footprints+roads, About/INFORME, textos/PDF, API, run-all, commit final (sin push).
