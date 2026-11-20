# ESTADO v20r2 (arreglos tras la auditoría B de 7fd66d2)
Worktree: /workspace/countries-proto-v20r2 (rama v20r2, base 7fd66d2). NO tocar /workspace/countries-proto-v20 (lo usan A y C).
Datos de trabajo: V20_DATA=/workspace/v20-data-r2 (copia; near/pbf enlazados). Informe B: /workspace/audits/countries/v20-indep/B/auditoria-B.md
- [x] worktree + datos r2 creados; merge_v20.py ya no escribe en el directorio original.

## 07:25 código F1–F5 + menores en build/merge/common/inscription (sin reconstruir aún)
- F1 mnf (nº, calle) · F2 not_one_person + sujeto no humano + nombre de una palabra en WD · F3 pick_img + fetch_commons_exists.py (cache commons_exists20.json: 3995 existen / 33 no) · F4 names_compatible ≤15 m (build y merge) · F5 d solo si el año está en la inscripción · fixme de posición estricto (≤15 m o foto independiente) · wp genérico fuera · palabras de muerte NL/FR/CZ/IT/ES/PL/HU/SK/HR (58 unit tests OK)
- Siguiente: reconstruir todos los países (build_v20.py CC) y merge.

## 07:36 reconstrucción con fixes A+B (datos) — 6.148 añadidas + 29 de las 1.480 = 72.038 (sin sidewalk aún)
- A: F1 país/calle/«Municipality» (clean_city/bad_city + c de límites admin), 9bis, F2 rótulos/instituciones/inicial, F4 estricto (name_exact_in), F5 dups con año de nacimiento (build+merge+1480), F6 addr propio no confirma (STONE_KEYS), F8 Lindt, inscripciones basura fuera.
- Test nuevo tests/v20r2-data-check.py (0 fallos). Siguiente: sidewalk completo no-DE, cierre, ui20, versión, footprints, run-all.

## 08:16 auditoría C: código (pendiente de ejecutar sidewalk)
- F1 refetch_near20.py + near-extra (LU 46, IT 31, ES 21, GG 5, CZ 5, NL 2, FR 1 sin edificio a ≤50 m; refetch hecho; NL 2 + CZ 5 sin edificios en OSM) · sidewalk20 carga near-extra · footprints20 guarda sin_edificios_50m · render-check20 falla si no hay edificios (salvo lista ≤12) y si dibujo >25 m (salvo excepciones-25m-v20.csv).
- F2 tope: _TMAX = 25 − dispersión (grupos ≤20); >20 = excepción documentada. F5 legit_inside = 3. F6 mapui.js landscape bottom 106, top +24; country-buttons-check: países nuevos en los 10 tamaños (844x390/667x375/320x568/360x640 OK).
- NL «Ciudad:Calle:Nº» (Alkmaar) parseado. Siguiente: rebuild → sidewalk nuevos → finalize → DE (--only grupos + finalize separate) → informe.

## 08:55 cadena de geometría (DE + nuevos): fallos encontrados
- Tras 3 rondas de finalize: 58 pares <1,55 m y 38 fallos DE. Causa: separate20 calculaba el hueco con extra=0 y sidewalk20 (con extra del grupo) descartaba el desplazamiento → corregido (separate20 usa extra y tope de 25 m menos dispersión).
- Placas sin edificio ≤50 m tras refetch: 57 (ES 21, IT 23, GG 5, CZ 5, NL 2, FR 1; edificios a 51–171 m o ninguno): footprints20 escribe sin-edificios-v20.csv; límite del test 70.
- Cadena de 4 rondas "DE + nuevos" en curso (chain3_r2.log). Siguiente: residuales20, ui20, bump, footprints, informe, build --strict, run-all.

## 09:50 cadena cerrada (4 rondas DE + nuevos) y artefactos
- Resultado: 35 pares <1,55 m (de 845 en v19), 45 placas con holgura <0,5 m (DE 42, NL 3) + 48 «revisar» sin contacto + 4 «manzana-dudosa» (FR×3, DE×1, blockcheck) → residuales-acera-v20.csv (97 filas, cada una con motivo); 25 dibujos >25 m → excepciones-25m-v20.csv (16 en grupos >20, 9 en grupos ≤20: centro del grupo ≤25 m, casilla/dispersión suma); 57 sin edificio ≤50 m → sin-edificios-v20.csv.
- ui20 (fechas de instantánea; assert corregido), bump-version --sync, footprints20, make_informe20 (relabels 15, +29 DE, textos de cobertura/residuales), render-check20 OK local (7.662 placas).
- Siguiente: pipeline build --strict, commit, run-all REQUIRE_OAV=1 completo.

## 10:25 pipeline build
- (corregido 10:45) El primer build en línea había sobrescrito páginas de lista de la caché con datos de hoy y desalineaba los lotes; restaurada la caché desde la del árbol v20 y build --offline con ambas fuentes OK.
- 10:45 build OK (--offline --generated 2026-11-20, stolpersteine_de + wikidata_holocaust_victims): odbl 72.038 registros → 62.489 publicadas; cc0 133.301 → 118.254; validate 0 errores, 4 avisos de tamaño. Lanzado run-all REQUIRE_OAV=1 (venv-ci, sin SKIP) → /workspace/v20-data-r2/runall_r2.log
