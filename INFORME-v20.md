# INFORME v20 — países nuevos, colocación en la acera (Alemania incluida) y las 1.480 de Wikidata

Generado 2026-11-20 09:38 (hora de Berlín). Prototipo local sobre la v19 publicada (commit 49e7725). **Nada publicado, sin push.**

## 1. Resumen

- Total de placas en el mapa: **72.038** (v19: 65.861; **+6.177**). 27 países con placas.
- Nuevas por país (países nuevos + las 29 de las 1.480 en Alemania): Países Bajos 1281 · Francia 1151 · Austria 1122 · Chequia 599 · Noruega 580 · Italia 440 · España 325 · Bélgica 171 · Luxemburgo 162 · Hungría 83 · Lituania 67 · Suiza 49 · Eslovaquia 33 · Polonia 30 · Alemania 29 · Croacia 17 · Dinamarca 14 · Guernsey 8 · Andorra 7 · Letonia 4 · Reino Unido 3 · Liechtenstein 2
- Datos abiertos únicamente: OpenStreetMap (ODbL; Geofabrik europe 2026-11-18 ~21:21 UTC, refrescado por id con Overpass el 2026-11-20) y Wikidata (CC0, consulta del 2026-11-20). Sin nombres de archivos cerrados.
- Las coordenadas de origen (`la`/`lo`) no se tocan nunca; la posición de dibujo va en `dla`/`dlo`.
- Controles aplicados a cada placa nueva (no todas tienen la misma confirmación de posición; ver cobertura abajo): nombre limpio (solo se quitan prefijos literales como «Stolperstein für»), nombre (palabras completas) tal cual en la inscripción cuando ésta existe, un solo nombre de persona (los registros con varias personas, rótulos o instituciones van a pendiente), año de muerte coherente con la inscripción, imagen de Commons existente, sin duplicado a ≤15 m (mismo nombre o subconjunto y mismo nacimiento), y, si OSM marca la posición como dudosa (`fixme`), solo con un objeto `addr:*` ajeno a la placa a ≤15 m o una foto cuya coordenada no sea copia de OSM; fusión OSM–Wikidata solo si ≤50 m y nombre compatible. Lo dudoso va a `pendiente-v20.csv` con su motivo.
- **Cobertura real de la confirmación de posición** de las 6177 placas nuevas: **A** objeto `addr:*` de OSM ajeno a la placa, misma calle y número, ≤40 m: **3478 (56 %)** · **B** foto de Commons con coordenada independiente: 161 · **C** foto de Commons cuya coordenada coincide con la de OSM al metro (no es independiente): 290 · **D** solo la coordenada de la fuente (sin dirección ni foto que la contraste): **2248 (36 %)**. La dirección o la inscripción de cada ficha viene de la fuente, pero la posición solo está contrastada de forma independiente en A+B. Por país (A/B/C/D): NL 562/0/2/717; FR 802/5/4/340; AT 925/8/114/75; CZ 93/9/19/478; NO 571/2/0/7; IT 71/37/104/228; ES 121/1/9/194; BE 115/1/2/53; LU 88/54/2/18; HU 0/33/24/26; LT 60/0/0/7; CH 32/1/4/12; SK 4/2/0/27; PL 2/7/4/17; DE 0/0/0/29; HR 13/1/2/1; DK 12/0/0/2; GG 0/0/0/8; AD 0/0/0/7; LV 4/0/0/0; GB 1/0/0/2; LI 2/0/0/0.
- Regla de «posible superviviente / vivo»: igual que en la v19 (`policy.py`, 110 años; marcadores multilingües de superviviente en `pipeline/inscription.py`).

## Notas de la versión v20 (para publicar)

