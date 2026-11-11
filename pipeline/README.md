# pipeline/ — datos abiertos de la Lista Kauffmann

Convierte las fuentes de datos (hoy: `data/stones.json` + `data/bio/`, Wikidata y, opcionalmente, OpenStreetMap
fuera de Alemania; mañana: Yad Vashem, Arolsen, USHMM y el Gedenkbuch del Bundesarchiv cuando haya permiso) en un
**registro común de persona** y lo publica como **API estática** (JSON en GitHub Pages) para el frontend y para
agentes de IA. Solo usa la librería estándar de Python (3.9+). No modifica `data/stones.json` ni `data/bio/`.

## Qué genera

| Ruta | Qué es | Licencia |
|---|---|---|
| `api/v1/index.json` | Catálogo para agentes: familias, endpoints, reglas de uso, fecha | CC0 (documentación) |
| `api/v1/openapi.json` | OpenAPI 3.1 de los archivos estáticos (GET) | CC0 |
| `api/v1/stats.json` | Estadísticas e informe de políticas aplicadas | CC0 |
| `api/v1/schema/person.schema.json` | Esquema del registro de persona | CC0 |
| `api/v1/odbl/…` | Familia ODbL: Stolpersteine (OSM + Wikidata) | ODbL 1.0 |
| `api/v1/cc0/…` | Familia CC0: personas solo de Wikidata | CC0 1.0 |
| `api/v1/partners/<fuente>/…` | Una familia por institución (fase 2), solo con permiso | la de cada institución |
| `data/search/index-<prefijo>.json` | Índice de **placas** para el mapa (solo lo que dice la placa) | ODbL 1.0 |
| `llms.txt`, `.well-known/api-catalog` | Descripción para agentes (RFC 9727 linkset) | CC0 |

Dentro de cada familia `<f>`:

- `<f>/index.json` — prefijos, regla de particionado, endpoints, meta con licencia y fuentes.
- `<f>/people/by-surname/<prefijo>.json` — **fichas completas** (archivo canónico; ≤ ~1 MB).
- `<f>/search/index-<prefijo>.json` — filas ligeras `[id, name, birth_year, locality, lat, lon, people_prefix]`.
- `<f>/person/<shard>.json` — búsqueda por id: filas `[id, people_prefix]`; `shard` = 2 últimos caracteres del id.
- `<f>/places/index.json` y `<f>/places/<país>/<slug>.json` (páginas extra `<slug>~2.json`…) — solo lugar del
  memorial y lugar de muerte (nunca por origen).
- `<f>/ids/<esquema>.json` — tabla de cruce `id externo → ids de persona` (wikidata, gedenkbuch, yad_vashem, ushmm…).
- `<f>/quality/possible-duplicates.json` y `blocked-merges.json` — informe de calidad (nada se fusiona por nombre).
- `<f>/stats.json`.

Todos los JSON de datos llevan `meta.license`, `meta.attribution`, `meta.source_url` y `meta.generated`. Las salidas
son deterministas (claves ordenadas, un registro por línea, fecha = la del snapshot de datos), así que un build
repetido no cambia ningún byte y los diffs de git muestran solo registros cambiados.

## Cómo se corre (desde la raíz del repo)

1. Pruebas: `python3 -m unittest`
2. Build completo sin red (datos actuales del sitio): `python3 -m pipeline build --sources stolpersteine_de --offline`
3. Validar lo generado: `python3 -m pipeline validate`
4. Prueba rápida con red de Wikidata (a otra carpeta, sin tocar el sitio):
   `python3 -m pipeline build --sources wikidata_holocaust_victims --limit 40 --out /tmp/kl-wd --no-site`
5. Build de todas las fuentes activadas (`enabled: true`): `python3 -m pipeline build`
6. Revisar informes internos (no publicados): `pipeline/reports/build.json` y `pipeline/reports/license_gate.json`
   (los tests escriben sus informes en un directorio temporal; después de `python3 -m unittest` no hace falta nada).

