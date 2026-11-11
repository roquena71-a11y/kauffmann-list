"""Adaptador Wikidata (SPARQL, CC0).

Dos fases para no saturar el servicio de consultas:
 1. Lista de Qids por cada selector (patrón de tripletas), paginada con ORDER BY + LIMIT/OFFSET.
 2. Detalle en lotes con VALUES (etiquetas, fechas con precisión, lugares, identificadores).
Todo pasa por HttpClient (caché en pipeline/cache/, reintentos, límite de velocidad).
"""
import json
import os
import re

from ..http import HttpClient
from ..util import REPO_ROOT, clean_str, load_json

ENTITY = "http://www.wikidata.org/entity/"

MANNER_FATE = {"Q149086": "murdered", "Q10737": "suicide"}


def _qid(uri):
    if uri and uri.startswith(ENTITY):
        return uri[len(ENTITY):]
    return None


def _date(value, precision):
    if not value:
        return None
    m = re.match(r"^([+-]?)(\d{4})-(\d{2})-(\d{2})", value)
    if not m or m.group(1) == "-":
        return None
    try:
        p = int(precision or 11)
    except ValueError:
        p = 11
    if p <= 8:
        return None  # década o menos precisa: no se convierte en año (no inventar precisión)
    if p == 9:
        return m.group(2)
    if p == 10:
        return "%s-%s" % (m.group(2), m.group(3))
    return "%s-%s-%s" % (m.group(2), m.group(3), m.group(4))


def _point(wkt):
    m = re.match(r"^Point\(([-\d.eE]+) ([-\d.eE]+)\)$", wkt or "")
    if not m:
        return None, None
    lon, lat = float(m.group(1)), float(m.group(2))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None, None
    return round(lat, 6), round(lon, 6)


def _single(value):
    """Valor único de un GROUP_CONCAT; None si hay varios distintos (no se elige al azar)."""
    vals = sorted(set(v for v in (value or "").split("|") if v))
    return vals[0] if len(vals) == 1 else None


def _many(value):
    return sorted(set(v for v in (value or "").split("|") if v))


def build_detail_query(qids, id_props, lang):
    values = " ".join("wd:" + q for q in qids)
    id_sel = " ".join('(GROUP_CONCAT(DISTINCT ?id_%s; separator="|") AS ?ids_%s)' % (p, p) for p in sorted(id_props))
    id_opt = "\n".join("  OPTIONAL { ?item wdt:%s ?id_%s }" % (p, p) for p in sorted(id_props))
    return """SELECT ?item
  (SAMPLE(?l1) AS ?label1) (SAMPLE(?l2) AS ?label2) (SAMPLE(?l3) AS ?label3)
  (GROUP_CONCAT(DISTINCT ?givenL; separator="|") AS ?given)
  (GROUP_CONCAT(DISTINCT ?familyL; separator="|") AS ?family)
  (GROUP_CONCAT(DISTINCT ?bname; separator="|") AS ?birth_name)
  (SAMPLE(?bt) AS ?birth) (SAMPLE(?bpr) AS ?birth_prec)
  (SAMPLE(?dt) AS ?death) (SAMPLE(?dpr) AS ?death_prec)
  (SAMPLE(?bp) AS ?bplace) (SAMPLE(?bpL) AS ?bplace_label) (SAMPLE(?bpC) AS ?bplace_coord) (SAMPLE(?bpCC) AS ?bplace_cc)
  (SAMPLE(?dp) AS ?dplace) (SAMPLE(?dpL) AS ?dplace_label) (SAMPLE(?dpC) AS ?dplace_coord) (SAMPLE(?dpCC) AS ?dplace_cc)
  (GROUP_CONCAT(DISTINCT ?mod; separator="|") AS ?manner)
  (GROUP_CONCAT(DISTINCT ?article; separator="|") AS ?articles)
  %s
WHERE {
  VALUES ?item { %s }
  OPTIONAL { ?item rdfs:label ?l1 FILTER(LANG(?l1)="%s") }
  OPTIONAL { ?item rdfs:label ?l2 FILTER(LANG(?l2)="%s") }
  OPTIONAL { ?item rdfs:label ?l3 FILTER(LANG(?l3)="%s") }
  OPTIONAL { ?item wdt:P735 ?g . ?g rdfs:label ?givenL FILTER(LANG(?givenL)="mul") }
  OPTIONAL { ?item wdt:P734 ?f . ?f rdfs:label ?familyL FILTER(LANG(?familyL)="mul") }
  OPTIONAL { ?item wdt:P1477 ?bname }
  OPTIONAL { ?item p:P569/psv:P569 [ wikibase:timeValue ?bt ; wikibase:timePrecision ?bpr ] }
  OPTIONAL { ?item p:P570/psv:P570 [ wikibase:timeValue ?dt ; wikibase:timePrecision ?dpr ] }
  OPTIONAL { ?item wdt:P19 ?bp . OPTIONAL { ?bp rdfs:label ?bpL FILTER(LANG(?bpL)="%s") } OPTIONAL { ?bp wdt:P625 ?bpC } OPTIONAL { ?bp wdt:P17/wdt:P297 ?bpCC } }
  OPTIONAL { ?item wdt:P20 ?dp . OPTIONAL { ?dp rdfs:label ?dpL FILTER(LANG(?dpL)="%s") } OPTIONAL { ?dp wdt:P625 ?dpC } OPTIONAL { ?dp wdt:P17/wdt:P297 ?dpCC } }
  OPTIONAL { ?item wdt:P1196 ?mod }
  OPTIONAL { ?article schema:about ?item ; schema:isPartOf <https://de.wikipedia.org/> }
%s
}
GROUP BY ?item
ORDER BY ?item""" % (id_sel, values, lang[0], lang[1], lang[2], lang[0], lang[0], id_opt)


