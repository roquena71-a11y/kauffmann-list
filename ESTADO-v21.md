# ESTADO v21 (rama v21 desde b142fa48; worktree /workspace/kl-v21; datos /workspace/v21-data)

Tarea: preparar (SIN push, SIN publicar, SIN correr publicar.yml) la importación de dos fuentes abiertas: Berlín Open Data CSV (CC BY; solo campos de la lista, NO biografías de stolpersteine-berlin.de) y Köln Open.NRW JSON (DL-DE Zero 2.0). Reverificar licencias en esta sesión. Deduplicar contra OSM/Wikidata. Colocar solo piedras genuinamente nuevas con las reglas de v20. Familias de API `cc-by` y `dl-de-zero` separadas. Tests con REQUIRE_OAV=1. No enviar visitas a kl-contador / *.workers.dev. No borrar nada en la caja.

Inicio de esta sesión: 2026-11-21 09:32:11 CET (Europe/Berlin).

## 09:32 Arranque
- Worktree creado: `git -C /workspace/countries-proto-v20 worktree add -b v21 /workspace/kl-v21 b142fa48`
- HEAD: b142fa48 (igual que v20r4 publicada)
- Datos de trabajo: /workspace/v21-data (nuevo; no se toca /workspace/v20-data-r4)

## Pendiente
1. Reverificar licencias en las fichas oficiales y guardar texto + URL + atribución.
2. Descargar CSV Berlín y JSON Köln.
3. Normalizar, deduplicar, listar solo nuevas.
4. Colocar (dla/dlo), país por OSM is_in, geocodificar solo con OSM/datos abiertos si faltan coordenadas.
5. Actualizar LICENCIAS.md, textos Acerca de (es/de/en), API/llms/tests.
6. run-all.sh REQUIRE_OAV=1 en venv fresco desde tests/requirements-ci.txt.
7. Informar cifras, colocación, tests, worktree/commit y dudas de licencia.

## 09:44 Licencias verificadas y cruce de duplicados (sin publicar)

**Inicio de sesión:** 2026-11-21 09:32:11 CET.