- **Corrección de país de 15 placas de la v19** (contadas como Alemania; el límite administrativo admin_level=2 de OSM las sitúa fuera): Luxemburgo 6, Austria 4, Polonia 3, Suiza 2. El contenido no cambia (Jersey 20, Finlandia 7, Irlanda 6, Suecia 6 y Rumanía 2 ya llevaban su país en la v19 publicada). Alemania: 65.820 (v19) − 15 + 29 de las 1.480 (Wikidata) = 65834.
- **27 países**: Alemania y 26 más de Europa (Países Bajos, Austria, Francia, Chequia, Noruega, Italia, España, Bélgica, Luxemburgo, Hungría, Lituania, Suiza, Polonia, Eslovaquia, Jersey, Croacia, Dinamarca, Guernsey, Finlandia, Andorra, Irlanda, Suecia, Letonia, Reino Unido, Rumanía y Liechtenstein). Botones de país y búsqueda en español, alemán e inglés; la fila de países se pliega en «Más países (N)».
- **+6.177 placas** verificables con datos abiertos (OSM ODbL + Wikidata CC0), cada una con enlace a su fuente; los casos dudosos quedan en pendiente con su motivo.
- **Todas las placas fuera de los edificios**: Alemania incluida, la posición de dibujo (`dla`/`dlo`) va a la acera con ≥0,5 m de holgura (salvo 45 placas residuales con holgura <0,5 m y 48 «revisar» sin contacto detectado y 4 con el dibujo junto a otra calle, todas documentadas una a una en `residuales-acera-v20.csv`; 25 dibujos a >25 m en `excepciones-25m-v20.csv`; 57 placas sin edificio de OSM a ≤50 m en `sin-edificios-v20.csv`); la coordenada de origen no se toca y es la que usan «Cómo llegar» y las descargas.
- Piedras con posición deducida de la foto de Commons: aviso «posición aproximada» propio. Regla de «posible superviviente» sin cambios.
- Caché del navegador: `kauffmann-v20-pages`.

## 2. Placas por país

| País | En el mapa | Nuevas v20 | Objetos OSM | Ítems WD | Pendientes (motivo en CSV) | Acera: ya bien | Acera: ajustadas | Dentro legítimo | Para revisar | Mayor desplazamiento (m) |
|--|--|--|--|--|--|--|--|--|--|--|
| Alemania (DE) | 65834 | 29 | — | — | — | 30314 | 35444 | 3 | 73 | 24.65 |
| Países Bajos (NL) | 1281 | 1281 | 2731 | 54 | 1487 | 299 | 978 | 0 | 4 | 22.55 |
| Francia (FR) | 1151 | 1151 | 1362 | 320 | 279 | 346 | 805 | 0 | 0 | 19.85 |
| Austria (AT) | 1126 | 1122 | 1502 | 149 | 466 | 630 | 496 | 0 | 0 | 17.7 |
| Chequia (CZ) | 599 | 599 | 2156 | 1525 | 2919 | 168 | 431 | 0 | 0 | 18.7 |
| Noruega (NO) | 580 | 580 | 158 | 759 | 282 | 170 | 410 | 0 | 0 | 18.35 |
| Italia (IT) | 440 | 440 | 561 | 167 | 277 | 211 | 229 | 0 | 0 | 21.1 |
| España (ES) | 325 | 325 | 434 | 114 | 149 | 156 | 169 | 0 | 0 | 20.8 |
| Bélgica (BE) | 171 | 171 | 238 | 52 | 118 | 47 | 124 | 0 | 0 | 21.5 |
| Luxemburgo (LU) | 168 | 162 | 175 | 4 | 7 | 67 | 101 | 0 | 0 | 18.15 |
| Hungría (HU) | 83 | 83 | 371 | 10 | 298 | 58 | 25 | 0 | 0 | 3.0 |
| Lituania (LT) | 67 | 67 | 74 | 0 | 7 | 47 | 20 | 0 | 0 | 1.15 |
| Suiza (CH) | 51 | 49 | 38 | 68 | 26 | 34 | 17 | 0 | 0 | 2.6 |
| Polonia (PL) | 33 | 30 | 53 | 7 | 24 | 9 | 24 | 0 | 0 | 6.15 |
| Eslovaquia (SK) | 33 | 33 | 83 | 1 | 51 | 28 | 5 | 0 | 0 | 0.45 |
| Jersey (JE) | 20 | 0 | — | — | — | — | — | — | — | — |
| Croacia (HR) | 17 | 17 | 33 | 15 | 30 | 12 | 5 | 0 | 0 | 1.25 |
| Dinamarca (DK) | 14 | 14 | 19 | 27 | 32 | 8 | 6 | 0 | 0 | 7.85 |
| Guernsey (GG) | 8 | 8 | 28 | 1 | 21 | 8 | — | 0 | 0 | — |
| Finlandia (FI) | 7 | 0 | — | — | — | — | — | — | — | — |
| Andorra (AD) | 7 | 7 | 8 | 0 | 1 | 1 | 6 | 0 | 0 | 4.05 |
| Irlanda (IE) | 6 | 0 | — | — | — | — | — | — | — | — |
| Suecia (SE) | 6 | 0 | — | — | — | — | — | — | — | — |
| Letonia (LV) | 4 | 4 | 4 | 4 | 0 | 0 | 4 | 0 | 0 | 1.8 |
| Reino Unido (GB) | 3 | 3 | 3 | 2 | 1 | 0 | 3 | 0 | 0 | 1.6 |
| Rumanía (RO) | 2 | 0 | — | — | — | — | — | — | — | — |
| Liechtenstein (LI) | 2 | 2 | 2 | 0 | 0 | 2 | — | 0 | 0 | — |

