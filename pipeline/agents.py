"""Capa para agentes de IA: api/v1/index.json, stats.json, openapi.json, /llms.txt y /.well-known/api-catalog."""
import os

from .find import ROW_COLUMNS
from .util import write_json, write_text

SITE = "https://roquena71-a11y.github.io/kauffmann-list"
API = SITE + "/api/v1"
FULL_DOWNLOAD = SITE + "/data/stones.json"
SCOPE = ("La API de personas (api/v1) excluye a las personas posiblemente vivas (sin indicio de muerte y nacidas hace "
         "menos de 110 años, o sin año) y quita los enlaces a fichas de registro de posibles supervivientes nacidos desde 1916. "
         "data/search/ y data/stones.json NO son fichas de personas: son transcripciones de placas públicas (memoriales "
         "físicos en la calle) e incluyen TODAS las placas, también las de personas posiblemente vivas. data/search/ solo "
         "contiene nombre tal como figura en la placa, dirección, coordenadas y año; data/stones.json es la base de placas "
         "completa (OpenStreetMap + Wikidata) con la inscripción y las etiquetas y enlaces que esas placas tienen en "
         "OSM/Wikidata. Para datos de personas usa api/v1.")
DOC_LICENSE = {"name": "CC0-1.0", "url": "https://creativecommons.org/publicdomain/zero/1.0/"}

USAGE_RULES = [
    "Cita siempre: 'Lista Kauffmann' + enlace a la ficha + la fuente original (sources[] de cada registro).",
    "Respeta la licencia de cada familia: ODbL 1.0 (share-alike + atribución '© OpenStreetMap contributors') en odbl/, CC0 en cc0/. Hoy solo se publican esas dos familias; los datos de una institución aparecerían únicamente con su permiso por escrito y su propia licencia.",
    "No combines registros de familias distintas en un mismo objeto para redistribuirlo; crúzalos solo por identificador (Qid de Wikidata o id institucional).",
    "No presentes inferencias como hechos: los datos proceden de placas y bases abiertas y pueden contener errores; remite a la fuente primaria.",
    "Prohibido usar estos datos para acosar, elaborar listas de descendientes, perfiles étnico-religiosos de personas vivas, negacionismo o fines antisemitas.",
    "Usa api/v1 para datos de personas; data/search/ y data/stones.json son transcripciones de placas, no fichas (ver scope).",
]


def _doc_meta(generated):
    return {"license": DOC_LICENSE["name"], "license_url": DOC_LICENSE["url"],
            "attribution": ["Lista Kauffmann (documentación de la API)"], "source_url": SITE + "/",
            "generated": generated,
            "note": "Esta es la licencia del catálogo/documentación. Cada familia de datos lleva su propia licencia (ver families)."}