**Build completo con Wikidata (pendiente de decisión; ~130.000 personas en `cc0/`, unos 30–60 min la primera vez,
luego desde caché):**
`python3 -m pipeline build --sources stolpersteine_de,wikidata_holocaust_victims && python3 -m pipeline validate`

Opciones: `--limit N` (registros por fuente), `--offline` (solo caché `pipeline/cache/`), `--out DIR`, `--no-site`
(no escribe `llms.txt`, `.well-known/` ni `data/search/`), `--fixture fuente=ruta` (archivo de prueba en vez de
red), `--strict` (falla si una fuente no se puede leer; por defecto se omite y se informa), `--generated AAAA-MM-DD`.

Atención: el build **publica exactamente las fuentes seleccionadas**: `api/v1/` se regenera entero (solo se borra si
lleva el marcador `.generated-by-kauffmann-pipeline`; nunca borra un directorio ajeno).

Red: User-Agent genérico `KauffmannList-pipeline/1.0`, caché en disco (`pipeline/cache/`, ignorada por git),
reintentos con espera exponencial (respeta `Retry-After` en 429/503) y un intervalo mínimo entre peticiones por
fuente (`network.min_interval_seconds`). Wikidata se pagina por selector (`ORDER BY ?item LIMIT/OFFSET`) y el
detalle se pide en lotes de 150 Qids con `VALUES`.

## Fuentes (`pipeline/sources/*.json`)

| Fuente | Fase | Activa | Publicable | Adaptador | Familia |
|---|---|---|---|---|---|
| `stolpersteine_de` | 1 | sí | sí | `stones` | odbl |
| `wikidata_holocaust_victims` | 1 | sí (red) | sí | `wikidata_sparql` | cc0 |

`wikidata_holocaust_victims` selecciona personas con id en holocaust.cz, Gedenkbuch, USHMM, Yad Vashem, Arolsen o
Joods Monument. **Tener uno de esos ids no implica haber muerto** (USHMM incluye supervivientes): `fate` solo se marca
con P1196 y, sin fecha de muerte, se aplica el filtro de posibles vivos. Mapping the Lives (P9805, censo de 1939) no se
usa porque no es una lista de víctimas.
| `osm_stolpersteine_europe` | 1 | no (Overpass pesado) | sí | `overpass` | odbl |
| `yadvashem`, `arolsen`, `ushmm`, `bundesarchiv_gedenkbuch` | 2 | no | **no** | `generic_tabular` | partners/<fuente> |

Campos de cada configuración: `id`, `name`, `phase`, `enabled`, `publish_allowed`, `adapter`, `license`,
`license_url`, `attribution`, `homepage`, `license_family`, `id_prefix`, `priority` (menor = gana en conflictos de
campo), y lo específico del adaptador (`input`, `mapping`, `endpoint`, `selectors`, `network`…).

## Cómo añadir una fuente de fase 2 (sin escribir código)

1. Guardar el archivo recibido en `pipeline/inbox/<fuente>.csv` (o `.json`/`.jsonl`; `pipeline/inbox/` está en
   `.gitignore`: los datos de socios nunca se suben sin permiso). Si llega como API, poner `input.url` en vez de
   `input.path`.
2. Abrir `pipeline/sources/<fuente>.json` (ya existen plantillas para las cuatro instituciones) y ajustar
   `input` (`format`, `delimiter`, `encoding`, `records_path` para JSON anidado, `retrieved`) y `mapping`: cada campo
   del registro común apunta a una columna. Formas admitidas:
   - `"Columna"` o `"a.b.c"` (ruta en JSON anidado)
   - `{"column": "Col", "format": "date|year|number|upper|lower", "map": {...}, "default": "...", "split": ";", "template": "https://…/{value}"}`
   - `{"concat": ["Nombre", "Apellido"], "sep": " "}`, `{"first": [spec, spec]}`, `{"const": "DE"}`,
     `{"template": "https://…/{Item ID}"}`
   - listas: `places` (`role`, `label`, `lat`, `lon`, `country`), `deportations` (`date`, `place`, `from`, `raw`),
     `links` (`type`, `url`), e `identifiers` (`wikidata`, `yad_vashem`, `arolsen`, `ushmm`, `gedenkbuch`…).
