# ESTADO v24 · PASO 2 (alinear grupos con su acera) — rama v24-align, worktree /workspace/kl-v24s2

Base: 6aa2adda (paso 1, v28; pendiente del sí de Carlos, NO publicar). Reglas: sin push, sin contador, no borrar nada.

## Plan
1. Exponer `window.KLGroups` (solo lectura) y volcar grupos/posiciones actuales (v28) → /workspace/v24-data/align/dump-v28.json.
2. `pipeline/tools/align24.py`: por grupo, calle OSM (nombre de la dirección ≤40 m; si no, vía rodada más cercana ≤30 m; si no, peatonal ≤20 m),
   rumbo del tramo, 1 fila (n≤5) / 2 filas (n≤16) / más (grupos enormes) paralelas al bordillo, paso 1,85 m; búsqueda del desplazamiento mínimo
   que cumple: columna (1,2 m) ≥0,5 m de edificios, centro fuera de calzada (exento a ≤6 m de fachada), ≤25 m de cada punto registrado,
   ≥1,55 m de columnas de otros grupos, sin apilar. Si no hay sitio / sin calle / excepción 25 m → se deja como está (contado e informado).
3. `data/align-v24.json` (solo dibujo) cargado DESPUÉS de montar overlays (no toca el presupuesto de 11 500 ms); sobrescribe _dla/_dlo/_ang.
4. Tests: render-compare/placement actualizados (posición esperada = archivo de alineación), nueva prueba global de reglas + histograma de ángulo.
5. v29, run-all completo (venv nuevo, contador bloqueado, caja ociosa), capturas antes/después en /workspace/v24-data/shots-align/.

## Bitácora
- 19:35 KLGroups expuesto (app3d.js). pipeline/tools/dump_groups24.py → /workspace/v24-data/align/dump-v28-raw.json (28 929 grupos base, 75 122 placas, 3 008 añadidas visibles, 143 alias).
- 19:37 pipeline/tools/align24_geo.py (fuentes OSM por placa, STRtree) + pipeline/tools/align24.py (solver). Prueba LU+CZ: 318/318 alineados en 2 s. Ejecución completa r1 en marcha → /workspace/v24-data/align/align-r1.log
- 19:39 align r1 (123 s): 30 228/30 366 grupos alineados (74 097 placas). data/align-v24.json 1,86 MB (620 KB gzip). Cliente KLAlign/applyAlign/startAlign + KLCols.relayout + ?alignoff=1.
- 19:46 tests/v24-align-check.py r1–r2; solver y test documentan las 3 placas «legítimas» (sidewalk-v20.json). r2: 0 reglas incumplidas, 99,67 % <2°.
- **20:16 LA CAJA SE RESTAURÓ a una instantánea de ~19:46**: se perdieron (y se rehacen ahora) el test con empates en nodos, el solver con rumbo coherente en el centro final,
  tests/align_expected.py + render-compare en dos pasadas + esperas KLAlign, la guarda _gi del cliente, LICENCIAS.md, /tmp/v24-ci-venv y los logs r3/r4.
  Resultado medido antes de perderse (r4): 99,96 % <2°, 0 reglas incumplidas, 1 tramo con dos rumbos (resuelto con la búsqueda coherente).
- 20:17 Rehecho tras la restauración: guarda _gi (app3d.js), LICENCIAS.md, solver coherente (r5 en marcha), test con empates, tests/align_expected.py, esperas KLAlign (6 pruebas + v24-plaque), v21-new-render-placement con v20 dibujadas de este cliente. venv de trabajo: /workspace/v24-data/venv-s2.
- 20:21 align r5 (solver coherente, 154 s): 30 225/30 366 grupos (74 089 placas) alineados; sin cambio: 102 sin calle, 28 excepción 25 m, 7 sin hueco, 3 esquina sin posición coherente, 1 legítima en interior. Ángulo cambia >2° en 26 481 grupos; posición >0,1 m en 14 685.
- 20:27 v24-align-check r5 **OK**: 0 apiladas / 0 <1,55 m / 0 edificio / 0 calzada / 0 >25 m / 0 cuadrícula; paralelismo 100,00 % <2° (30 224 <1°, 1 entre 1–2°) frente a 12,55 % en v28; 0 tramos con dos rumbos. Log /workspace/v24-data/align/check-r5.log.
- 20:28 bump-version → v29 (version-test OK); run-all.sh ejecuta tests/v24-align-check.py.
- 20:32 Capturas antes/después (misma cámara) en /workspace/v24-data/shots-align/ (westend, niedenau, eschersheimer, berlin-zimmerstrasse; 0 peticiones al contador). Script /workspace/v24-data/shots-align.py.
