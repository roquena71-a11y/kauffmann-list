# INFORME v21 — Berlín Open Data y Stolpersteine Köln

Preparación en el worktree `/workspace/kl-v21`, rama `v21`, partiendo de `b142fa48` (v20 publicada). **Sin push, sin publicar, sin correr `publicar.yml`.** Zona horaria: Europe/Berlin (CET, UTC+1).

- Inicio: 2026-11-21 09:32:11 CET
- Fin (tests oficiales, ronda inicial): 2026-11-21 11:47:46 CET
- Commit de aquella ronda: `316362af` / tip `54cdee54` (11:49–11:50 CET)
- Corrección tras auditoría A (ronda 1, FAIL sobre `54cdee54`): en curso el 2026-11-21 desde las 12:00 CET
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

Criterio: duplicada clara = mismo `name_key` y (≤25 m o misma `addr_key`), **o** el mismo identificador estable de la fuente ya guardado en OSM. En Berlín: `ref` de OSM o el id de `https://www.stolpersteine-berlin.de/…/biografie/{id}` (el mismo que la columna «Url zu Biografie» / `ber-{id}`). En Colonia: el parámetro `stid=` de la URL de nsdok/museenkoeln que trae el JSON (no el `id` del geoportal, que es otro numerador y choca por casualidad con otros `stid`). Probable (no se importa) = mismo nombre a 25–150 m o a ≤30 km; homónimo a más de 30 km = nueva. Las 20 filas de Berlín con `Virtueller-Stein=virtuell` se excluyen del mapa físico y de la API (no son placas en la acera).

| Fuente | Entrada | Duplicadas claras | Probables (fuera) | Virtuales (fuera) | Nuevas en el mapa |
| --- | ---: | ---: | ---: | ---: | ---: |
| Berlín | 11.137 | 10.763 | 64 | 20 | **290** |
| Colonia | 2.960 | 1.297 | 113 | 0 | **1.550** |
| Total | 14.097 | 12.060 | 177 | 20 | **1.840** |

Las 90 placas que la auditoría A señaló (misma `ref` / URL de biografía, tabla `berlin-missed-dups-ref.csv`) están ahora todas en duplicadas, no en nuevas. De ellas, 3 quedan documentadas como misma `ref` pero lejanas (no se importan como segunda placa sin revisión): `ber-2007` Manfred Ephraim Joel / `n13968440828`, 562 m (OSM tiene además `n8205782058` a 150,8 km con la misma `ref`); `ber-8876` Rolph Eduard Henoch / `n13302465638`, 788 m; `ber-8877` Ernst Peter Henoch / `n13302465640`, 787 m. Josephine / Josefine Huldschinsky (`ber-3776`, `ref=3776`) es la misma placa ya publicada, no una duda.

En Colonia se apartaron 7 «nuevas» que compartían `stid=` con un nodo OSM ya publicado (mismo nombre y dirección, 3–13 m; el OSM suele añadir «geb. …»).

Todas las nuevas traían coordenadas. No se inventan nombres ni fechas (`Geburtsjahr` 0 se omite; 1965 y 1968 se dejan tal cual). 3 placas de Colonia van sin nombre, como en la fuente. Los 11 nombres de Berlín que el parser había invertido por una coma interna se publican ahora exactamente como `Vorname + " " + Nachname` (comillas y corchetes de la fuente; a lo sumo se colapsan espacios). En Colonia se sigue volcando el patrón claro «Apellido, Nombre» del campo único `name`.

## Colocación (reglas de v20; solo dla/dlo)

