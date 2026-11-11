"""Build: fuentes → gate de licencia → retiradas → merge por familia → políticas → api/v1 estática."""
import datetime
import os
import re
import shutil
import sys

from . import agents
from .adapters import ADAPTERS
from .config import load_families, load_sources, load_suppressed
from .http import HttpError, OfflineCacheMiss
from .jsonschema_lite import Validator
from .merge import merge_family, possible_duplicates
from .policy import apply_person_policy, license_gate, suppress
from .util import (PIPELINE_DIR, REPO_ROOT, clean_str, date_year, fold, load_json, person_shard, slugify,
                   surname_key, write_json)

MARKER = ".generated-by-kauffmann-pipeline"
MAX_PER_BUCKET = 2000
PEOPLE_PER_FILE = 650      # fichas completas (~1 KB c/u) → archivos < ~1 MB
SEARCH_PER_FILE = 4000     # filas ligeras (~90 B c/u)
PLACE_PAGE = 4000
SITE_BASE = "https://roquena71-a11y.github.io/kauffmann-list/"
FULL_DOWNLOAD = SITE_BASE + "data/stones.json"
TITLES = re.compile(r"^(dr\.?|prof\.?|rabbiner|rabbi|sanitätsrat|justizrat|dipl\.-ing\.)\s+", re.I)


class Context:
    def __init__(self, offline=False, limit=None, today=None, fixtures=None):
        self.offline = offline
        self.limit = limit
        self.today = today or datetime.date.today().isoformat()
        self.fixtures = fixtures or {}
        self.notes = {}

    def fixture_for(self, source_id):
        return self.fixtures.get(source_id)

    def note(self, source_id, key, value, add=False):
        d = self.notes.setdefault(source_id, {})
        d[key] = d.get(key, 0) + value if add else value


def log(msg):
    sys.stderr.write(msg + "\n")
    sys.stderr.flush()


# ---------------------------------------------------------------- particionado

def sort_surname(p):
    """Clave de particionado. Usa family_name solo si la fuente lo da; si no, el último token del nombre
    (heurística de PARTICIONADO, no se publica como apellido)."""
    if p.get("family_name"):
        return surname_key(p["family_name"])
    name = clean_str(p.get("name")) or ""
    name = re.sub(r"[\"'„“”‚‘’].*?[\"'„“”‚‘’]", " ", name)
    name = re.sub(r"\(.*?\)", " ", name)
    while TITLES.match(name):
        name = TITLES.sub("", name, count=1)
    toks = [t for t in re.split(r"\s+", name.strip()) if t]
    if not toks:
        return ""
    return surname_key(toks[-1]) or surname_key(name)


def assign_prefixes(keys, max_per=MAX_PER_BUCKET, max_depth=6):
    """keys: lista de claves (str). Devuelve dict prefijo → índices. Divide recursivamente hasta 6 letras."""
    def pad(k, d):
        return (k + "_" * d)[:d]

    out = {}

    def rec(idx, depth):
        groups = {}
        for i in idx:
            groups.setdefault(pad(keys[i], depth), []).append(i)
        for pre, members in groups.items():
            if len(members) > max_per and depth < max_depth and not pre.endswith("_"):
                rec(members, depth + 1)
            else:
                out[pre] = members
    rec(list(range(len(keys))), 1)
    return out


def lookup_prefix(key, prefixes):
    for n in (6, 5, 4, 3, 2, 1):
        cand = (key + "______")[:n]
        if cand in prefixes:
            return cand
    return "_"


# ---------------------------------------------------------------- meta

