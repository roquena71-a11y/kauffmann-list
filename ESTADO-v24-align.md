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
- 20:23 v24-align-check r5 **OK**: 0 apiladas / 0 <1,55 m / 0 edificio / 0 calzada / 0 >25 m / 0 cuadrícula; paralelismo 100,00 % <2° (30 224 <1°, 1 entre 1–2°) frente a 12,55 % en v28; 0 tramos con dos rumbos. Log /workspace/v24-data/align/check-r5.log.
- 20:23 bump-version → v29 (version-test OK); run-all.sh ejecuta tests/v24-align-check.py.
- 20:24 Capturas antes/después (misma cámara) en /workspace/v24-data/shots-align/ (westend, niedenau, eschersheimer, berlin-zimmerstrasse; 0 peticiones al contador). Script /workspace/v24-data/shots-align.py.
- 20:24 run-all completo lanzado (venv nuevo /workspace/v24-data/venv-runall-align, bwrap con hosts del contador bloqueados, carga 1,0) → /workspace/v24-data/run-all-align.log
- 20:30 run-all #1 FALLÓ en sidewalk-render-check20: 'chincheta 2D a menos de 0,5 m de una huella' (156 no documentadas). El solver solo respetaba la columna 1,2 m; la chincheta 2D (12 px a z19 ≈ 1,15 m de semilado en DE) exige centro ≥ semilado+0,5 m. Arreglo: regla de chincheta en align24.py (PIN_PX_HALF=6, +0,53 m); grupos cuya chincheta ya estaba justa en v28 se dejan sin cambio. Repetir r6 + check con la regla en v24-align-check.
- 20:36 r6 (regla estricta de chincheta) dejaba 7 899 grupos sin cambio (en v28 la chincheta ya estaba a <semilado+0,53 m con la geometría OSM actual en 8 167 placas) → r7: umbral POR PLACA = min(semilado+0,53, distancia que tenía en v28) (nunca más cerca que en v28). r7: 30 220 grupos / 74 059 placas alineados; sin cambio 102 sin calle, 28 exc. 25 m, 12 sin hueco, 3 esquina, 1 legítima. Comprobando sidewalk-render-check20 + v24-align-check (con regla de chincheta).
- 20:47 r7: sidewalk-render-check20 OK (9 329 placas; 21 residuales documentados usados) · v24-align-check OK (0 reglas, chincheta2D=0 con tolerancia de cuantización 1,5 cm por el redondeo a 1e-7°; paralelismo 100 % <2°; 0 tramos con dos rumbos). Logs check-r7b.log, sw20-r7.log. Rehaciendo capturas y luego run-all #2.
- 20:55 capturas rehechas con r7 (0 peticiones al contador). run-all #2 lanzado y PARADO al momento: otro agente está ejecutando run-all en /workspace/kl-v24 (desde 20:54, puerto 8899, venv /tmp/v24-publish-venv); no se toca. Se espera a que termine para tener la máquina libre (venv-runall-align2 quedó a medias: no se usa).
- 21:32 Paso 1 publicado (origin/main = 6aa2adda). Máquina libre (carga 1,2, sin otras pruebas). run-all #3 lanzado (venv nuevo venv-runall-align3, contador bloqueado con bwrap) → /workspace/v24-data/run-all-align3.log
- 21:42 run-all #3 en marcha: hasta ahora OK (unittest, ai-door/ai-sim, sidewalk, sidewalk20, v21-v20-render-compare [sin/con alineación], v21-new-render-placement).
- 21:52 run-all #3: también OK v22-render-compare (sin/con alineación), v22-new-render-placement, v24-align-check, fila de países, Hassall; sigue (attribution-check, luego country-buttons ~20 min).
- 21:53 run-all #3 FALLÓ en attribution-check (390x844, ficha abierta: '#detail' no se abre en 20 s tras buscar 'Moses'); todo lo anterior OK. Investigando (¿carrera con la carga de align-v24.json?).
- 22:08 attribution-check suelto (venv align3, contador bloqueado): OK 2/2 (attr-1.log, attr-2.log). La ficha se abre por JS y nada de la alineación toca #detail (applyAlign solo recalcula dla/dlo/ang + relayout + refreshSel); parece intermitente. run-all #4 lanzado (venv nuevo venv-runall-align4) → run-all-align4.log; si repite el fallo se investiga a fondo.
- 22:22 Reanudado tras interrupción: run-all #4 sigue vivo (no se relanza). Hasta ahora OK: node/unit, contador/sw/versión v29, sidewalk, sidewalk20, map2d; en marcha v21-v20-render-compare.
- 22:40 run-all #4: OK también v22 compare/placement, v24-align-check, attribution-check (esta vez OK; el fallo de #3 fue intermitente), v23 UX y presupuesto de carga (overlays 9 564 ms ≤ 11 500; fcp 188, dcl 925, overview 5 383, vis 10 138). En marcha v24-plaque-contrast; falta country-buttons (~20 min).
