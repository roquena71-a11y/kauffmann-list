# INFORME v20 — países nuevos, colocación en la acera (Alemania incluida) y las 1.480 de Wikidata

Generado 2026-11-20 05:52 (hora de Berlín). Prototipo local sobre la v19 publicada (commit 49e7725). **Nada publicado, sin push.**

## 1. Resumen

- Total de placas en el mapa: **72.273** (v19: 65.861; **+6.412**). 27 países con placas.
- Nuevas por país (países nuevos + las 32 de las 1.480 en Alemania): Países Bajos 1367 · Austria 1193 · Francia 1172 · Chequia 604 · Noruega 583 · Italia 443 · España 342 · Bélgica 175 · Luxemburgo 164 · Hungría 93 · Lituania 70 · Suiza 53 · Eslovaquia 34 · Alemania 32 · Polonia 32 · Croacia 17 · Dinamarca 14 · Guernsey 8 · Andorra 7 · Letonia 4 · Reino Unido 3 · Liechtenstein 2
- Datos abiertos únicamente: OpenStreetMap (ODbL; Geofabrik europe 2026-11-18 ~21:21 UTC, refrescado por id con Overpass el 2026-11-20) y Wikidata (CC0, consulta del 2026-11-20). Sin nombres de archivos cerrados.
- Las coordenadas de origen (`la`/`lo`) no se tocan nunca; la posición de dibujo va en `dla`/`dlo`.
- Cada placa nueva cumple: nombre limpio (solo se quitan prefijos literales como «Stolperstein für»), nombre contenido en la inscripción, dirección etiquetada contrastada con objetos `addr:*` de OSM (≤40 m; sin calle ≤25 m) o con la coordenada de la foto de Commons, sin `fixme` de posición sin comprobar, fusión OSM–Wikidata solo si ≤50 m y nombre compatible. Lo dudoso va a `pendiente-v20.csv` con su motivo.
- Regla de «posible superviviente / vivo»: igual que en la v19 (`policy.py`, 110 años; marcadores multilingües de superviviente en `pipeline/inscription.py`).

## Notas de la versión v20 (para publicar)

- **27 países**: Alemania y 26 más de Europa (Países Bajos, Austria, Francia, Chequia, Noruega, Italia, España, Bélgica, Luxemburgo, Hungría, Lituania, Suiza, Polonia, Eslovaquia, Jersey, Croacia, Dinamarca, Guernsey, Finlandia, Andorra, Irlanda, Suecia, Letonia, Reino Unido, Rumanía y Liechtenstein). Botones de país y búsqueda en español, alemán e inglés; la fila de países se pliega en «Más países (N)».
- **+6.412 placas** verificables con datos abiertos (OSM ODbL + Wikidata CC0), cada una con enlace a su fuente; los casos dudosos quedan en pendiente con su motivo.
- **Todas las placas fuera de los edificios**: Alemania incluida, la posición de dibujo (`dla`/`dlo`) va a la acera con ≥0,5 m de holgura (salvo 36 placas residuales documentadas en `residuales-acera-v20.csv`); la coordenada de origen no se toca y es la que usan «Cómo llegar» y las descargas.
- Piedras con posición deducida de la foto de Commons: aviso «posición aproximada» propio. Regla de «posible superviviente» sin cambios.
- Caché del navegador: `kauffmann-v20-pages`.

## 2. Placas por país

