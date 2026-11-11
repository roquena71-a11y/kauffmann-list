"""Unificación conservadora DENTRO de una familia de licencia.

Reglas:
- Mismo Qid de Wikidata, o mismo id externo (Gedenkbuch, Yad Vashem, USHMM, Arolsen, holocaust.cz,
  Joods Monument, OSM) → misma persona.
- Nunca se une solo por nombre. Coincidencias de nombre + año de nacimiento se listan como
  'posibles duplicados' en un informe, sin fusionar.
- Guardas: no se unen dos grupos con Qids distintos ni con años de nacimiento incompatibles (> 1 año);
  esos casos van al informe como 'merges bloqueados'.
- Cada valor conserva su fuente (field_sources) y los valores discrepantes se guardan en variants.
- Registros de familias distintas NUNCA llegan aquí juntos (build.py agrupa por familia antes).
"""
import json

from .util import date_year, fold

MERGE_SCHEMES = ("gedenkbuch", "yad_vashem", "ushmm", "arolsen", "holocaust_cz", "joods_monument", "mapping_the_lives", "osm")
SCALARS = ["name", "given_name", "family_name", "birth_name", "birth_date", "birth_place",
           "death_date", "death_place", "fate", "fate_basis", "subject_type"]
LISTS = ["deportations", "places", "memorials", "links"]
KEEP_NULL = {"name"}  # claves requeridas por el esquema aunque sean null; el resto se omite si es null


class _UF:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x


def _years(r):
    ys = set()
    y = date_year(r.get("birth_date"))
    if y:
        ys.add(y)
    return ys


def cluster(records, report):
    n = len(records)
    uf = _UF(n)
    qids = [set([r["identifiers"].get("wikidata")]) - {None} for r in records]
    years = [_years(r) for r in records]
    index = {}
    for i, r in enumerate(records):
        ids = r.get("identifiers") or {}
        if ids.get("wikidata"):
            index.setdefault(("wikidata", ids["wikidata"]), []).append(i)
        for scheme in MERGE_SCHEMES:
            for v in ids.get(scheme) or []:
                index.setdefault((scheme, v), []).append(i)
        index.setdefault(("id", r["id"]), []).append(i)
    blocked = []
    for key in sorted(index):
        members = index[key]
        for j in members[1:]:
            a, b = uf.find(members[0]), uf.find(j)
            if a == b:
                continue
            if qids[a] and qids[b] and not (qids[a] & qids[b]):
                blocked.append({"key": list(key), "reason": "different_wikidata",
                                "ids": sorted([records[members[0]]["id"], records[j]["id"]])})
                continue
            # El mismo Qid (o el mismo id de persona) es identidad fuerte: se une aunque los años discrepen
            # (la discrepancia queda en variants). Para ids externos se exige compatibilidad de año.
            if key[0] not in ("wikidata", "id") and years[a] and years[b] and \
                    min(abs(x - y) for x in years[a] for y in years[b]) > 1:
                blocked.append({"key": list(key), "reason": "birth_year_mismatch",
                                "ids": sorted([records[members[0]]["id"], records[j]["id"]])})
                continue
            root, child = (a, b) if a < b else (b, a)
            uf.parent[child] = root
            qids[root] |= qids[child]
            years[root] |= years[child]
    groups = {}
    for i in range(n):
        groups.setdefault(uf.find(i), []).append(records[i])
    report["blocked_merges"] = report.get("blocked_merges", []) + blocked
    return list(groups.values())


def _precision(v):
    return len(v) if isinstance(v, str) else 0


def _choose(field, cands):
    """cands: [(value, source_id)] ya ordenados por prioridad de fuente."""
    first = cands[0][0]
    if field in ("birth_date", "death_date"):
        compatible = [c for c in cands if isinstance(c[0], str) and c[0].startswith(first[:4])
                      and (c[0].startswith(first) or first.startswith(c[0]))]
        best = max(compatible, key=lambda c: _precision(c[0]))[0]
        return best
    if field == "fate":
        known = [c for c in cands if c[0] != "unknown"]
        return known[0][0] if known else first
    return first


def _dedupe(items):
    seen, out = set(), []
    for it in items:
        k = json.dumps(it, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k)
            out.append(it)
    return out