def write_catalog(w, fam_indexes, fam_stats, families, sources, generated, report, policy):
    fams = {}
    for fid, idx in sorted(fam_indexes.items()):
        fam = families[fid]
        fams[fid] = {
            "path": fid + "/",
            "index": fid + "/index.json",
            "license": fam["license"], "license_url": fam.get("license_url"),
            "attribution": fam.get("attribution"), "description": fam.get("description"),
            "count_people": idx["count_people"],
            "sources": [s["id"] for s in idx["meta"]["sources"]],
            "endpoints": idx["endpoints"],
        }
    catalog = {
        "meta": _doc_meta(generated),
        "name": "Lista Kauffmann – API estática de datos abiertos",
        "description": ("Registros de personas perseguidas por el nacionalsocialismo (Stolpersteine y víctimas de la Shoah), "
                        "como archivos JSON estáticos (GitHub Pages). Sin claves, sin límites, solo GET."),
        "version": "v1",
        "base_url": API + "/",
        "generated": generated,
        "families": fams,
        "license_families_rule": ("Cada familia de licencia es un árbol separado y nunca se mezcla con otra. "
                                  "El cruce entre familias es solo por identificador (ids/<scheme>.json) y se hace en el cliente."),
        "how_to": [
            "RÁPIDO – por nombre, lugar o año: <familia>/find/index.json (manifiesto) → find/name/<prefijo>.json, find/city/index.json → find/city/<país>/<slug>.json, find/year/<birth|death>/<año>.json. Cada fila lleva people_prefix: la ficha con sources[] está en <familia>/people/by-surname/<people_prefix>.json (objeto con ese id). Guía completa: llms-full.txt.",
            "Buscar por apellido: normaliza el apellido (surname_prefix_rule en <familia>/index.json), elige el prefijo de people_prefixes y descarga <familia>/people/by-surname/<prefijo>.json (fichas completas), o el de search_prefixes para <familia>/search/index-<prefijo>.json (ligero).",
            "Por id: calcula el shard (person_shard_rule), descarga <familia>/person/<shard>.json → people_prefix → <familia>/people/by-surname/<people_prefix>.json.",
            "Por lugar: <familia>/places/index.json → <familia>/places/<país>/<slug>.json (si pages>1, páginas <slug>~2.json, <slug>~3.json…).",
            "Cruce con otra familia: <familia>/ids/wikidata.json (u otro esquema) da los ids de persona para un Qid o id institucional.",
        ],
        "schema": "schema/person.schema.json",
        "agent_guide": {"llms_txt": SITE + "/llms.txt", "llms_full_txt": SITE + "/llms-full.txt"},
        "citation": {"template": CITE_TEMPLATE, "person_link": {"odbl": SITE + "/#s={memorials[0].memorial_id}", "cc0": SITE + "/#p={id}"},
                     "record": API + "/<familia>/people/by-surname/{people_prefix}.json (objeto con ese id)",
                     "rule": "Cita 'Lista Kauffmann' + enlace de la ficha + la fuente original (sources[].url) + fecha de los datos + licencia. Solo campos presentes en la ficha."},
        "openapi": "openapi.json",
        "stats": "stats.json",
        "scope": SCOPE,
        "full_database": {"url": FULL_DOWNLOAD, "license": "ODbL-1.0",
                          "note": "Base de placas completa descargable (oferta ODbL §4.6). Es una transcripción de placas públicas, "
                                  "no una base de fichas de personas: para datos de personas usa api/v1."},
        "plaque_index": {"url": SITE + "/data/search/manifest.json", "license": "ODbL-1.0",
                         "note": "Índice de placas para el mapa: texto de la placa (nombre), dirección, coordenadas y año; "
                                 "sin enlaces ni destino. No es la API de personas."},
        "usage_rules": USAGE_RULES,
        "corrections": {"how": "Corrige en OpenStreetMap o Wikidata (fuente original), o pide la retirada de una ficha al proyecto; las retiradas se aplican en el siguiente build mediante pipeline/suppressed.json (solo ids).",
                        "repository": "https://github.com/roquena71-a11y/kauffmann-list"},
        "phase2_sources_pending": sorted(s["id"] for s in sources.values() if s["phase"] == 2 and not s["publish_allowed"]),
    }
    w.json("index.json", catalog)
    total = sum(st["people"] for st in fam_stats.values())
    w.json("stats.json", {"meta": _doc_meta(generated), "generated": generated, "people_total": total,
                          "families": fam_stats, "policy": policy,
                          "note": "people_total suma familias: una misma persona puede aparecer en odbl y en cc0 (enlazadas por Qid)."})
    w.json("openapi.json", openapi(fam_indexes, families, generated))


def _example_meta(fam, fid, generated):
    return {"family": fid, "license": fam["license"], "license_url": fam.get("license_url"),
            "attribution": list(fam.get("attribution") or []), "source_url": fam.get("source_url"), "generated": generated}


def _ex(fam_indexes, fid):
    return (fam_indexes[fid].get("find") or {}).get("example") or {}


# ---------------------------------------------------------------- OpenAPI 3.1

_META_SCHEMA = {"type": "object", "required": ["license", "attribution", "source_url", "generated"], "properties": {
    "family": {"type": "string"}, "license": {"type": "string", "examples": ["ODbL-1.0", "CC0-1.0"]},
    "license_url": {"type": ["string", "null"], "format": "uri"},
    "attribution": {"type": "array", "items": {"type": "string"}},
    "source_url": {"type": "string", "format": "uri"}, "generated": {"type": "string", "format": "date"},
    "catalog": {"type": "string", "format": "uri"}}}


def _rows_schema(cols_desc):
    return {"type": "array", "description": cols_desc, "items": {"type": "array"}}


def _resp(desc, schema, example=None):
    media = {"schema": schema}
    if example is not None:
        media["example"] = example
    return {"200": {"description": desc, "content": {"application/json": media}},
            "404": {"description": "Ese archivo no existe (prefijo, lugar o año sin datos). No es un error del servidor."}}


def _ref(name):
    return {"$ref": "#/components/schemas/" + name}


