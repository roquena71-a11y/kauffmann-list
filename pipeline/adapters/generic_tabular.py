"""Adaptador genérico CSV / JSON / JSONL con mapeo declarativo de columnas.

Pensado para la fase 2 (Yad Vashem, Arolsen, USHMM, Bundesarchiv...): basta con un
sources/<fuente>.json con "input" y "mapping"; no hay que escribir código.

Especificación de un campo (field spec):
  "Columna"                                 -> valor de la columna (admite ruta con puntos para JSON anidado)
  {"column": "Col", "map": {...}, "default": x, "format": "date|year|number|upper|lower",
   "split": ";", "template": "https://.../{value}", "strip_prefix": "..."}
  {"const": "DE"}
  {"concat": [spec, spec, ...], "sep": " "}
  {"template": "https://x.org/{Col A}/{Col B}"}    -> sustituye {Columna} con valores de la fila
  {"first": [spec, spec]}                           -> primer valor no vacío
"""
import csv
import io
import json
import os
import re

from ..http import HttpClient
from ..util import REPO_ROOT, clean_str, normalize_date, date_year

SCALARS = ["name", "given_name", "family_name", "birth_name", "birth_date", "birth_place",
           "death_date", "death_place", "fate"]
FATES = {"murdered", "died_in_persecution", "suicide", "missing", "survived", "fled", "deported",
         "imprisoned", "unknown"}
ID_SCHEMES = ["wikidata", "gedenkbuch", "yad_vashem", "ushmm", "arolsen", "holocaust_cz", "joods_monument", "mapping_the_lives", "osm"]


class MappingError(Exception):
    pass


def get_path(row, path):
    if path in row:
        return row[path]
    cur = row
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return None
    return cur


def _fmt(value, fmt):
    if value is None:
        return None
    if fmt == "date":
        return normalize_date(value)
    if fmt == "year":
        y = date_year(normalize_date(value))
        return str(y) if y else None
    if fmt == "number":
        try:
            return float(str(value).replace(",", "."))
        except ValueError:
            return None
    if fmt == "upper":
        return str(value).upper()
    if fmt == "lower":
        return str(value).lower()
    return value


def resolve(spec, row):
    """Devuelve el valor (str/num/None o lista si 'split')."""
    if spec is None:
        return None
    if isinstance(spec, str):
        v = get_path(row, spec)
        return clean_str(v) if isinstance(v, str) else v
    if not isinstance(spec, dict):
        raise MappingError("spec inválida: %r" % (spec,))
    if "const" in spec:
        return spec["const"]
    if "first" in spec:
        for s in spec["first"]:
            v = resolve(s, row)
            if v not in (None, "", []):
                return v
        return spec.get("default")
    if "concat" in spec:
        parts = [resolve(s, row) for s in spec["concat"]]
        parts = [str(p) for p in parts if p not in (None, "")]
        return clean_str(spec.get("sep", " ").join(parts)) if parts else spec.get("default")
    if "column" not in spec and "template" in spec:
        missing = []

        def sub(m):
            v = get_path(row, m.group(1))
            if v in (None, ""):
                missing.append(m.group(1))
                return ""
            return str(v)
        out = re.sub(r"\{([^{}]+)\}", sub, spec["template"])
        return None if missing else out
    if "column" not in spec:
        raise MappingError("spec sin column/const/concat/template: %r" % (spec,))
    v = get_path(row, spec["column"])
    if isinstance(v, str):
        v = clean_str(v)
    if v in (None, ""):
        v = None
    if v is not None and spec.get("strip_prefix") and str(v).startswith(spec["strip_prefix"]):
        v = str(v)[len(spec["strip_prefix"]):]
    if v is not None and "split" in spec:
        items = [clean_str(x) for x in re.split(spec["split"], str(v))]
        items = [_fmt(x, spec.get("format")) for x in items if x]
        if "template" in spec:
            items = [spec["template"].format(value=x) for x in items]
        return [x for x in items if x not in (None, "")]
    if v is not None and "map" in spec:
        key = str(v).strip().lower()
        mapping = {str(k).lower(): val for k, val in spec["map"].items()}
        v = mapping.get(key, spec.get("default"))
    v = _fmt(v, spec.get("format"))
    if v is None:
        return spec.get("default")
    if "template" in spec:
        return spec["template"].format(value=v)
    return v