def family_meta(fam_id, fam, sources_used, generated):
    return {
        "family": fam_id,
        "license": fam["license"],
        "license_url": fam.get("license_url"),
        "attribution": list(fam.get("attribution") or []),
        "source_url": fam.get("source_url"),
        "generated": generated,
        "description": fam.get("description"),
        "full_database": FULL_DOWNLOAD if fam_id == "odbl" else None,
        "sources": [{"id": s["id"], "name": s["name"], "license": s["license"], "license_url": s.get("license_url"),
                     "attribution": s["attribution"], "homepage": s.get("homepage")} for s in sources_used],
        "schema": SITE_BASE + "api/v1/schema/person.schema.json",
        "notice": "Datos conmemorativos con fuente por registro. Pueden contener errores: verifica en la fuente primaria. "
                  "No presentes inferencias como hechos. Correcciones/retirada: ver index.json (corrections).",
    }


def data_meta(fam_id, fam, generated):
    """Meta compacta de cada archivo de datos (licencia, atribución, fuente, fecha: obligatorias)."""
    return {"family": fam_id, "license": fam["license"], "license_url": fam.get("license_url"),
            "attribution": list(fam.get("attribution") or []), "source_url": fam.get("source_url"),
            "generated": generated, "catalog": SITE_BASE + "api/v1/%s/index.json" % fam_id}


def locate(p):
    """Primer punto con coordenadas: memorial; si no, lugar con coordenadas."""
    for m in p.get("memorials") or []:
        if m.get("lat") is not None:
            return m.get("locality"), m.get("lat"), m.get("lon")
    for pl in p.get("places") or []:
        if pl.get("lat") is not None:
            return pl.get("locality") or pl.get("label"), pl.get("lat"), pl.get("lon")
    m = (p.get("memorials") or [{}])[0]
    return m.get("locality"), None, None


def place_entries(p):
    """(rol, país, etiqueta-lugar, etiqueta-detalle, lat, lon) para el índice de lugares.
    Solo memorial y lugar de muerte; nunca nacimiento/origen (docs/legal regla 11)."""
    out = []
    for m in p.get("memorials") or []:
        loc = m.get("locality")
        if loc and m.get("country"):
            out.append(("memorial", m["country"], loc, m.get("address"), m.get("lat"), m.get("lon")))
    for pl in p.get("places") or []:
        if pl["role"] == "death" and pl.get("country"):
            out.append(("death", pl["country"], pl.get("locality") or pl["label"], pl["label"], pl.get("lat"), pl.get("lon")))
    return out


# ---------------------------------------------------------------- escritura

def safe_reset(path):
    """Borra un directorio generado SOLO si lleva el marcador del pipeline (nunca datos ajenos)."""
    if os.path.exists(path):
        if not os.path.exists(os.path.join(path, MARKER)):
            raise RuntimeError("%s existe y no fue generado por el pipeline (sin %s); no se borra." % (path, MARKER))
        shutil.rmtree(path)
    os.makedirs(path)
    with open(os.path.join(path, MARKER), "w") as f:
        f.write("Directorio generado por `python3 -m pipeline build`. No editar a mano.\n")


class Writer:
    def __init__(self, root):
        self.root = root
        self.files = {}

    def json(self, rel, obj, line_keys=()):
        n = write_json(os.path.join(self.root, rel), obj, line_keys)
        self.files[rel] = n
        return n


