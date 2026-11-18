"""`python3 -m pipeline validate`: comprueba la salida publicada.

- Cada ficha de <familia>/person/*.json cumple schema/person.schema.json.
- Todo JSON lleva meta.license, meta.attribution, meta.source_url y meta.generated (salvo openapi y el esquema).
- Ninguna fuente con publish_allowed:false aparece en la salida.
- Cada familia solo contiene registros de sus propias fuentes (no hay mezcla entre familias de licencia).
- Ningún id de pipeline/suppressed.json aparece.
- Tamaños: avisa de archivos > 1 MB.
"""
import json
import os

from .config import load_sources, load_suppressed
from .jsonschema_lite import Validator
from .util import PIPELINE_DIR, REPO_ROOT, load_json

MAX_BYTES = 1024 * 1024
NO_META = {"openapi.json", "schema/person.schema.json"}


def validate(out=None, sources=None, suppressed=None, max_bytes=MAX_BYTES):
    out = out or os.path.join(REPO_ROOT, "api", "v1")
    sources = sources if sources is not None else load_sources()
    suppressed = load_suppressed() if suppressed is None else set(suppressed)
    validator = Validator(load_json(os.path.join(PIPELINE_DIR, "schema", "person.schema.json")))
    blocked = {k for k, v in sources.items() if not v["publish_allowed"]}
    fam_of = {k: v["license_family"] for k, v in sources.items()}
    errors, warnings = [], []
    n_files = n_people = 0
    total = biggest = 0
    biggest_file = None
    if not os.path.isdir(out):
        return {"errors": ["no existe %s" % out], "warnings": [], "files": 0, "people": 0}
    for dirpath, _, files in os.walk(out):
        for fn in sorted(files):
            if not fn.endswith(".json"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, out).replace(os.sep, "/")
            size = os.path.getsize(path)
            n_files += 1
            total += size
            if size > biggest:
                biggest, biggest_file = size, rel
            if size > max_bytes:
                warnings.append("%s ocupa %d bytes (> %d)" % (rel, size, max_bytes))
            try:
                data = load_json(path)
            except ValueError as e:
                errors.append("%s: JSON inválido (%s)" % (rel, e))
                continue
            if rel not in NO_META:
                meta = data.get("meta") if isinstance(data, dict) else None
                if not isinstance(meta, dict):
                    errors.append("%s: falta meta" % rel)
                else:
                    for k in ("license", "attribution", "source_url", "generated"):
                        if not meta.get(k):
                            errors.append("%s: falta meta.%s" % (rel, k))
                    for s in meta.get("sources") or []:
                        if s.get("id") in blocked:
                            errors.append("%s: meta incluye fuente no publicable %s" % (rel, s["id"]))
            text = json.dumps(data, ensure_ascii=False)
            for sid in blocked:
                if '"source_id": "%s"' % sid in text:
                    errors.append("%s: contiene datos de la fuente no publicable %s" % (rel, sid))
            if "/people/by-surname/" in "/" + rel:
                family = rel.split("/people/by-surname/")[0]
                for p in data.get("people", []):
                    n_people += 1
                    for e in validator.errors(p)[:3]:
                        errors.append("%s %s: %s" % (rel, p.get("id"), e))
                    for s in p.get("sources", []):
                        if fam_of.get(s["source_id"]) != family:
                            errors.append("%s %s: fuente %s no pertenece a la familia %s" % (rel, p["id"], s["source_id"], family))
                    keys = {p["id"]} | set(p.get("alternate_ids") or []) | {s["record_id"] for s in p.get("sources", [])}
                    q = (p.get("identifiers") or {}).get("wikidata")
                    if q:
                        keys.add(q)
                    if keys & suppressed:
                        errors.append("%s %s: id retirado presente" % (rel, p["id"]))
    errors.extend(_check_find(out))
    return {"errors": errors, "warnings": warnings, "files": n_files, "people": n_people, "bytes": total,
            "max_bytes": biggest, "max_file": biggest_file}


def _check_find(out):
    """find/: todos los archivos que anuncia el manifiesto existen y las filas tienen el formato común."""
    errors = []
    for fam in sorted(os.listdir(out)):
        fi = os.path.join(out, fam, "find", "index.json")
        if not os.path.exists(fi):
            continue
        base = os.path.join(out, fam, "find")
        idx = load_json(fi)
        for pre, n in idx["name"]["prefixes"].items():
            path = os.path.join(base, "name", pre + ".json")
            if not os.path.exists(path):
                errors.append("%s/find: falta name/%s.json" % (fam, pre))
                continue
            d = load_json(path)
            if len(d["rows"]) != n:
                errors.append("%s/find/name/%s.json: %d filas, el manifiesto dice %d" % (fam, pre, len(d["rows"]), n))
            if d["columns"] != ["token", "id", "name", "birth_year", "death_year", "place", "people_prefix"]:
                errors.append("%s/find/name/%s.json: columnas inesperadas" % (fam, pre))
        for kind in ("birth", "death"):
            for y, n in idx["year"][kind].items():
                path = os.path.join(base, "year", kind, y + ".json")
                if not os.path.exists(path) or load_json(path)["count"] != n:
                    errors.append("%s/find/year/%s/%s.json: falta o recuento distinto" % (fam, kind, y))
                    continue
                for pg in range(2, load_json(path)["pages"] + 1):
                    if not os.path.exists(os.path.join(base, "year", kind, "%s~%d.json" % (y, pg))):
                        errors.append("%s/find/year/%s: falta %s~%d.json" % (fam, kind, y, pg))
        for key, cc, slug, label, count, pages in load_json(os.path.join(base, "city", "index.json"))["rows"]:
            for pg in range(pages):
                name = slug if pg == 0 else "%s~%d" % (slug, pg + 1)
                if not os.path.exists(os.path.join(base, "city", cc.lower(), name + ".json")):
                    errors.append("%s/find/city: falta %s/%s.json" % (fam, cc.lower(), name))
    return errors
