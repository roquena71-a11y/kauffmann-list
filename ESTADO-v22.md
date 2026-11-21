# ESTADO v22 — Ampliación con fuentes abiertas de clase 1

**Rama / worktree:** `v22` en `/workspace/kl-v22` (desde `990ddc10`).
**Estado:** **Lote 1 completado y verificado tras auditorías A, B y C (ronda 1)** (pendiente de revisión antes de pasar al Lote 2 / Wikipedia).
**Reglas mantenidas:** solo fuentes clase 1 con licencia abierta verificada; sin copiar biografías (solo campos estructurados, URLs de referencia e inscripciones literales en Grevenbroich/Florencia); nada inventado; exclusión de posiblemente vivas (<110 años sin muerte) en `api/v1/`; familias de licencia separadas; colocación estricta en `_dla`/`_dlo`; las 73.950 placas de v20+v21 (`990ddc10`) se dibujan idénticas.

---

## Resumen del Lote 1 (15 fuentes municipales geolocalizadas con licencia abierta)

| Fuente | Licencia / familia | Entrada | Excluidas | Duplicadas | Probables | Nuevas | Fichas API publicadas | Archivo mapa |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Den Haag (NL) | `CC-BY-4.0` (`cc-by-4`) | 306 | 5 | 15 | 0 | **306** | 15 | `data/denhaag-added-20261121.json` |
| Krefeld (DE) | `dl-de/zero-2-0` (`dl-de-zero`) | 272 | 0 | 90 | 9 | **173** | 157 | `data/krefeld-added-20261121.json` |
| Mönchengladbach (DE) | `dl-de/zero-2-0` (`dl-de-zero`) | 336 | 1 | 156 | 9 | **170** | 0 | `data/moenchengladbach-added-20261121.json` |
| Monza e Brianza (IT) | `CC0-1.0` (`cc0-opendata`) | 166 | 0 | 3 | 1 | **162** | 161 | `data/monza-added-20261121.json` |
| Viersen (DE) | `dl-de/zero-2-0` (`dl-de-zero`) | 135 | 4 | 2 | 7 | **122** | 114 | `data/viersen-added-20261121.json` |
| Firenze (IT) | `CC-BY-4.0` (`cc-by-4`) | 59 | 1 | 24 | 4 | **95** | 94 | `data/firenze-added-20261121.json` |
| Moers GDI-DE (DE) | `dl-de/zero-2-0` (`dl-de-zero`) | 128 | 0 | 70 | 8 | **50** | 50 | `data/moers-added-20261121.json` |
| Xanten (DE) | `dl-de/zero-2-0` (`dl-de-zero`) | 47 | 0 | 2 | 2 | **43** | 40 | `data/xanten-added-20261121.json` |
| Grevenbroich (DE) | `CC0-1.0` (`cc0-opendata`) | 83 | 0 | 40 | 7 | **36** | 35 | `data/grevenbroich-added-20261121.json` |
| Memmingen (DE) | `CC-BY-4.0` (`cc-by-4`) | 129 | 0 | 121 | 1 | **7** | 2 | `data/memmingen-added-20261121.json` |
| Erkrath (DE) | `dl-de/zero-2-0` (`dl-de-zero`) | 6 | 1 | 0 | 1 | **4** | 0 | `data/erkrath-added-20261121.json` |
| Dresden (DE) | `dl-de/by-2-0` (`dl-de-by`) | 419 | 2 | 392 | 22 | **3** | 0 | `data/dresden-added-20261121.json` |
| Dormagen (DE) | `dl-de/zero-2-0` (`dl-de-zero`) | 39 | 0 | 32 | 5 | **2** | 0 | `data/dormagen-added-20261121.json` |
| Aachen (DE) | `dl-de/by-2-0` | 96 | 0 | 94 | 2 | **0** | 0 | *(sin archivo nuevo: 100% cubierta)* |
| Schwalmtal (DE) | `dl-de/zero-2-0` | 7 | 0 | 7 | 0 | **0** | 0 | *(sin archivo nuevo: 100% cubierta)* |
| **TOTAL LOTE 1** | **4 familias abiertas** | **2.228** | **14** | **1.048** | **78** | **1.173** | **668** | **13 archivos nuevos** |

