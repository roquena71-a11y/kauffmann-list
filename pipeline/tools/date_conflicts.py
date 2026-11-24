#!/usr/bin/env python3
"""v25: choques entre el año de la inscripción y el dato estructurado (b/d).

Solo lectura de las coordenadas de origen (no se tocan la/lo). No inventa fechas.
Uso (desde la raíz del repo):

  python3 -m pipeline.tools.date_conflicts

Escribe:
  /workspace/v24-data/review/fechas-conflicto.csv
  data/date-conflicts-v25.json  (sidecar para la ficha; solo registros con choque de año)
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.inscription import dates_conflict, dates_day_conflict, inscription_event_dates
from pipeline.util import date_year, normalize_date

ADDED_FILES = [
    "data/berlin-added-20261121.json",
    "data/koeln-added-20261121.json",
    "data/moenchengladbach-added-20261121.json",
    "data/denhaag-added-20261121.json",
    "data/krefeld-added-20261121.json",
    "data/monza-added-20261121.json",
    "data/viersen-added-20261121.json",
    "data/memmingen-added-20261121.json",
    "data/moers-added-20261121.json",
    "data/grevenbroich-added-20261121.json",
    "data/firenze-added-20261121.json",
    "data/xanten-added-20261121.json",
    "data/dresden-added-20261121.json",
    "data/erkrath-added-20261121.json",
    "data/dormagen-added-20261121.json",
]
CITY_SRCS = {
    "berlin", "koeln", "moenchengladbach", "denhaag", "krefeld", "monza", "viersen",
    "memmingen", "moers", "grevenbroich", "firenze", "xanten", "dresden", "erkrath", "dormagen",
}
CSV_PATH = Path("/workspace/v24-data/review/fechas-conflicto.csv")
JSON_PATH = ROOT / "data" / "date-conflicts-v25.json"
BERLIN = timezone(timedelta(hours=1))

SRC_LABEL = {
    "osm": "OpenStreetMap",
    "wd": "Wikidata",
    "osm+wd": "Wikidata o OpenStreetMap",
}
# Para municipales, el propio src es la etiqueta corta; la ficha ya tiene el nombre de la fuente.


def src_group(s):
    src = s.get("src") or ""
    if src in CITY_SRCS or s.get("_added"):
        return "city"
    if src in ("osm", "wd", "osm+wd"):
        return src
    return "city" if src else "unknown"


def other_label(s):
    g = src_group(s)
    if g == "city":
        return s.get("src") or "lista municipal"
    return SRC_LABEL.get(s.get("src"), s.get("src") or "dato estructurado")


def load_stones():
    data = json.loads((ROOT / "data/stones.json").read_text(encoding="utf-8"))
    stones = list(data["stones"])
    for rel in ADDED_FILES:
        part = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        for s in part.get("stones") or []:
            s = dict(s)
            s["_added"] = True
            stones.append(s)
    return stones


def load_bio():
    bio = {}
    bdir = ROOT / "data" / "bio"
    for path in sorted(bdir.glob("*.json")):
        if path.name == "manifest.json":
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict):
                    bio[k] = v
    return bio


def bio_year(rec, role):
    """Año que la ficha ya muestra en la cabecera (paquete bio), si se puede leer."""
    if not rec:
        return None
    insc = rec.get("insc") or {}
    raw = insc.get({"birth": "birth", "death": "death", "deportation": "deportation"}[role])
    if not raw:
        return None
    # birth en el paquete suele ser '1870' o '9.1.1870'
    nd = normalize_date(raw)
    if nd:
        return date_year(nd)
    ev = inscription_event_dates(str(raw))
    # Si el campo bio es una frase, extraer el rol correspondiente; si no, cualquier año.
    if role in ev and ev[role]["value"]:
        return date_year(ev[role]["value"])
    years = []
    for r in ev.values():
        for v, _ in r.get("all") or []:
            y = date_year(v)
            if y:
                years.append(y)
    if len(set(years)) == 1:
        return years[0]
    return None


def compare_field(s, role, structured, ev):
    """Devuelve un dict de fila o None si no hay nada que decir."""
    info = ev.get(role) or {}
    insc_val = info.get("value")
    insc_raw = info.get("raw")
    ambiguous = bool(info.get("ambiguous"))
    all_vals = info.get("all") or []
    st = normalize_date(structured) if structured else None
    year_c = dates_conflict(st, insc_val) if (st and insc_val) else False
    day_c = dates_day_conflict(st, insc_val) if (st and insc_val) else False
    # Inscripción ambigua frente a un estructurado: no se elige; se informa.
    amb_conflict = False
    if ambiguous and st:
        years = {date_year(v) for v, _ in all_vals}
        years.discard(None)
        if years and date_year(st) not in years:
            amb_conflict = True
        elif years and date_year(st) in years and len(years) > 1:
            # El estructurado coincide con uno de los años de la placa, pero la placa es ambigua.
            amb_conflict = False  # no es un choque claro estructurado-vs-placa
    if not (year_c or day_c or amb_conflict):
        return None
    return {
        "id": s.get("id"),
        "name": s.get("n") or "",
        "address": s.get("a") or "",
        "city": s.get("c") or s.get("cd") or "",
        "src_group": src_group(s),
        "src": s.get("src") or "",
        "field": role,
        "insc_raw": insc_raw or " | ".join(r for _, r in all_vals),
        "insc_date": insc_val or "",
        "insc_all": " | ".join("%s (%s)" % (v, r) for v, r in all_vals),
        "structured": st or (str(structured) if structured else ""),
        "other_src": other_label(s),
        "year_conflict": "yes" if year_c or amb_conflict else "no",
        "day_conflict": "yes" if day_c else "no",
        "insc_ambiguous": "yes" if ambiguous else "no",
        "person_qid": s.get("p") or "",
        "stone_qid": s.get("wd") or "",
        "notes": "inscripción con varios años distintos; no se elige" if ambiguous else "",
    }


def main():
    stones = load_stones()
    bio = load_bio()
    rows = []
    # Conteos de cobertura (no son conflictos).
    cover = Counter()
    by = defaultdict(Counter)
    for s in stones:
        ev = inscription_event_dates(s.get("i") or "")
        cover["stones"] += 1
        if s.get("i"):
            cover["with_inscription"] += 1
        g = src_group(s)
        cover[g] += 1
        # Cabecera de la ficha (bio) vs estructurado, como lo vio Carlos.
        rec = bio.get(s["id"])
        for role, field in (("birth", "b"), ("death", "d"), ("deportation", None)):
            structured = s.get(field) if field else None
            if ev.get(role) and ev[role].get("value"):
                cover["insc_%s" % role] += 1
            if structured:
                cover["struct_%s" % role] += 1
            if ev.get(role) and ev[role].get("value") and structured:
                cover["both_%s" % role] += 1
            row = compare_field(s, role, structured, ev)
            if row:
                # Añadir año de la cabecera bio, por transparencia.
                byear = bio_year(rec, role)
                row["bio_header_year"] = str(byear) if byear else ""
                rows.append(row)
                if row["year_conflict"] == "yes":
                    by[role][g] += 1
                    cover["year_conflict_%s" % role] += 1
                if row["day_conflict"] == "yes":
                    cover["day_conflict_%s" % role] += 1

    # Anna Mayer debe aparecer.
    anna = [r for r in rows if r["id"] == "n13186756540"]
    if not any(r["field"] == "birth" and r["year_conflict"] == "yes" for r in anna):
        raise SystemExit("ERROR: Anna Mayer (n13186756540) no aparece como choque de nacimiento")

    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    cols = [
        "id", "name", "address", "city", "src_group", "src", "field",
        "insc_raw", "insc_date", "insc_all", "structured", "other_src",
        "year_conflict", "day_conflict", "insc_ambiguous", "bio_header_year",
        "person_qid", "stone_qid", "notes",
    ]
    rows.sort(key=lambda r: (r["field"], r["src_group"], r["id"] or ""))
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})

    # Sidecar: choques de año o de día (mismo año, distinta fecha completa).
    # En ambos casos la inscripción es la principal.
    conflicts = {}
    for r in rows:
        if r["year_conflict"] != "yes" and r["day_conflict"] != "yes":
            continue
        if r["insc_ambiguous"] == "yes" and not r["insc_date"]:
            # No hay un valor único de inscripción que mostrar como principal.
            rec = conflicts.setdefault(r["id"], {})
            rec[r["field"]] = {
                "insc": None,
                "insc_all": r["insc_all"],
                "other": r["structured"],
                "other_src": r["other_src"],
                "ambiguous": True,
            }
            continue
        rec = conflicts.setdefault(r["id"], {})
        rec[r["field"]] = {
            "insc": r["insc_date"],
            "raw": r["insc_raw"],
            "other": r["structured"],
            "other_src": r["other_src"],
            "ambiguous": False,
        }

    now = datetime.now(BERLIN).strftime("%Y-%m-%dT%H:%M%z")
    sidecar = {
        "meta": {
            "generated": now,
            "from_commit": "3e46ab52",
            "rule": "Si el año de la inscripción y el dato estructurado no coinciden, la inscripción es la principal; el otro valor se conserva como 'otra fuente'. No se elige en silencio. No se tocan la/lo.",
            "year_conflicts": {
                "birth": dict(by["birth"]),
                "death": dict(by["death"]),
                "deportation": dict(by["deportation"]),
            },
            "n_stones_with_year_conflict": len({r["id"] for r in rows if r["year_conflict"] == "yes"}),
            "n_year_conflict_rows": sum(1 for r in rows if r["year_conflict"] == "yes"),
            "n_day_conflict_rows": sum(1 for r in rows if r["day_conflict"] == "yes"),
        },
        "conflicts": conflicts,
    }
    JSON_PATH.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    def fmt(counter):
        return ", ".join("%s %d" % (k, counter[k]) for k in ("osm", "wd", "osm+wd", "city") if counter[k])

    print("stones", cover["stones"], "with inscription", cover["with_inscription"])
    print("year conflicts birth:", cover["year_conflict_birth"], "by source:", fmt(by["birth"]))
    print("year conflicts death:", cover["year_conflict_death"], "by source:", fmt(by["death"]))
    print("year conflicts deportation:", cover["year_conflict_deportation"], "by source:", fmt(by["deportation"]))
    print("same-year day conflicts birth/death/dep:",
          cover["day_conflict_birth"], cover["day_conflict_death"], cover["day_conflict_deportation"])
    print("both (insc+struct) birth/death:", cover["both_birth"], cover["both_death"])
    print("csv", CSV_PATH, "rows", len(rows))
    print("json", JSON_PATH, "stones", len(conflicts))
    print("Anna Mayer", anna)


if __name__ == "__main__":
    main()