Países con datos abiertos pero **sin ninguna placa verificable** (todo en pendiente): Grecia (7 objetos/ítems), Eslovenia (6 objetos/ítems), Ucrania (89 objetos/ítems).

## 3. Motivos de pendiente por país (resumen)

- **Andorra**: OSM marca la posición como dudosa: 1
- **Austria**: sin nombre: 141; el nombre de OSM no coincide con la inscripción: 98; el nombre parece colectivo o de varias personas: 48; el nombre junta a varias personas: 44; la dirección de Wikidata no tiene calle y número legibles; sin comprob: 30; el nombre contiene cifras: 26
- **Bélgica**: sin coordenadas P625 únicas en Wikidata: 50; sin nombre: 28; sin dirección ni inscripción en OSM: 20; OSM marca la posición como dudosa: 7; el nombre parece colectivo o de varias personas: 5; la dirección etiquetada existe en OSM pero a 90 m de la posición de la: 2
- **Suiza**: la dirección de Wikidata no tiene calle y número legibles; sin comprob: 8; sin dirección ni inscripción en OSM: 4; Wikidata trae varias direcciones o inscripciones distintas: 4; el nombre de OSM no coincide con la inscripción: 3; la coordenada de Wikidata no se confirma con una dirección de OSM ni c: 3; el nombre de Wikidata no coincide con su inscripción: 3
- **Chequia**: sin dirección ni inscripción en OSM: 1540; la etiqueta de Wikidata: 1003; sin dirección P6375 ni inscripción P1684 en Wikidata: 216; sin coordenadas P625 únicas en Wikidata: 66; sin nombre: 14; el nombre parece colectivo o de varias personas: 14
- **Dinamarca**: sin nombre: 13; sin coordenadas P625 únicas en Wikidata: 10; OSM marca la posición como dudosa: 3; sin dirección P6375 ni inscripción P1684 en Wikidata: 3; la coordenada de Wikidata no se confirma con una dirección de OSM ni c: 2; nombre de una sola palabra: 1
- **España**: sin dirección ni inscripción en OSM: 37; el nombre parece colectivo o de varias personas: 24; el nombre de OSM no coincide con la inscripción: 21; sin dirección P6375 ni inscripción P1684 en Wikidata: 17; sin nombre: 13; la etiqueta de Wikidata: 13
- **Francia**: OSM marca la posición como dudosa: 158; sin nombre: 55; el nombre de OSM no coincide con la inscripción: 15; la coordenada de Wikidata no se confirma con una dirección de OSM ni c: 15; sin coordenadas P625 únicas en Wikidata: 8; la dirección etiquetada existe en OSM pero a 45 m de la posición de la: 5
- **Reino Unido**: sin dirección ni inscripción en OSM: 1
- **Guernsey**: OSM marca la posición como dudosa: 20; sin coordenadas P625 únicas en Wikidata: 1
- **Grecia**: el nombre de OSM no coincide con la inscripción: 5; sin nombre: 2
- **Croacia**: sin dirección ni inscripción en OSM: 28; el nombre contiene cifras: 1; sin coordenadas P625 únicas en Wikidata: 1
- **Hungría**: sin nombre: 252; sin dirección ni inscripción en OSM: 18; OSM marca la posición como dudosa: 16; el nombre de OSM no coincide con la inscripción: 3; sin dirección P6375 ni inscripción P1684 en Wikidata: 3; la coordenada de Wikidata no se confirma con una dirección de OSM ni c: 3
- **Italia**: sin dirección ni inscripción en OSM: 71; la dirección de Wikidata no tiene calle y número legibles; sin comprob: 67; sin nombre: 57; el nombre de OSM no coincide con la inscripción: 21; la coordenada de Wikidata no se confirma con una dirección de OSM ni c: 21; nombre genérico con texto que no es un nombre: 11
- **Lituania**: el nombre de OSM no coincide con la inscripción: 2; OSM marca la posición como dudosa: 2; la dirección etiquetada existe en OSM pero a 43 m de la posición de la: 2; la dirección etiquetada existe en OSM pero a 47 m de la posición de la: 1
- **Luxemburgo**: el nombre de OSM no coincide con la inscripción: 4; la foto de Commons está a 480 m de la posición de la placa en OSM: 2; Stolperschwelle: 1
- **Países Bajos**: sin nombre: 927; sin dirección ni inscripción en OSM: 354; el nombre de OSM no coincide con la inscripción: 56; el nombre junta a varias personas: 49; propuesta: 21; OSM marca la posición como dudosa: 15
- **Noruega**: la coordenada de Wikidata no se confirma con una dirección de OSM ni c: 107; la dirección de Wikidata no tiene calle y número legibles; sin comprob: 83; sin dirección ni inscripción en OSM: 61; sin nombre: 13; el nombre de OSM no coincide con la inscripción: 4; OSM marca la posición como dudosa: 4
- **Polonia**: sin nombre: 11; sin dirección ni inscripción en OSM: 8; el nombre contiene cifras: 1; el nombre parece colectivo o de varias personas: 1; el nombre de OSM no coincide con la inscripción: 1; nombre de una sola palabra: 1
- **Eslovenia**: sin nombre: 3; sin dirección ni inscripción en OSM: 2; el nombre de OSM no coincide con la inscripción: 1
- **Eslovaquia**: el nombre de OSM no coincide con la inscripción: 21; nombre de una sola palabra: 13; sin nombre: 9; el nombre parece colectivo o de varias personas: 3; sin dirección ni inscripción en OSM: 2; el nombre contiene cifras: 1
- **Ucrania**: sin nombre: 82; el nombre de OSM no coincide con la inscripción: 3; sin dirección ni inscripción en OSM: 2; el nombre contiene cifras: 2