**Totales del mapa:**
- `data/stones.json` (ODbL, OSM + Wikidata): **72.110** (DE: 65.830)
- `v21` añadidos (`berlin` 290 `cc-by`, `koeln` 1.550 `dl-de-zero`): **1.840** (DE: 1.840)
- `v22` Lote 1 (13 fuentes): **1.173** (DE: 610, NL: 306, IT: 257)
- **Total en mapa:** **75.123** placas (DE: 68.280, NL: 1.590, IT: 731).

**Notas de normalización y desglose:**
- **Den Haag (`pipeline/denhaag_names.py`):** 306 entidades GIS → 5 filas no personales excluidas; desdobladas filas multi-persona explícitas solo por `,`, `+` o `\s+en\s+` (nunca dentro de `Henriette`/`Helena`); eliminados sufijos de título web (`| Erelijst...`, `| Oorlogsgravenstichting`, `- Nationaal Monument...`, `? Dokin`); extraído `(born 14 December 1929)` al campo `b` (`dh-193`) → 321 candidatos individuales: 15 duplicados + **306 nuevas**.
- **Mönchengladbach:** invertidos los sufijos de título (`Vogel, Kurt, Dr.` → `Dr. Kurt Vogel`).
- **Firenze:** las 58 placas no colectivas se desglosan por persona a partir de los bloques estructurados de `trascrizione` (123 candidatos individuales, con su fecha de fallecimiento `d` cuando figura en la piedra, p. ej. `fi-328705` `1944-01-20`): 24 duplicados individuales (incluidos los 5 hermanos Calò `fi-330786`) + 4 probables + **95 nuevas**.
- **Deduplicación:** plegado Unicode NFD y apóstrofos (`fi-330786`), variantes `ij`/`y` (`dh-18`), `stein_id` de Dresden (`dr-1119`), conjunto de apellidos de soltera/casada (`mm-29`), alias entre paréntesis/coma (`kr-96`), años de nacimiento en inscripción (`mo-392`), reordenación de nombres (`mm-88`).

### Exclusiones documentadas del Lote 1 (14 registros)
- **Den Haag (5):** `Non Actief`, 3 URLs sueltas sin persona y 1 título de blog.
- **Viersen (4):** registro de prueba `bbbb aaaa`, colectivo anónimo (`ca. 6500 unbekannte Arbeiter`), Stolperschwelle (`441`) y entrada colectiva/desubicada `Familie Abraham` (`301`).
- **Dresden (2):** `DHMD Kopfstein` y `Stolperschwelle Alter Leipziger Bahnhof`.
- **Mönchengladbach (1):** `Stolperschwelle` (`OBJECTID 99`).
- **Firenze (1):** memorial colectivo `Ospizio Israelitico Ospedale` (`#23`).
- **Erkrath (1):** colectivo `Alte und behinderte Frauen` (`395`).

### Fuentes de clase 1 comprobadas pero descartadas o diferidas para Lote 2+
- **Wikipedia (`de.wikipedia.org`, `CC BY-SA 4.0` + ToU Wikimedia):** **Diferida al Lote 2.** Ya descargadas las 2.285 páginas en `/workspace/v22-data/raw/wp_de_pages.jsonl` (68,1 MB; ~44.689 `{{Coordinate}}`, ~6.390+ a >80 m de placas existentes).
- **Duisburg** (`cc-by-de/3.0`) y **Essen** (`dl-by-de/2.0`): servidores inalcanzables (TLS EOF / 504).
- **Kiel** (`cc-by/4.0`): WFS `ims.kiel.de` en mantenimiento (`Wartungsarbeiten`).
- **Soest** (`dl-by-de/2.0`): JSON 404 en `opendata.soest.de`.
- **Elmshorn** (`cc-by/4.0`): CSV/GeoJSON sin nombres de personas ni calles.
- **Penzberg** (`cc-by/4.0`): CSV sin coordenadas (25 filas, 17 ya en `stones.json`).
- **Eindhoven** (NL): excluida por contradicción de licencia en la ficha (`Publiek domein` vs `Copyright Stichting 18-september`).

