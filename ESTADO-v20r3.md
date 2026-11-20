# ESTADO v20r3 (rama v20r3 desde 87215e2; datos V20_DATA=/workspace/v20-data-r3; servidor local 8913)
Auditorías ronda 2 sobre 87215e2: A FAIL menor, B PASS con avisos, C FAIL. Tareas: C (13 centros dentro, 4 calzada, grupos por calle sin número, CSV de pares, padding), A (c='CZ', no-personas, tags OSM en inscripciones, 72 WD pendientes, fusiones >50 m, INFORME), B (1480 estado, textos públicos, b/d no fecha, Echternach, Sr./Jr., NO portal). Luego run-all REQUIRE_OAV=1 completo + build offline API. Sin push, sin auditorías.

## 12:25 worktree + datos r3 creados (cp de r2, rutas reescritas)

## 12:55 C (código) hecho: groups_of/app3d (calle sin número ⇒ 8 m), solve_relaxed en sidewalk20, sidewalk-facade20.json (3 grupos), DE/FR/NL --only recalculados (DE revisar → 0). Pendiente: datos A/B, rebuild, sidewalk nuevos, finalize, tests C (centro dentro, pares CSV, padding).

## 61bf2b97 A/B (código) confirmado; rebuild en curso (rebuild_r3.sh → /workspace/v20-data-r3/rebuild_r3.log)
Tras el rebuild: DE transplanta dla de 628f59d9; sidewalk completo a los nuevos (ccs_new.txt) + `--only` DE (changed_groups.json); finalize21; luego tests C, texts20.py (proyecto/) + hook ui20 (index/jsonld), INFORME, build API offline, run-all.

## 13:00 commit e373ca2d+ (datos A/B rehechos) y siguientes
- Datos: no-personas (Waisenhaus/Bethaus/Verein/Familie/…, hechos >1950 sin fecha 1933-45 ni palabra de persecución, n8307048446 manual) → pendiente; c=ISO arreglado; WD IT/NO verificadas con OSM ≤40 m recuperadas; motivo veraz; fechas b/d ISO; Echternach; 1.480 = 29+3 duplicados con la placa destino.
- C código: solve_relaxed, fachada, agrupación 8 m sin número; test render-check: centro (3D y 2D) dentro de edificio SIN excepción; footprints con ids fijos; padding rotBtns dinámico (mapui.js).
- Pendiente (en curso): chain3.sh (sidewalk nuevos + finalize 3 rondas) → gaps → residuales (pares-solapados-v20.csv) → rebuild con commons coords de todas las imágenes (tools-r3/fetch_commons_missing.py ya ejecutado) y parseo HU «CP Ciudad calle nº» → sidewalk otra vez → texts20.py, ui20, bump, footprints, INFORME, build API offline, run-all.
