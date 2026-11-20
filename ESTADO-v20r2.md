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