def openapi(fam_indexes, families, generated):
    paths = {
        "/index.json": {"get": {
            "tags": ["catalog"], "summary": "Catálogo para agentes: familias, licencias, endpoints, reglas de uso",
            "operationId": "getCatalog", "responses": _resp("Catálogo", _ref("Catalog"))}},
        "/stats.json": {"get": {"tags": ["catalog"], "summary": "Estadísticas globales", "operationId": "getStats",
                                "responses": _resp("Estadísticas", {"type": "object"})}},
        "/schema/person.schema.json": {"get": {
            "tags": ["catalog"], "summary": "JSON Schema (2020-12) del registro de persona", "operationId": "getPersonSchema",
            "responses": _resp("JSON Schema", {"type": "object"})}},
    }

    def param(name, desc, enum=None, pattern=None, typ="string", example=None):
        sch = {"type": typ}
        if enum:
            sch["enum"] = enum
        if pattern:
            sch["pattern"] = pattern
        prm = {"name": name, "in": "path", "required": True, "description": desc, "schema": sch}
        if example is not None:
            prm["example"] = example
        return prm

    for fid in sorted(fam_indexes):
        op = fid.replace("/", "_")
        lic = families[fid]["license"]
        tag = [fid]
        p = "/" + fid
        idx = fam_indexes[fid]
        fx = idx.get("find") or {}
        ex = fx.get("example") or {}
        ex_name = ex.get("name") or {}
        ex_city = ex.get("city") or {}
        ex_year = ex.get("year") or {}
        paths[p + "/index.json"] = {"get": {"tags": tag, "summary": "Índice de la familia %s (%s)" % (fid, lic),
                                            "operationId": op + "_index", "responses": _resp("Índice", {"type": "object"})}}
        paths[p + "/stats.json"] = {"get": {"tags": tag, "summary": "Estadísticas (%s)" % lic,
                                            "operationId": op + "_stats", "responses": _resp("Estadísticas", {"type": "object"})}}
        paths[p + "/people/by-surname/{prefix}.json"] = {"get": {
            "tags": tag, "summary": "Fichas completas (Person) por prefijo de apellido (%s)" % lic,
            "operationId": op + "_people", "description": idx["surname_prefix_rule"],
            "parameters": [param("prefix", "Prefijo normalizado (people_prefixes del índice de la familia)", idx["people_prefixes"])],
            "responses": _resp("{meta, prefix, count, people: Person[]}", _ref("PeopleFile"))}}
        paths[p + "/person/{shard}.json"] = {"get": {
            "tags": tag, "summary": "Búsqueda por id: filas [id, people_prefix]", "operationId": op + "_personLookup",
            "description": idx["person_shard_rule"],
            "parameters": [param("shard", "Fragmento", idx["person_shards"])],
            "responses": _resp("{meta, shard, columns, rows}", _ref("TableFile"))}}
        paths[p + "/search/index-{prefix}.json"] = {"get": {
            "tags": tag, "summary": "Índice de búsqueda ligero por apellido (id, name, birth_year, locality, lat, lon, people_prefix)",
            "operationId": op + "_search",
            "parameters": [param("prefix", "Prefijo normalizado (search_prefixes)", idx["search_prefixes"])],
            "responses": _resp("{meta, prefix, columns, rows}", _ref("TableFile"))}}
        paths[p + "/places/index.json"] = {"get": {"tags": tag, "summary": "Lugares (memorial / muerte) con recuento",
                                                   "operationId": op + "_places", "responses": _resp("{meta, columns, rows}", _ref("TableFile"))}}
        paths[p + "/places/{country}/{slug}.json"] = {"get": {
            "tags": tag, "summary": "Personas de un lugar; páginas adicionales como {slug}~2.json",
            "operationId": op + "_place",
            "parameters": [param("country", "ISO 3166-1 alpha-2 en minúsculas", pattern="^[a-z]{2}$", example="de"),
                           param("slug", "slug del lugar (places/index.json); con ~N para la página N", pattern="^[a-z0-9-]+(~[0-9]+)?$")],
            "responses": _resp("{meta, country, slug, label, count, page, pages, columns, rows}", _ref("TableFile"))}}
        paths[p + "/ids/{scheme}.json"] = {"get": {
            "tags": tag, "summary": "Tabla de cruce: id externo → ids de persona en esta familia",
            "operationId": op + "_ids", "parameters": [param("scheme", "Esquema", idx["id_schemes"])],
            "responses": _resp("{meta, scheme, columns, rows}", _ref("TableFile"))}}
        paths[p + "/quality/possible-duplicates.json"] = {"get": {"tags": tag, "summary": "Posibles duplicados (no fusionados)",
                                                                  "operationId": op + "_dups", "responses": _resp("Informe", {"type": "object"})}}
        paths[p + "/quality/blocked-merges.json"] = {"get": {"tags": tag, "summary": "Uniones bloqueadas por conflicto",
                                                             "operationId": op + "_blocked", "responses": _resp("Informe", {"type": "object"})}}
        if not fx:
            continue
        ftag = [fid, "find"]
        paths[p + "/find/index.json"] = {"get": {
            "tags": ftag, "operationId": op + "_findIndex",
            "summary": "Manifiesto de búsqueda: prefijos de nombre, años disponibles y reglas",
            "description": "Empieza aquí para buscar a una persona por nombre, lugar o año.",
            "responses": _resp("Manifiesto", _ref("FindIndex"))}}
        paths[p + "/find/name/{prefix}.json"] = {"get": {
            "tags": ftag, "operationId": op + "_findName",
            "summary": "Personas cuyo nombre contiene una palabra con ese prefijo (%s)" % lic,
            "description": fx.get("rule") if isinstance(fx.get("rule"), str) else
            "Normaliza la palabra con fold(), prueba clave[:6]…clave[:1] y usa el primer prefijo listado en find/index.json → name.prefixes. "
            "Filtra las filas por el primer valor (token). Cada fila apunta a la ficha (people_prefix).",
            "parameters": [param("prefix", "Prefijo (claves de name.prefixes en find/index.json); '_' rellena claves cortas",
                                 pattern="^[a-z_]{1,6}$", example=ex_name.get("prefix"))],
            "responses": _resp("{meta, prefix, columns, rows}", _ref("FindNameFile"),
                               {"meta": _example_meta(families[fid], fid, generated), "prefix": ex_name.get("prefix"),
                                "columns": ["token"] + ROW_COLUMNS, "rows": [ex_name.get("row")]} if ex_name else None)}}
        paths[p + "/find/city/index.json"] = {"get": {
            "tags": ftag, "operationId": op + "_findCityIndex",
            "summary": "Lugares buscables por nombre normalizado (más alias de ciudades conocidas)",
            "responses": _resp("{meta, rule, columns, rows, aliases}", _ref("FindCityIndex"))}}
        paths[p + "/find/city/{country}/{slug}.json"] = {"get": {
            "tags": ftag, "operationId": op + "_findCity",
            "summary": "Personas con memorial o muerte en un lugar (páginas extra {slug}~2.json)",
            "parameters": [param("country", "ISO 3166-1 alpha-2 en minúsculas", pattern="^[a-z]{2}$", example=ex_city.get("country")),
                           param("slug", "slug del lugar (find/city/index.json)", pattern="^[a-z0-9-]+(~[0-9]+)?$",
                                 example=ex_city.get("slug"))],
            "responses": _resp("{meta, country, slug, label, count, page, pages, columns, rows}", _ref("FindCityFile"))}}
        paths[p + "/find/year/{kind}/{year}.json"] = {"get": {
            "tags": ftag, "operationId": op + "_findYear",
            "summary": "Personas por año de nacimiento o de muerte (páginas extra {year}~2.json si count > 4000)",
            "parameters": [param("kind", "birth o death", ["birth", "death"], example=ex_year.get("kind")),
                           param("year", "Año de 4 cifras (solo existen los años con datos; ver find/index.json → year); con ~N la página N",
                                 pattern="^[0-9]{4}(~[0-9]+)?$", example=str(ex_year.get("year")) if ex_year else None)],
            "responses": _resp("{meta, kind, year, count, columns, rows}", _ref("FindYearFile"))}}
    row_desc = ("Cada fila = [id, name, birth_year, death_year, place, people_prefix]. La ficha completa (con sources[]) está en "
                "<familia>/people/by-surname/{people_prefix}.json, objeto con id == fila.id. Enlace humano: odbl → SITE/#s={memorials[0].memorial_id} "
                "(abre la placa en el mapa); cc0 → SITE/#p={id}. `name` puede ser null (memorial anónimo): no cites 'None', escribe 'sin nombre'.")
    name_row_desc = ("Cada fila = [token, id, name, birth_year, death_year, place, people_prefix]: la fila de PersonRow con la palabra del "
                     "nombre que coincidió (token) DELANTE. Filtra por token; el resto como PersonRow.")
    table = {"type": "object", "properties": {"meta": _ref("Meta"), "columns": {"type": "array", "items": {"type": "string"}},
                                              "rows": {"type": "array", "items": {"type": "array"}}}}

    def rowsfile(extra, row="PersonRow", desc=row_desc, columns=None):
        s = {"type": "object", "required": ["meta", "columns", "rows"], "properties": {
            "meta": _ref("Meta"),
            "columns": {"type": "array", "items": {"type": "string"}, **({"const": columns} if columns else {})},
            "rows": {"type": "array", "description": desc, "items": _ref(row)}}}
        s["properties"].update(extra)
        return s
    person_items = [{"type": "string", "description": "id de la persona (p. ej. wd-Q123 o st-n123)"},
                    {"type": ["string", "null"], "description": "nombre tal como lo da la fuente; null en memoriales anónimos"},
                    {"type": ["integer", "null"], "description": "año de nacimiento"},
                    {"type": ["integer", "null"], "description": "año de muerte"},
                    {"type": ["string", "null"], "description": "lugar del memorial o de muerte (nunca el de nacimiento)"},
                    {"type": "string", "description": "prefijo del archivo people/by-surname donde está la ficha"}]
    return {
        "openapi": "3.1.0",
        "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
        "info": {"title": "Lista Kauffmann – API estática", "version": "1.1.0",
                 "summary": "Datos abiertos de Stolpersteine y víctimas de la Shoah como archivos JSON (solo GET).",
                 "description": ("Archivos JSON estáticos servidos por GitHub Pages: sin claves, sin límites propios, sin servidor. "
                                 "Cada archivo lleva su licencia en meta.license (ODbL-1.0 en odbl/, CC0-1.0 en cc0/). "
                                 "Cita siempre 'Lista Kauffmann', el enlace de la ficha y la fuente original (sources[]). "
                                 "No inventes datos: si un campo no existe, di que no consta. Guía paso a paso: "
                                 + SITE + "/llms.txt y " + SITE + "/llms-full.txt. "
                                 "Lema: Cada placa, cada nombre, cada historia. Nunca olvidar."),
                 "contact": {"name": "Lista Kauffmann", "url": "https://github.com/roquena71-a11y/kauffmann-list"},
                 "license": {"name": "CC0-1.0 (esta descripción); datos: ver meta.license de cada archivo",
                             "identifier": "CC0-1.0"}},
        "externalDocs": {"description": "Instrucciones para agentes (llms.txt)", "url": SITE + "/llms.txt"},
        "servers": [{"url": API, "description": "GitHub Pages (estático)"}],
        "tags": [{"name": "catalog", "description": "Catálogo, esquema y estadísticas"}] +
                [{"name": "find", "description": "Búsqueda precalculada por nombre, lugar y año"}] +
                [{"name": f, "description": "Familia de licencia " + families[f]["license"]} for f in sorted(fam_indexes)],
        "paths": paths,
        "components": {"schemas": {
            "Meta": _META_SCHEMA,
            "Person": {"$ref": API + "/schema/person.schema.json"},
            "Catalog": {"type": "object", "properties": {"meta": _ref("Meta"), "families": {"type": "object"},
                                                         "how_to": {"type": "array", "items": {"type": "string"}},
                                                         "usage_rules": {"type": "array", "items": {"type": "string"}}}},
            "PeopleFile": {"type": "object", "properties": {
                "meta": _ref("Meta"), "prefix": {"type": "string"}, "count": {"type": "integer"},
                "people": {"type": "array", "items": _ref("Person")}}},
            "TableFile": table,
            "PersonRow": {"type": "array", "description": row_desc, "minItems": 6, "maxItems": 6,
                          "prefixItems": person_items},
            "NameRow": {"type": "array", "description": name_row_desc, "minItems": 7, "maxItems": 7,
                        "prefixItems": [{"type": "string", "description": "palabra normalizada (fold) del nombre que coincidió"}] + person_items},
            "FindIndex": {"type": "object", "properties": {
                "meta": _ref("Meta"), "name": {"type": "object"}, "city": {"type": "object"}, "year": {"type": "object"},
                "row": {"type": "object"}, "count_people": {"type": "integer"}}},
            "FindNameFile": rowsfile({"prefix": {"type": "string"}}, "NameRow", name_row_desc, ["token"] + ROW_COLUMNS),
            "FindCityIndex": {"type": "object", "properties": {
                "meta": _ref("Meta"), "rule": {"type": "string"},
                "columns": {"type": "array", "items": {"type": "string"}}, "rows": {"type": "array", "items": {"type": "array"}},
                "aliases": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}}},
            "FindCityFile": rowsfile({"country": {"type": "string"}, "slug": {"type": "string"}, "label": {"type": "string"},
                                      "count": {"type": "integer"}, "page": {"type": "integer"}, "pages": {"type": "integer"}}),
            "FindYearFile": rowsfile({"kind": {"type": "string", "enum": ["birth", "death"]}, "year": {"type": "integer"},
                                      "count": {"type": "integer"}, "page": {"type": "integer"}, "pages": {"type": "integer"}}),
        }},
        "x-generated": generated,
        "x-agent-instructions": SITE + "/llms.txt",
    }