| País | En el mapa | Nuevas v20 | Objetos OSM | Ítems WD | Pendientes (motivo en CSV) | Acera: ya bien | Acera: ajustadas | Dentro legítimo | Para revisar | Mayor desplazamiento (m) |
|--|--|--|--|--|--|--|--|--|--|--|
| Alemania (DE) | 65837 | 32 | — | — | — | 30328 | 35442 | 9 | 58 | 24.9 |
| Países Bajos (NL) | 1367 | 1367 | 2731 | 54 | 1403 | 345 | 1018 | 0 | 4 | 22.55 |
| Austria (AT) | 1197 | 1193 | 1502 | 149 | 396 | 654 | 543 | 0 | 0 | 17.7 |
| Francia (FR) | 1172 | 1172 | 1362 | 320 | 266 | 354 | 818 | 0 | 0 | 19.85 |
| Chequia (CZ) | 604 | 604 | 2156 | 1525 | 2941 | 170 | 434 | 0 | 0 | 18.7 |
| Noruega (NO) | 583 | 583 | 158 | 759 | 280 | 172 | 411 | 0 | 0 | 18.35 |
| Italia (IT) | 443 | 443 | 561 | 167 | 275 | 218 | 225 | 0 | 0 | 21.1 |
| España (ES) | 342 | 342 | 434 | 114 | 130 | 165 | 177 | 0 | 0 | 20.8 |
| Bélgica (BE) | 175 | 175 | 238 | 52 | 115 | 49 | 126 | 0 | 0 | 21.5 |
| Luxemburgo (LU) | 170 | 164 | 175 | 4 | 6 | 107 | 63 | 0 | 0 | 2.45 |
| Hungría (HU) | 93 | 93 | 371 | 10 | 288 | 64 | 29 | 0 | 0 | 6.75 |
| Lituania (LT) | 70 | 70 | 74 | 0 | 4 | 50 | 20 | 0 | 0 | 1.15 |
| Suiza (CH) | 55 | 53 | 38 | 68 | 25 | 36 | 19 | 0 | 0 | 2.6 |
| Polonia (PL) | 35 | 32 | 53 | 7 | 22 | 10 | 25 | 0 | 0 | 6.15 |
| Eslovaquia (SK) | 34 | 34 | 83 | 1 | 50 | 28 | 6 | 0 | 0 | 1.05 |
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
- **Austria**: sin nombre: 141; el nombre de OSM no coincide con la inscripción: 93; el nombre parece colectivo o de varias personas: 48; la dirección de Wikidata no tiene calle y número legibles; sin comprob: 33; el nombre contiene cifras: 26; sin coordenadas P625 únicas en Wikidata: 18
- **Bélgica**: sin coordenadas P625 únicas en Wikidata: 50; sin nombre: 28; sin dirección ni inscripción en OSM: 20; OSM marca la posición como dudosa: 6; el nombre parece colectivo o de varias personas: 5; la dirección etiquetada existe en OSM pero a 90 m de la posición de la: 2
- **Suiza**: la dirección de Wikidata no tiene calle y número legibles; sin comprob: 8; sin dirección ni inscripción en OSM: 4; Wikidata trae varias direcciones o inscripciones distintas: 4; el nombre de OSM no coincide con la inscripción: 3; la coordenada de Wikidata no se confirma con una dirección de OSM ni c: 3; el nombre de Wikidata no coincide con su inscripción: 2
- **Chequia**: sin dirección ni inscripción en OSM: 1559; el ítem de Wikidata no es una piedra de una persona con nombre: 1126; sin dirección P6375 ni inscripción P1684 en Wikidata: 123; sin coordenadas P625 únicas en Wikidata: 66; sin nombre: 14; el nombre parece colectivo o de varias personas: 14
- **Dinamarca**: sin nombre: 13; sin coordenadas P625 únicas en Wikidata: 10; OSM marca la posición como dudosa: 3; sin dirección P6375 ni inscripción P1684 en Wikidata: 3; la coordenada de Wikidata no se confirma con una dirección de OSM ni c: 2; nombre de una sola palabra: 1
- **España**: sin dirección ni inscripción en OSM: 37; el nombre parece colectivo o de varias personas: 24; el ítem de Wikidata no es una piedra de una persona con nombre: 17; sin dirección P6375 ni inscripción P1684 en Wikidata: 14; sin nombre: 13; OSM y Wikidata: 7
- **Francia**: OSM marca la posición como dudosa: 149; sin nombre: 55; la coordenada de Wikidata no se confirma con una dirección de OSM ni c: 19; el nombre de OSM no coincide con la inscripción: 8; sin coordenadas P625 únicas en Wikidata: 8; la dirección etiquetada existe en OSM pero a 45 m de la posición de la: 5
- **Reino Unido**: sin dirección ni inscripción en OSM: 1
- **Guernsey**: OSM marca la posición como dudosa: 20; sin coordenadas P625 únicas en Wikidata: 1
- **Grecia**: el nombre de OSM no coincide con la inscripción: 5; sin nombre: 2
- **Croacia**: sin dirección ni inscripción en OSM: 28; el nombre contiene cifras: 1; sin coordenadas P625 únicas en Wikidata: 1
- **Hungría**: sin nombre: 252; sin dirección ni inscripción en OSM: 18; OSM marca la posición como dudosa: 8; sin dirección P6375 ni inscripción P1684 en Wikidata: 3; la coordenada de Wikidata no se confirma con una dirección de OSM ni c: 3; el nombre de OSM no coincide con la inscripción: 2
- **Italia**: sin dirección ni inscripción en OSM: 75; la dirección de Wikidata no tiene calle y número legibles; sin comprob: 69; sin nombre: 57; la coordenada de Wikidata no se confirma con una dirección de OSM ni c: 21; el nombre de OSM no coincide con la inscripción: 20; nombre genérico con texto que no es un nombre: 11
- **Lituania**: la dirección etiquetada existe en OSM pero a 43 m de la posición de la: 2; la dirección etiquetada existe en OSM pero a 47 m de la posición de la: 1; el nombre de OSM no coincide con la inscripción: 1
- **Luxemburgo**: el nombre de OSM no coincide con la inscripción: 2; la foto de Commons está a 480 m de la posición de la placa en OSM: 2; Stolperschwelle: 1; la dirección de Wikidata no tiene calle y número legibles; sin comprob: 1
- **Países Bajos**: sin nombre: 927; sin dirección ni inscripción en OSM: 351; el nombre de OSM no coincide con la inscripción: 28; propuesta: 21; el ítem de Wikidata no es una piedra de una persona con nombre: 15; el nombre parece colectivo o de varias personas: 13
- **Noruega**: la coordenada de Wikidata no se confirma con una dirección de OSM ni c: 107; la dirección de Wikidata no tiene calle y número legibles; sin comprob: 83; sin dirección ni inscripción en OSM: 62; sin nombre: 13; OSM marca la posición como dudosa: 4; el nombre contiene cifras: 2
- **Polonia**: sin nombre: 11; sin dirección ni inscripción en OSM: 8; el nombre contiene cifras: 1; el nombre parece colectivo o de varias personas: 1; la dirección de Wikidata no tiene calle y número legibles; sin comprob: 1
- **Eslovenia**: sin nombre: 3; sin dirección ni inscripción en OSM: 2; el nombre de OSM no coincide con la inscripción: 1
- **Eslovaquia**: el nombre de OSM no coincide con la inscripción: 20; nombre de una sola palabra: 13; sin nombre: 9; el nombre parece colectivo o de varias personas: 3; sin dirección ni inscripción en OSM: 2; el nombre contiene cifras: 1
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

