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

**Unión legal confirmada en Commons: 1.621 placas** (la revisión anterior estimó 1.650). Desglose:

- Candidatos locales: 1.632 (P18 970 + imgx Commons 311 + OSM no-DE 351; se omitieron 21 `imgx` y 405 OSM que no son Commons, y 15 categorías).
- La API de Commons confirmó 1.621. Se omitieron 11 nombres que no existen (etiquetas OSM rotas o archivo borrado; los 11 eran de OSM fuera de DE).
- Por origen exclusivo final: P18 970, imgx 311, OSM no-DE 340.
- Por el nombre del archivo: 1.322 parecen foto de la placa, **299** se marcan como posiblemente retrato o casa (no se ocultan; la ficha lo dice).

Aplicación: sidecar `data/photos-added-v25.json` (no se reescribe `stones.json`, no se tocan `la`/`lo`). El cliente asigna `img` solo si faltaba.

Ficha: si no hay foto, «Sin foto todavía». Si hay, autor y licencia (créditos Commons, carga perezosa al abrir la ficha) y, si el nombre del archivo no habla de la placa, un aviso honesto.

**Créditos Commons (terminado, 0 fallos de red):** 52.191 nombres únicos consultados el 24-nov-2026 a las 03:52 Europe/Berlin. 51.563 con autor, 51.564 con licencia. Licencias más frecuentes: CC BY-SA 4.0 (23.987), CC BY-SA 3.0 (16.663), CC0 (5.740), CC BY-SA 3.0 de (3.415). Archivo `data/photo-credits-v25.json` (7,7 MiB; se carga solo al abrir una ficha). Caché de trabajo en `/workspace/v24-data/review/commons-extmetadata.json`.

**Dato ya publicado, no se ha cambiado:** 680 placas que *ya* tenían `img` apuntan a un archivo que hoy no está en Commons (626 nombres únicos; p. ej. archivos borrados o renombrados). No se ha tocado `stones.json`. Carlos puede decidir si se ocultan y se muestra «Sin foto todavía».

## Pendiente / decisiones de Carlos

- ¿Se ocultan las 299 fotos nuevas que no parecen de la placa, o solo se avisa? (ahora solo se avisa.)
- ¿Se ocultan las 680 fotos ya publicadas cuyo archivo ya no está en Commons?
- OSM Alemania: sigue sin extracto local; no se ha inventado ninguna foto de ahí.
- No publicar hasta su sí y las 3 auditorías.

## Archivos tocados (repo)

- `pipeline/inscription.py` — extractor de fechas de la inscripción.
- `pipeline/adapters/stones.py` — conflicto de muerte igual que el de nacimiento.
- `pipeline/tools/date_conflicts.py`, `photo_sources.py`, `fetch_commons_credits.py`.
- `pipeline/tests/test_pipeline.py`.
- `data/date-conflicts-v25.json`, `data/photos-added-v25.json`.
- `app3d.js` — solo ficha (fechas, foto, créditos). No se toca el render 3D.
- `ESTADO-v25-data.md`.

## 24-11-2026 19:10– (hora de Berlín) — v34: v25-data sobre v33 (f510fbb2, en vivo)
Rama NUEVA `v25-fotos-fechas` desde f510fbb2, worktree `/workspace/kl-v25-fotos`; ba90a7ca y 86809db7 copiados con cherry-pick
(63cf96ea, 72e2deaf; v25-data no se reescribe). Conflicto en app3d.js resuelto conservando la limpieza de marcado de v33 (plainTxt).
Decisiones de Carlos (24-11-2026 19:10): las 299 fotos nuevas que parecen retrato o casa → «Muéstralas con aviso»;
las 680 fotos publicadas cuyo archivo ya no está en Commons → «Déjalas como están» (ni ocultar ni «Sin foto todavía»).
Cambios respecto a v25-data:
- Sidecars (fechas, fotos) perezosos: se piden en paralelo pero no retrasan el mapa; ficha y búsqueda esperan a tenerlos
  (nunca se elige una fecha en silencio). Las fotos se aplican DESPUÉS de la fusión de duplicados (no cambian qué registro
  es el principal); si el registro es un alias, la foto pasa al principal si este no tiene.
- Aviso SOLO en las 299 fotos añadidas cuyo nombre no habla de la placa (v25-data lo ponía también en 4.167 fotos ya publicadas).
  Texto: «Aviso: puede que esta foto no muestre la placa (quizá es un retrato o la casa).» (es/de/en), recuadro ámbar, contraste 10,97:1.
- Sin foto: como antes (nada); se quitó «Sin foto todavía».
- Créditos: autor · licencia (data/photo-credits-v25.json, solo al abrir una ficha con foto). Si el archivo no tiene crédito en
  Commons (las 680 + 1 sin licencia), el pie queda como antes.
- Versión v34 (kauffmann-v34-pages). Prueba nueva tests/v34-photos-dates-check.py (en run-all). Capturas: /workspace/v24-data/shots-v34/