def write_family(w, fam_id, fam, persons, sources_used, generated, quality, shard_chars):
    meta = family_meta(fam_id, fam, sources_used, generated)
    dmeta = data_meta(fam_id, fam, generated)
    base = fam_id + "/"
    keys = [sort_surname(p) for p in persons]
    # 1) Fichas completas, una sola vez, agrupadas por prefijo de apellido (archivo canónico).
    people_buckets = assign_prefixes(keys, max_per=PEOPLE_PER_FILE)
    people_prefixes = sorted(people_buckets)
    where = {}
    for pre in people_prefixes:
        idx = sorted(people_buckets[pre], key=lambda i: (keys[i], fold(persons[i].get("name")), persons[i]["id"]))
        for i in idx:
            where[persons[i]["id"]] = pre
        w.json(base + "people/by-surname/%s.json" % pre,
               {"meta": dmeta, "prefix": pre, "count": len(idx), "people": [persons[i] for i in idx]}, ("people",))
    # 2) Búsqueda ligera (prefijos más gruesos: menos archivos).
    search_buckets = assign_prefixes(keys, max_per=SEARCH_PER_FILE)
    search_prefixes = sorted(search_buckets)
    for pre in search_prefixes:
        idx = sorted(search_buckets[pre], key=lambda i: (keys[i], fold(persons[i].get("name")), persons[i]["id"]))
        rows = []
        for i in idx:
            p = persons[i]
            loc, lat, lon = locate(p)
            rows.append([p["id"], p.get("name"), date_year(p.get("birth_date")), loc,
                         round(lat, 5) if lat is not None else None, round(lon, 5) if lon is not None else None,
                         where[p["id"]]])
        w.json(base + "search/index-%s.json" % pre,
               {"meta": dmeta, "prefix": pre,
                "columns": ["id", "name", "birth_year", "locality", "lat", "lon", "people_prefix"], "rows": rows}, ("rows",))
    # 3) Búsqueda por id: person/<shard>.json da el prefijo del archivo by-surname que contiene la ficha.
    shards = {}
    for p in persons:
        shards.setdefault(person_shard(p["id"], shard_chars), []).append([p["id"], where[p["id"]]])
    for sh, rows in sorted(shards.items()):
        w.json(base + "person/%s.json" % sh, {"meta": dmeta, "shard": sh, "columns": ["id", "people_prefix"],
                                              "rows": sorted(rows)}, ("rows",))
    # 4) Lugares.
    places = {}
    for p in persons:
        seen = set()
        for role, cc, label, detail, lat, lon in place_entries(p):
            k = (cc.lower(), slugify(label))
            if (k, role) in seen:
                continue
            seen.add((k, role))
            d = places.setdefault(k, {"labels": {}, "rows": []})
            d["labels"][label] = d["labels"].get(label, 0) + 1
            d["rows"].append([p["id"], p.get("name"), date_year(p.get("birth_date")), role, detail,
                              round(lat, 5) if lat is not None else None, round(lon, 5) if lon is not None else None])
    pindex = []
    cols = ["id", "name", "birth_year", "role", "detail", "lat", "lon"]
    for (cc, slug), d in sorted(places.items()):
        label = sorted(d["labels"].items(), key=lambda x: (-x[1], x[0]))[0][0]
        rows = sorted(d["rows"], key=lambda r: (fold(r[1]), r[0], r[3]))
        pts = [r for r in rows if r[5] is not None]
        lat = round(sum(r[5] for r in pts) / len(pts), 5) if pts else None
        lon = round(sum(r[6] for r in pts) / len(pts), 5) if pts else None
        pages = max(1, (len(rows) + PLACE_PAGE - 1) // PLACE_PAGE)
        for pg in range(pages):
            name = slug if pg == 0 else "%s~%d" % (slug, pg + 1)
            w.json(base + "places/%s/%s.json" % (cc, name),
                   {"meta": dmeta, "country": cc.upper(), "slug": slug, "label": label, "count": len(rows),
                    "page": pg + 1, "pages": pages, "columns": cols,
                    "rows": rows[pg * PLACE_PAGE:(pg + 1) * PLACE_PAGE]}, ("rows",))
        pindex.append([cc.upper(), slug, label, len(rows), lat, lon, pages])
    w.json(base + "places/index.json", {"meta": dmeta, "columns": ["country", "slug", "label", "count", "lat", "lon", "pages"],
                                        "rows": pindex}, ("rows",))
    # 5) Tablas de identificadores (clave de cruce entre familias; el join se hace en el cliente).
    id_maps = {}
    for p in persons:
        for scheme, v in (p.get("identifiers") or {}).items():
            if scheme == "osm":
                continue  # stone→persona ya está en data/search (person_id) y en memorials[].memorial_id
            for x in ([v] if isinstance(v, str) else (v or [])):
                id_maps.setdefault(scheme, {}).setdefault(x, set()).add(p["id"])
    for scheme, mp in sorted(id_maps.items()):
        rows = [[k] + sorted(v) for k, v in sorted(mp.items())]
        w.json(base + "ids/%s.json" % scheme, {"meta": dmeta, "scheme": scheme,
                                              "columns": ["external_id", "person_id", "..."], "rows": rows}, ("rows",))
    w.json(base + "quality/possible-duplicates.json",
           {"meta": dmeta, "rule": "Mismo nombre normalizado y mismo año de nacimiento, sin identificador compartido. NO se han fusionado.",
            "groups": quality["possible_duplicates"]}, ("groups",))
    w.json(base + "quality/blocked-merges.json",
           {"meta": dmeta, "rule": "Registros que comparten un identificador pero tienen Qid distinto o año de nacimiento incompatible. NO se han fusionado.",
            "items": quality["blocked_merges"]}, ("items",))
    stats = family_stats(persons)
    w.json(base + "stats.json", {"meta": dmeta, "stats": stats})
    findex = {
        "meta": meta,
        "family": fam_id,
        "count_people": len(persons),
        "surname_prefix_rule": ("clave = apellido normalizado: minúsculas, ß→ss, sin acentos, ä/ae→a, ö/oe→o, ü/ue→u, solo a-z, "
                                "sin partículas iniciales (von, van, de, zu…). Si la fuente no da apellido, se usa el último "
                                "token del nombre (solo para particionar; no se publica como apellido). Probar clave[:6], clave[:5], … "
                                "clave[:1] (rellenando con '_') y usar el primero que exista en la lista de prefijos."),
        "people_prefixes": people_prefixes,
        "search_prefixes": search_prefixes,
        "person_shard_chars": shard_chars,
        "person_shard_rule": ("shard = los %d últimos caracteres del id en minúsculas, otros caracteres → '_' "
                              "(JS: id.slice(-%d).toLowerCase().replace(/[^a-z0-9]/g,'_')). person/<shard>.json da el "
                              "people_prefix; la ficha completa está en people/by-surname/<people_prefix>.json."
                              % (shard_chars, shard_chars)),
        "person_shards": sorted(shards),
        "id_schemes": sorted(id_maps),
        "places": len(pindex),
        "endpoints": {
            "people": base + "people/by-surname/{prefix}.json",
            "person_lookup": base + "person/{shard}.json",
            "search": base + "search/index-{prefix}.json",
            "places_index": base + "places/index.json",
            "place": base + "places/{country}/{slug}.json",
            "ids": base + "ids/{scheme}.json",
            "stats": base + "stats.json",
        },
    }
    w.json(base + "index.json", findex)
    return findex, stats


def family_stats(persons):
    by_fate, by_decade, links, countries = {}, {}, {}, {}
    memorials = 0
    for p in persons:
        by_fate[p["fate"]] = by_fate.get(p["fate"], 0) + 1
        y = date_year(p.get("birth_date"))
        if y:
            dec = "%ds" % (y // 10 * 10)
            by_decade[dec] = by_decade.get(dec, 0) + 1
        for l in p.get("links", []):
            links[l["type"]] = links.get(l["type"], 0) + 1
        memorials += len(p.get("memorials") or [])
        for m in p.get("memorials") or []:
            if m.get("country"):
                countries[m["country"]] = countries.get(m["country"], 0) + 1
    return {"people": len(persons), "memorials": memorials, "by_fate": dict(sorted(by_fate.items())),
            "by_birth_decade": dict(sorted(by_decade.items())), "links_by_type": dict(sorted(links.items())),
            "memorials_by_country": dict(sorted(countries.items())),
            "with_birth_date": sum(1 for p in persons if p.get("birth_date")),
            "with_death_date": sum(1 for p in persons if p.get("death_date")),
            "restricted_survivor_minimization": sum(1 for p in persons if "survivor_minimization" in (p.get("restrictions") or []))}


def write_plaques(root, plaques, published_ids, generated, fam):
    """Índice de búsqueda de placas para el frontend (data/search/): SOLO lo que dice la placa."""
    safe_reset(root)
    w = Writer(root)
    meta = data_meta("odbl", fam, generated)
    meta["description"] = ("Índice ligero para buscar placas en el mapa sin descargar data/stones.json. Solo datos "
                           "de la placa (nombre, dirección, año JG). person_id apunta a la ficha en api/v1/odbl si existe.")
    keys = [sort_surname({"name": pl.get("n")}) for pl in plaques]
    buckets = assign_prefixes(keys, max_per=4000)
    for pre, idx in sorted(buckets.items()):
        idx = sorted(idx, key=lambda i: (keys[i], fold(plaques[i].get("n")), plaques[i]["stone_id"]))
        rows = [[plaques[i]["stone_id"], plaques[i].get("n"), plaques[i].get("a"), plaques[i].get("c"),
                 round(plaques[i]["la"], 6) if plaques[i].get("la") is not None else None,
                 round(plaques[i]["lo"], 6) if plaques[i].get("lo") is not None else None,
                 plaques[i].get("jg"), published_ids.get(plaques[i]["stone_id"])] for i in idx]
        w.json("index-%s.json" % pre, {"meta": meta, "prefix": pre,
                                       "columns": ["stone_id", "name", "address", "locality", "lat", "lon", "jg", "person_id"],
                                       "rows": rows}, ("rows",))
    w.json("manifest.json", {"meta": meta, "prefixes": sorted(buckets), "count": len(plaques),
                             "prefix_rule": "igual que api/v1/odbl/index.json surname_prefix_rule"})
    return w.files


# ---------------------------------------------------------------- orquestación

def run(source_ids=None, limit=None, offline=False, out=None, site_root=None, fixtures=None,
        strict=False, sources=None, suppressed=None, generated=None, shard_chars=2, write_site=True,
        sources_dir=None):
    out = out or os.path.join(REPO_ROOT, "api", "v1")
    all_sources = sources if sources is not None else load_sources(sources_dir)
    families = load_families(sources=all_sources)
    suppressed = load_suppressed() if suppressed is None else set(suppressed)
    if source_ids:
        missing = [s for s in source_ids if s not in all_sources]
        if missing:
            raise SystemExit("Fuentes desconocidas: %s" % ", ".join(missing))
        selected = [all_sources[s] for s in source_ids]
    else:
        selected = [s for s in all_sources.values() if s["enabled"]]
    ctx = Context(offline=offline, limit=limit, fixtures=fixtures)
    report = {"sources": {}, "failures": {}}
    records, retrieved_dates = [], []
    for cfg in selected:
        log("· %s (%s)…" % (cfg["id"], cfg["adapter"]))
        got = []
        try:
            for r in ADAPTERS[cfg["adapter"]](cfg, ctx):
                got.append(r)
        except (OfflineCacheMiss, HttpError, FileNotFoundError, OSError) as e:
            report["failures"][cfg["id"]] = str(e)
            log("  ✗ %s: %s" % (cfg["id"], e))
            if strict:
                raise
            continue
        report["sources"][cfg["id"]] = {"records": len(got)}
        log("  %d registros" % len(got))
        for r in got:
            rd = r["sources"][0].get("retrieved")
            if rd:
                retrieved_dates.append(rd[:10])
        records.extend(got)
    snap = [str(v.get("snapshot"))[:10] for v in ctx.notes.values() if v.get("snapshot")]
    generated = generated or max(snap + retrieved_dates or [ctx.today])
    ref_year = int(generated[:4])
    gate_report = {}
    records = license_gate(records, all_sources, gate_report)
    # Las retiradas se aplican tras el merge, sobre todos los ids de la persona (id, ids alternativos,
    # ids de registro y Qid): retirar un id retira a la persona entera, no solo una de sus placas.
    by_family = {}
    for r in records:
        fam = all_sources[r["sources"][0]["source_id"]]["license_family"]
        by_family.setdefault(fam, []).append(r)
    priorities = {k: v["priority"] for k, v in all_sources.items()}
    schema = load_json(os.path.join(PIPELINE_DIR, "schema", "person.schema.json"))
    validator = Validator(schema)
    safe_reset(out)
    w = Writer(out)
    fam_indexes, fam_stats, plaques, published_ids = {}, {}, [], {}
    policy_report = {}
    for fam_id in sorted(by_family):
        mreport = {}
        persons = merge_family(by_family[fam_id], priorities, mreport, qid_ids=not fam_id.startswith("partners/"))
        persons = suppress(persons, suppressed, report, "person")
        dups = possible_duplicates(persons)
        published = []
        fam_policy = {}
        for p in persons:
            pls = p.pop("_plaques", None)
            q = apply_person_policy(p, ref_year, fam_policy)
            if q is not None:
                published.append(q)
            if pls and fam_id == "odbl":
                for pl in pls:
                    plaques.append(pl)
                    if q is not None:
                        published_ids[pl["stone_id"]] = q["id"]
        pub_ids = set(p["id"] for p in published)
        dups = [g for g in dups if len([i for i in g["ids"] if i in pub_ids]) > 1]
        for g in dups:
            g["ids"] = [i for i in g["ids"] if i in pub_ids]
        blocked = [b for b in mreport.get("blocked_merges", []) if all(i in pub_ids for i in b["ids"])]
        errors = []
        for p in published:
            errs = validator.errors(p)
            if errs:
                errors.append((p["id"], errs[:3]))
        if errors:
            for pid, errs in errors[:20]:
                log("  ✗ esquema %s: %s" % (pid, errs))
            raise SystemExit("%d registros no cumplen el esquema en %s" % (len(errors), fam_id))
        used = sorted(set(s["source_id"] for p in published for s in p["sources"]))
        fidx, fst = write_family(w, fam_id, families[fam_id], published, [all_sources[s] for s in used], generated,
                                 {"possible_duplicates": dups, "blocked_merges": blocked}, shard_chars)
        fidx["merged_records"] = mreport.get("merged_records", 0)
        fam_indexes[fam_id] = fidx
        fam_stats[fam_id] = fst
        policy_report[fam_id] = dict(fam_policy, input_records=len(by_family[fam_id]), people_after_merge=len(persons),
                                     published=len(published), possible_duplicate_groups=len(dups),
                                     blocked_merges=len(blocked))
        log("  familia %s: %d registros → %d personas → %d publicadas" % (fam_id, len(by_family[fam_id]), len(persons), len(published)))
    # catálogo y documentación para agentes
    w.json("schema/person.schema.json", schema)
    agents.write_catalog(w, fam_indexes, fam_stats, families, all_sources, generated, report, policy_report)
    site_files = {}
    if write_site:
        site_root = site_root or os.path.dirname(os.path.dirname(out))
        site_files.update(agents.write_site_files(site_root, fam_indexes, families, generated))
        if plaques and "odbl" in families:
            plaques = [pl for pl in plaques if not (set([pl["stone_id"]]) & suppressed)]
            pf = write_plaques(os.path.join(site_root, "data", "search"), plaques, published_ids, generated,
                               families["odbl"])
            site_files.update({"data/search/" + k: v for k, v in pf.items()})
    # informes internos (no publicados; pueden mencionar ids retenidos)
    rep_dir = os.path.join(PIPELINE_DIR, "reports")
    os.makedirs(rep_dir, exist_ok=True)
    write_json(os.path.join(rep_dir, "license_gate.json"), {"generated": generated, "withheld_by_license": gate_report.get("withheld_by_license", {})})
    write_json(os.path.join(rep_dir, "build.json"), {"generated": generated, "sources": report["sources"],
                                                     "failures": report["failures"], "suppressed": report.get("suppressed", []),
                                                     "policy": policy_report, "notes": ctx.notes,
                                                     "files": len(w.files), "bytes": sum(w.files.values()),
                                                     "max_file_bytes": max(w.files.values()) if w.files else 0})
    return {"files": w.files, "site_files": site_files, "report": report, "policy": policy_report,
            "gate": gate_report, "generated": generated, "families": fam_indexes}