def _as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def row_to_record(row, cfg, retrieved):
    sid = cfg["id"]
    m = cfg["mapping"]
    rid = resolve(m["record_id"], row)
    if rid in (None, ""):
        return None
    rid = str(rid)
    rec = {k: None for k in SCALARS}
    for k in SCALARS:
        if k in m:
            v = resolve(m[k], row)
            rec[k] = str(v) if v not in (None, "") and not isinstance(v, list) else None
    for k in ("birth_date", "death_date"):
        rec[k] = normalize_date(rec[k])
    if rec["fate"] not in FATES:
        rec["fate"] = "unknown"
    identifiers = {}
    for scheme, spec in sorted((m.get("identifiers") or {}).items()):
        if scheme not in ID_SCHEMES:
            raise MappingError("esquema de identificador desconocido: %s" % scheme)
        vals = sorted(set(str(x) for x in _as_list(resolve(spec, row)) if x not in (None, "")))
        if scheme == "wikidata":
            vals = [v for v in vals if re.match(r"^Q\d+$", v)]
            identifiers["wikidata"] = vals[0] if len(vals) == 1 else None
        elif vals:
            identifiers[scheme] = vals
    places = []
    for p in m.get("places") or []:
        label = resolve(p.get("label"), row)
        if not label:
            continue
        lat = _fmt(resolve(p.get("lat"), row), "number")
        lon = _fmt(resolve(p.get("lon"), row), "number")
        cc = resolve(p.get("country"), row)
        places.append({"role": p["role"], "label": str(label), "locality": resolve(p.get("locality"), row),
                       "lat": lat if lat is not None and -90 <= lat <= 90 else None,
                       "lon": lon if lon is not None and -180 <= lon <= 180 else None,
                       "country": str(cc).upper() if cc and re.match(r"^[A-Za-z]{2}$", str(cc)) else None,
                       "wikidata": None, "source_id": sid})
    deportations = []
    for d in m.get("deportations") or []:
        date, place, frm, raw = (resolve(d.get(k), row) for k in ("date", "place", "from", "raw"))
        if any(x not in (None, "") for x in (date, place, frm, raw)):
            deportations.append({"date": normalize_date(date), "place": place, "from": frm, "raw": raw,
                                 "source_id": sid})
    links = []
    for ln in m.get("links") or []:
        for url in _as_list(resolve(ln.get("url"), row)):
            if url and re.match(r"^https?://", str(url)):
                links.append({"type": ln.get("type", "record"), "url": str(url), "label": ln.get("label"),
                              "license": None, "text_url": None, "source_id": sid})
    rec_url = resolve(m.get("record_url"), row) if m.get("record_url") else None
    prefix = cfg["id_prefix"]
    rec.update({
        "id": prefix + "-" + re.sub(r"[^A-Za-z0-9_.:-]", "_", rid),
        "subject_type": "person",
        "fate_basis": "source_field" if rec["fate"] != "unknown" else None,
        "deportations": deportations,
        "places": places,
        "memorials": [],
        "links": links,
        "identifiers": identifiers,
        "sources": [{"source_id": sid, "record_id": rid, "url": rec_url, "license": cfg["license"],
                     "license_url": cfg.get("license_url"), "attribution": cfg["attribution"],
                     "retrieved": retrieved}],
        "_variants": {},
    })
    return rec


def read_rows(cfg, ctx):
    inp = cfg["input"]
    fmt = inp.get("format", "csv")
    if inp.get("url"):
        client = HttpClient(cfg["id"], offline=ctx.offline, min_interval=inp.get("min_interval_seconds", 1.0))
        raw = client.request(inp["url"], headers=inp.get("headers"))
    else:
        path = inp["path"] if os.path.isabs(inp["path"]) else os.path.join(REPO_ROOT, inp["path"])
        if not os.path.exists(path):
            raise FileNotFoundError("Entrada no encontrada para %s: %s" % (cfg["id"], path))
        with open(path, "rb") as f:
            raw = f.read()
    text = raw.decode(inp.get("encoding", "utf-8-sig"))
    if fmt == "csv":
        return list(csv.DictReader(io.StringIO(text), delimiter=inp.get("delimiter", ",")))
    if fmt == "jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if fmt == "json":
        data = json.loads(text)
        if inp.get("records_path"):
            data = get_path(data, inp["records_path"])
        if not isinstance(data, list):
            raise MappingError("El JSON de %s no contiene una lista de registros" % cfg["id"])
        return data
    raise MappingError("formato no soportado: %s" % fmt)


def fetch(cfg, ctx):
    rows = read_rows(cfg, ctx)
    retrieved = cfg.get("input", {}).get("retrieved") or ctx.today
    n = 0
    for row in rows:
        rec = row_to_record(row, cfg, retrieved)
        if rec is None:
            ctx.note(cfg["id"], "rows_without_id", 1, add=True)
            continue
        yield rec
        n += 1
        if ctx.limit and n >= ctx.limit:
            break
