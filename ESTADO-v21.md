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
- Versión de caché: `kauffmann-v22-pages`.

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
- Commit local (sin push): `316362af884fedb20c9273ec8b3e558d018fa414` (`316362af`), 2026-11-21 11:49:54 CET, padre `b142fa48`. Mensaje: «v21: Berlín CC BY y Colonia DL-DE Zero, colocación, API, INFORME, run-all OK». Excluidos `__pycache__` y `pipeline/cache`. `data/stones.json` no forma parte del commit (sigue intacto).
- Cierre de la sesión de preparación: 2026-11-21 11:50 CET (inicio 09:32:11 CET).

## 12:00 Auditoría A ronda 1 — FAIL; se corrige en este worktree

- Informe: `/workspace/audits/v21/A/auditoria-A-ronda1.md` sobre el commit `54cdee54`. No se toca el worktree del auditor (`/workspace/audits/v21/A/wt`). Auditores B y C siguen sobre `54cdee54`.
- Hallazgos a corregir: (1) 90 de Berlín ya en OSM por `ref`/URL de biografía; (2) `parse_display_name` invierte comas internas; (3) 2 piedras virtuales importadas como físicas; (4) `koeln-562` a 25,001 m; (5) `dl-de-zero.sources` vacío y JSON-LD/index.html con fecha/cifra de v20.
- En Colonia hay un identificador equivalente: `stid=` en la URL de nsdok/museenkoeln (no el `id` del JSON, que no coincide con OSM). Se usará solo el `stid`.

## 12:13 Correcciones de la auditoría A aplicadas; falta run-all

- Dedupe: Berlín 11.137 → 10.763 dup / 64 probables / 20 virtuales / **290 nuevas**. Colonia 2.960 → 1.297 / 113 / **1.550**. Las 90 de `berlin-missed-dups-ref.csv` son duplicadas. 7 de Colonia por `stid=`. `stones.json` intacto.
- Nombres de Berlín = `Vorname + Nachname` de la fuente. Piedras `Virtueller-Stein=virtuell` fuera del mapa y de la API.
- Colocación: 1.440 con dla, 400 en origen, máx. 24,9977 m; `koeln-562` reajustado 25,0011 → 24,952 m. Total mapa 73.950.
- API: cc-by 290 → 228; dl-de-zero 1.550 → 0 (sources con `koeln_opendata`). Total fichas 181.001.
- JSON-LD e index.html actualizados (2026-11-21, ODbL 72.110 vs mapa 73.950).
- Run-all a continuación con `REQUIRE_OAV=1` en `/workspace/venv-v21-ci` y `KL_HTTP_PORT` distinto de 8899 (ese puerto lo usa el auditor B; no se toca su worktree).

## 12:34 Auditoría B ronda 1 — FAIL; se corrige en el mismo worktree

- Informe: `/workspace/audits/v21/B/auditoria-B-ronda1.md` sobre `54cdee54`. No se toca `/workspace/audits/v21/B/wt` ni su servidor en 8899. El auditor C sigue en marcha.
- Cifras usadas: las posteriores a A (mapa 73.950 = 72.110 + 290 + 1.550; API cc-by 228 / dl-de-zero 0).
- B1: «Acerca de» es/de/en parte el total por fuente y licencia. B2: ya actualizado con A (JSON-LD e index.html, 2026-11-21). B3: `robots.txt`. B4: `sitemap.xml`. B5: `v21-added-test.cjs` con `hav()` y 25 m (OK en solitario, máx. 24,9696 m).
- El run-all iniciado a las 12:13 CET (puerto 8960) sigue en country-buttons; no se lanza otro hasta que termine. Después hará falta un run-all oficial sobre el código A+B.

## 12:48 Auditoría C ronda 1 — FAIL; se corrige en el mismo worktree

- Informe y evidencia: `/workspace/audits/v21/C/auditoria-C-ronda1.md` y `/workspace/audits/v21/C/r1/`. Commit auditado: `54cdee54`. No se toca `/workspace/audits/v21/C/wt` ni los HTTP 8941/8942.
- Causa: `buildStones` de v21 mezclaba las placas municipales en agrupación, fusión, ángulo de calle y desplazamiento, y movía 146 de v20 (máx. 14,666 m; 109 a >200 m, p. ej. Freiburg, Verden, Dresden, Hamburgo).
- Corrección en `app3d.js`: el layout de `b142fa48` corre solo sobre las 72.110; las nuevas visibles se clavan al `dla`/`dlo` del archivo; una nueva puede ser alias de una primaria de v20, nunca al revés. `cc: "DE"` en los JSON añadidos.
- Test nuevo: `tests/v21-v20-render-compare.py` (en `run-all`), compara `_dla`/`_dlo`/`_ang` de las 72.110 con el cliente de `/workspace/countries-proto-v20r4` (b142fa48), tolerancia 1 cm / 0,5°, y comprueba que las nuevas visibles coinciden con el archivo. Bloquea `kl-contador` y `*.workers.dev`. No modifica el worktree de v20.
- El run-all iniciado a las 12:13 CET (puerto 8960, código A, docs B aún a medias, sin el arreglo de C) terminó con `run-all: OK` / `EXIT:0` (log `/workspace/v21-data/out/run-all-ronda2.log`). No cuenta como oficial de A+B+C. A continuación, run-all oficial sobre el árbol completo.

