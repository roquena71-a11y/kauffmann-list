"""Búsqueda estática para agentes: índices precalculados por nombre, lugar y año (api/v1/<familia>/find/).

Todo se deriva de las fichas YA publicadas (después del filtro de posibles vivos y de las retiradas), así que
hereda esas políticas y la licencia de la familia. No añade datos nuevos ni mezcla familias de licencia.

Fila común (columns): id, name, birth_year, death_year, place, people_prefix
  · id            → ficha completa en <familia>/people/by-surname/<people_prefix>.json (campo sources[] con las fuentes)
  · place         → lugar del memorial o de muerte (nunca el de nacimiento/origen); puede ser null
  · enlace humano → odbl: SITE/#s=<memorials[0].memorial_id>; cc0: SITE/#p=<id> (se abre en el mapa)
"""
import re

from .util import date_year, fold, slugify, NAME_PARTICLES

SITE_BASE = "https://roquena71-a11y.github.io/kauffmann-list/"
ROW_COLUMNS = ["id", "name", "birth_year", "death_year", "place", "people_prefix"]
NAME_PER_FILE = 3000
PAGE_ROWS = 4000        # filas por página en city/ y year/ (archivos ≲ 500 KB)
YEAR_MIN, YEAR_MAX = 1700, 2100
_TITLES = {"dr", "prof", "rabbiner", "rabbi", "sanitatsrat", "justizrat", "dipl", "ing", "pfarrer", "pastor"}
# Nombres alternativos de ciudades muy conocidas. Solo se publican si la ciudad existe en los datos.
EXONYMS = {
    "cologne": "koln", "munich": "munchen", "nuremberg": "nurnberg", "hanover": "hannover",
    "brunswick": "braunschweig", "vienna": "wien", "prague": "praha", "warsaw": "warszawa",
    "terezin": "theresienstadt",
}


def name_tokens(name):
    """Tokens normalizados de un nombre (≥2 letras, sin títulos ni partículas). Misma normalización que fold()."""
    out, seen = [], set()
    for t in fold(re.sub(r"\(.*?\)", " ", name or "")).split():
        if len(t) < 2 or t in NAME_PARTICLES or t in _TITLES or t.isdigit() or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def place_of(p):
    """Lugar del memorial; si no, lugar de muerte. Nunca nacimiento/origen (regla 11 de docs/legal)."""
    for m in p.get("memorials") or []:
        if m.get("locality"):
            return m["locality"], (m.get("country") or "").upper()
    for pl in p.get("places") or []:
        if pl.get("role") == "death" and (pl.get("locality") or pl.get("label")):
            return pl.get("locality") or pl["label"], (pl.get("country") or "").upper()
    return None, ""


def city_entries(p):
    """[(país, etiqueta)] únicos del memorial y la muerte (mismo criterio que places/)."""
    out, seen = [], set()
    for m in p.get("memorials") or []:
        loc = m.get("locality")
        if loc and m.get("country"):
            k = (m["country"].lower(), fold(loc))
            if k not in seen:
                seen.add(k)
                out.append((m["country"].lower(), loc))
    for pl in p.get("places") or []:
        if pl.get("role") == "death" and pl.get("country"):
            loc = pl.get("locality") or pl["label"]
            k = (pl["country"].lower(), fold(loc))
            if loc and k not in seen:
                seen.add(k)
                out.append((pl["country"].lower(), loc))
    return out


def row_of(p, where):
    loc, _ = place_of(p)
    return [p["id"], p.get("name"), date_year(p.get("birth_date")), date_year(p.get("death_date")), loc, where[p["id"]]]


def _assign(keys_to_idx, max_per, max_depth=6):
    """keys_to_idx: lista de (clave, idx). Devuelve {prefijo: [(clave, idx)…]} (partición adaptativa por prefijo)."""
    out = {}

    def pad(k, d):
        return (k + "_" * d)[:d]

    def rec(items, depth):
        groups = {}
        for k, i in items:
            groups.setdefault(pad(k, depth), []).append((k, i))
        for pre, members in groups.items():
            if len(members) > max_per and depth < max_depth and not pre.endswith("_"):
                rec(members, depth + 1)
            else:
                out[pre] = members
    rec(keys_to_idx, 1)
    return out