3. Rellenar `license`, `license_url` y `attribution` con los términos exactos del permiso.
4. Probar sin publicar: `python3 -m pipeline build --sources stolpersteine_de,<fuente> --out /tmp/kl-test` con
   `enabled: true` y `publish_allowed: false` → `pipeline/reports/license_gate.json` muestra cuántos registros se
   leyeron y retuvieron.
5. Solo cuando haya **permiso escrito**: `"publish_allowed": true`, y build normal. La fuente aparece en
   `api/v1/partners/<fuente>/` con su licencia; nunca se mezcla con la familia ODbL.

La validación de configuración impide errores de licencia: una fuente de fase 2 debe tener
`license_family = "partners/<su id>"`.

## Políticas que aplica el build (docs/legal/analisis-licencias.md §4)

1. **Gate de licencia**: los registros de fuentes con `publish_allowed: false` se descartan *antes* del merge (ni
   siquiera influyen en qué registros se unen). `python3 -m pipeline validate` comprueba que no aparecen.
2. **Familias de licencia separadas**: el merge solo ocurre dentro de una familia. Odbl, cc0 y cada socio son árboles
   distintos; se cruzan solo por identificador (`ids/wikidata.json`, `ids/gedenkbuch.json`…), y la unión se hace en
   el navegador. Los extractos de Wikipedia (CC BY-SA) no se copian: solo el permalink.
3. **Posibles vivos fuera de la API**: sin indicio de muerte (fecha de muerte, o placa con ERMORDET/TOT/…) y con
   nacimiento hace menos de 110 años (respecto al año de los datos) o desconocido → no se publica la ficha. La placa
   sigue en `data/search/` (solo el texto de la placa).
4. **Supervivientes**: placa con ÜBERLEBT/FLUCHT/BEFREIT/ENTKAM (y variantes; "Flucht in den Tod" no cuenta) y
   nacimiento ≥ 1916 o desconocido → sin enlaces a fichas ni ids de registros (`restrictions: ["survivor_minimization"]`).
5. **Sin terceros**: solo se publica lo que dice la placa o la fuente estructurada; ningún texto biográfico.
6. **Calidad de fechas**: nacimiento < 1800 o posterior al año de los datos, muerte < 1800 o posterior, o nacimiento
   posterior a la muerte → el dato NO se corrige; se marca en `quality_flags` de la ficha, se cuenta en `stats.json` y
   se lista en `<familia>/quality/date-flags.json`.
7. **Supervivencia frente a muerte** (`inscription.py`): las marcas de supervivencia se reconocen como prefijo de
   palabra (überlebt/überlebte/ueberlebte, gerettet, befreit, entkam/entkommen, versteckt; huida: Flucht…, geflohen,
   emigriert). Con marca de supervivencia/huida, las palabras de muerte "débiles" (tot, Tod, Todesmarsch, gestorben,
   starb, umgekommen…) solo cuentan si van con fecha ("tot 28.2.1945"); si no → `survived` (o `fled` si solo hay
   huida). Excepción deliberada: un asesinato explícito (ermordet, hingerichtet, erschossen, vergast…) cuenta aunque no
   lleve fecha ("FLUCHT 1939 HOLLAND … AUSCHWITZ ERMORDET"), porque convertir en superviviente a una persona asesinada
   sería el error más grave. "Versuchte Flucht in den Tod … überlebt" es un intento, no un suicidio.
