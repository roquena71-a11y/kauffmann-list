"""Capa para agentes de IA: api/v1/index.json, stats.json, openapi.json, /llms.txt y /.well-known/api-catalog."""
import os

from .util import write_json, write_text

SITE = "https://roquena71-a11y.github.io/kauffmann-list"
API = SITE + "/api/v1"
FULL_DOWNLOAD = SITE + "/data/stones.json"
DOC_LICENSE = {"name": "CC0-1.0", "url": "https://creativecommons.org/publicdomain/zero/1.0/"}

USAGE_RULES = [
    "Cita siempre: 'Lista Kauffmann' + enlace a la ficha + la fuente original (sources[] de cada registro).",
    "Respeta la licencia de cada familia: ODbL 1.0 (share-alike + atribución '© OpenStreetMap contributors') en odbl/, CC0 en cc0/, la licencia propia de cada institución en partners/<fuente>/.",
    "No combines registros de familias distintas en un mismo objeto para redistribuirlo; crúzalos solo por identificador (Qid de Wikidata o id institucional).",
    "No presentes inferencias como hechos: los datos proceden de placas y bases abiertas y pueden contener errores; remite a la fuente primaria.",
    "Prohibido usar estos datos para acosar, elaborar listas de descendientes, perfiles étnico-religiosos de personas vivas, negacionismo o fines antisemitas.",
    "Personas posiblemente vivas no están en esta API (sin indicio de muerte y nacidas hace menos de 110 años o sin año).",
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
            "Buscar por apellido: normaliza el apellido (surname_prefix_rule en <familia>/index.json), elige el prefijo de people_prefixes y descarga <familia>/people/by-surname/<prefijo>.json (fichas completas), o el de search_prefixes para <familia>/search/index-<prefijo>.json (ligero).",
            "Por id: calcula el shard (person_shard_rule), descarga <familia>/person/<shard>.json → people_prefix → <familia>/people/by-surname/<people_prefix>.json.",
            "Por lugar: <familia>/places/index.json → <familia>/places/<país>/<slug>.json (si pages>1, páginas <slug>~2.json, <slug>~3.json…).",
            "Cruce con otra familia: <familia>/ids/wikidata.json (u otro esquema) da los ids de persona para un Qid o id institucional.",
        ],
        "schema": "schema/person.schema.json",
        "openapi": "openapi.json",
        "stats": "stats.json",
        "full_database": {"url": FULL_DOWNLOAD, "license": "ODbL-1.0",
                          "note": "Base completa descargable (oferta ODbL §4.6)."},
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


def _resp(desc, schema_ref=None):
    content = {"application/json": {"schema": {"$ref": schema_ref} if schema_ref else {"type": "object"}}}
    return {"200": {"description": desc, "content": content}, "404": {"description": "No existe ese fragmento/prefijo"}}


def openapi(fam_indexes, families, generated):
    paths = {
        "/index.json": {"get": {"summary": "Catálogo para agentes: familias, licencias, endpoints, reglas de uso",
                                "operationId": "getCatalog", "responses": _resp("Catálogo")}},
        "/stats.json": {"get": {"summary": "Estadísticas globales", "operationId": "getStats", "responses": _resp("Estadísticas")}},
        "/schema/person.schema.json": {"get": {"summary": "JSON Schema del registro de persona", "operationId": "getPersonSchema",
                                               "responses": _resp("JSON Schema")}},
    }
    for fid in sorted(fam_indexes):
        op = fid.replace("/", "_")
        lic = families[fid]["license"]
        tag = [fid]
        p = "/" + fid

        def param(name, desc, enum=None):
            sch = {"type": "string"}
            if enum:
                sch["enum"] = enum
            return {"name": name, "in": "path", "required": True, "description": desc, "schema": sch}
        idx = fam_indexes[fid]
        paths[p + "/index.json"] = {"get": {"tags": tag, "summary": "Índice de la familia %s (%s)" % (fid, lic),
                                            "operationId": op + "_index", "responses": _resp("Índice")}}
        paths[p + "/stats.json"] = {"get": {"tags": tag, "summary": "Estadísticas (%s)" % lic,
                                            "operationId": op + "_stats", "responses": _resp("Estadísticas")}}
        paths[p + "/people/by-surname/{prefix}.json"] = {"get": {
            "tags": tag, "summary": "Fichas completas (Person) por prefijo de apellido (%s)" % lic,
            "operationId": op + "_people", "description": idx["surname_prefix_rule"],
            "parameters": [param("prefix", "Prefijo normalizado (people_prefixes)", idx["people_prefixes"])],
            "responses": _resp("{meta, prefix, count, people: Person[]}", "#/components/schemas/PeopleFile")}}
        paths[p + "/person/{shard}.json"] = {"get": {
            "tags": tag, "summary": "Búsqueda por id: filas [id, people_prefix]", "operationId": op + "_personLookup",
            "description": idx["person_shard_rule"],
            "parameters": [param("shard", "Fragmento", idx["person_shards"])],
            "responses": _resp("{meta, shard, columns, rows}")}}
        paths[p + "/search/index-{prefix}.json"] = {"get": {
            "tags": tag, "summary": "Índice de búsqueda ligero (filas id, name, birth_year, locality, lat, lon, people_prefix)",
            "operationId": op + "_search",
            "parameters": [param("prefix", "Prefijo normalizado (search_prefixes)", idx["search_prefixes"])],
            "responses": _resp("{meta, prefix, columns, rows}")}}
        paths[p + "/places/index.json"] = {"get": {"tags": tag, "summary": "Lugares (memorial / muerte) con recuento",
                                                   "operationId": op + "_places", "responses": _resp("{meta, columns, rows}")}}
        paths[p + "/places/{country}/{slug}.json"] = {"get": {
            "tags": tag, "summary": "Personas de un lugar; páginas adicionales como {slug}~2.json",
            "operationId": op + "_place",
            "parameters": [param("country", "ISO 3166-1 alpha-2 en minúsculas"), param("slug", "slug del lugar (places/index.json)")],
            "responses": _resp("{meta, country, slug, label, count, page, pages, columns, rows}")}}
        paths[p + "/ids/{scheme}.json"] = {"get": {
            "tags": tag, "summary": "Tabla de cruce: id externo → ids de persona en esta familia",
            "operationId": op + "_ids", "parameters": [param("scheme", "Esquema", idx["id_schemes"])],
            "responses": _resp("{meta, scheme, columns, rows}")}}
        paths[p + "/quality/possible-duplicates.json"] = {"get": {"tags": tag, "summary": "Posibles duplicados (no fusionados)",
                                                                  "operationId": op + "_dups", "responses": _resp("Informe")}}
        paths[p + "/quality/blocked-merges.json"] = {"get": {"tags": tag, "summary": "Uniones bloqueadas por conflicto",
                                                             "operationId": op + "_blocked", "responses": _resp("Informe")}}
    return {
        "openapi": "3.1.0",
        "info": {"title": "Lista Kauffmann – API estática", "version": "1.0.0",
                 "description": "Archivos JSON estáticos servidos por GitHub Pages (solo GET, sin autenticación). "
                                "Cada familia de datos tiene su propia licencia en meta.license de cada archivo.",
                 "license": {"name": "CC0-1.0 (esta descripción); datos: ver meta.license de cada archivo",
                             "identifier": "CC0-1.0"}},
        "servers": [{"url": API}],
        "paths": paths,
        "components": {"schemas": {
            "Person": {"$ref": API + "/schema/person.schema.json"},
            "PeopleFile": {"type": "object", "properties": {
                "meta": {"type": "object"}, "prefix": {"type": "string"}, "count": {"type": "integer"},
                "people": {"type": "array", "items": {"$ref": "#/components/schemas/Person"}}}},
        }},
        "x-generated": generated,
    }