def write_find(w, fam_id, fam, persons, where, dmeta, generated):
    """Escribe <familia>/find/…; devuelve el bloque `find` del índice de la familia."""
    base = fam_id + "/find/"
    rows = [row_of(p, where) for p in persons]
    sortk = lambda i: (fold(persons[i].get("name")), persons[i]["id"])

    # 1) Por nombre: una entrada por cada token del nombre (nombre de pila o apellido, en cualquier orden).
    pairs = []
    for i, p in enumerate(persons):
        for t in name_tokens(p.get("name")):
            pairs.append((t, i))
    buckets = _assign(pairs, NAME_PER_FILE)
    name_prefixes = {}
    for pre, items in sorted(buckets.items()):
        items = sorted(set(items), key=lambda x: (x[0], sortk(x[1])))
        w.json(base + "name/%s.json" % pre,
               {"meta": dmeta, "prefix": pre, "columns": ["token"] + ROW_COLUMNS,
                "rows": [[t] + rows[i] for t, i in items]}, ("rows",))
        name_prefixes[pre] = len(items)
    name_cols = ["token"] + ROW_COLUMNS
    # 2) Por lugar.
    cities = {}
    for i, p in enumerate(persons):
        for cc, label in city_entries(p):
            d = cities.setdefault((cc, slugify(label)), {"labels": {}, "idx": []})
            d["labels"][label] = d["labels"].get(label, 0) + 1
            d["idx"].append(i)
    cindex, alias = [], {}
    for (cc, slug), d in sorted(cities.items()):
        label = sorted(d["labels"].items(), key=lambda x: (-x[1], x[0]))[0][0]
        idx = sorted(set(d["idx"]), key=sortk)
        pages = max(1, (len(idx) + PAGE_ROWS - 1) // PAGE_ROWS)
        for pg in range(pages):
            name = slug if pg == 0 else "%s~%d" % (slug, pg + 1)
            w.json(base + "city/%s/%s.json" % (cc, name),
                   {"meta": dmeta, "country": cc.upper(), "slug": slug, "label": label, "count": len(idx),
                    "page": pg + 1, "pages": pages, "columns": ROW_COLUMNS,
                    "rows": [rows[i] for i in idx[pg * PAGE_ROWS:(pg + 1) * PAGE_ROWS]]}, ("rows",))
        key = fold(label).replace(" ", "")
        cindex.append([key, cc.upper(), slug, label, len(idx), pages])
    known = {r[0] for r in cindex}
    aliases = [[a, t] for a, t in sorted(EXONYMS.items()) if t in known and a not in known]
    w.json(base + "city/index.json",
           {"meta": dmeta,
            "rule": ("key = nombre del lugar normalizado: fold() (minúsculas, ß→ss, sin acentos, ä/ae→a, ö/oe→o, ü/ue→u) "
                     "y sin espacios ni guiones. Busca la clave en rows; si hay varias filas (mismo nombre en otro país) "
                     "usa country. Archivo: city/<country en minúsculas>/<slug>.json; páginas extra <slug>~2.json. "
                     "aliases = nombres alternativos conocidos (exónimos) → key."),
            "columns": ["key", "country", "slug", "label", "count", "pages"], "rows": cindex, "aliases": aliases},
           ("rows",))
    # 3) Por año de nacimiento / de muerte.
    years = {"birth": {}, "death": {}}
    for i, p in enumerate(persons):
        for kind, f in (("birth", "birth_date"), ("death", "death_date")):
            y = date_year(p.get(f))
            if y and YEAR_MIN <= y <= YEAR_MAX:
                years[kind].setdefault(y, []).append(i)
    year_counts = {}
    for kind in ("birth", "death"):
        year_counts[kind] = {}
        for y, idx in sorted(years[kind].items()):
            idx = sorted(idx, key=sortk)
            pages = max(1, (len(idx) + PAGE_ROWS - 1) // PAGE_ROWS)
            for pg in range(pages):
                name = str(y) if pg == 0 else "%d~%d" % (y, pg + 1)
                w.json(base + "year/%s/%s.json" % (kind, name),
                       {"meta": dmeta, "kind": kind, "year": y, "count": len(idx), "page": pg + 1, "pages": pages,
                        "columns": ROW_COLUMNS, "rows": [rows[i] for i in idx[pg * PAGE_ROWS:(pg + 1) * PAGE_ROWS]]},
                       ("rows",))
            year_counts[kind][str(y)] = len(idx)
    fidx = {
        "meta": dmeta,
        "name": {"prefixes": name_prefixes, "columns": name_cols,
                 "rule": ("1) Normaliza cada palabra del nombre buscado con fold(): minúsculas, ß→ss, quitar acentos, "
                          "ä→a, ö→o, ü→u, 'ae/oe/ue'→a/o/u, solo a-z0-9. 2) Elige UNA palabra (mejor el apellido). "
                          "3) Prueba clave[:6], clave[:5], … clave[:1] (rellena con '_' hasta esa longitud) y usa el primer prefijo "
                          "que exista en `prefixes`. 4) Abre name/<prefijo>.json y filtra filas cuyo primer valor (token) "
                          "empiece por tu clave; luego compara el nombre completo y el año. Cada persona aparece una vez "
                          "por cada palabra de su nombre."),
                 "path": "name/{prefix}.json"},
        "city": {"index": "city/index.json", "path": "city/{country}/{slug}.json"},
        "year": {"birth": year_counts["birth"], "death": year_counts["death"], "range": [YEAR_MIN, YEAR_MAX],
                 "range_note": "Solo años entre %d y %d; fechas fuera de ese rango (erratas de la fuente) no se listan por año, pero siguen en la ficha." % (YEAR_MIN, YEAR_MAX),
                 "path": "year/{birth|death}/{year}.json",
                 "paging": "Máximo %d filas por archivo: si count > %d hay páginas extra {year}~2.json, {year}~3.json… (campo pages)." % (PAGE_ROWS, PAGE_ROWS)},
        "row": {"columns": ROW_COLUMNS,
                "record": "<familia>/people/by-surname/{people_prefix}.json → people[] con id == fila.id (sources[], links[], inscription)",
                "human_link": SITE_BASE + ("#s={memorials[0].memorial_id}" if fam_id == "odbl" else "#p={id}"),
                "note": "place = lugar del memorial o de muerte, nunca el de nacimiento. Una fila no es una ficha: cita la ficha y su fuente."},
        "count_people": len(persons),
    }
    w.json(base + "index.json", fidx)
    # Ejemplo determinista (para OpenAPI y la documentación): primer prefijo con ≥20 filas, la ciudad más grande
    # y el año de nacimiento más frecuente.
    ex = {}
    for pre, n in sorted(name_prefixes.items()):
        if n >= 20:
            ex["name"] = {"prefix": pre, "row": json_row(w, base + "name/%s.json" % pre)}
            break
    if cindex:
        big = sorted(cindex, key=lambda r: (-r[4], r[0]))[0]
        ex["city"] = {"key": big[0], "country": big[1].lower(), "slug": big[2], "label": big[3], "count": big[4]}
    if year_counts["birth"]:
        y = sorted(year_counts["birth"].items(), key=lambda kv: (-kv[1], kv[0]))[0]
        ex["year"] = {"kind": "birth", "year": int(y[0]), "count": y[1]}
    return {"index": base + "index.json", "name_prefixes": len(name_prefixes), "cities": len(cindex),
            "birth_years": len(years["birth"]), "death_years": len(years["death"]), "example": ex}


def json_row(w, rel):
    """Primera fila de un archivo ya escrito (solo para el ejemplo del OpenAPI)."""
    import json
    import os
    with open(os.path.join(w.root, rel), encoding="utf-8") as f:
        return json.load(f)["rows"][0]