# ---------------------------------------------------------------- llms.txt / llms-full.txt

MOTTO = "Cada placa, cada nombre, cada historia. Nunca olvidar. · Jede Platte, jeder Name, jede Geschichte. · Every plaque, every name, every story."

CITE_TEMPLATE = ("{name} ({birth}–{death}). Lista Kauffmann, ficha {id}, {permalink}. "
                 "Fuente: {source_url}. Datos de {generated}. Licencia {license} ({attribution}).")


def llms_txt(fam_indexes, families, generated):
    n = {f: fam_indexes[f]["count_people"] for f in fam_indexes}
    total = sum(n.values())
    L = []
    a = L.append
    a("# Lista Kauffmann")
    a("")
    a("> Free, open map and static JSON data of Stolpersteine (Germany and Ireland) and victims of the Shoah: %s people records across %d licence %s, each with its sources. %s" % (
        "{:,}".format(total), len(n), "family" if len(n) == 1 else "families", MOTTO))
    a("")
    a("Este archivo es informativo y NO tiene valor jurídico propio: lo que obliga son las licencias de los datos. "
      "(This file is informational and has no legal force: the data licences bind.)")
    a("")
    a("Personal, non-commercial; no third-party trackers (only our own cookieless visit counter). "
      "Never invent data: if a field is missing in a record, say it is not recorded. Data date: %s." % generated)
    a("")
    a("## Start here")
    a("")
    a("- [Full agent guide (llms-full.txt)](%s/llms-full.txt): step-by-step how to find a person, normalisation code, citation template, licences." % SITE)
    a("- [OpenAPI 3.1](%s/openapi.json): every static endpoint with schemas and examples." % API)
    a("- [API catalogue](%s/index.json): licence families, endpoints, usage rules." % API)
    a("- [Person record JSON Schema](%s/schema/person.schema.json)" % API)
    a("- [Statistics](%s/stats.json)" % API)
    a("")
    a("## Find a person (static files, GET only)")
    a("")
    for fid in sorted(fam_indexes):
        fam = families[fid]
        a("- [Search manifest – %s (%s)](%s/%s/find/index.json): %s people. By name: `%s/%s/find/name/<prefix>.json`; by place: `find/city/index.json` → `find/city/<cc>/<slug>.json`; by year: `find/year/birth|death/<yyyy>.json`." % (
            fid, fam["license"], API, fid, "{:,}".format(n[fid]), API, fid))
    a("")
    a("1. Normalise a word of the name with fold(): lowercase, ß→ss, strip accents, ä→a ö→o ü→u, ae/oe/ue→a/o/u, keep a-z0-9 (Müller → `muller`).")
    a("2. Try the first 6, 5, … 1 letters of that key (pad short keys with `_`) until a prefix exists in `name.prefixes` of the manifest.")
    a("3. Open `find/name/<prefix>.json`, keep rows whose first value (token) starts with your key, compare full name and years. Hyphenated names: split fold() on spaces and search each token. Particles/titles (von, van, de, zu, Dr., Prof.…) and words of 1 letter are not indexed: search the surname.")
    a("4. Each row ends with `people_prefix`: open `<family>/people/by-surname/<people_prefix>.json` and take the person whose `id` equals the row id. That record holds `sources[]` (original URLs), `links[]`, memorials and inscription.")
    a("5. The same person can exist in both families (linked by Wikidata Qid in `identifiers.wikidata`); check both and keep each licence separate.")
    a("")
    a("## Cite")
    a("")
    a("- Always cite: **Lista Kauffmann** + the person link + the original source from `sources[].url` + data date + licence.")
    a("- Person link (opens it in the map): odbl → `%s/#s=<memorials[0].memorial_id>` (the plaque); cc0 → `%s/#p=<id>`. Machine-readable record: `%s/<family>/people/by-surname/<people_prefix>.json` (object with that id)." % (SITE, SITE, API))
    a("- Template: `%s`" % CITE_TEMPLATE)
    a("- Use only fields present in the record. Do not add biography, family, motives or dates that are not in `sources[]`.")
    a("")
    a("## Licences")
    a("")
    a("- `api/v1/odbl/`, `data/search/`: ODbL 1.0, derived from OpenStreetMap (© OpenStreetMap contributors, https://www.openstreetmap.org/copyright) + Wikidata (CC0). Share-alike and attribution if you redistribute the database or a substantial extract.")
    a("- `api/v1/cc0/`: Wikidata only, CC0 1.0.")
    a("- Wikipedia text is never copied (links only; CC BY-SA 4.0).")
    a("- Documentation and catalogues: CC0 1.0. Each data file states its licence in `meta.license`.")
    a("- [Complete plaque database (ODbL)](%s): transcription of public street memorials, not person records." % FULL_DOWNLOAD)
    a("")
    a("## Scope and care")
    a("")
    a(SCOPE)
    a("")
    a("- Do not use this data to harass, to build lists of descendants, for ethnic-religious profiling of living people, for denialism or antisemitic purposes.")
    a("- Do not present inferences as facts; point to the primary source. Records can contain errors.")
    a("")
    a("## Optional")
    a("")
    a("- [Map and app](%s/): 3D map, search by name or address (JavaScript)." % SITE)
    a("- [Schema.org JSON-LD](%s/kauffmann-list.jsonld)" % SITE)
    a("- [Sitemap](%s/sitemap.xml)" % SITE)
    a("- [Project (for institutions)](%s/proyecto/)" % SITE)
    a("- Corrections or removal of a record: fix it in OpenStreetMap or Wikidata, or ask the project (https://github.com/roquena71-a11y/kauffmann-list).")
    a("")
    return "\n".join(L)