def compose(group, priorities, qid_ids=True):
    group = sorted(group, key=lambda r: (priorities.get(r["sources"][0]["source_id"], 99), r["id"]))
    qid = next((r["identifiers"].get("wikidata") for r in group if r["identifiers"].get("wikidata")), None)
    if qid_ids:
        pid = ("wd-" + qid) if qid else group[0]["id"]
    else:
        # Familias partners/<fuente>: el id es siempre el de la institución (yv-…, ar-…); el Qid es solo referencia.
        pid = sorted(r["id"] for r in group if not r["id"].startswith("wd-"))[0] if any(
            not r["id"].startswith("wd-") for r in group) else group[0]["id"]
    person = {"id": pid}
    field_sources, variants = {}, {}
    for f in SCALARS:
        cands = [(r.get(f), r["sources"][0]["source_id"]) for r in group if r.get(f) not in (None, "")]
        if not cands:
            person[f] = None if f not in ("fate", "subject_type") else ("unknown" if f == "fate" else "person")
            continue
        val = _choose(f, cands)
        person[f] = val
        if f in ("fate_basis", "subject_type"):
            continue
        if f == "fate" and val == "unknown":
            field_sources[f] = sorted(set(s for v, s in cands if v == val))
            continue
        field_sources[f] = sorted(set(s for v, s in cands if v == val
                                      or (f in ("birth_date", "death_date") and isinstance(v, str) and val.startswith(v))))
        others = []
        for v, s in cands:
            if v == val or (f in ("birth_date", "death_date") and isinstance(v, str) and val.startswith(v)):
                continue
            if f == "fate" and v == "unknown":
                continue
            others.append({"value": v, "source_id": s})
        if others:
            variants[f] = _dedupe(others)
    for r in group:
        for f, vs in (r.get("_variants") or {}).items():
            for v in vs:
                if v["value"] != person.get(f):
                    variants.setdefault(f, [])
                    if v not in variants[f]:
                        variants[f].append(v)
    if person.get("fate") == "unknown":
        person["fate_basis"] = None
    for f in LISTS:
        items = []
        for r in group:
            # En objetos anidados se omiten las claves nulas (opcionales en el esquema): archivos más pequeños.
            items.extend({k: v for k, v in it.items() if v is not None} for it in (r.get(f) or []))
        person[f] = _dedupe(items)
    ids = {"wikidata": qid}
    for r in group:
        for k, v in (r.get("identifiers") or {}).items():
            if k == "wikidata" or not v:
                continue
            ids.setdefault(k, set()).update(v)
    person["identifiers"] = {k: (sorted(v) if isinstance(v, set) else v) for k, v in sorted(ids.items()) if v}
    person["sources"] = _dedupe([{k: v for k, v in s.items() if v is not None} for r in group for s in r["sources"]])
    alt = sorted(set(r["id"] for r in group) - {pid})
    if alt:
        person["alternate_ids"] = alt
    person["field_sources"] = field_sources
    if variants:
        person["variants"] = {k: sorted(v, key=lambda x: (str(x["value"]), x["source_id"])) for k, v in variants.items()}
    for f in SCALARS:
        if person.get(f) is None and f not in KEEP_NULL:
            del person[f]
    for f in LISTS:
        if not person[f]:
            del person[f]
    if person.get("subject_type") == "person":
        del person["subject_type"]  # valor por defecto; solo se escribe 'collective'
    plaques = [r["_plaque"] for r in group if r.get("_plaque")]
    if plaques:
        person["_plaques"] = plaques
    return person


def merge_family(records, priorities, report, qid_ids=True):
    groups = cluster(records, report)
    persons = [compose(g, priorities, qid_ids) for g in groups]
    persons.sort(key=lambda p: p["id"])
    # Ids duplicados tras compose (p.ej. dos grupos bloqueados con el mismo Qid no pueden ocurrir, pero se verifica)
    seen = {}
    for p in persons:
        if p["id"] in seen:
            raise ValueError("id duplicado tras merge: %s" % p["id"])
        seen[p["id"]] = True
    report["merged_records"] = report.get("merged_records", 0) + (len(records) - len(persons))
    return persons


def possible_duplicates(persons):
    """Mismo nombre normalizado + mismo año de nacimiento, sin identificador compartido: solo informe."""
    buckets = {}
    for p in persons:
        if not p.get("name") or p.get("subject_type") == "collective":
            continue
        nm = fold(p["name"])
        y = date_year(p.get("birth_date"))
        if len(nm.split()) < 2 or not y:
            continue
        buckets.setdefault((nm, y), []).append(p["id"])
    out = []
    for (nm, y), ids in sorted(buckets.items()):
        if len(ids) > 1:
            out.append({"name_key": nm, "birth_year": y, "ids": sorted(ids)})
    return out
