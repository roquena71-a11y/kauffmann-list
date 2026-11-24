# ESTADO v25 — datos (fechas en conflicto y fotos)

Worktree `/workspace/kl-v25-data`, rama `v25-data` desde `3e46ab52` (v29 en vivo).
No se toca el render 3D (`/workspace/kl-v25-review`, rama `v25-corners`).
No se publica, no hay push a main, no se borra nada, no se pega al contador.
CPU con `nice -n 19`.

## A · Fechas en conflicto (hecho, listo para revisión)

Caso de Carlos: Anna Mayer, Steinheimer Str. 4, Seligenstadt (`n13186756540`, `src=osm+wd`, persona Wikidata `Q105371628`). Inscripción «JG. 1870»; campo estructurado `b=1876-01-09`. La muerte coincide (`Tot 11.10.1942` = `1942-10-11`).

Auditoría de las 75.122 placas del mapa (stones.json + listas municipales). CSV: `/workspace/v24-data/review/fechas-conflicto.csv` (2.435 filas). Sidecar de la ficha: `data/date-conflicts-v25.json` (2.351 placas). No se tocan `la`/`lo`. No se reescribe `stones.json`.

**Choques de año** (el año de la inscripción ≠ el año del dato estructurado):

| Campo | Total | osm | wd | osm+wd | city |
|---|---:|---:|---:|---:|---:|
| Nacimiento | 1.156 | 306 | 180 | 670 | 0 |
| Muerte | 796 | 52 | 314 | 430 | 0 |
| Deportación | 0 | — | — | — | — |

Hay 1.893 placas con al menos un choque de año. La deportación no tiene campo estructurado en el mapa, por eso va a 0.

**Mismo año, distinta fecha completa** (también en el CSV y en el sidecar): nacimiento 3, muerte 480 (4 de ellas municipales). Ejemplos típicos: `10.12.1941` en la placa frente a `1941-10-12` en el dato (día y mes intercambiados).

Notas, sin inventar:

- De los 796 choques de año en la muerte, **508 tienen `d=1940`** y la inscripción dice otra cosa (tot/ermordet 1942, 1943, 1944…). El 1940 estructurado es sistemático y no se elige en silencio.
- En el nacimiento, 601 de 1.156 se apartan en un solo dígito, 65 en 100 años (p. ej. 1875 vs 1975), 45 son anagramas (p. ej. Jg. 1983 vs 1893). Son choques reales, no errores del recuento.
- La API (`pipeline/adapters/stones.py`) ya prefería la inscripción en el nacimiento; ahora hace lo mismo con la muerte y guarda el otro valor en `variants`.
- La ficha del mapa carga el sidecar y muestra la fecha de la inscripción como principal, con «otra fuente: 1876-01-09 (Wikidata o OpenStreetMap)». En `osm+wd` no podemos afirmar con certeza si el dato estructurado salió de OSM o de Wikidata, por eso la etiqueta es honesta.

Pruebas: `python3 -m unittest pipeline.tests.test_pipeline` — 48 tests, OK.

## B · Fotos (inventario hecho; créditos Commons en curso)

Inventario exacto, de consultas reales a datos locales (no se ha usado Overpass; OSM DE sigue sin extracto local):

- 75.122 registros, 53.587 con `img`, 21.535 sin foto (el recuento visible de la revisión, sin alias, era 21.503 sin foto).
- Wikidata P18 (CSV SPARQL 24-nov-2026): **970** placas sin foto con archivo (392 filas solo-categoría, omitidas).
- `imgx` ya en nuestros datos: **311** URLs de Commons; **21** omitidas por no ser Commons (p. ej. stolpersteine-bamberg.de, erport-do.de).
- OSM `wikimedia_commons`/`image` fuera de DE (extractos v20 + FI/JE/RO/SE): **358** placas sin foto con archivo Commons (405 no-Commons omitidas, p. ej. stolpersteine-salzburg.at; 15 categorías omitidas). 351 quedan solo en esta fuente.

**Unión legal: 1.632 placas** (no 1.650: la revisión anterior contó como Commons las 21 `imgx` que no lo son, y hubo un solape distinto). Por origen exclusivo: P18 970, imgx 311, OSM no-DE 351. Por el nombre del archivo: 1.331 parecen foto de la placa, **301** se marcan como posiblemente retrato o casa (no se ocultan; la ficha lo dice).

Aplicación: sidecar `data/photos-added-v25.json` (no se reescribe `stones.json`, no se tocan `la`/`lo`). El cliente asigna `img` solo si faltaba.

Ficha: si no hay foto, «Sin foto todavía». Si hay, se pide autor y licencia (créditos Commons) y, si el nombre del archivo no habla de la placa, un aviso honesto.

**Créditos Commons:** `pipeline/tools/fetch_commons_credits.py` consulta 52.191 nombres únicos (los ya mostrados + los 1.632 nuevos), en lotes de 40, User-Agent con la URL del proyecto, 0,45 s entre lotes, caché en `/workspace/v24-data/review/commons-extmetadata.json`. Salida prevista: `data/photo-credits-v25.json` (se carga solo al abrir una ficha, no en la carga inicial). En curso al escribir esto.

## Pendiente

- Terminar la descarga de créditos y generar `data/photo-credits-v25.json`.
- Decisión de Carlos: ¿se ocultan las 301 fotos que no parecen de la placa, o solo se avisa?
- OSM Alemania: sigue sin extracto; no se ha inventado ninguna foto de ahí.
- No publicar hasta su sí y las 3 auditorías.

## Archivos tocados (repo)

- `pipeline/inscription.py` — extractor de fechas de la inscripción.
- `pipeline/adapters/stones.py` — conflicto de muerte igual que el de nacimiento.
- `pipeline/tools/date_conflicts.py`, `photo_sources.py`, `fetch_commons_credits.py`.
- `pipeline/tests/test_pipeline.py`.
- `data/date-conflicts-v25.json`, `data/photos-added-v25.json`.
- `app3d.js` — solo ficha (fechas, foto, créditos). No se toca el render 3D.
- `ESTADO-v25-data.md`.