def build_list_query(selector, limit, offset):
    return "SELECT DISTINCT ?item WHERE { %s . ?item wdt:P31 wd:Q5 . } ORDER BY ?item LIMIT %d OFFSET %d" % (
        selector, limit, offset)


def binding_to_record(b, cfg, retrieved):
    sid = cfg["id"]
    v = {k: x.get("value") for k, x in b.items()}
    qid = _qid(v.get("item"))
    if not qid:
        return None
    id_props = cfg["identifier_properties"]
    identifiers = {"wikidata": qid}
    for prop, scheme in sorted(id_props.items()):
        ids = _many(v.get("ids_" + prop))
        if ids:
            identifiers[scheme] = ids
    name = clean_str(v.get("label1") or v.get("label2") or v.get("label3"))
    death_date = _date(v.get("death"), v.get("death_prec"))
    manner = [_qid(x) for x in _many(v.get("manner"))]
    fate, basis = "unknown", None
    for q in manner:
        if q in MANNER_FATE:
            fate, basis = MANNER_FATE[q], "wikidata_manner_of_death"
            break
    places = []
    for role, pre in (("birth", "bplace"), ("death", "dplace")):
        label = clean_str(v.get(pre + "_label"))
        if not label:
            continue
        lat, lon = _point(v.get(pre + "_coord"))
        cc = (v.get(pre + "_cc") or "").upper() or None
        places.append({"role": role, "label": label, "locality": label, "lat": lat, "lon": lon,
                       "country": cc if cc and re.match(r"^[A-Z]{2}$", cc) else None,
                       "wikidata": _qid(v.get(pre)), "source_id": sid})
    links = [{"type": "wikidata", "url": "https://www.wikidata.org/wiki/" + qid, "label": name,
              "license": None, "text_url": None, "source_id": sid}]
    for a in _many(v.get("articles")):
        links.append({"type": "wikipedia", "url": a, "label": None, "license": "CC BY-SA 4.0",
                      "text_url": None, "source_id": sid})
    tpl = cfg.get("link_templates", {})
    for scheme in ("gedenkbuch", "yad_vashem", "ushmm", "arolsen", "holocaust_cz", "joods_monument", "mapping_the_lives"):
        for i in identifiers.get(scheme, []):
            if tpl.get(scheme):
                links.append({"type": scheme, "url": tpl[scheme].format(id=i), "label": None, "license": None,
                              "text_url": None, "source_id": sid})
    return {
        "id": cfg["id_prefix"] + "-" + qid,
        "subject_type": "person",
        "name": name,
        "given_name": _single(v.get("given")),
        "family_name": _single(v.get("family")),
        "birth_name": _single(v.get("birth_name")),
        "birth_date": _date(v.get("birth"), v.get("birth_prec")),
        "birth_place": next((p["label"] for p in places if p["role"] == "birth"), None),
        "death_date": death_date,
        "death_place": next((p["label"] for p in places if p["role"] == "death"), None),
        "fate": fate,
        "fate_basis": basis,
        "deportations": [],
        "places": places,
        "memorials": [],
        "links": links,
        "identifiers": identifiers,
        "sources": [{"source_id": sid, "record_id": qid, "url": "https://www.wikidata.org/wiki/" + qid,
                     "license": cfg["license"], "license_url": cfg.get("license_url"),
                     "attribution": cfg["attribution"], "retrieved": retrieved}],
        "_variants": {},
    }


def _sparql(client, endpoint, query):
    return client.post_json(endpoint, {"query": query}, headers={"Accept": "application/sparql-results+json"})


def fetch(cfg, ctx):
    # El fixture solo se usa si se pide explícitamente (--fixture o tests); nunca como dato publicado por defecto.
    fixture = ctx.fixture_for(cfg["id"])
    if fixture:
        path = fixture if os.path.isabs(fixture) else os.path.join(REPO_ROOT, fixture)
        data = load_json(path)
        bindings = data["results"]["bindings"]
        if ctx.limit:
            bindings = bindings[: ctx.limit]
        for b in bindings:
            rec = binding_to_record(b, cfg, data.get("retrieved"))
            if rec:
                yield rec
        return
    net = cfg.get("network", {})
    client = HttpClient(cfg["id"], offline=ctx.offline, min_interval=net.get("min_interval_seconds", 1.5),
                        retries=net.get("retries", 4), timeout=net.get("timeout_seconds", 120))
    endpoint = cfg["endpoint"]
    page = int(net.get("page_size", 5000))
    limit = ctx.limit
    qids = set()
    for selector in cfg["selectors"]:
        offset = 0
        while True:
            want = page if not limit else min(page, max(limit - len(qids), 0))
            if limit and want <= 0:
                break
            res = _sparql(client, endpoint, build_list_query(selector, want, offset))
            got = [_qid(b["item"]["value"]) for b in res["results"]["bindings"]]
            got = [q for q in got if q]
            for q in got:
                if not limit or len(qids) < limit:
                    qids.add(q)
            if len(got) < want:
                break
            offset += want
        if limit and len(qids) >= limit:
            break
    ordered = sorted(qids, key=lambda q: int(q[1:]))
    batch = int(net.get("detail_batch_size", 150))
    lang = (cfg.get("label_languages") or ["de", "en", "mul"]) + ["en", "mul"]
    retrieved = ctx.today
    for i in range(0, len(ordered), batch):
        res = _sparql(client, endpoint, build_detail_query(ordered[i:i + batch], cfg["identifier_properties"], lang[:3]))
        for b in res["results"]["bindings"]:
            rec = binding_to_record(b, cfg, retrieved)
            if rec:
                yield rec
    ctx.note(cfg["id"], "http", dict(client.stats))
