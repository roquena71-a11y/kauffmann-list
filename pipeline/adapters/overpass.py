"""Adaptador Overpass (OpenStreetMap, ODbL): Stolpersteine fuera de Alemania.

Una consulta por país (paginación natural por área ISO 3166-1), caché y límite de velocidad.
Solo se copian etiquetas presentes en OSM; no se completa nada.
"""
import os
import re

from .. import inscription as ins
from ..http import HttpClient
from ..util import REPO_ROOT, clean_str, normalize_date, load_json

QUERY = """[out:json][timeout:{timeout}];
area["ISO3166-1"="{cc}"][admin_level=2]->.a;
(node["memorial"="stolperstein"](area.a);way["memorial"="stolperstein"](area.a););
out center tags;"""


def element_to_record(el, cc, cfg, retrieved):
    sid = cfg["id"]
    tags = el.get("tags") or {}
    osm_id = ("n" if el.get("type") == "node" else "w") + str(el["id"])
    lat = el.get("lat", (el.get("center") or {}).get("lat"))
    lon = el.get("lon", (el.get("center") or {}).get("lon"))
    name_raw = tags.get("memorial:name") or tags.get("name") or tags.get("person:name")
    name, birth_name = ins.split_name(name_raw)
    insc = clean_str(tags.get("inscription") or tags.get("memorial:text"))
    if not birth_name and insc:
        birth_name = ins.birth_name_from(insc)
    street = " ".join(x for x in (tags.get("addr:street"), tags.get("addr:housenumber")) if x)
    locality = clean_str(tags.get("addr:city") or tags.get("addr:place"))
    address = clean_str(", ".join(x for x in (street, locality) if x)) or clean_str(tags.get("memorial:addr"))
    fate, basis = ins.fate_from_text(insc)
    qid = tags.get("subject:wikidata") if re.match(r"^Q\d+$", tags.get("subject:wikidata") or "") else None
    lic = (cfg["license"], cfg.get("license_url"), cfg["attribution"])
    url = "https://www.openstreetmap.org/%s/%s" % ("node" if osm_id[0] == "n" else "way", osm_id[1:])
    links = []  # el enlace al nodo OSM es sources[].url
    if qid:
        links.append({"type": "wikidata", "url": "https://www.wikidata.org/wiki/" + qid, "label": None,
                      "license": None, "text_url": None, "source_id": sid})
    return {
        "id": ("wd-" + qid) if qid else cfg["id_prefix"] + "-" + osm_id,
        "subject_type": "person",
        "name": name, "given_name": None, "family_name": None, "birth_name": birth_name,
        "birth_date": normalize_date(tags.get("person:date_of_birth") or tags.get("birth")),
        "birth_place": None,
        "death_date": normalize_date(tags.get("person:date_of_death") or tags.get("death")),
        "death_place": ins.death_place_from(insc),
        "fate": fate, "fate_basis": basis,
        "deportations": [],
        "places": [],  # el lugar del memorial está en memorials[]
        "memorials": [{"type": "stolperstein", "memorial_id": osm_id, "inscription": insc, "address": address,
                       "locality": locality, "country": cc, "lat": lat, "lon": lon,
                       "laid": normalize_date(tags.get("start_date")), "image": None, "source_id": sid}],
        "links": links,
        "identifiers": {"wikidata": qid, "osm": [osm_id]},
        "sources": [{"source_id": sid, "record_id": osm_id, "url": url, "license": lic[0], "license_url": lic[1],
                     "attribution": lic[2], "retrieved": retrieved}],
        "_variants": {},
        "_plaque": {"stone_id": osm_id, "n": clean_str(name_raw), "a": address, "c": locality, "la": lat, "lo": lon,
                    "jg": ins.birth_year_from_inscription(insc)},
    }


def fetch(cfg, ctx):
    fixture = ctx.fixture_for(cfg["id"])
    count = 0
    if fixture:
        data = load_json(fixture if os.path.isabs(fixture) else os.path.join(REPO_ROOT, fixture))
        for el in data.get("elements", []):
            if ctx.limit and count >= ctx.limit:
                return
            count += 1
            yield element_to_record(el, data.get("country", "XX"), cfg, data.get("retrieved"))
        return
    net = cfg.get("network", {})
    client = HttpClient(cfg["id"], offline=ctx.offline, min_interval=net.get("min_interval_seconds", 10),
                        retries=net.get("retries", 3), timeout=net.get("timeout_seconds", 300))
    for cc in cfg["countries"]:
        q = QUERY.format(timeout=int(net.get("query_timeout", 240)), cc=cc)
        data = client.post_json(cfg["endpoint"], {"data": q})
        for el in sorted(data.get("elements", []), key=lambda e: (e.get("type"), e.get("id"))):
            if ctx.limit and count >= ctx.limit:
                return
            count += 1
            yield element_to_record(el, cc, cfg, ctx.today)
    ctx.note(cfg["id"], "http", dict(client.stats))