8. **Nunca inferir**: `given_name`/`family_name` solo si la fuente los da; el apellido usado para particionar es una
   heurística interna que no se publica; fechas de Wikidata con precisión de década o peor no se convierten en año;
   si Wikidata da dos apellidos distintos no se elige uno. `fate` sale solo de palabras escritas en la placa o del
   campo de la fuente (`fate_basis`), y los valores que discrepan se guardan en `variants`.
9. **Sin índices por origen o religión**: lugares solo por memorial y por lugar de muerte.
10. **Alcance exacto** (también en `index.json` → `scope` y en `llms.txt`): la API de personas (`api/v1`) excluye a
    los posibles vivos. `data/search/` y `data/stones.json` NO son fichas de personas sino transcripciones de placas
    públicas e incluyen TODAS las placas; `data/search/` solo lleva nombre de la placa, dirección, coordenadas y año
    (`jg` solo si la placa dice "Jg."), sin enlaces ni destino.

## Retiradas (`pipeline/suppressed.json`)

1. Recibir la petición (familiar, error grave, petición de una institución). Plazo objetivo ≤ 14 días.
2. Añadir el id a `"ids"` en `pipeline/suppressed.json` — **solo ids**, nunca motivos ni datos personales. Formatos:
   - id de persona: `st-n123…`, `wd-Q…`, `yv-…`
   - id de la placa: nodo/vía OSM `n123…`/`w123…` o Qid de la placa en Wikidata
   - Qid de la persona: `Q123…`
   - id externo `<esquema>:<id>`: `gedenkbuch:851018`, `yad_vashem:…`, `ushmm:…`, `arolsen:…`, `holocaust_cz:…`

   Los ids de nodo OSM pueden cambiar (se borra y se vuelve a crear el nodo); por eso conviene retirar además por
   Qid o por id externo cuando existan.
3. `python3 -m pipeline build --sources stolpersteine_de --offline && python3 -m pipeline validate` (la validación
   falla si un id retirado sigue presente) y commit.
4. Retirar un id elimina a la persona entera (todas sus placas) de `api/v1/` y de `data/search/`. `data/stones.json`
   lo genera otro proceso fuera de este repo: avisar también allí y, si procede, corregir en OSM/Wikidata.

## Decisión de arquitectura (ADR-001)

**Contexto.** GitHub Pages solo sirve archivos estáticos; el repo ya pesa ~55 MB de datos; habrá 60.000–200.000
personas; varias licencias incompatibles (ODbL con share-alike, CC0, CC BY-SA y licencias propietarias de socios);
los agentes de IA necesitan JSON predecible; git debe seguir siendo manejable.

**Decisión.**
- Un árbol por **familia de licencia** (`odbl/`, `cc0/`, `partners/<x>/`), sin fusionar registros entre familias;
  cruce solo por id.
- Fichas completas **una sola vez**, en archivos por prefijo de apellido normalizado, divididos de forma adaptativa
  (1 a 6 letras) hasta ≤ 650 fichas (~1 MB); búsqueda por id mediante 100 tablas pequeñas `person/<2 últimos
  caracteres>.json`; índice de búsqueda ligero aparte con prefijos más gruesos (≤ 4.000 filas).
- Un registro por línea y claves ordenadas → salidas deterministas y diffs limpios.
- Conectores de fase 2 por configuración declarativa (`generic_tabular`), sin código nuevo.

**Alternativas descartadas.**
- *Un archivo por persona* (`person/<shard>/<id>.json`): ~56.000–200.000 archivos; clones y checkouts lentos, cada
  build reescribe miles de archivos y GitHub Pages tarda en desplegar. Descartado.
- *Fichas completas por id y resúmenes por apellido*: duplicaba los datos (~145 MB). Descartado tras medirlo.
- *Un JSON único / SQLite en el navegador*: obliga a bajar decenas de MB, igual que hoy `stones.json`.
- *Fusionar socios con OSM en un solo objeto*: arrastraría sus datos al share-alike ODbL (riesgo R3 del análisis legal).
- *Servidor/API dinámica*: coste y mantenimiento; contrario al sitio estático sin cookies.

