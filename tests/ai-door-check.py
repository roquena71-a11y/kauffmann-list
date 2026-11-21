"""Comprobaciones sobre el sitio ya generado (tras `python3 -m pipeline build`): enlaces, OpenAPI, find/, tamaños.

Uso: python3 tests/ai-door-check.py [raíz]    (no publica nada; solo lee archivos locales)
"""
import json
import os
import random
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from pipeline.find import name_tokens  # noqa: E402

BASE = "https://roquena71-a11y.github.io/kauffmann-list/"
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
SOLO_FIND = "--solo-find" in sys.argv          # para los tests unitarios: solo OpenAPI y find/ (sin index.html, robots, sitemap)
ROOT = os.path.abspath(ARGS[0] if ARGS else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
errors, notes = [], []


def err(m):
    errors.append(m)


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def text(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def local(url):
    u = url.split("#")[0].split("?")[0]
    rel = u[len(BASE):]
    return os.path.join(ROOT, rel) if rel else os.path.join(ROOT, "index.html")


# 1) enlaces propios en las superficies para agentes
surfaces = {} if SOLO_FIND else {f: text(f) for f in ("llms.txt", "llms-full.txt", "robots.txt", "sitemap.xml", "index.html", ".well-known/api-catalog",
                                 "api/v1/index.json", "kauffmann-list.jsonld")}
n_links = 0
for name, t in surfaces.items():
    for m in re.finditer(r"https://roquena71-a11y\.github\.io/kauffmann-list/[^\s)\"'`<>\]|]*", t):
        url = m.group(0).rstrip(".,;")
        nxt = t[m.end():m.end() + 1]
        if any(c in url for c in "{}<>$*") or nxt in "<{" or url.endswith("/api/v1/") or "{" in url or url.endswith("/find/name/"):
            continue
        n_links += 1
        p = local(url)
        if url.endswith("/"):
            p = os.path.join(p, "index.html") if os.path.isdir(p) else p
        if not os.path.exists(p):
            err("%s: enlace roto %s" % (name, url))
# enlaces relativos de index.html (rel=…)
for m in re.finditer(r'<link rel="(?:alternate|service-desc|service-doc|describedby|api-catalog)"[^>]*href="([^"]+)"', surfaces.get("index.html", "")):
    if not os.path.exists(os.path.join(ROOT, m.group(1))):
        err("index.html: <link> roto %s" % m.group(1))
notes.append("%d enlaces propios comprobados" % n_links)

# 2) OpenAPI
oa = load("api/v1/openapi.json")
if oa.get("openapi") != "3.1.0":
    err("openapi no es 3.1.0")
try:
    from openapi_spec_validator import validate
    validate(oa)
    notes.append("openapi-spec-validator: válido")
except ImportError:
    if os.environ.get("REQUIRE_OAV"):
        err("openapi-spec-validator no instalado y REQUIRE_OAV está activo")
    notes.append("openapi-spec-validator no instalado (solo comprobación estructural)")
except Exception as e:  # noqa
    err("OpenAPI inválido: %s" % str(e)[:300])
checked = 0
for path, item in oa["paths"].items():
    params = item["get"].get("parameters") or []
    combos = [{}]
    for prm in params:
        if prm["name"] == "kind":
            prm = dict(prm, schema={"type": "string", "enum": [prm.get("example") or "birth"]})
        sch = prm["schema"]
        vals = sch.get("enum") or ([prm["example"]] if prm.get("example") is not None else [])
        if not vals:
            combos = []
            break
        vals = vals[:3]
        combos = [dict(c, **{prm["name"]: v}) for c in combos for v in vals]
    for c in combos:
        rel = "api/v1" + path
        for k, v in c.items():
            rel = rel.replace("{%s}" % k, str(v))
        if "{" in rel:
            continue
        checked += 1
        if not os.path.exists(os.path.join(ROOT, rel)):
            err("OpenAPI %s: ejemplo %s no existe" % (path, rel))
notes.append("%d rutas de ejemplo del OpenAPI existen" % checked)

# 3) find/: coherencia con las fichas y tamaños
sizes = {}


def year_of(v):
    return int(str(v)[:4]) if v and re.match(r"^\d{4}", str(v)) else None


def place_of(p):
    """Reimplementación independiente: lugar del memorial; si no, lugar de muerte. Nunca nacimiento."""
    for m in p.get("memorials") or []:
        if m.get("locality"):
            return m["locality"]
    for pl in p.get("places") or []:
        if pl.get("role") == "death" and (pl.get("locality") or pl.get("label")):
            return pl.get("locality") or pl["label"]
    return None


def city_keys(p):
    ks = set()
    for m in p.get("memorials") or []:
        if m.get("locality") and m.get("country"):
            ks.add((m["country"].lower(), norm(m["locality"])))
    for pl in p.get("places") or []:
        if pl.get("role") == "death" and pl.get("country") and (pl.get("locality") or pl.get("label")):
            ks.add((pl["country"].lower(), norm(pl.get("locality") or pl["label"])))
    return ks


def norm(label):
    return re.sub(r"[^a-z0-9]", "", name_fold(label))


from pipeline.util import fold as name_fold  # noqa: E402
from pipeline.jsonschema_lite import Validator  # noqa: E402

# Validador de los esquemas del propio OpenAPI (Person, externo, se valida aparte en el build)
oa_local = json.loads(json.dumps(oa))
oa_local["components"]["schemas"]["Person"] = {}
schema_validator = Validator(oa_local)
find_routes = []
for path, item in oa["paths"].items():
    if "/find/" not in path:
        continue
    sch = item["get"]["responses"]["200"]["content"]["application/json"]
    rx = "^" + re.sub(r"\\\{[a-z|]+\\\}", "[^/]+", re.escape(path.lstrip("/"))) + "$"
    find_routes.append((re.compile(rx), sch["schema"], path, sch.get("example")))
# los ejemplos del OpenAPI cumplen su propio esquema
for rx, sch, path, example in find_routes:
    if example is not None:
        for e in schema_validator.errors(example, sch)[:3]:
            err("OpenAPI %s: el ejemplo no cumple su esquema: %s" % (path, e))
n_schema_files = n_rows = 0

for fam in sorted(os.listdir(os.path.join(ROOT, "api/v1"))):
    fdir = os.path.join(ROOT, "api/v1", fam)
    if not os.path.isdir(os.path.join(fdir, "find")):
        continue
    fam_idx = load("api/v1/%s/index.json" % fam)
    fam_meta = fam_idx["meta"]
    facts, nameless = {}, set()
    people_dir = os.path.join(fdir, "people", "by-surname")
    for fn in (os.listdir(people_dir) if os.path.isdir(people_dir) else []):
        with open(os.path.join(fdir, "people", "by-surname", fn), encoding="utf-8") as f:
            pk = json.load(f)
        for p in pk["people"]:
            facts[p["id"]] = (p.get("name"), year_of(p.get("birth_date")), year_of(p.get("death_date")), place_of(p), fn[:-5], city_keys(p))
            if not name_tokens(p.get("name")):
                nameless.add(p["id"])          # memorial anónimo: no se busca por nombre (sí por lugar/año si los tiene)
    people_ids = set(facts)
    bad = {"meta": 0, "schema": 0, "row": 0}
    shown = [0]

    def fail(kind, msg):
        bad[kind] += 1
        if shown[0] < 12:
            shown[0] += 1
            err(msg)

    def check_row(rel, r, off=0):
        """Una fila de find contra la ficha publicada: nombre, años, lugar y people_prefix tienen que ser idénticos."""
        pid = r[off]
        f = facts.get(pid)
        if f is None:
            fail("row", "%s: id %s no está publicado" % (rel, pid))
            return None
        if tuple(r[off + 1:off + 6]) != f[:5]:
            fail("row", "%s: fila alterada %s ≠ ficha %s" % (rel, r[off:off + 6], (pid,) + f[:5]))
        return f

    in_name = set()
    got_year, got_city = {}, {}          # lo que contienen los archivos year/city, para detectar filas borradas
    n_files = 0
    for dp, _, fns in os.walk(os.path.join(fdir, "find")):
        for fn in fns:
            path = os.path.join(dp, fn)
            rel = os.path.relpath(path, os.path.join(ROOT, "api/v1")).replace(os.sep, "/")
            with open(path, encoding="utf-8") as fh:
                d = json.load(fh)
            n_files += 1
            # licencia/atribución/fuente/fecha idénticas a las de la familia, también en find/index.json
            m = d.get("meta") or {}
            for k in ("family", "license", "license_url", "attribution", "source_url", "generated"):
                if m.get(k) != fam_meta.get(k):
                    fail("meta", "%s: meta.%s = %r ≠ familia %r" % (rel, k, m.get(k), fam_meta.get(k)))
            # el archivo cumple el esquema que publica el OpenAPI
            hit = [r for r in find_routes if r[0].match(rel)]
            if len(hit) != 1:
                fail("schema", "%s: el OpenAPI no describe este archivo (rutas: %d)" % (rel, len(hit)))
            else:
                n_schema_files += 1
                for e in schema_validator.errors(d, hit[0][1])[:2]:
                    fail("schema", "%s: no cumple el esquema %s: %s" % (rel, hit[0][2], e))
            parts = rel.split("/")
            if parts[2] == "name":
                for r in d["rows"]:
                    n_rows += 1
                    f = check_row(rel, r, 1)
                    in_name.add(r[1])
                    if f is not None:
                        if r[-1] != f[4]:
                            fail("row", "%s: people_prefix equivocado en %s" % (rel, r[1]))
                        if r[0] not in name_tokens(f[0]):
                            fail("row", "%s: token %r no está en el nombre %r" % (rel, r[0], f[0]))
                        if not r[0].startswith(d["prefix"].rstrip("_")):
                            fail("row", "%s: token %r fuera del prefijo %s" % (rel, r[0], d["prefix"]))
            elif parts[2] == "year":
                for r in d["rows"]:
                    n_rows += 1
                    f = check_row(rel, r)
                    got_year.setdefault((d["kind"], d["year"]), []).append(r[0])
                    if f is not None and f[1 if d["kind"] == "birth" else 2] != d["year"]:
                        fail("row", "%s: %s tiene otro año de %s" % (rel, r[0], d["kind"]))
            elif parts[2] == "city" and fn != "index.json":
                for r in d["rows"]:
                    n_rows += 1
                    f = check_row(rel, r)
                    got_city.setdefault((d["country"].lower(), norm(d["label"])), []).append(r[0])
                    if f is not None and (d["country"].lower(), norm(d["label"])) not in f[5]:
                        fail("row", "%s: %s no tiene memorial ni muerte en %s" % (rel, r[0], d["label"]))
    # nadie falta ni sobra en year/city: el conjunto de cada archivo es exactamente el de las fichas
    exp_year, exp_city = {}, {}
    for pid, f in facts.items():
        for kind, y in (("birth", f[1]), ("death", f[2])):
            if y is not None and 1700 <= y <= 2100:      # rango publicado en find/index.json → year.range
                exp_year.setdefault((kind, y), set()).add(pid)
        for k in f[5]:
            exp_city.setdefault(k, set()).add(pid)
    for label, got, exp in (("year", got_year, exp_year), ("city", got_city, exp_city)):
        for k in sorted(set(got) | set(exp), key=str):
            g, e = got.get(k, []), exp.get(k, set())
            if len(g) != len(set(g)):
                fail("row", "find/%s %s: filas repetidas" % (label, k))
            if set(g) != e:
                fail("row", "find/%s %s: faltan %d filas y sobran %d respecto a las fichas" % (label, k, len(e - set(g)), len(set(g) - e)))
    if in_name != people_ids - nameless:
        err("%s: find/name no coincide con las fichas (faltan %d, sobran %d)" % (fam, len((people_ids - nameless) - in_name), len(in_name - people_ids)))
    total = 0
    biggest = (0, "")
    for dp, _, fns in os.walk(os.path.join(fdir, "find")):
        for fn in fns:
            sz = os.path.getsize(os.path.join(dp, fn))
            total += sz
            biggest = max(biggest, (sz, os.path.relpath(os.path.join(dp, fn), ROOT)))
    sizes[fam] = (len(people_ids), total, biggest)
    if biggest[0] > 1024 * 1024:
        err("%s: archivo find > 1 MB: %s" % (fam, biggest))
    notes.append("%s: %d personas (%d sin nombre, memoriales anónimos), %d archivos find, find/ %.1f MB, mayor archivo %.0f KB (%s); fallos meta/esquema/fila: %d/%d/%d" % (
        fam, len(people_ids), len(nameless), n_files, total / 1e6, biggest[0] / 1e3, biggest[1], bad["meta"], bad["schema"], bad["row"]))
notes.append("%d archivos find validados contra el esquema del OpenAPI; %d filas comparadas con la ficha" % (n_schema_files, n_rows))

# 4) los enlaces humanos #s= apuntan a placas que existen en data/stones.json
if os.path.exists(os.path.join(ROOT, "data", "stones.json")) and os.path.isdir(os.path.join(ROOT, "api/v1/odbl/people")):
    stones = json.load(open(os.path.join(ROOT, "data", "stones.json"), encoding="utf-8"))
    ids = {s["id"] for s in stones["stones"]}
    rnd = random.Random(7)
    d = os.path.join(ROOT, "api/v1/odbl/people/by-surname")
    miss = tot = 0
    for fn in rnd.sample(os.listdir(d), min(120, len(os.listdir(d)))):
        for p in json.load(open(os.path.join(d, fn), encoding="utf-8"))["people"]:
            mid = (p.get("memorials") or [{}])[0].get("memorial_id")
            tot += 1
            if not mid or mid not in ids:
                miss += 1
    if miss:
        err("odbl: %d de %d permalinks #s= no existen en data/stones.json" % (miss, tot))
    notes.append("odbl: %d permalinks #s= comprobados contra data/stones.json (%d sin placa)" % (tot, miss))

# 5) sitemap
if not SOLO_FIND:
    t = ET.fromstring(text("sitemap.xml"))
    for e in t.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        if not os.path.exists(local(e.text)) and not e.text.endswith("/"):
            err("sitemap: %s no existe" % e.text)

for n in notes:
    print("· " + n)
for e in errors[:50]:
    print("ERROR: " + e)
print("ai-door-check: %d errores" % len(errors))
sys.exit(1 if errors else 0)
