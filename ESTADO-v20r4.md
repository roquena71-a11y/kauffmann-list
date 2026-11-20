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