---

## Colocación y pruebas verificadas (Lote 1)
- **Extractos OSM (`near/`):**
  - `/workspace/v22-data/near/DE-batch1.pkl` (`2026-11-18T21:21:02Z`, 334.107 edificios incl. relaciones `multipolygon`, 105.741 vías con `width`/`est_width`/`sidewalk*`).
  - `/workspace/v22-data/near/NL-denhaag.pkl` (`2026-11-21T20:00:00Z`, 115.013 edificios incl. relaciones `multipolygon`, 25.328 vías).
  - `/workspace/v22-data/near/IT-batch1.pkl` (`2026-11-20T21:21:21Z`, **232.412 edificios** incl. relaciones `multipolygon` vía `osmium` `area()`+`way()`, **128.596 vías**).
- **Colocación (`/workspace/v22-data/scripts/place_batch1.py`):** 705/705 grupos resueltos (`702` `strict`, `2` `facade_exempt`, `1` `linear_strip` para `fi-329393_1..5` en acera estrecha de Via dei Macci 59; `0` excepciones >25 m, `0` calzada; desplazamiento máximo `hav() = 23,6005 m` en `xa-164`).
- **Pipeline:** `python3 -m unittest discover -s pipeline/tests -t .` (**63 tests OK**), `python3 -m pipeline build --strict --offline --sources ...` (**7 familias**, **181.669 fichas**, **10.418 archivos**), `python3 -m pipeline validate` (**0 errores**, 4 avisos de tamaño >1 MB en `cc0`/`odbl`), `REQUIRE_OAV=1 tests/ai-door-check.py` (**0 errores**, 4.519 archivos `find/`, 733.934 filas comparadas), `tests/ai-sim.py` (**20/20** en seed 1 y seed 2).
- **Navegador / Render (`bwrap` bloqueando `kl-contador` / `workers.dev`, entorno venv limpio, sin omisiones):**
  - `tests/run-all.sh`: **OK** completo (`FALLOS: ninguno` en `country-buttons-check.py`, `v22-added-test.cjs` OK, `v21-v20-render-compare.py` OK, `v21-new-render-placement.py` OK, `sidewalk-render-check`, `sidewalk-render-check20`, `map2d-check`, `country-row-check`, `disc-card-check`, `attribution-check`, `version-test` v23).
  - `tests/v22-render-compare.py` contra `990ddc10`: **73.950 placas existentes con `moved=0 ang_only=0`**, **1.173 nuevas clavadas a `dla`/`dlo` (`pin_fail=0`)**.
  - `tests/v22-new-render-placement.py`: **1.173 nuevas comprobadas en Playwright** frente a geometría OSM completa (incluidas relaciones `multipolygon`) → `stacked=0 inside=0 col<0.5=0 road=0 gap_old=0 gap_new=0 over25=0 grid_fail=0`.

---

## Próximo paso (tras auditoría del Lote 1)
1. **Lote 2 — Listas de Wikipedia (`de.wikipedia.org`):** procesar `/workspace/v22-data/raw/wp_de_pages.jsonl` (ya descargadas 2.285 páginas), extraer filas estructuradas con `{{Coordinate}}` (solo hechos factuales permitidos por Wikimedia ToU: nombre, dirección, coordenadas, fechas, enlace al artículo; nunca prosa), dedupe estricto contra las 75.123 placas ya presentes (73.950 + 1.173 del Lote 1), colocar según reglas v20/v21, añadir fuente/familia separada si procede y pruebas.