- Extracto OSM Berlín+Colonia: timestamp `2026-11-18T21:21:02Z`
- 730 grupos: 514 solo nuevas, 216 mixtos (970 placas ya publicadas; `stones.json` no se reescribió; `existing_dla_changed = 0`)
- 1.778 ajustadas (dla/dlo de la posición final de cada columna); 62 se quedan en el punto de origen (sin dla)
- Desplazamientos >25 m: **0** (no hace falta `excepciones-25m-v21.csv`). Máximo vigente: **24,952 m** (`koeln-562` Kurt (Dr.) Frankenstein, Buchforststraße 2, Köln; hav oficial 24,9240 m). En C ronda 2 el máximo llegó a 24,9836 m (`ber-11663`); esa pareja se remalló a paso 1,85 m en C ronda 3 y ya no marca el techo.
- `koeln-562` Kurt (Dr.) Frankenstein, Buchforststraße 2, Köln, quedaba a **25,0011 m** por el redondeo a 7 decimales (el haversine daba 24,973 m; el informe anterior citó 24,97 m y no era exacto). Se reajustó sobre el mismo vector a **24,952 m** (`dlo` 7,0096718 → 7,0096711). `la`/`lo` de origen no se tocan. No hace falta excepción.
- Berlín: 284/290 con dla. Colonia: 1.494/1.550 con dla
- Archivos: `data/berlin-added-20261121.json`, `data/koeln-added-20261121.json`
- Total en el mapa si se cargan los tres archivos: **73.950** (72.110 ODbL + 1.840)
- El cliente (`app3d.js`) calcula el layout de v20 **solo** con las 72.110 placas de `stones.json`, con el mismo algoritmo que `b142fa48`. Las placas municipales no entran en agrupación, fusión, ángulo, cuadrícula ni desplazamiento: se dibujan exactamente en el `dla`/`dlo` (o `la`/`lo`) del archivo, donde el constructor ya ha escrito la casilla final de la malla (paso 1,85 m), con holgura de columna 1,2 m a ≥0,5 m de las fachadas, centro fuera de la calzada (regla de v20) y ≥1,55 m de los grupos de v20 ya dibujados. Si una nueva es la misma persona que una ya publicada (mismo nombre, ≤25 m, misma `addr_key`), queda como alias de esa primaria y no la sustituye. Todas las nuevas llevan `cc: "DE"`.

## API (build offline, generated=2026-11-21)

La regla de posiblemente vivas no se ha relajado (sin indicio de muerte y nacimiento hace menos de 110 años, o sin año → no hay ficha).

| Familia | Registros de entrada | Publicadas | Excluidas (posiblemente vivas) |
| --- | ---: | ---: | ---: |
| cc-by (Berlín) | 290 | **228** | 62 |
| dl-de-zero (Colonia) | 1.550 | **0** | 1.550 (el JSON no trae fechas) |
| odbl | 72.110 | 62.519 | 8.906 (más otras políticas) |
| cc0 | 133.301 | 118.254 | 15.047 |
| Total fichas API |  | **181.001** |  |

