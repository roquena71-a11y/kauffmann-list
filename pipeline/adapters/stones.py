"""Adaptador 'stones': lee los datos actuales del sitio (data/stones.json + data/bio/*.json).

Solo lectura: no modifica ningún archivo existente.
"""
import glob
import os
import re

from .. import inscription as ins
from ..util import REPO_ROOT, clean_str, normalize_date, date_year, load_json

ODBL = ("ODbL-1.0", "https://opendatacommons.org/licenses/odbl/1-0/",
        "© OpenStreetMap contributors (ODbL 1.0) + Wikidata (CC0 1.0)")
CC0 = ("CC0-1.0", "https://creativecommons.org/publicdomain/zero/1.0/", "Wikidata (CC0 1.0)")

LOCAL_BIO = {"berlin": "Stolpersteine in Berlin (Koordinierungsstelle)",
             "hamburg": "Stolpersteine in Hamburg",
             "bremen": "Stolpersteine in Bremen"}


def _locality(s):
    for v in (s.get("c"), s.get("cd")):
        v = clean_str(v)
        if v and re.search(r"[A-Za-zÄÖÜäöüß]", v) and not re.match(r"^\d", v):
            return v
    addr = clean_str(s.get("a"))
    if addr:
        last = clean_str(re.sub(r"^\d{5}\s*", "", addr.split(",")[-1]))
        if last and re.search(r"[A-Za-zÄÖÜäöüß]{3}", last) and not re.search(r"\d", last):
            return last
    return None


def _date_in(text):
    m = re.search(r"\b(\d{1,2}\.\s?\d{1,2}\.\s?\d{4})\b", text or "")
    if m:
        return normalize_date(m.group(1).replace(" ", ""))
    return None


def load_bio(bio_dir):
    bio = {}
    for path in sorted(glob.glob(os.path.join(bio_dir, "*.json"))):
        if os.path.basename(path) == "manifest.json":
            continue
        data = load_json(path)
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict):
                    bio[k] = v
    return bio


