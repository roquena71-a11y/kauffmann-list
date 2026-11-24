#!/usr/bin/env python3
"""v25: autor y licencia de cada foto de Commons mostrada en la ficha.

Lotes educados a la API de Commons (extmetadata). No pega al contador ni a workers.dev.
Reanudable: caché en /workspace/v24-data/review/commons-extmetadata.json.

Uso: python3 pipeline/tools/fetch_commons_credits.py
"""
from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEW = Path("/workspace/v24-data/review")
CACHE = REVIEW / "commons-extmetadata.json"
OUT = ROOT / "data" / "photo-credits-v25.json"
UA = "ListaKauffmann/25 (https://roquena71-a11y.github.io/kauffmann-list/; https://github.com/roquena71-a11y/kauffmann-list)"
BATCH = 40
SLEEP = 0.45
BERLIN = timezone(timedelta(hours=1))

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


def load_filenames():
    names = set()
    stones = json.loads((ROOT / "data/stones.json").read_text(encoding="utf-8"))["stones"]
    for s in stones:
        if s.get("img"):
            names.add(s["img"])
    for rel in ADDED_FILES:
        p = ROOT / rel
        if not p.exists():
            continue
        part = json.loads(p.read_text(encoding="utf-8"))
        for s in part.get("stones") or []:
            if s.get("img"):
                names.add(s["img"])
    added = ROOT / "data/photos-added-v25.json"
    if added.exists():
        for fn in (json.loads(added.read_text(encoding="utf-8")).get("photos") or {}).values():
            if fn:
                names.add(fn)
    return sorted(names)


def strip_html(t):
    if not t:
        return None
    t = re.sub(r"<br\s*/?>", " ", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    return t or None


def extract_credit(meta):
    """meta: extmetadata dict from Commons. No se inventa: si falta un campo, queda vacío."""
    def val(*keys):
        for k in keys:
            v = meta.get(k) or {}
            if isinstance(v, dict):
                v = v.get("value")
            s = strip_html(v) if v else None
            if s:
                return s
        return None
    author = val("Artist", "Attribution", "Credit")
    license_name = val("LicenseShortName", "UsageTerms")
    license_url = val("LicenseUrl")
    return {"a": author, "l": license_name, "u": license_url, "missing": not (author or license_name)}


def api_batch(titles):
    q = urllib.parse.urlencode({
        "action": "query",
        "titles": "|".join("File:" + t.replace("_", " ") for t in titles),
        "prop": "imageinfo",
        "iiprop": "extmetadata",
        "format": "json",
        "formatversion": "2",
        "redirects": "1",
    })
    url = "https://commons.wikimedia.org/w/api.php?" + q
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def normalize_title(t):
    t = re.sub(r"(?i)^File:", "", t or "").replace("_", " ").strip()
    return t


def main():
    REVIEW.mkdir(parents=True, exist_ok=True)
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    names = load_filenames()
    todo = [n for n in names if n not in cache]
    print("filenames", len(names), "cached", len(cache), "todo", len(todo), flush=True)
    fails = 0
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i + BATCH]
        data = None
        for attempt in range(4):
            try:
                data = api_batch(batch)
                break
            except Exception as ex:
                time.sleep(3 * (attempt + 1))
                last = ex
                data = None
        if data is None:
            fails += 1
            print("FAIL batch", i, last, flush=True)
            continue
        # Map redirected titles back.
        redir = {}
        for r in data.get("redirects") or []:
            redir[normalize_title(r.get("from"))] = normalize_title(r.get("to"))
        # normalized requested
        wanted = {normalize_title(x): x for x in batch}
        pages = data.get("query", {}).get("pages") or []
        seen = set()
        for page in pages:
            title = normalize_title(page.get("title") or "")
            info = (page.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            rec = extract_credit(meta)
            rec["missing_page"] = bool(page.get("missing"))
            rec["canonical"] = title
            # attach to original names that redirect here or match
            origins = [title] + [k for k, v in redir.items() if v == title]
            for orig in origins:
                orig_raw = wanted.get(orig) or orig
                cache[orig_raw] = rec
                seen.add(orig)
                if orig_raw != orig:
                    cache[orig] = rec
        # titles requested that got no page (shouldn't happen often)
        for raw in batch:
            if raw not in cache and normalize_title(raw) not in seen:
                cache[raw] = {"a": None, "l": None, "u": None, "missing": True, "missing_page": True}
        if (i // BATCH) % 10 == 0 or i + BATCH >= len(todo):
            CACHE.write_text(json.dumps(cache, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
            print("progress", min(i + BATCH, len(todo)), "/", len(todo), "cache", len(cache), flush=True)
        time.sleep(SLEEP)
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # Compact sidecar for the site: only author/licence/url, keyed by the filename we store (spaces).
    compact = {}
    for n in names:
        rec = cache.get(n) or cache.get(n.replace("_", " ")) or {}
        item = {k: rec[k] for k in ("a", "l", "u") if rec.get(k)}
        if rec.get("missing_page"):
            item["x"] = "missing"
        elif rec.get("missing"):
            item["x"] = "nolicense"
        compact[n] = item
    out = {
        "meta": {
            "generated": datetime.now(BERLIN).strftime("%Y-%m-%dT%H:%M%z"),
            "source": "Wikimedia Commons API imageinfo/extmetadata",
            "n": len(compact),
            "with_author": sum(1 for v in compact.values() if v.get("a")),
            "with_license": sum(1 for v in compact.values() if v.get("l")),
            "missing_page": sum(1 for v in compact.values() if v.get("x") == "missing"),
            "nolicense": sum(1 for v in compact.values() if v.get("x") == "nolicense"),
        },
        "credits": compact,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print("wrote", OUT, "bytes", OUT.stat().st_size, "meta", out["meta"], "fails", fails)


if __name__ == "__main__":
    main()