## 12:50 Comparación de renderizado v20/v21 OK; arranca run-all oficial A+B+C

- `tests/v21-v20-render-compare.py` en solitario (v21 :8961, v20 b142fa48 :8970): **OK**, ~40 s. Las 72.110 coinciden en `_dla`/`_dlo`/`_ang` (1 cm / 0,5°). 1.836 nuevas visibles clavadas al archivo; 4 alias de una primaria de v20; 1.840 con `cc=DE`. Total DATA 73.950. Sin hits a `kl-contador` ni `*.workers.dev` (hosts: 127.0.0.1 y tiles.openfreemap.org). Log: `/workspace/v21-data/out/v21-v20-render-compare.log`.
- A continuación `REQUIRE_OAV=1 tests/run-all.sh` en `/workspace/venv-v21-ci`, `KL_HTTP_PORT=8960`, `KL_HTTP_PORT_V20=8970`. No se tocan 8941/8942.

## 12:53 run-all oficial falló: faltaba subir la versión de caché

- `tests/version-test.cjs`: FAIL porque `app3d.js` cambió sin `tests/bump-version.py`. El resto (incl. `v21-added-test`) había pasado; no se llegó a Playwright.
- Ejecutado `python3 tests/bump-version.py` → versión **22**, `kauffmann-v22-pages`, `?v=22` en `index.html` y `sw.js`. Huellas actualizadas en `tests/app-version.json`.
- Se relanza el run-all oficial (`REQUIRE_OAV=1`, `KL_HTTP_PORT=8960`, `KL_HTTP_PORT_V20=8970`).

## 13:30 run-all oficial A+B+C OK — cierre de esta ronda

- Fin: 2026-11-21 13:30:22 CET (inicio 12:57:53 CET). `REQUIRE_OAV=1`, venv `/workspace/venv-v21-ci`, `KL_HTTP_PORT=8960`, `KL_HTTP_PORT_V20=8970`.
- Resultado: **`run-all: OK` / `EXIT:0`**. Incluye `v21-v20-render-compare` (72.110 idénticas a b142fa48) y country-buttons **FALLOS: ninguno**. Log: `/workspace/v21-data/out/run-all-oficial.log`.
- Un intento anterior (12:53 CET) falló solo por no haber subido la versión de caché; otro (12:53 con `bash -lc`) perdió el PATH del venv y `REQUIRE_OAV` no encontró el validador. No se reutilizan. Los servidores de los auditores (8941/8942, y 8899 si seguía) no se tocaron.
- INFORME actualizado. Commit local a continuación, sin push ni `publicar.yml`.

## 13:34 Commit local A+B+C (sin push)

- Se incluye el código, docs, API, tests y JSON municipales de las correcciones A+B+C. Se excluyen `__pycache__` y `pipeline/cache`. `data/stones.json` no entra (sha256 intacto). Sin push y sin `publicar.yml`.

## 13:34 Commit local A+B+C hecho

- `fad34d85457373878e9b17526127b845583c0021` (`fad34d85`), 2026-11-21 13:34:38 CET, rama `v21`, padre `54cdee54`. 154 archivos. Sin push, sin `publicar.yml`, sin hits al contador, sin borrar nada del disco. `stones.json` sha256 `2834ce9ab8747a04bfda2004ae5f83c7cc8d31b99bcdbc64128c670298fc09dc`.

## 13:48 Auditoría C ronda 2 — FAIL; se corrigen las 100 nuevas en archivo