FOLD_JS = """function fold(s){            // identical to pipeline/util.py fold()
  s = String(s||'').toLowerCase().replace(/ß/g,'ss').replace(/ä/g,'a').replace(/ö/g,'o').replace(/ü/g,'u')
        .replace(/ł/g,'l').replace(/ø/g,'o').replace(/đ/g,'d').replace(/ð/g,'d').replace(/þ/g,'th').replace(/æ/g,'ae')
        .replace(/œ/g,'oe').replace(/ı/g,'i');
  s = s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');
  return s.replace(/ae/g,'a').replace(/oe/g,'o').replace(/ue/g,'u').replace(/[^a-z0-9]+/g,' ').trim();
}"""

FOLD_PY = """import re, unicodedata
def fold(s):                 # identical to pipeline/util.py fold()
    s = str(s or '').lower().replace('ß','ss').replace('ä','a').replace('ö','o').replace('ü','u')
    s = s.translate(str.maketrans({'ł':'l','ø':'o','đ':'d','ð':'d','þ':'th','æ':'ae','œ':'oe','ı':'i'}))
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = s.replace('ae','a').replace('oe','o').replace('ue','u')
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()"""


def llms_full_txt(fam_indexes, families, generated):
    L = []
    a = L.append
    a("# Lista Kauffmann – full guide for AI agents")
    a("")
    a("> %s" % MOTTO)
    a("")
    a("Este archivo es informativo y NO tiene valor jurídico propio: lo que obliga son las licencias de los datos.")
    a("")
    a("Site: %s/ · API root: %s/ · Data date: %s · Static files only (GitHub Pages): no keys, no rate limit of our own, GET only. "
      "Please be polite: fetch only the files you need, cache them, and prefer `find/` over crawling `people/`." % (SITE, API, generated))
    a("")
    a("## 1. What is here")
    a("")
    for fid in sorted(fam_indexes):
        fam, idx = families[fid], fam_indexes[fid]
        a("- **%s** (%s, %s people): %s" % (fid, fam["license"], "{:,}".format(idx["count_people"]), fam.get("description")))
    a("- Possibly-living people are excluded from all person records. `data/search/` and `data/stones.json` are transcriptions of public street plaques, not person records.")
    a("")
    a("## 2. Find a person by name")
    a("")
    a("Normalise with fold() (Müller → `muller`, Großmann → `grossmann`, Bär → `bar`, Maier stays `maier`):")
    a("")
    a("```python")
    a(FOLD_PY)
    a("```")
    a("")
    a("```javascript")
    a(FOLD_JS)
    a("```")
    a("")
    a("1. Read `<family>/find/index.json` → `name.prefixes` (prefix → number of rows).")
    a("2. key = fold(word). For n in 6..1: prefix = (key + '_'*6)[:n]; the first prefix present in `name.prefixes` is the file.")
    a("3. GET `<family>/find/name/<prefix>.json`. Rows are `[token, id, name, birth_year, death_year, place, people_prefix]`. Keep rows whose `token` starts with key.")
    a("   Not indexed by name: text in parentheses (e.g. `Robert Eger (Arbeit)` is found as `robert`/`eger`, not as `arbeit`: drop the parenthesised text before folding), particles and titles (von, van, de, der, zu, vom, Dr., Prof.…), words shorter than 2 letters, and memorials without a name (see below). Hyphenated names are indexed one token per part: fold('Müller-Großmann') = `muller grossmann`, so split fold() output on spaces and search each token (a surname alone is enough).")
    a("4. Disambiguate with full name, years and place. If several people remain, say so; do not choose silently.")
    a("5. GET `<family>/people/by-surname/<people_prefix>.json` and take the object whose `id` equals the row id. It has `sources[]`, `links[]`, `memorials[]` (address, inscription), `deportations[]`, `identifiers`.")
    a("")
    a("Example path: `%s/odbl/find/name/<prefix>.json` and `%s/cc0/find/name/<prefix>.json`." % (API, API))
    a("")
    a("## 3. Find people by place")
    a("")
    a("1. GET `<family>/find/city/index.json`. Rows are `[key, country, slug, label, count, pages]`; `aliases` maps alternative names (Cologne → koln) to a key.")
    a("2. key = fold(place name) without spaces (Frankfurt am Main → `frankfurtammain`).")
    a("3. GET `<family>/find/city/<country in lowercase>/<slug>.json` (extra pages: `<slug>~2.json`). Rows use the common person row `[id, name, birth_year, death_year, place, people_prefix]`.")
    a("4. Places are memorial locations and places of death, never places of birth.")
    a("")
    a("## 4. Find people by year")
    a("")
    a("`<family>/find/year/birth/<yyyy>.json` and `<family>/find/year/death/<yyyy>.json`; the available years and counts are in `find/index.json` → `year`. Rows as above. Only years 1700–2100 are listed (out-of-range dates, usually source typos, stay in the record but not in the year files; see `year.range`). Files hold at most 4000 rows: when `count` > 4000 read the extra pages `<yyyy>~2.json`, `<yyyy>~3.json`… (field `pages`).")
    a("")
    a("## 5. Other lookups")
    a("")
    a("- By id: `<family>/person/<shard>.json` (shard = last 2 chars of the id, lowercase, other chars → `_`) → `people_prefix`.")
    a("- By external id (Wikidata Qid, Gedenkbuch, Yad Vashem, USHMM, Arolsen…): `<family>/ids/<scheme>.json`.")
    a("- By address on the map: `data/search/index-<prefix>.json` (plaque text only, includes all plaques).")
    a("- All endpoints with schemas and examples: [openapi.json](%s/openapi.json)." % API)
    a("")
    a("## 6. How to cite")
    a("")
    a("Minimum: **Lista Kauffmann** + person link + original source + data date + licence.")
    a("")
    a("- Person link (opens it in the map): odbl → `%s/#s=<memorials[0].memorial_id>` (the plaque); cc0 → `%s/#p=<id>`. Machine record: `%s/<family>/people/by-surname/<people_prefix>.json` (object with that id)." % (SITE, SITE, API))
    a("- Original source: each `sources[].url` (OpenStreetMap node, Wikidata item…) and, when present, `links[]` (Gedenkbuch, Yad Vashem, USHMM, municipal pages).")
    a("- Template:")
    a("")
    a("```")
    a(CITE_TEMPLATE)
    a("```")
    a("")
    a("- Licence text: odbl → `ODbL-1.0`, attribution `© OpenStreetMap contributors` + Wikidata (CC0); cc0 → `CC0-1.0`, Wikidata.")
    a("- Write only what the record says. Missing death date → say \"no consta\"/\"not recorded\". Never fill gaps from memory.")
    a("- Records without a name (anonymous memorials, `name` = null; they exist in the person files and in the place/year files, not in `find/name/`): cite them as \"sin nombre\" / \"no name recorded\", never as \"None\" or \"null\".")
    a("- `meta.attribution` is a list: join it with \"; \" when you write the citation.")
    a("")
    a("## 7. Rules")
    a("")
    for r in USAGE_RULES:
        a("- " + r)
    a("")
    a("## 8. Scope")
    a("")
    a(SCOPE)
    a("")
    a("## 9. Corrections and removal")
    a("")
    a("Correct the original in OpenStreetMap or Wikidata, or ask the project to remove a record (https://github.com/roquena71-a11y/kauffmann-list). Removals are applied at the next build.")
    a("")
    return "\n".join(L)


SITE_PAGES_EXTRA = ["llms.txt", "llms-full.txt", "api/v1/openapi.json", "api/v1/index.json"]


def write_site_files(site_root, fam_indexes, families, generated):
    files = {}
    files["llms.txt"] = write_text(os.path.join(site_root, "llms.txt"), llms_txt(fam_indexes, families, generated))
    files["llms-full.txt"] = write_text(os.path.join(site_root, "llms-full.txt"), llms_full_txt(fam_indexes, families, generated))
    licenses = [{"href": families[f]["license_url"]} for f in sorted(families) if f in fam_indexes and families[f].get("license_url")]
    linkset = {"linkset": [{
        "anchor": API + "/",
        "service-desc": [{"href": API + "/openapi.json", "type": "application/vnd.oai.openapi+json;version=3.1"}],
        "service-doc": [{"href": SITE + "/llms.txt", "type": "text/plain"},
                        {"href": SITE + "/llms-full.txt", "type": "text/plain"}],
        "describedby": [{"href": API + "/index.json", "type": "application/json"}],
        "license": licenses,
    }]}
    files[".well-known/api-catalog"] = write_json(os.path.join(site_root, ".well-known", "api-catalog"), linkset)
    return files