### Licencias (reverificadas en esta sesión)
- **Berlín:** CKAN `license_id=cc-by`, `license_title=Creative Commons Attribution`, `license_url=https://opendefinition.org/licenses/cc-by/` (ficha https://datenregister.berlin.de/api/3/action/package_show?id=liste-der-stolpersteine-berlin; catálogo https://daten.berlin.de/datensaetze/liste-der-stolpersteine-berlin). CSV: https://www.stolpersteine-berlin.de/de/stolpersteine-finden/download (archivo `stolpersteine_2026-11-21_09-33-47.csv`, 11.137 filas, sha256 `907f127ac37a98dc6cc666a4ed42cdc210b3be51bc75851091a871d242a7a52c`). Autor del dataset: Koordinierungsstelle Stolpersteine Berlin.
  - **Duda de licencia:** el catálogo no indica versión de CC BY (3.0 vs 4.0); solo «Creative Commons Attribution» + opendefinition.org/licenses/cc-by/.
  - Impressum (https://www.stolpersteine-berlin.de/de/impressum), texto literal: «Auf die biografischen Texte haben die bei den Texten genannten Autorinnen und Autoren das Copyright. Ihnen sind alle Rechte auf diese Texte vorbehalten, insbesondere die der Übersetzung, der Sendung im Rundfunk und Fernsehen und der Bereitstellung im Internet.» No se copian biografías; solo el enlace de la columna del CSV (campo `lb`) cuando existe.
- **Colonia:** Open.NRW https://open.nrw/dataset/stolpersteine-koln-k y Offene Daten Köln (distribución JSON) «Lizenz: Datenlizenz Deutschland – Zero – Version 2.0» (https://www.govdata.de/dl-de/zero-2-0, DCAT `http://dcat-ap.de/def/licenses/dl-zero-de/2.0`). JSON oficial del geoportal: 2.960 entidades (sha256 `d47280ab474ca07899b30a290c16ce832c34336bbe56d16362b9a5b95513f1fd`). La ficha dice «rund 2.300» / otra «über 2.400»; el recuento real del JSON de esta sesión es 2.960. Una entidad (`id` 3319, Gustav Bermel, Melatengürtel 86) no trae geometría; ya estaba en OSM y se clasificó como duplicada (no se geocodificó). Las URLs a museenkoeln.de/nsdok.de se guardan solo como enlace; no se copia esa base (clase 2).

### Cruce (contra 72.110 placas OSM/Wikidata; script `/workspace/v21-data/scripts/normalize_dedupe.py`)
| Fuente | Entrada | Duplicadas (clara) | Probables (no se importan) | Nuevas |
| --- | ---: | ---: | ---: | ---: |
| Berlín | 11.137 | 10.476 | 277 | **384** |
| Colonia | 2.960 | 1.281 | 114 | **1.565** |
| Total a colocar |  |  |  | **1.949** (todas con coordenadas) |

Las 277+114 probables quedan fuera (mismo nombre a 25–150 m, o a ≤30 km). Los homónimos a más de 30 km sí entran como nuevas. No se inventan nombres ni fechas (Geburtsjahr 0 se omite; 1965 y 1968 se conservan tal cual). 3 placas de Colonia van sin nombre (así en la fuente).

### Siguiente
Colocar las 1.949 (dla/dlo, reglas v20; familias de API separadas; textos; tests). Sin push.

## 10:03–10:05 Colocación (dla/dlo)

- Extracto OSM de Berlín+Colonia: `/workspace/v21-data/near/DE-berlin-koeln.pkl` (timestamp `2026-11-18T21:21:02Z`, el mismo PBF que v20). El `DE.pkl` de v20 no cubría direcciones nuevas.
- 821 grupos (551 solo nuevas, 270 mixtos con 1.221 placas ya publicadas). Las placas de `stones.json` no se reescribieron.
- 1.534 ajustadas (dla/dlo); 415 en origen (sin dla). `move_gt_25 = 0`; máximo 24,97 m. 920 partían dentro de un edificio. Holgura mínima posterior a edificios: 1,53 m.
- Por fuente: Berlín 338/384 con dla; Colonia 1.196/1.565 con dla.
- Archivos del mapa (en el repo, sin mezclar con stones.json): `data/berlin-added-20261121.json` (384), `data/koeln-added-20261121.json` (1.565). Total en el mapa si se cargan: 74.059.

## 10:07 API (offline, --strict, generated=2026-11-21)

- Familias: `cc-by` 384 → 279 publicadas (105 excluidas por posiblemente vivas: nacimiento hace <110 años y sin indicio de muerte). `dl-de-zero` 1.565 → **0 publicadas** (la fuente de Colonia no trae año de nacimiento ni de muerte; la regla de 110 años las deja todas fuera). `cc0` 118.254 y `odbl` 62.519 se mantienen. Total API: 181.052 fichas.
- `data/search/` y `data/stones.json` siguen siendo solo ODbL (72.110). validate: 0 errores, 4 avisos de tamaño (los de siempre en cc0/odbl hirsch y ids).
- No se inventan fechas ni se copian biografías para «salvar» esas exclusiones.

## Pendiente al cierre de esta fase
- bump-version.py 20→21; INFORME-v21.md; tests/run-all.sh con REQUIRE_OAV=1 en venv fresco; commit local (sin push).

## 10:11–10:22 Tests y colocación en el cliente

- bump-version a v21. venv fresco: `/workspace/venv-v21-ci`.
- `tests/v21-added-test.cjs` OK (384+1.565, sin colisión). unit tests 58 OK. ai-door-check 0 errores (REQUIRE_OAV=1). ai-sim 20/20 ×2.
- `sidewalk-render-check20` falló: al añadir placas nuevas a 270 grupos mixtos, el cliente rehacía la cuadrícula de las ya publicadas (p. ej. Clara Berkowitz, Erna Putziger, Gertrud Lisbeth Heller) y alguna placa vecina rotaba el ángulo de un grupo que no había cambiado (Pestalozzistraße).
- Un primer arreglo (usar dla del servidor en todos los grupos «pinned») rompió placas que en v20 el cliente había recolocado bien (Erna Moritz, Gertrud Herrmann, Julie Bernstein sobre la calzada). Revertido en espíritu.
- Siguiente: en grupos sin placas nuevas, dejar la cuadrícula y el ángulo exactamente como en v20; en grupos mixtos, colocar solo las nuevas alrededor de las existentes, sin mover las de `stones.json`. Sin push.


## 10:23–11:09 Cliente y tests intermedios

- En grupos sin placas municipales nuevas, la cuadrícula y el ángulo son los de v20 (los vecinos nuevos no rotan la calle). En grupos mixtos, las de `stones.json` se colocan como en v20 y solo las nuevas se sientan alrededor, sin mover las ya publicadas. Los grupos con placas existentes no se desplazan por culpa de un grupo solo-nuevo.
- `sidewalk-render-check.py` y `sidewalk-render-check20` OK (9.329 placas, 109 residuales documentadas).
- `map2d-check.py`: el fixture de 41 placas (IE/SE/JE/FI/RO) ahora intercepta también `data/*-added-*.json` (vacío), porque el mapa 2D carga Berlín y Colonia.
- Al cargar tres JSON, `style.load` podía montar `pts` antes de `buildStones()` (GeoJSON indefinido) y, con `isStyleLoaded()` a veces en falso, las capas no se añadían. `tryAddOverlays()` espera a `POINTS_FC`/`STONES_FC`/`AGG` y reintenta. El recorrido de países (incl. DE en 320×568) dejó de caer el renderer.
- `country-buttons-check.py` en solitario: **FALLOS: ninguno** (10 tamaños).
- Versión de caché: `kauffmann-v21-pages`.

## 11:09 run-all oficial

- Arranque: 2026-11-21 11:09:12 CET. `REQUIRE_OAV=1`, venv `/workspace/venv-v21-ci`.
- Hasta ahora: unit tests 58 OK, ai-door 0 errores, ai-sim 20/20 ×2, sidewalk v19 y v20, mapa 2D, fila de países, ficha Hassall. Sigue attribution y country-buttons. Sin push.

## 11:43 run-all sigue en country-buttons

- El log oficial no ha crecido desde las 11:14:44 CET (último OK: atribución visible y axe 0 en 7 tamaños). `country-buttons-check.py` (PID 263269) imprime el JSON y «FALLOS» solo al final; la espera es por el proceso, no por líneas nuevas.
- A las 11:43 CET el test llevaba ~28 min (el recorrido en solitario tardó ~18–20 min). Sigue vivo: un renderer de Chrome nuevo (~2,8 GB RSS) arrancó ~3 min antes, coherente con un tamaño de viewport reciente, no con un cuelgue claro. HTTP 8899 y bash de run-all siguen arriba. No se lanza una segunda suite.

## 11:47 run-all oficial OK — cierre

- Fin de `tests/run-all.sh`: 2026-11-21 11:47:46 CET. `REQUIRE_OAV=1`, venv `/workspace/venv-v21-ci`.
- `country-buttons-check.py` terminó con **FALLOS: ninguno** (el JSON solo se imprime al final; el proceso no estaba colgado: los renderers de Chrome se iban renovando).
- Resultado: **`run-all: OK` / `EXIT:0`**. 58 unitarios OK, ai-door 0 errores, ai-sim 20/20 ×2, sidewalk v19 y v20 (9.329), mapa 2D, fila de países, Hassall, atribución, country-buttons 10 tamaños.
- Log: `/workspace/v21-data/out/run-all.log`. `tests-end-ok.txt` a las 11:47:46 CET.
- INFORME-v21.md actualizado (tests + opciones de la API de Colonia sin inventar fechas). Sin push, sin `publicar.yml`, sin hits al contador, sin borrar nada.
- Commit local a continuación en `/workspace/kl-v21` (rama `v21`), excluyendo `__pycache__` y `pipeline/cache`.