Lista completa (id, nombre, motivo, coordenada): `pendiente-v20.csv`.

## 4. Las 1.480 piedras de Wikidata sin coordenadas (v14)

Regla: se añade solo si el ítem tiene nombre limpio (y está en su inscripción), su propia imagen (P18) de Commons tiene coordenadas y menciona el nombre, y esa coordenada cae a ≤40 m de un objeto `addr:*` de OSM cuya calle y número aparecen en la foto o en el ítem; sin duplicado a ≤60 m. La posición es la de la foto (aproximada; marcada `gm=commons:coordinates`, con aviso en la ficha).

- **Añadidas: 32** · **pendientes: 1448** (de 1480).
  - el ítem no tiene imagen: 1045
  - la imagen de Commons no tiene coordenadas: 257
  - ningún objeto addr:* de OSM a ≤40 m coincide con la calle y número de la foto/ítem: 91
  - el nombre no está en la inscripción de Wikidata: 23
  - ya hay una placa del mismo nombre a ≤60 m en el mapa: 18
  - la foto: 7
  - sin nombre en Wikidata: 5
  - nombre no válido: nombre genérico con texto que no es un nombre: 2

Detalle por ítem: `pendiente-1480-v20.csv` (resultado, motivo v14 y motivo v20).

## 5. Colocación en la acera (Alemania y países nuevos)

- Alemania: 30314 placas ya bien, **35444 con posición de dibujo ajustada**, 3 dentro de un edificio por indicación de la fuente (nivel −1, Stolperschwellen), 73 para revisar.
- Regla: columna 3D de 1,2 m + chincheta 2D de 12 px (zoom 19) a ≥0,5 m de toda huella de OSM; desplazamiento mínimo hacia la calle, máximo 25 m (+ cuadrícula del grupo); el bucle con la **disposición real de la app** (`_dla/_dlo/_ang` en Chrome) comprueba cada columna y añade holgura por grupo; el bucle se cerró con 45 residuales con holgura <0,5 m (no con 0; ver abajo). Las coordenadas de «Cómo llegar», GeoJSON y KML son las de origen.
- Detalle de las placas movidas o por revisar: `data/sidewalk-v20.json`.