`pipeline validate` en el build: 0 errores. `data/search/` sigue siendo solo ODbL. `api/v1/index.json` y `api/v1/dl-de-zero/index.json` listan `koeln_opendata` en `sources` (URL https://open.nrw/dataset/stolpersteine-koln-k) aunque haya 0 fichas publicadas.

El mapa carga las 1.550 placas nuevas de Colonia; la API de esa familia sigue en 0 personas por la regla de 110 años y la ausencia de fechas en la fuente. Opciones, sin inventar datos ni copiar biografías: (1) dejarlo como está; (2) si más adelante la fuente abierta incluye fechas, repetir el build; (3) no raspar museenkoeln.de / nsdok.de; (4) no tratar «aparecer en una lista de Stolpersteine» como prueba de muerte sin un cambio de política explícito.

## Cliente y documentos públicos

- Versión de caché: `kauffmann-v22-pages` (`tests/bump-version.py`).
- Al cargar tres JSON, `style.load` podía dispararse después de asignar `DATA` y antes de `buildStones()`, y montaba la capa `pts` con datos vacíos. `tryAddOverlays()` espera a `POINTS_FC`/`STONES_FC`/`AGG` y no depende de `map.isStyleLoaded()`.
- «Acerca de» (es/de/en): el total del mapa (${count} = 73.950) se parte en 72.110 de OSM/Wikidata (ODbL), 290 de la lista abierta de Berlín (CC BY) y 1.550 de la de Colonia (DL-DE Zero 2.0).
- `index.html` y `kauffmann-list.jsonld` (2026-11-21, sincronizados): 72.110 es solo ODbL; el mapa con las listas municipales suma 73.950.
- `robots.txt` cita también CC BY (`api/v1/cc-by`) y dl-de/zero-2-0 (`api/v1/dl-de-zero`).
- `sitemap.xml`: `lastmod` 2026-11-21 en las páginas tocadas; añadidos `api/v1/cc-by/find/index.json` y `api/v1/dl-de-zero/find/index.json`.
- `tests/v21-added-test.cjs` mide el desplazamiento con `hav()` oficial (R=6.371.000 m) y el tope es 25 m, salvo excepción documentada. Máximo actual: **24,9240 m** (`koeln-562`, hav); con el mayor de hav y equirectangular (`M_LAT=111320`): **24,952 m** (mismo id). `ber-11663` ya no es el máximo (tras rehacer su malla en C ronda 3 queda a 4,191 m hav).

## Tests

`REQUIRE_OAV=1 tests/run-all.sh` oficial sobre el código con las correcciones de C ronda 3: **OK / EXIT:0**, 2026-11-21 14:59:01–15:28:18 CET, venv `/workspace/venv-v21-ci`, `KL_HTTP_PORT=8960`, `KL_HTTP_PORT_V20=8970`. Log: `/workspace/v21-data/out/run-all-c-r3.log`. 58 unitarios OK, ai-door 0, ai-sim 20/20 ×2, sidewalk v19 y v20 (9.329), mapa 2D, comparación de las 72.110 contra `b142fa48` (0 movidas; 1.836 nuevas visibles clavadas al archivo; 4 alias; 1.840 con `cc=DE`; sin hits a `kl-contador` ni `*.workers.dev`), `v21-new-render-placement` sobre el volcado renderizado de las 1.840 (width OSM de `w4490370`, todas las vías a ≤80 m, malla intra-grupo 1,85 m, huella, calzada, 1,55 m, ≤25 m), fila de países, Hassall, atribución, country-buttons (FALLOS: ninguno). Versión de caché `kauffmann-v22-pages` (`?v=22`). El run-all oficial de C ronda 2 (13:59:33–14:26:53 CET, log `run-all-c-r2.log`) permanece como antecedente.

## Worktree y commit

- Worktree: `/workspace/kl-v21`, rama `v21`, creada desde `b142fa48` (v20 publicada). Padre de esta corrección: `54cdee54`.
- Commit local C ronda 2 (sin push): `a8817b90` y `1ce9f27d`, 2026-11-21 14:27 CET, padre `26d8eedd` (hashes anotados en el tip `17ef7fcc`).
- Commit local C ronda 3 (sin push; el hash se anota en el commit siguiente): `dla`/`dlo` de 28 placas en `data/berlin-added-20261121.json` y `data/koeln-added-20261121.json`, test `tests/v21-new-render-placement.py` (width OSM, todas las vías a ≤80 m, malla 1,85 m, las 1.840), INFORME y ESTADO. Padre: `17ef7fcc`. Excluidos `__pycache__` y `pipeline/cache`. `data/stones.json` no forma parte del commit (sigue intacto).
- `data/stones.json` intacto (72.110, solo ODbL, sha256 `2834ce9ab8747a04bfda2004ae5f83c7cc8d31b99bcdbc64128c670298fc09dc`).

## Dudas (no bloquean la preparación)

- Berlín: el catálogo indica `license_id: cc-by` pero no aclara si es CC BY 3.0 o 4.0.
- Colonia: la ficha habla de «rund 2.300» / «über 2.400»; esta descarga tiene 2.960 entidades.
- El auditor C devolvió FAIL sobre `54cdee54` (colocación en el cliente renderizado); las correcciones van en este mismo worktree, junto con A y B.

## Estado de los hallazgos de la auditoría A (ronda 1)

1. HIGH, 90 duplicadas por `ref`/URL: **corregido** (las 90 están fuera de nuevas y de `api/v1/cc-by/`; también se aplica `stid=` en Colonia, 7 casos).
2. HIGH, 11 nombres invertidos por coma interna: **corregido** (`parse_display_name` ya no trata esas comas como «Apellido, Nombre»; los nombres coinciden con la fuente).
3. HIGH, 2 piedras virtuales: **corregido** (las 20 con `Virtueller-Stein=virtuell` se excluyen del mapa y de la API; criterio documentado).
4. LOW, máximo 25,001 m en `koeln-562`: **corregido** (reajuste a 24,952 m; el máximo con equirectangular es 24,9977 m; con `hav()` oficial, 24,9696 m; INFORME actualizado).
5. LOW, `sources` vacío y JSON-LD desfasado: **corregido** (`dl-de-zero` declara `koeln_opendata`; JSON-LD e `index.html` con fecha 2026-11-21 y cifras ODbL 72.110 vs mapa 73.950).

## Estado de los hallazgos de la auditoría B (ronda 1)

Las cifras de B sobre `54cdee54` (384+1.565=74.059, API 279) se han recalculado tras las correcciones de A.

1. MEDIA, «Acerca de» atribuye el total solo a OSM/Wikidata: **corregido** (es/de/en parten 73.950 = 72.110 ODbL + 290 CC BY + 1.550 DL-DE Zero).
2. MEDIA, JSON-LD/`index.html` en 72.110 y 2026-11-20: **corregido** (fecha 2026-11-21; 72.110 queda como ODbL y se declara el total del mapa 73.950).
3. MEDIA, `robots.txt` sin las licencias nuevas: **corregido**.
4. MEDIA, `sitemap.xml` desfasado: **corregido** (`lastmod` 2026-11-21 y find de `cc-by` / `dl-de-zero`).
5. MEDIA, test v21 con umbral 60 m: **corregido** (`hav()` oficial, tope 25 m, solo excepciones documentadas).

## Estado de los hallazgos de la auditoría C (ronda 1)

Informe: `/workspace/audits/v21/C/auditoria-C-ronda1.md` sobre `54cdee54` (cifras pre-A: 384+1.565). No se toca `/workspace/audits/v21/C/wt` ni sus servidores. Las reglas de colocación deben cumplirse en la posición **dibujada**, no solo en el `dla`/`dlo` del archivo.

1. GRAVE, 146 placas de v20 se mueven al dibujarlas (máx. 14,666 m, Frieda Meyer, Jakordenstraße 17, Köln; 109 a más de 200 m de cualquier nueva): **corregido** (el layout de v20 corre solo sobre las 72.110; test de comparación de las 72.110 contra `b142fa48`).
2. GRAVE, fusión del grupo de Jakordenstraße 17 (24 de v20 + 4 nuevas): **corregido** (las nuevas no entran en la agrupación).
3. GRAVE, 61 centros de nuevas dentro de edificios al renderizar: **corregido en el cliente** (se clavan al `dla`/`dlo` del archivo, que el auditor vio por lo general fuera del edificio).
4. GRAVE, 12 nuevas a más de 25 m al renderizar (máx. 32,002 m) y `koeln-562` a 25,001 m en archivo: **corregido** (sin relayout en el cliente; `koeln-562` ya reajustado en archivo a 24,952 m, hallazgo A4).
5. GRAVE, 40 nuevas sobre la calzada al renderizar: **corregido en el cliente** (posición = archivo, sin desplazamiento de grupo).
6. MEDIO, 72 con holgura de columna <0,5 m al renderizar: **corregido en el cliente** (misma política).
7. MEDIO, alias `ber-6881` desplaza una de v20 2,053 m: **corregido** (una nueva nunca es primaria de una de v20; el centroide de v20 no cambia).
8. MEDIO, 28 cambios solo de ángulo en v20: **corregido** (el ángulo de calle se calcula solo con las 72.110).
9. MEDIO, 2 pares entre grupos <1,55 m al renderizar: **corregido en el cliente**. En archivo esas distancias ya eran legales (p. ej. `koeln-1194` frente a `n2283343674` = 5,639 m; `ber-10773` frente a `Q132155276` = 10,33 m).
10. AVISO, nuevas sin `cc`: **corregido** (`cc: "DE"` en los JSON y en el generador).

## Estado de los hallazgos de la auditoría C (ronda 2)

Informe: `/workspace/audits/v21/C/auditoria-C-ronda2.md` sobre `26d8eedd` / `fad34d85`. Las 72.110 de v20 siguen idénticas a `b142fa48` (PASS de la ronda 2). Auditor A ronda 2: PASSED (cuentas, nombres y dedupe no se han vuelto a tocar: solo `dla`/`dlo` y `move_m`). No se toca el worktree del auditor ni 8941/8942.

El constructor ahora escribe en el archivo la posición final de cada columna (malla de paso 1,85 m). El cliente sigue clavando las nuevas a ese `dla`/`dlo`. `calzada-v21.csv` y `excepciones-25m-v21.csv` existen (0 filas: se encontró hueco legal a ≤25 m para todas). Test nuevo: `tests/v21-new-render-placement.py`.

1. GRAVE, 22 nuevas con la columna a <0,5 m de un edificio (Rubensstraße 33, Schaevenstraße 4, Wißmannstraße 1a; huella 1,2 m): **corregido** en el `dla`/`dlo` de archivo.
2. GRAVE, 34 nuevas sobre la calzada en 10 direcciones (Solinger Straße 1, Im Dau 12, Luxemburger Straße 37, …): **corregido** (regla de calzada de v20; no hizo falta documentar excepciones).
3. GRAVE, 75 pares nuevos–v20 a <1,55 m (44 placas, 13 racimos, mín. 0,545 m en Zwirnerstraße 33): **corregido** (cada nueva queda a ≥1,55 m de las 72.110 dibujadas).
4. AVISO A1, las 4 de Jakordenstraße 17 compartían un `dla`/`dlo`: **corregido** (malla 2×2 a 1,85 m, a 8,1–10,4 m de Frieda Meyer, sin mover v20).

## Estado de los hallazgos de la auditoría C (ronda 3)

Informe: `/workspace/audits/v21/C/auditoria-C-ronda3.md` sobre `17ef7fcc`. Las 72.110 de v20 siguen idénticas a `b142fa48`. Auditor A ronda 3: PASSED (cuentas, nombres, `la`/`lo` y dedupe no se han tocado: solo `dla`/`dlo` y `move_m` de 28 placas). B ronda 3 sigue en su worktree (no se toca). C: no se toca `/workspace/audits/v21/C/wt` ni 8941/8942.

Causa: el extracto OSM cercano descartaba el tag `width` (y `est_width`, `sidewalk*`); `w4490370` se trataba como residencial de semiancho 2,50 m en vez de 5,50. El índice de vías usaba radio 1 y se omitía la calzada si el edificio más cercano estaba a >25 m. Además, el tope de 25 m aplicado piedra a piedra comprimía la malla rígida de 1,85 m. El sidecar `/workspace/v21-data/near/highway-tags-extra.json` (PBF oficial `2026-11-18T21:21:02Z`) enriquece 157.443 vías. El reparador `repair_v21_r3.py` (14:52:27–14:53:00 CET) recolocó **6 grupos / 28 placas** (3 de Berlín, 25 de Colonia); 0 sin hueco; `calzada-v21.csv` y `excepciones-25m-v21.csv` siguen con 0 filas. Con dla: 1.778 (Berlín 284/290, Colonia 1.494/1.550). Máx. 24,952 m (`koeln-562`, sin cambio).

El test `tests/v21-new-render-placement.py` ahora: (1) aplica `width` OSM, (2) mira todas las vías vehiculares a ≤80 m (rc=4; no salta si `d_center` >25 m; exención de fachada solo <6 m), (3) exige malla intra-grupo de paso 1,85 m (±0,08 m), (4) recorre las 1.840. Sobre `17ef7fcc` el test **falla** exactamente en los casos de C: `ber-10773` −2,608 m y `koeln-2440` −0,114 m en calzada; grupos Bonner (mín. 0,067 m), Alteburger (1,003 m), Zülpicher (0,923 m) y Feige (1,593 m). Sobre el árbol actual, `--from-files` en las 1.840: **OK**. Run-all oficial (14:59:01–15:28:18 CET): **OK / EXIT:0** (log `/workspace/v21-data/out/run-all-c-r3.log`).

1. GRAVE F1, `ber-10773` Selma Riese, Solinger Straße 1, seguía en el mismo dla, −2,608 m dentro de `w4490370` (width=11, semiancho 5,50): **corregido**. Nuevo dla 52,5198712 / 13,3350472 (5,001 m del origen). `rd_clear` +0,216 m respecto al eje (distancia al eje 5,716 m). No hizo falta ficha en `calzada-v21.csv`.
2. GRAVE F1, `koeln-2440` Eva Helene Katz, Melatengürtel 13, −0,114 m en Scheidtweilerstraße `w241680539` (el chequeo la saltaba porque el edificio estaba a 25,014 m): **corregido**. Nuevo dla 50,9382734 / 6,9087154 (1,018 m). `rd_clear` +0,249 m. El grupo de 4 en esa dirección se desplazó con ella.
3. GRAVE F2, `koeln-86` y `koeln-88` (Bonner Straße 33) apiladas a 0,067 m: **corregido**. Las 5 del grupo quedan en malla de paso 1,85 m (mín. 1,846 m).
4. MEDIA F3, mallas irregulares en Alteburger Straße 11 (mín. 1,003 m, 8 placas) y Zülpicher Platz 4 (mín. 0,923 m, 8 placas): **corregido** (mín. 1,846 m y 1,847 m; 10 lados ≈1,85 m en cada grupo). Aviso `ber-11662`/`ber-11663` (Choriner Str. 13) a 1,593 m: **corregido** (mín. 1,849 m), sin acercarse al tope de 25 m.