- Informe: `/workspace/audits/v21/C/auditoria-C-ronda2.md` sobre `26d8eedd` / `fad34d85`. Las 72.110 de v20 se dibujan idénticas a `b142fa48` (PASS). Auditor A ronda 2 PASSED. B sigue en marcha (no se toca su worktree ni 8899). C: no se toca `/workspace/audits/v21/C/wt` ni 8941/8942.
- F1 GRAVE: 22 nuevas con columna a <0,5 m de edificio (Rubensstraße 33, Schaevenstraße 4, Wißmannstraße 1a). Hay que usar la huella 1,2 m, no solo el centro.
- F2 GRAVE: 34 nuevas sobre calzada en 10 direcciones (Solinger Straße 1, Im Dau 12, Luxemburger Straße 37, …). Aplicar la regla de calzada de v20; si no hay acera, documentar en CSV como v20.
- F3 GRAVE: 75 pares nuevos–v20 <1,55 m (44 placas, 13 racimos). Además A1: las 4 de Jakordenstraße 17 comparten un mismo dla/dlo y hay que mallarlas.
- Plan: recalcular `dla`/`dlo` de archivo de esas nuevas (sin mover v20, sin cambiar cuentas/nombres/dedupe de A), tope 25 m o excepción documentada; tests sobre la posición renderizada. Luego run-all oficial.

## 13:52 C ronda 2: se recalculan dla/dlo de las nuevas (sin tocar v20)

- Causa raíz: el constructor guardaba el origen+desplazamiento del grupo y confiaba en que el cliente mallara; el cliente v21 clava las nuevas al archivo, así que 1.486 placas de 396 grupos quedan apiladas en el mismo punto. De ahí F1/F2/F3 y el aviso de Jakordenstraße 17.
- Se escribe un reparador que calcula la posición final de cada columna (malla 1,85 m) en el `dla`/`dlo` de archivo: huella 1,2 m a ≥0,5 m de edificios, centro fuera de calzada (regla v20), ≥1,55 m de las 72.110 dibujadas, ≤25 m o excepción. `la`/`lo`, nombres y cuentas no se tocan.

## 14:00 C ronda 2: dla/dlo recalculados; tests de archivo OK; arranca run-all oficial

- Reparador `/workspace/v21-data/scripts/repair_v21_r2.py`: 728 grupos, 1.531 `dla`/`dlo` cambiados, 0 sin hueco, 0 en `calzada-v21.csv`, 0 excepciones >25 m. Máx. 24,9836 m (`ber-11663`; hav() 24,9556 m). Con dla: 1.778 (Berlín 284/290, Colonia 1.494/1.550). Jakordenstraße 17: malla 2×2 a 1,85 m, 8,1–10,4 m de Frieda. Verificación: 0 dentro de edificio, 0 columna <0,5 m, 0 calzada, 0 pares <1,55 m, 0 apiladas. Cuentas/nombres/`la`/`lo` idénticos a `26d8eedd`. `stones.json` intacto.
- `tests/v21-new-render-placement.py --from-files` OK. `v21-added-test.cjs` OK. En `run-all` el test nuevo vuelca la app y comprueba la posición dibujada.
- A continuación `REQUIRE_OAV=1 tests/run-all.sh` en `/workspace/venv-v21-ci`, `KL_HTTP_PORT=8960`, `KL_HTTP_PORT_V20=8970`. No se tocan 8941/8942.

## 14:27 run-all oficial C ronda 2 OK — commit local a continuación

- Fin: 2026-11-21 14:26:53 CET (inicio 13:59:33 CET). `REQUIRE_OAV=1`, venv `/workspace/venv-v21-ci`, puertos 8960/8970.
- Resultado: **`run-all: OK` / `EXIT:0`**. Incluye compare de las 72.110 (idénticas a b142fa48) y `v21-new-render-placement` sobre posiciones dibujadas. country-buttons **FALLOS: ninguno**. Log: `/workspace/v21-data/out/run-all-c-r2.log`.
- No se tocaron los worktrees ni HTTP de los auditores (C 8941/8942; B en 18899/18970). Sin push ni `publicar.yml`. `stones.json` intacto.

## 14:27 Commits locales C ronda 2 (sin push)

- `a8817b903d8482886247dcaf81177f6cc9e6e007` (`a8817b90`), 14:27:17 CET: test `v21-new-render-placement.py`, `calzada-v21.csv`, `excepciones-25m-v21.csv`.
- `1ce9f27d8a3f48c1ad38628bffcb302e74810236` (`1ce9f27d`), 14:27:27 CET: `dla`/`dlo` de `data/berlin-added-20261121.json` y `data/koeln-added-20261121.json`, INFORME, hook en `run-all.sh`, ESTADO. Padre de la serie: `26d8eedd`. Sin push, sin `publicar.yml`, `stones.json` sha256 `2834ce9ab8747a04bfda2004ae5f83c7cc8d31b99bcdbc64128c670298fc09dc`.
- El commit inmediatamente posterior en `v21` solo anota estos hashes en ESTADO e INFORME (HEAD de la rama).