- Alemania: 30328 placas ya bien, **35442 con posición de dibujo ajustada**, 9 dentro de un edificio por indicación de la fuente (nivel −1, Stolperschwellen), 58 para revisar.
- Regla: columna 3D de 1,2 m + chincheta 2D de 12 px (zoom 19) a ≥0,5 m de toda huella de OSM; desplazamiento mínimo hacia la calle, máximo 25 m (+ cuadrícula del grupo); el bucle con la **disposición real de la app** (`_dla/_dlo/_ang` en Chrome) comprueba cada columna y añade holgura por grupo; el bucle se cerró con 36 residuales documentados (ver abajo), no con 0. Las coordenadas de «Cómo llegar», GeoJSON y KML son las de origen.
- Detalle de las placas movidas o por revisar: `data/sidewalk-v20.json`.

- **Grupos fijos (cambio de la app en v20):** con `meta.layout_pinned` la app ya no empuja ni encoge los grupos de columnas (en la v19 los empujaba hasta 8 m y podía devolver una columna a un edificio). La separación entre grupos la calcula ahora `pipeline/tools/separate20.py` (columnas de grupos distintos a ≥1,8 m salvo casos sin hueco): pares de columnas a <1,55 m pasaron de 845 a 68.
- **Solver exacto** (`sidewalk20.py`): cada chincheta 2D en su coordenada y cada columna 3D en su casilla de la cuadrícula real (ángulo tomado de la app) a ≥0,5 m de toda huella de OSM; la chincheta 2D se exige además en la casilla de la columna (así miden las auditorías).
- **Comprobación independiente** (`/workspace/v20-data/tools/check_layout20.py`, shapely, sobre el volcado de la app real): tras el cierre quedan **36 placas con holgura <0,5 m (33 Alemania, 3 Países Bajos)** y 26 «revisar» sin solape detectado; todas listadas con motivo y déficit en `residuales-acera-v20.csv` (grupos grandes sin hueco en la acera a ≤25 m, p. ej. 10 placas en una calle estrecha). No se ha movido ninguna de ellas más allá de 25 m para no falsear su dirección.
- Las placas «legítimas» según la fuente (OSM nivel −1 / Stolperschwellen; lista de 60 en `legit_inside.json`) no se mueven; el solver marca «legítima» solo a las que de verdad siguen dentro del edificio (9 en Alemania).

## 6. Auditoría

Los scripts de auditoría y los datos están en `/workspace/audits/countries/v20-indep/` (A: fuente cruda; B: contraste en vivo; C: geometría en vivo + interfaz) y `/workspace/v20-data/`. **Las auditorías independientes las ejecutan auditores distintos del constructor**; sus informes irán a `/workspace/audits/countries/v20-indep/{A,B,C}/`.

## 7. Archivos

- `data/stones.json` (con `dla`/`dlo`), `data/v20-added-20261120.json` (manifiesto), `data/sidewalk-v20.json`, `pendiente-v20.csv`, `pendiente-1480-v20.csv`, `INFORME-v20-personas.csv`.
- Código: `pipeline/tools/{v20_common,build_v20,merge_v20,verify1480,sidewalk20,ui20,make_informe20}.py`.