**Consecuencias.**
- Build completo actual: **56.451 fichas** publicadas (64.576 placas → 63.911 personas tras unir por Qid/ids;
  7.460 posibles vivos excluidos; 1.120 fichas de supervivientes minimizadas), **2.268 archivos, 92 MB** en
  `api/v1` (máximo 1,03 MB) + 102 archivos y 7,8 MB en `data/search/`. Pages sirve gzip (~5× menos en red).
- Una consulta típica de agente = 1–2 GET de ≤ 1 MB. Una búsqueda del frontend = 1 GET de ~50–300 KB.
- El peso total crecerá con Wikidata completo (~133.000 personas en `cc0/`): si el repo se vuelve incómodo, mover
  `api/` a una rama `gh-pages` generada por CI sin cambiar las URLs.
- El id de persona es `wd-<Qid>` si hay Qid; si no, `<prefijo de fuente>-<id de registro>`. Si una placa gana un
  Qid su id cambia; el anterior queda en `alternate_ids`.

## Cambio que necesitará el frontend (fase siguiente; aún NO aplicado)

Hoy `app3d.js` (`load()`, línea ~334) y `2d/app.js` (línea ~44) descargan `data/stones.json` (23 MB) entero para
buscar y pintar. Cambio propuesto para la **búsqueda**:

1. Al arrancar, `fetch('data/search/manifest.json')` → lista `prefixes`.
2. En `search()`: normalizar cada token de la consulta con la misma `norm()` (sin la regla `str→strasse`), quitar
   partículas (`von`, `van`, `de`…) y para cada token de ≥ 2 letras calcular el prefijo:
   `for (n=6;n>=1;n--){ c=(tok+'______').slice(0,n); if (prefixes.has(c)) return c; } return '_';`
   Descargar (con caché en memoria) `data/search/index-<prefijo>.json` de cada token (normalmente 1–2 archivos de
   50–450 KB) y aplicar sobre `rows` el mismo algoritmo de puntuación actual (`lev`, `startsWith`…), usando las
   columnas `[stone_id, name, address, locality, lat, lon, jg, person_id]`.
3. Limitación: el índice se parte por apellido; buscar solo por nombre de pila o solo por calle exige otro índice
   (por ejemplo `places/`); mientras tanto el frontend puede seguir usando `stones.json` como respaldo para esas
   búsquedas.
4. Ficha: si `person_id` no es null, mostrar datos y enlaces de `api/v1/odbl/person/<shard>.json` →
   `people/by-surname/<people_prefix>.json`; si es null (posible vivo), mostrar solo el texto de la placa. Si existe
   una familia `cc0/` o `partners/<x>/`, buscar el Qid en su `ids/wikidata.json` y unir **en el navegador**.
5. El **mapa** (los 64.576 puntos) sigue necesitando coordenadas de todas las placas: hasta tener teselas vectoriales,
   puede seguir con `stones.json` o con la unión de todos los `data/search/index-*.json` (7,8 MB en total).
6. Añadir en el pie del mapa el aviso ODbL y el enlace a la base descargable (`data/stones.json`).

## Estructura del código

- `__main__.py` CLI · `build.py` orquestación y escritura · `merge.py` unificación por familia · `policy.py` gate de
  licencia, retiradas, vivos, supervivientes · `inscription.py` extracción literal de placas · `agents.py`
  catálogo, OpenAPI, `llms.txt`, `api-catalog` · `validate.py` validación de salida · `jsonschema_lite.py` validador
  de esquema sin dependencias · `http.py` cliente con caché/reintentos · `config.py` carga de fuentes y familias ·
  `adapters/` (`stones`, `wikidata_sparql`, `overpass`, `generic_tabular`) · `tests/` (unittest + fixtures).
