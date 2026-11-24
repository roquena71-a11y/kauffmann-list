#!/usr/bin/env python3
"""v25: inventario de fotos legales aún no usadas en la ficha.

Fuentes (solo Commons, nunca una categoría ni un sitio de licencia desconocida):
  - Wikidata P18 (SPARQL del 24-nov-2026, /workspace/v24-data/review/wd-img-cat.csv)
  - campo imgx ya presente en nuestros datos (URL de Commons)
  - OSM wikimedia_commons / image (extractos locales fuera de DE)

No consulta Overpass ni pega al contador. No inventa. No toca la/lo.
Uso: python3 pipeline/tools/photo_sources.py
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
REVIEW = Path("/workspace/v24-data/review")
OUT_CSV = REVIEW / "fotos-nuevas.csv"
OUT_JSON = REVIEW / "fotos-nuevas.json"

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

# Palabras que, en el nombre del archivo, indican foto de la placa (no retrato ni casa).
STONE_WORDS = re.compile(
    r"(stolperstein|stolperschwelle|pietra.?d.?inciampo|struikelsteen|"
    r"stumble.?stone|pierre.?d.?achoppement|snublestein|snubbelstein|"
    r"kamen.?u.?tlačovatele|kámen.?zmizel|stolpersteine)",
    re.I,
)

COMMONS_PATH = re.compile(
    r"(?:commons\.wikimedia\.org/(?:wiki/)?(?:Special:FilePath/|File:)|"
    r"upload\.wikimedia\.org/wikipedia/commons/(?:thumb/)?[0-9a-f]/[0-9a-f]{2}/)"
    r"([^?#]+)",
    re.I,
)


def commons_filename(raw):
    """Devuelve el nombre de archivo de Commons, o None si es categoría o no es Commons."""
    if not raw:
        return None
    s = unquote(str(raw).strip())
    if not s:
        return None
    # Varios valores separados por ; o |
    # Solo el primero que sea válido (el llamador puede partir).
    if re.search(r"(?i)^(Category:|category:|Kategorie:)", s) or "/Category:" in s or "Category:" in s[:40]:
        if re.search(r"(?i)^(Category:|Kategorie:)", s) or re.search(r"(?i)commons\.wikimedia\.org/wiki/Category:", s):
            return None
    # Si es una URL que no es Commons, no.
    if re.match(r"^https?://", s, re.I) and "wikimedia.org" not in s.lower() and "wikipedia.org" not in s.lower():
        return None
    m = COMMONS_PATH.search(s.replace(" ", "_"))
    if m:
        name = unquote(m.group(1)).replace("_", " ")
        # Special:FilePath y thumbs a veces traen /thumb/.../500px-Foo
        if "/thumb/" in s and "/" in name:
            # el último componente tras quitar prefijo de tamaño
            name = unquote(name.split("/")[-1])
            name = re.sub(r"^\d+px-", "", name).replace("_", " ")
        if re.match(r"(?i)^Category:", name):
            return None
        return name
    if re.match(r"^https?://", s, re.I):
        return None
    # File:Nombre.jpg o Nombre.jpg
    name = s
    name = re.sub(r"(?i)^File:", "", name).strip()
    name = unquote(name).replace("_", " ")
    if not name or re.match(r"(?i)^Category:", name):
        return None
    # Sin ruta tipo http residual
    if "/" in name and not name.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff", ".gif", ".webp")):
        return None
    if not name.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff", ".gif", ".webp")):
        return None
    return name


def split_values(raw):
    if not raw:
        return []
    return [p.strip() for p in re.split(r"\s*[;|]\s*", str(raw)) if p.strip()]


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


def load_p18():
    """item Qid -> [filenames] (P18). Las filas solo-categoría (img vacío, cat lleno) se saltan."""
    by = {}
    cats_only = 0
    with_p18 = 0
    path = REVIEW / "wd-img-cat.csv"
    with path.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            item = (row.get("item") or "").rstrip("/").split("/")[-1]
            img = (row.get("img") or "").strip()
            cat = (row.get("cat") or "").strip()
            if not item:
                continue
            fn = commons_filename(img) if img else None
            if fn:
                by.setdefault(item, [])
                if fn not in by[item]:
                    by[item].append(fn)
                with_p18 += 1
            elif cat and not img:
                cats_only += 1
    return by, with_p18, cats_only


def load_osm_files():
    files = []
    v20 = Path("/workspace/v20-data")
    for p in sorted(v20.glob("osm20_*.json")):
        cc = p.name.replace("osm20_", "").replace(".json", "")
        if cc == "DE":
            continue
        files.append((cc, p))
    extra = [
        ("FI", Path("/workspace/v19-data/osm_fi.json")),
        ("JE", Path("/workspace/v19-data/osm_je.json")),
        ("RO", Path("/workspace/v19-data/osm_ro.json")),
        ("SE", Path("/workspace/se-data/osm_se.json")),
    ]
    for cc, p in extra:
        if p.exists():
            files.append((cc, p))
    return files


def load_osm_commons():
    """osm id (n123 / w123) -> [(filename, tag, cc)]"""
    by = {}
    skipped_non_commons = 0
    skipped_category = 0
    for cc, path in load_osm_files():
        data = json.loads(path.read_text(encoding="utf-8"))
        els = data.get("elements") if isinstance(data, dict) else data
        if not isinstance(els, list):
            els = []
        for e in els:
            typ = e.get("type") or ""
            eid = e.get("id")
            if typ not in ("node", "way") or eid is None:
                continue
            oid = typ[0] + str(eid)
            tags = e.get("tags") or {}
            for key in ("wikimedia_commons", "image"):
                for raw in split_values(tags.get(key)):
                    if re.match(r"(?i)^(Category:|Kategorie:)", raw) or re.search(r"(?i)/Category:", raw):
                        skipped_category += 1
                        continue
                    fn = commons_filename(raw)
                    if not fn:
                        if raw:
                            skipped_non_commons += 1
                        continue
                    by.setdefault(oid, [])
                    rec = (fn, key, cc)
                    if rec not in by[oid]:
                        by[oid].append(rec)
    return by, skipped_non_commons, skipped_category


def photo_kind(fn):
    if not fn:
        return "unknown"
    if STONE_WORDS.search(fn):
        return "stone"
    return "possibly_not_stone"


def pick_filename(cands):
    """Elige un fichero: preferir el que parece de la placa; si no, el primero."""
    stone = [c for c in cands if photo_kind(c["filename"]) == "stone"]
    return (stone or cands)[0]


def main():
    stones = load_stones()
    p18, p18_rows, cats_only = load_p18()
    osm, skip_nc, skip_cat = load_osm_commons()

    no_img = [s for s in stones if not s.get("img")]
    has_img = [s for s in stones if s.get("img")]

    rows = []
    # Conteos de candidatos por fuente (placas sin img).
    src_hit = Counter()
    union_ids = set()

    def add(s, filename, origin, extra=""):
        if not filename:
            return
        union_ids.add(s["id"])
        src_hit[origin] += 1
        rows.append({
            "id": s["id"],
            "name": s.get("n") or "",
            "city": s.get("c") or s.get("cd") or "",
            "cc": s.get("cc") or "DE",
            "src": s.get("src") or "",
            "filename": filename,
            "origin": origin,
            "kind": photo_kind(filename),
            "wd": s.get("wd") or (s["id"] if re.fullmatch(r"Q\d+", s["id"]) else ""),
            "note": extra,
        })

    # 1) P18 de Wikidata, por Qid de la placa (s.wd o s.id si es Q…)
    p18_stones = 0
    for s in no_img:
        qids = []
        if s.get("wd"):
            qids.append(s["wd"])
        if re.fullmatch(r"Q\d+", s["id"] or ""):
            qids.append(s["id"])
        fns = []
        for q in qids:
            for fn in p18.get(q) or []:
                if fn not in fns:
                    fns.append(fn)
        if fns:
            p18_stones += 1
            add(s, fns[0], "wikidata_p18", "" if len(fns) == 1 else "también: " + " | ".join(fns[1:]))

    # 2) imgx ya en nuestros datos (solo Commons)
    imgx_ok = imgx_skip = 0
    for s in no_img:
        raw = s.get("imgx")
        if not raw:
            continue
        fn = commons_filename(raw)
        if not fn:
            imgx_skip += 1
            continue
        imgx_ok += 1
        add(s, fn, "imgx")

    # 3) OSM fuera de DE
    osm_ok = 0
    for s in no_img:
        if not re.fullmatch(r"[nw]\d+", s.get("id") or ""):
            continue
        recs = osm.get(s["id"]) or []
        if not recs:
            continue
        fn = recs[0][0]
        osm_ok += 1
        extra = ""
        if len(recs) > 1:
            extra = "también: " + " | ".join("%s (%s)" % (a, b) for a, b, _ in recs[1:])
        add(s, fn, "osm_commons_non_de", extra)

    # Unión por placa: una fila "elegida" por id
    by_id = {}
    for r in rows:
        by_id.setdefault(r["id"], []).append(r)
    chosen = []
    origin_priority = {"wikidata_p18": 0, "imgx": 1, "osm_commons_non_de": 2}
    for sid, cands in by_id.items():
        # Preferir origen en ese orden; dentro, foto que parece de la placa.
        cands_sorted = sorted(cands, key=lambda r: (origin_priority.get(r["origin"], 9), 0 if r["kind"] == "stone" else 1))
        best = cands_sorted[0]
        origins = sorted(set(c["origin"] for c in cands))
        best = dict(best)
        best["origins"] = "+".join(origins)
        chosen.append(best)

    REVIEW.mkdir(parents=True, exist_ok=True)
    cols = ["id", "name", "city", "cc", "src", "filename", "origin", "origins", "kind", "wd", "note"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in sorted(chosen, key=lambda x: (x["origin"], x["id"])):
            w.writerow({k: r.get(k, "") for k in cols})

    summary = {
        "stones_total": len(stones),
        "with_img": len(has_img),
        "without_img": len(no_img),
        "p18_rows_with_file": p18_rows,
        "p18_category_only_rows": cats_only,
        "p18_stones_without_img": p18_stones,
        "imgx_commons_without_img": imgx_ok,
        "imgx_skipped_non_commons": imgx_skip,
        "osm_non_de_without_img": osm_ok,
        "osm_skipped_non_commons": skip_nc,
        "osm_skipped_category": skip_cat,
        "union_stones": len(chosen),
        "union_by_origin_exclusive": dict(Counter(r["origin"] for r in chosen)),
        "union_by_kind": dict(Counter(r["kind"] for r in chosen)),
        "already_reviewed_estimate": "P18 969 + imgx 332 + OSM no-DE 356 → unión 1650 (revisión 03:12)",
    }
    OUT_JSON.write_text(json.dumps({"summary": summary, "chosen": chosen}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("csv", OUT_CSV, "rows", len(chosen))


if __name__ == "__main__":
    main()
