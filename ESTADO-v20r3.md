# ESTADO v20r3 (rama v20r3 desde 87215e2; datos V20_DATA=/workspace/v20-data-r3; servidor local 8913)
Auditorías ronda 2 sobre 87215e2: A FAIL menor, B PASS con avisos, C FAIL. Tareas: C (13 centros dentro, 4 calzada, grupos por calle sin número, CSV de pares, padding), A (c='CZ', no-personas, tags OSM en inscripciones, 72 WD pendientes, fusiones >50 m, INFORME), B (1480 estado, textos públicos, b/d no fecha, Echternach, Sr./Jr., NO portal). Luego run-all REQUIRE_OAV=1 completo + build offline API. Sin push, sin auditorías.

## 12:25 worktree + datos r3 creados (cp de r2, rutas reescritas)

## 12:55 C (código) hecho: groups_of/app3d (calle sin número ⇒ 8 m), solve_relaxed en sidewalk20, sidewalk-facade20.json (3 grupos), DE/FR/NL --only recalculados (DE revisar → 0). Pendiente: datos A/B, rebuild, sidewalk nuevos, finalize, tests C (centro dentro, pares CSV, padding).