def llms_txt(fam_indexes, families, generated):
    lines = [
        "# Lista Kauffmann",
        "",
        "> Mapa y datos abiertos de Stolpersteine (Alemania) y víctimas de la Shoah. Cada placa, cada nombre, cada historia.",
        "",
        "Este archivo es informativo y NO tiene valor jurídico propio: lo que obliga son las licencias de los datos.",
        "",
        "## API estática (solo GET, JSON)",
        "",
        "- [Catálogo para agentes](%s/index.json): familias de licencia, endpoints, reglas de uso, fecha de datos (%s)." % (API, generated),
        "- [OpenAPI 3.1](%s/openapi.json)" % API,
        "- [Esquema de persona](%s/schema/person.schema.json)" % API,
        "- [Estadísticas](%s/stats.json)" % API,
    ]
    for fid in sorted(fam_indexes):
        fam = families[fid]
        lines.append("- [Familia %s – %s](%s/%s/index.json): %d personas." % (fid, fam["license"], API, fid, fam_indexes[fid]["count_people"]))
    lines += [
        "",
        "## Licencias",
        "",
        "- `api/v1/odbl/` y `data/search/`: Open Database License 1.0 (ODbL). Es una base de datos derivada de OpenStreetMap "
        "(© OpenStreetMap contributors, https://www.openstreetmap.org/copyright) + Wikidata (CC0). Si redistribuyes la base o un extracto "
        "sustancial, debe seguir bajo ODbL (share-alike) y con atribución.",
        "- `api/v1/cc0/`: Wikidata, CC0 1.0.",
        "- `api/v1/partners/<fuente>/` (si existe): licencia propia de cada institución, en meta.license de cada archivo; no reutilizar fuera de lo que permita.",
        "- Textos de Wikipedia: no se copian en la API; solo enlaces (permalink con oldid). Su licencia es CC BY-SA 4.0.",
        "- [Base completa descargable (ODbL)](%s)" % FULL_DOWNLOAD,
        "",
        "## Reglas de uso",
        "",
    ]
    lines += ["- " + r for r in USAGE_RULES]
    lines += [
        "",
        "## Correcciones y retiradas",
        "",
        "- Corrige en OpenStreetMap o Wikidata, o pide la retirada de una ficha al proyecto (https://github.com/roquena71-a11y/kauffmann-list).",
        "",
    ]
    return "\n".join(lines)


def write_site_files(site_root, fam_indexes, families, generated):
    files = {}
    files["llms.txt"] = write_text(os.path.join(site_root, "llms.txt"), llms_txt(fam_indexes, families, generated))
    linkset = {"linkset": [{
        "anchor": API + "/",
        "service-desc": [{"href": API + "/openapi.json", "type": "application/vnd.oai.openapi+json;version=3.1"}],
        "service-doc": [{"href": SITE + "/llms.txt", "type": "text/plain"}],
        "describedby": [{"href": API + "/index.json", "type": "application/json"}],
        "license": [{"href": "https://opendatacommons.org/licenses/odbl/1-0/"}],
    }]}
    files[".well-known/api-catalog"] = write_json(os.path.join(site_root, ".well-known", "api-catalog"), linkset)
    return files