- **Grupos fijos (cambio de la app en v20):** con `meta.layout_pinned` la app ya no empuja ni encoge los grupos de columnas (en la v19 los empujaba hasta 8 m y podía devolver una columna a un edificio). La separación entre grupos la calcula ahora `pipeline/tools/separate20.py` (columnas de grupos distintos a ≥1,8 m salvo casos sin hueco): pares de columnas dibujadas a <1,55 m: de 845 (v19) a 35 tras v20r2 (los 35 restantes son grupos contiguos sin hueco libre para separarlos ≤8 m; los 7 casos «sin solución» de `separate20` están entre ellos).
- **Solver exacto** (`sidewalk20.py`): cada chincheta 2D en su coordenada y cada columna 3D en su casilla de la cuadrícula real (ángulo tomado de la app) a ≥0,5 m de toda huella de OSM; la chincheta 2D se exige además en la casilla de la columna (así miden las auditorías).
- **Comprobación independiente** (`check_layout20.py`, shapely, sobre el volcado de la app real): tras el cierre quedan **45 placas con holgura <0,5 m (DE 42, NL 3)**; el CSV `residuales-acera-v20.csv` tiene **97 filas = 45 de esas + 48 «revisar»** (el solver no halló hueco, pero la comprobación independiente no detecta contacto con ninguna huella) **+ 4 «manzana-dudosa»** (FR `n13041383986`, `n13032352978`, `n13032352980`, DE `Q133230139`: el dibujo queda más cerca de otra calle que la de su dirección; comprobado, sin corregir). Cada fila lleva su motivo. Son grupos grandes en calles sin hueco libre de edificios a ≤25 m; no se mueven más para no falsear su dirección. **Estas placas siguen pendientes de decisión de Carlos** (no se afirma que estén bien colocadas).
- **Tope de 25 m de lo dibujado** (auditoría C): el solver reduce el desplazamiento máximo del grupo en la dispersión de su cuadrícula (grupos de hasta 20 placas); los grupos de más de 20 placas con la misma dirección (campos de Stolpersteine, p. ej. Brahmsallee y Grindelallee en Hamburgo) no caben en 25 m: **25 placas dibujadas a >25 m**, listadas en `excepciones-25m-v20.csv`.
- **Placas sin ningún edificio de OSM a ≤50 m** (tras volver a traer de Overpass las huellas en 120 m de radio para LU, IT, ES, GG, CZ, NL y FR): **57 placas** (sobre todo Sabadell/Terrassa y Trieste: edificios no mapeados o coordenada en calle ancha; GG y CZ rurales); la lista explícita y la distancia al edificio más cercano están en `sin-edificios-v20.csv` (y `sin_edificios_50m` en `tests/sidewalk/footprints-v20.json.gz`). Para ellas la comprobación se hace contra el edificio más cercano que existe en OSM; el test falla si aparece cualquier otra placa sin edificio a ≤50 m. Es una carencia de datos de OSM, no una verificación.
- Las placas «legítimas» según la fuente (solo las 3 con `level=-1`/`location=indoor` en OSM: `n12461266505/6/7`, museo) no se mueven; las otras 57 Stolperschwellen que la v20 inicial eximía **ya se colocan en la acera como cualquier placa** (solo el dibujo; las coordenadas de origen no cambian).

## 6. Auditoría

Los scripts de auditoría y los datos están en `/workspace/audits/countries/v20-indep/` (A: fuente cruda; B: contraste en vivo; C: geometría en vivo + interfaz) y `/workspace/v20-data/`. **Las auditorías independientes las ejecutan auditores distintos del constructor**; sus informes irán a `/workspace/audits/countries/v20-indep/{A,B,C}/`.

## 6b. Pruebas ejecutadas (por el constructor, no son auditorías independientes)

- `tests/run-all.sh` con `REQUIRE_OAV=1` en un venv nuevo (`tests/requirements-ci.txt`, **sin** `SKIP_COUNTRY_BUTTONS`): unitarias del pipeline (58 de inscripción), `v20-added-test`, `v20r2-data-check` (nuevo: 6.177 placas añadidas; ciudad ≠ país/calle, sin multipersonas ni rótulos, imágenes existentes en Commons, fechas frente a la inscripción, nombre exacto en la inscripción, duplicados ≤15 m), ai-door-check, ai-sim, sidewalk-render-check y sidewalk-render-check20 (placas de los países nuevos + 1.500 de Alemania; falla si falta edificio a ≤50 m fuera de `sin-edificios-v20.csv` o si el dibujo está a >25 m fuera de `excepciones-25m-v20.csv`), map2d, fila de países, ficha de Hassall, atribución + axe, y `country-buttons-check` en los 10 tamaños (incl. 844×390, 667×375, 320×568, 360×640, 412×915) para los 27 países. El resultado de la pasada final está en `ESTADO-v20r2.md`.
- Capturas a 412 px: `shots/p412-v20-*.png` (inicio con la fila plegada, fila abierta, vista de NL/FR/AT/NO/CZ, primeros planos 2D y 3D en acera de NL/FR/NO/AT/DE), `shots/v20-shots.json`.

## 7. Archivos

- `data/stones.json` (con `dla`/`dlo`), `data/v20-added-20261120.json` (manifiesto), `data/sidewalk-v20.json`, `pendiente-v20.csv`, `pendiente-1480-v20.csv`, `INFORME-v20-personas.csv`.
- Código: `pipeline/tools/{v20_common,build_v20,merge_v20,verify1480,sidewalk20,ui20,make_informe20}.py`.
