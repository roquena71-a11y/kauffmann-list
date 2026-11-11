"""Políticas de publicación (docs/legal/analisis-licencias.md, §4).

- license_gate: nada de una fuente con publish_allowed:false llega a la salida (se filtra ANTES del merge,
  así ni siquiera influye en qué registros se unen).
- suppression: retiradas por id (pipeline/suppressed.json).
- living_filter: sin indicio de muerte y nacido hace < 110 años (o sin año) → fuera de la API.
- survivor_minimization: placa con ÜBERLEBT/FLUCHT/BEFREIT/ENTKAM y nacimiento ≥ 1916 → sin enlaces
  a fichas biográficas/registros (solo el propio memorial).
"""
from .inscription import DEATH_FATES, has_survivor_marker
from .util import date_year

LIVING_YEARS = 110
SURVIVOR_BIRTH_YEAR = 1916
MEMORIAL_LINK_TYPES = {"openstreetmap", "wikidata_memorial"}
REGISTRY_ID_SCHEMES = ("gedenkbuch", "yad_vashem", "ushmm", "arolsen", "holocaust_cz", "joods_monument", "mapping_the_lives")


def license_gate(records, sources, report):
    """Devuelve solo los registros de fuentes con publish_allowed:true. Registra lo retenido (solo ids)."""
    kept = []
    for r in records:
        sid = r["sources"][0]["source_id"]
        cfg = sources.get(sid)
        if cfg and cfg.get("publish_allowed") is True:
            kept.append(r)
        else:
            w = report.setdefault("withheld_by_license", {}).setdefault(sid, {"count": 0, "record_ids": []})
            w["count"] += 1
            w["record_ids"].append(r["sources"][0]["record_id"])
    return kept


def record_keys(r):
    keys = {r["id"]}
    for s in r.get("sources", []):
        keys.add(s["record_id"])
        keys.add("%s:%s" % (s["source_id"], s["record_id"]))
    q = (r.get("identifiers") or {}).get("wikidata")
    if q:
        keys.add(q)
        keys.add("wd-" + q)
    for k in r.get("alternate_ids") or []:
        keys.add(k)
    return keys


def suppress(items, suppressed, report, stage):
    if not suppressed:
        return items
    kept = []
    for r in items:
        hit = record_keys(r) & suppressed
        if hit:
            report.setdefault("suppressed", []).append({"stage": stage, "matched": sorted(hit)})
        else:
            kept.append(r)
    return kept


def death_evidence(p):
    return bool(p.get("death_date")) or p.get("fate") in DEATH_FATES


def birth_year(p):
    return date_year(p.get("birth_date"))


def possibly_living(p, ref_year):
    if death_evidence(p):
        return False
    by = birth_year(p)
    return by is None or by > ref_year - LIVING_YEARS


def survivor_restricted(p):
    texts = [m.get("inscription") for m in p.get("memorials", []) if m.get("inscription")]
    marker = any(has_survivor_marker(t) for t in texts) or p.get("fate") in ("survived", "fled")
    if not marker:
        return False
    by = birth_year(p)
    return by is None or by >= SURVIVOR_BIRTH_YEAR


def apply_person_policy(p, ref_year, report):
    """Devuelve la persona (posiblemente reducida) o None si no debe publicarse en la API."""
    if possibly_living(p, ref_year):
        report["possibly_living_excluded"] = report.get("possibly_living_excluded", 0) + 1
        return None
    if survivor_restricted(p):
        before = len(p.get("links", []))
        p["links"] = [l for l in p.get("links", []) if l["type"] in MEMORIAL_LINK_TYPES]
        ids = p.get("identifiers") or {}
        for k in REGISTRY_ID_SCHEMES:
            ids.pop(k, None)
        p["restrictions"] = sorted(set((p.get("restrictions") or []) + ["survivor_minimization"]))
        report["survivor_minimized"] = report.get("survivor_minimized", 0) + 1
        report["survivor_links_removed"] = report.get("survivor_links_removed", 0) + before - len(p["links"])
    return p