def stone_to_record(s, bio_rec, cfg, retrieved):
    sid = cfg["id"]
    stone_id = s["id"]
    src = s.get("src") or ""
    lic = ODBL if "osm" in src else CC0
    is_osm = bool(re.match(r"^[nw]\d+$", stone_id))
    insc_txt = clean_str(s.get("i"))
    insc = (bio_rec or {}).get("insc") or {}
    links_bio = (bio_rec or {}).get("links") or {}

    name, birth_name = ins.split_name(s.get("n"))
    if not birth_name and insc_txt:
        birth_name = ins.birth_name_from(insc_txt)

    # Fecha de nacimiento: dato estructurado (OSM/Wikidata) si concuerda con el año de la placa.
    plaque_birth = normalize_date(insc.get("birth")) or normalize_date(ins.birth_year_from_inscription(insc_txt))
    plaque_year = plaque_birth[:4] if plaque_birth else None
    b = normalize_date(s.get("b"))
    variants = {}
    if b and plaque_year and date_year(b) != int(plaque_year):
        birth_date = plaque_birth
        variants["birth_date"] = [{"value": b, "source_id": sid}]
    else:
        birth_date = b or plaque_birth

    death_date = normalize_date(s.get("d")) or _date_in(insc.get("death"))
    fate_text = " ".join(x for x in (insc_txt, insc.get("deportation"), insc.get("death")) if x)
    fate, fate_basis = ins.fate_from_text(fate_text)
    death_place = ins.death_place_from(insc.get("death") or insc_txt)

    lat, lon = s.get("la"), s.get("lo")
    lat = round(float(lat), 7) if lat is not None else None
    lon = round(float(lon), 7) if lon is not None else None
    locality = _locality(s)
    address = clean_str(s.get("a"))
    kind = "stolperschwelle" if s.get("kind") == "stolperschwelle" else "stolperstein"

    image = None
    if s.get("img"):
        image = "https://commons.wikimedia.org/wiki/File:" + s["img"].replace(" ", "_")
    elif s.get("imgx"):
        image = s["imgx"]

    memorial = {"type": kind, "memorial_id": stone_id, "inscription": insc_txt, "address": address,
                "locality": locality, "country": "DE", "lat": lat, "lon": lon,
                "laid": normalize_date(s.get("laid")), "image": image, "source_id": sid}
    # El lugar del memorial (dirección + coordenadas) está en memorials[]; aquí no se repite.
    places = []
    if insc_txt and re.search(r"\bwohnte\b", insc_txt, re.I) and (address or locality):
        places.append({"role": "residence", "label": address or locality, "locality": locality,
                       "country": "DE", "source_id": sid})
    deportations = ins.deportations_from(insc.get("deportation"), sid)
    # Los destinos de deportación ya están en deportations[]; no se repiten en places[].
    if death_place:
        places.append({"role": "death", "label": death_place, "source_id": sid})

    links = []

    def add(t, url, label=None, lic_=None):
        if url and re.match(r"^https?://", url):
            links.append({"type": t, "url": url, "label": label, "license": lic_, "text_url": None, "source_id": sid})

    gb = sorted(set((links_bio.get("gedenkbuch") or []) + (s.get("gb") or [])))
    yv = sorted(set((links_bio.get("yadvashem") or []) + (s.get("yv") or [])))
    us = sorted(set((links_bio.get("ushmm") or []) + (s.get("us") or [])))
    tpl = cfg.get("link_templates", {})
    for g in gb:
        add("gedenkbuch", tpl.get("gedenkbuch", "").format(id=g), "Gedenkbuch – Bundesarchiv")
    for y in yv:
        add("yad_vashem", tpl.get("yad_vashem", "").format(id=y), "Yad Vashem – Names Database")
    for u in us:
        add("ushmm", tpl.get("ushmm", "").format(id=u), "USHMM – Holocaust Survivors and Victims Database")
    for key, label in LOCAL_BIO.items():
        if links_bio.get(key):
            add("local_biography", links_bio[key], label)
    for u in sorted(set((links_bio.get("describedAt") or []) + (s.get("w") or []))):
        add("described_at", u)
    if s.get("wp"):
        m = re.match(r"^([a-z\-]+):(.+)$", s["wp"])
        if m:
            add("wikipedia", "https://%s.wikipedia.org/wiki/%s" % (m.group(1), m.group(2).replace(" ", "_")), s["wp"])
    wp = (bio_rec or {}).get("wp")
    if wp and wp.get("permalink"):
        # Solo el enlace (permalink con oldid); el texto CC BY-SA no se copia en la API.
        add("wikipedia_list_entry", wp["permalink"], wp.get("title"), wp.get("license"))
    # El enlace al propio memorial (OSM / Wikidata) es sources[].url; no se duplica en links[].
    if s.get("p"):
        add("wikidata", "https://www.wikidata.org/wiki/" + s["p"])

    qid = s.get("p") if s.get("p") and re.match(r"^Q\d+$", s["p"]) else None
    identifiers = {"wikidata": qid, "gedenkbuch": gb, "yad_vashem": yv, "ushmm": us,
                   "osm": [stone_id] if is_osm else []}
    pid = ("wd-" + qid) if qid else cfg["id_prefix"] + "-" + stone_id
    rec_url = None
    if is_osm:
        rec_url = "https://www.openstreetmap.org/%s/%s" % ("node" if stone_id[0] == "n" else "way", stone_id[1:])
    elif s.get("wd"):
        rec_url = "https://www.wikidata.org/wiki/" + s["wd"]

    return {
        "id": pid,
        "subject_type": "collective" if kind == "stolperschwelle" else "person",
        "name": name,
        "given_name": None,
        "family_name": None,
        "birth_name": birth_name,
        "birth_date": birth_date,
        "birth_place": None,
        "death_date": death_date,
        "death_place": death_place,
        "fate": fate,
        "fate_basis": fate_basis,
        "deportations": deportations,
        "places": places,
        "memorials": [memorial],
        "links": links,
        "identifiers": identifiers,
        "sources": [{"source_id": sid, "record_id": stone_id, "url": rec_url, "license": lic[0],
                     "attribution": lic[2], "retrieved": retrieved}],
        "_variants": variants,
        "_plaque": {"stone_id": stone_id, "n": clean_str(s.get("n")), "a": address, "c": locality,
                    "la": lat, "lo": lon, "jg": plaque_year},
    }


def fetch(cfg, ctx):
    inp = cfg.get("input", {})
    stones_path = os.path.join(REPO_ROOT, inp.get("stones", "data/stones.json"))
    bio_dir = os.path.join(REPO_ROOT, inp.get("bio_dir", "data/bio"))
    data = load_json(stones_path)
    meta = data.get("meta", {})
    retrieved = (meta.get("osm_snapshot") or meta.get("generated") or "")[:10] or None
    ctx.note(cfg["id"], "snapshot", meta.get("generated"))
    bio = load_bio(bio_dir) if os.path.isdir(bio_dir) else {}
    stones = sorted(data.get("stones", []), key=lambda s: s["id"])
    if ctx.limit:
        stones = stones[: ctx.limit]
    for s in stones:
        yield stone_to_record(s, bio.get(s["id"]), cfg, retrieved)
