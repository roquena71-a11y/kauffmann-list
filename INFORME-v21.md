# INFORME v21 — Berlín Open Data y Stolpersteine Köln

Preparación en el worktree `/workspace/kl-v21`, rama `v21`, partiendo de `b142fa48` (v20 publicada). **Sin push, sin publicar, sin correr `publicar.yml`.** Zona horaria: Europe/Berlin (CET, UTC+1).

- Inicio: 2026-11-21 09:32:11 CET
- Fin (tests oficiales): 2026-11-21 11:47:46 CET
- Commit local: 2026-11-21 11:49:54 CET (`316362af`)
- Datos de trabajo: `/workspace/v21-data` (no se ha tocado `/workspace/v20-data-r4`)
- `data/stones.json` sigue siendo solo ODbL (72.110 placas OSM + Wikidata). Las listas municipales van en archivos y familias de licencia aparte.

## Licencias (reverificadas el 2026-11-21)

### Berlín (Open Data)
- Ficha CKAN: https://datenregister.berlin.de/api/3/action/package_show?id=liste-der-stolpersteine-berlin
- Catálogo: https://daten.berlin.de/datensaetze/liste-der-stolpersteine-berlin
- `license_id`: `cc-by`. Título: «Creative Commons Attribution». `license_url`: https://opendefinition.org/licenses/cc-by/
- CSV: https://www.stolpersteine-berlin.de/de/stolpersteine-finden/download — archivo `stolpersteine_2026-11-21_09-33-47.csv`, 11.137 filas, sha256 `907f127ac37a98dc6cc666a4ed42cdc210b3be51bc75851091a871d242a7a52c`
- Atribución: Koordinierungsstelle Stolpersteine Berlin, Liste der Stolpersteine Berlin
- Campos usados: nombre, dirección, año de nacimiento, coordenadas. Enlace a biografía cuando el CSV lo trae. **No se copian biografías.**
- Impressum (https://www.stolpersteine-berlin.de/de/impressum), texto literal: «Auf die biografischen Texte haben die bei den Texten genannten Autorinnen und Autoren das Copyright. Ihnen sind alle Rechte auf diese Texte vorbehalten, insbesondere die der Übersetzung, der Sendung im Rundfunk und Fernsehen und der Bereitstellung im Internet.»
- **Duda:** el catálogo no indica si es CC BY 3.0 o 4.0.

### Colonia (Open.NRW / Offene Daten Köln)
- Ficha: https://open.nrw/dataset/stolpersteine-koln-k
- Licencia: Datenlizenz Deutschland – Zero – Version 2.0 (https://www.govdata.de/dl-de/zero-2-0). Texto: «Jede Nutzung ist ohne Einschränkungen oder Bedingungen zulässig.»
- JSON del geoportal: 2.960 entidades, sha256 `d47280ab474ca07899b30a290c16ce832c34336bbe56d16362b9a5b95513f1fd`
- La ficha dice «rund 2.300» / «über 2.400»; el recuento real de esta descarga es 2.960.
- Atribución (no exigida por DL-DE Zero; se indica igual): Stadt Köln / NS-Dokumentationszentrum der Stadt Köln, Stolpersteine Köln
- No se copian biografías de museenkoeln.de / nsdok.de; solo se guarda el enlace que trae el JSON.
- Una entidad sin geometría (id 3319, Gustav Bermel, Melatengürtel 86) ya estaba en OSM y se trató como duplicada; no se geocodificó.

## Cruce contra las 72.110 placas OSM/Wikidata

Criterio: duplicada clara = mismo `name_key` y (≤25 m o misma `addr_key`); probable (no se importa) = mismo nombre a 25–150 m o a ≤30 km; homónimo a más de 30 km = nueva.

| Fuente | Entrada | Duplicadas claras | Probables (fuera) | Nuevas en el mapa |
| --- | ---: | ---: | ---: | ---: |
| Berlín | 11.137 | 10.476 | 277 | **384** |
| Colonia | 2.960 | 1.281 | 114 | **1.565** |
| Total | 14.097 | 11.757 | 391 | **1.949** |

Todas las nuevas traían coordenadas. No se inventan nombres ni fechas (`Geburtsjahr` 0 se omite; 1965 y 1968 se dejan tal cual). 3 placas de Colonia van sin nombre, como en la fuente.

## Colocación (reglas de v20; solo dla/dlo)

- Extracto OSM Berlín+Colonia: timestamp `2026-11-18T21:21:02Z`
- 821 grupos: 551 solo nuevas, 270 mixtos (1.221 placas ya publicadas; `stones.json` no se reescribió)
- 1.534 ajustadas (dla/dlo); 415 se quedan en el punto de origen (sin dla)
- Desplazamientos >25 m: **0**. Máximo: **24,97 m**
- 920 partían dentro de un edificio. Holgura mínima posterior a edificios: 1,53 m (≥0,5 m)
- Berlín: 338/384 con dla. Colonia: 1.196/1.565 con dla
- Archivos: `data/berlin-added-20261121.json`, `data/koeln-added-20261121.json`
- Total en el mapa si se cargan los tres archivos: **74.059**
- El cliente (app3d.js) dibuja las placas ya publicadas como en v20; solo coloca alrededor las municipales nuevas, y no toma el ángulo de calle de grupos que no existían en v20. Así no se mueven las de `stones.json`.

## API (build offline, generated=2026-11-21)

La regla de posiblemente vivas no se ha relajado (sin indicio de muerte y nacimiento hace menos de 110 años, o sin año → no hay ficha).

| Familia | Registros de entrada | Publicadas | Excluidas (posiblemente vivas) |
| --- | ---: | ---: | ---: |
| cc-by (Berlín) | 384 | **279** | 105 |
| dl-de-zero (Colonia) | 1.565 | **0** | 1.565 (el JSON no trae fechas) |
| odbl | 72.110 | 62.519 | 8.906 (más otras políticas) |
| cc0 | 133.301 | 118.254 | 15.047 |
| Total fichas API |  | **181.052** |  |

`pipeline validate`: 0 errores, 4 avisos de tamaño (los de siempre). `data/search/` sigue siendo solo ODbL.

## Cliente

- Versión de caché: `kauffmann-v21-pages` (`tests/bump-version.py`).
- Al cargar tres JSON, `style.load` podía dispararse después de asignar `DATA` y antes de `buildStones()`, y montaba la capa `pts` con datos vacíos. `tryAddOverlays()` espera a `POINTS_FC`/`STONES_FC`/`AGG` y no depende de `map.isStyleLoaded()` (en este Chrome a veces sigue en falso tras cargar el estilo).

## Tests

`tests/run-all.sh` con `REQUIRE_OAV=1` en el venv fresco `/workspace/venv-v21-ci`. Arranque: 2026-11-21 11:09:12 CET. Fin: 11:47:46 CET. Log: `/workspace/v21-data/out/run-all.log`.

- `tests/v21-added-test.cjs`: OK (Berlín 384 + Colonia 1.565, sin colisión con `stones.json`)
- 58 tests unitarios en 5,185 s: OK
- counter/SW, actualizaciones y versión única v21: OK (`kauffmann-v21-pages`)
- `pipeline validate` en el suite: 0 errores de meta/esquema/fila en las cuatro familias; 4.152 archivos `find` validados; 730.859 filas frente a la ficha
- ai-door-check: 0 errores (la familia vacía `dl-de-zero` tiene directorios vacíos y no rompe el chequeo)
- ai-sim: 20/20 correctas × 2 (seed 1 y 2), 0 avisos
- sidewalk v19 y v20: OK (ninguna columna ni chincheta a <0,5 m de un edificio en 9.329 placas; 109 residuales ya documentados)
- mapa 2D: OK (41 chinchetas; el fixture intercepta `data/*-added-*.json` vacío)
- fila de países en el teléfono, ficha Hassall (es/de/en) y atribución: OK, axe 0
- `country-buttons-check.py`: **FALLOS: ninguno** (10 tamaños)
- Resultado oficial: **`run-all: OK` / `EXIT:0`**

No se ha enviado ningún hit a kl-contador ni a `*.workers.dev`. No se ha hecho push ni se ha corrido `publicar.yml`. No se ha borrado nada en la caja.

## API de Colonia: 1.565 placas en el mapa, 0 fichas

El mapa carga las 1.565 placas nuevas de Colonia (`data/koeln-added-20261121.json`). En `api/v1/dl-de-zero/` el build publica **0 personas**. No es un fallo del pipeline: la regla de posiblemente vivas no se ha tocado (`LIVING_YEARS = 110`). Si no hay indicio de muerte y el año de nacimiento falta o es de hace menos de 110 años, no se emite ficha de persona. El mapa sigue mostrando la placa.

El JSON de Offene Daten Köln solo trae `id`, `adresse_original`, `stadtteil`, `name` y `url`. No hay año de nacimiento ni de muerte, así que las 1.565 entran al filtro y salen todas excluidas. En Berlín la misma regla deja fuera 105 de 384 y publica 279, porque el CSV sí trae años de nacimiento (los anteriores a 1916 pasan).

Opciones, **sin inventar datos ni copiar biografías**:

1. **Dejarlo como está** (lo preparado en este worktree). El mapa enseña las 1.565 placas; la API no publica a quien, con los campos disponibles, no se puede descartar como posiblemente viva. Es conservador y coherente con la política vigente.
2. **Si más adelante la fuente abierta incluye fechas** —un campo del propio JSON o CSV de Offene Daten Köln / Open.NRW—, repetir el build de la familia `dl-de-zero` con esos campos. Hoy no los trae.
3. **No raspar** museenkoeln.de / nsdok.de para sacar fechas o textos: esa base no declara licencia abierta; solo se guarda el enlace que ya viene en el JSON.
4. **No tratar «aparecer en una lista de Stolpersteine» como prueba de muerte** sin un cambio de política explícito. Eso relajaría la regla de 110 años para toda la API, no solo para Colonia.

Ninguna de estas opciones rellena años inventados.

## Worktree y commit

- Worktree: `/workspace/kl-v21`, rama `v21`, creada desde `b142fa48` (v20 publicada).
- Commit local (sin push): `316362af884fedb20c9273ec8b3e558d018fa414` (`316362af`), 2026-11-21 11:49:54 CET, padre `b142fa48`. Sin `publicar.yml`.
- `data/stones.json` intacto (72.110, solo ODbL). `data/search/` regenerado con la misma fecha `generated=2026-11-21`, sigue siendo solo ODbL (72.110).

## Dudas (no bloquean la preparación)

- Berlín: el catálogo indica `license_id: cc-by` pero no aclara si es CC BY 3.0 o 4.0.
- Colonia: la ficha habla de «rund 2.300» / «über 2.400»; esta descarga tiene 2.960 entidades.
- Josefine / Josephine Huldschinsky en Ahornallee 50 (Berlín): posible la misma persona con grafía distinta; ante la duda se han dejado las dos (no se ha fusionado) y el cliente ya no desplaza las placas ya publicadas de ese grupo.
