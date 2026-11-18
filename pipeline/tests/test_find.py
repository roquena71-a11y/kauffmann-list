"""Puerta para IA: búsqueda estática (find/), OpenAPI 3.1, llms.txt, robots.txt y enlaces de index.html."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from pipeline import agents
from pipeline.build import Writer
from pipeline.find import ROW_COLUMNS, name_tokens, place_of, write_find
from pipeline.util import REPO_ROOT, fold, load_json

from .test_pipeline import BuildCase, run_build
from .helpers import people


def band(root):
    """Todos los JSON bajo root → {ruta relativa: objeto}."""
    out = {}
    for dp, _, fns in os.walk(root):
        for fn in fns:
            if fn.endswith(".json"):
                out[os.path.relpath(os.path.join(dp, fn), root)] = load_json(os.path.join(dp, fn))
    return out


class TestNameTokens(unittest.TestCase):
    def test_tokens(self):
        self.assertEqual(name_tokens("Dr. Max von Mustermann"), ["max", "mustermann"])
        self.assertEqual(name_tokens("Käthe Müller-Großmann"), ["kathe", "muller", "grossmann"])
        self.assertEqual(name_tokens("Anna (geb. Meyer) Levi"), ["anna", "levi"])
        self.assertEqual(name_tokens(None), [])
        self.assertEqual(name_tokens("Max Max"), ["max"])

    def test_fold_js_equals_python(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("sin node")
        text = agents.llms_full_txt({"odbl": {"count_people": 1}}, {"odbl": {"license": "ODbL-1.0", "description": "x"}},
                                    "2026-01-01")
        js = re.search(r"```javascript\n(.*?)\n```", text, re.S).group(1)
        names = ["Müller", "Großmann", "Bär", "Maier", "Łukasz Żółć", "Œuvre", "Søren", "Dvořák", "O'Brien-Smith", "Mueller", "Schönberg", "Ærø"]
        prog = js + "\nconsole.log(JSON.stringify(%s.map(fold)));" % json.dumps(names, ensure_ascii=False)
        res = subprocess.run([node, "-e", prog], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(res.stdout), [fold(n) for n in names])
        py = re.search(r"```python\n(.*?)\n```", text, re.S).group(1)
        ns = {}
        exec(py, ns)
        self.assertEqual([ns["fold"](n) for n in names], [fold(n) for n in names])


def person(pid, name, birth=None, death=None, memorials=None, places=None):
    return {"id": pid, "name": name, "birth_date": birth, "death_date": death, "memorials": memorials or [],
            "places": places or [], "sources": [{"source_id": "x", "url": "https://example.org/" + pid}]}


class TestWriteFind(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="kl-find-")
        ps = [
            person("wd-Q1", "Anna Müller", "1890-01-02", "1943", [{"locality": "Köln", "country": "DE"}]),
            person("wd-Q2", "Dr. Max von Mustermann", "1880", None, [], [
                {"role": "birth", "label": "Geburtsdorf", "locality": "Geburtsdorf", "country": "DE"},
                {"role": "death", "label": "Theresienstadt", "locality": "Terezín", "country": "CZ"}]),
            person("st-n3", "Sinti Rose", "1920", "1944", [{"locality": "Berlin", "country": "DE"}]),
        ]
        where = {"wd-Q1": "mul", "wd-Q2": "mus", "st-n3": "ros"}
        w = Writer(os.path.join(self.tmp, "api"))
        dmeta = {"license": "CC0-1.0", "attribution": ["x"], "source_url": "u", "generated": "2026-11-18"}
        fam = {"license": "CC0-1.0"}
        self.info = write_find(w, "cc0", fam, ps, where, dmeta, "2026-11-18")
        self.api = band(os.path.join(self.tmp, "api"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_name_rows_and_prefix_rule(self):
        idx = self.api["cc0/find/index.json"]
        self.assertEqual(idx["count_people"], 3)
        key = fold("Müller")                                  # → muller
        pre = next(p for n in (6, 5, 4, 3, 2, 1) for p in [(key + "______")[:n]] if p in idx["name"]["prefixes"])
        f = self.api["cc0/find/name/%s.json" % pre]
        self.assertEqual(f["columns"], ["token"] + ROW_COLUMNS)
        rows = [r for r in f["rows"] if r[0].startswith(key)]
        self.assertEqual([r[1] for r in rows], ["wd-Q1"])
        self.assertEqual(rows[0][2:], ["Anna Müller", 1890, 1943, "Köln", "mul"])

    def test_birth_place_never_indexed(self):
        blob = json.dumps(self.api, ensure_ascii=False)
        self.assertNotIn("Geburtsdorf", blob)
        self.assertEqual(place_of(person("x", "Y", places=[{"role": "birth", "label": "Z", "locality": "Z"}]))[0], None)
        cidx = self.api["cc0/find/city/index.json"]
        self.assertEqual(sorted(r[0] for r in cidx["rows"]), ["berlin", "koln", "terezin"])
        self.assertEqual(self.api["cc0/find/city/cz/terezin.json"]["rows"][0][0], "wd-Q2")

    def test_year_files_and_meta(self):
        self.assertEqual([r[0] for r in self.api["cc0/find/year/birth/1890.json"]["rows"]], ["wd-Q1"])
        self.assertEqual([r[0] for r in self.api["cc0/find/year/death/1944.json"]["rows"]], ["st-n3"])
        self.assertNotIn("cc0/find/year/death/1880.json", self.api)
        self.assertIn("cc0/find/index.json", self.api)         # también el manifiesto lleva licencia y atribución
        for rel, d in self.api.items():
            self.assertEqual(d["meta"]["license"], "CC0-1.0", rel)
            self.assertTrue(d["meta"]["attribution"] and d["meta"]["generated"], rel)

    def test_aliases_only_when_city_exists(self):
        al = dict(self.api["cc0/find/city/index.json"]["aliases"])
        self.assertEqual(al.get("cologne"), "koln")
        self.assertNotIn("munich", al)


class TestPaging(unittest.TestCase):
    def test_year_and_city_pages(self):
        from pipeline import find
        tmp = tempfile.mkdtemp(prefix="kl-find-pg-")
        old = find.PAGE_ROWS
        find.PAGE_ROWS = 2
        try:
            ps = [person("wd-Q%d" % i, "Person Nr%d" % i, "1900", "1942", [{"locality": "Ulm", "country": "DE"}]) for i in range(5)]
            dmeta = {"license": "CC0-1.0", "attribution": ["x"], "source_url": "u", "generated": "2026-11-18"}
            w = Writer(os.path.join(tmp, "api"))
            write_find(w, "cc0", {"license": "CC0-1.0"}, ps, {p["id"]: "per" for p in ps}, dmeta, "2026-11-18")
            api = band(os.path.join(tmp, "api"))
            ids = []
            for n in ("1942", "1942~2", "1942~3"):
                f = api["cc0/find/year/death/%s.json" % n]
                self.assertEqual((f["count"], f["pages"]), (5, 3))
                ids += [r[0] for r in f["rows"]]
            self.assertEqual(sorted(ids), sorted(p["id"] for p in ps))
            self.assertNotIn("cc0/find/year/death/1942~4.json", api)
            self.assertEqual(api["cc0/find/city/de/ulm~3.json"]["page"], 3)
            self.assertEqual(api["cc0/find/index.json"]["year"]["death"], {"1942": 5})
        finally:
            find.PAGE_ROWS = old
            shutil.rmtree(tmp, ignore_errors=True)


class TestFindInBuild(BuildCase):
    def test_find_follows_policies_and_links(self):
        tmp, sources = self.env(partner=False)
        out, _ = run_build(sources, tmp)
        ps = people(out)
        api = band(os.path.join(out, "odbl", "find"))
        blob = json.dumps(api, ensure_ascii=False)
        self.assertNotIn("Kurt Lebend", blob)                  # posible vivo: fuera de find/ como de la API
        ids_in_find = set()
        for rel, d in api.items():
            if rel.startswith("name" + os.sep):
                for r in d["rows"]:
                    ids_in_find.add(r[1])
                    self.assertIn(r[1], ps)                      # cada fila apunta a una ficha publicada
                    pre = r[-1]
                    pack = load_json(os.path.join(out, "odbl", "people", "by-surname", pre + ".json"))
                    self.assertIn(r[1], [p["id"] for p in pack["people"]])   # y people_prefix es correcto
        self.assertEqual(ids_in_find, set(ps))                  # nadie falta y nadie sobra
        idx = load_json(os.path.join(out, "odbl", "index.json"))
        self.assertIn("find_name", idx["endpoints"])
        self.assertEqual(idx["find"]["cities"], len(api["city/index.json"]["rows"]))

    def test_agent_docs(self):
        tmp, sources = self.env(partner=False)
        out, _ = run_build(sources, tmp)
        oa = load_json(os.path.join(out, "openapi.json"))
        self.assertEqual(oa["openapi"], "3.1.0")
        for path in ("/odbl/find/index.json", "/odbl/find/name/{prefix}.json", "/odbl/find/city/index.json",
                     "/odbl/find/city/{country}/{slug}.json", "/odbl/find/year/{kind}/{year}.json"):
            self.assertIn(path, oa["paths"])
        blob = json.dumps(oa)
        for ref in set(re.findall(r'"\$ref": "#/components/schemas/(\w+)"', blob)):
            self.assertIn(ref, oa["components"]["schemas"], ref)
        ids = [op["operationId"] for pi in oa["paths"].values() for op in pi.values()]
        self.assertEqual(len(ids), len(set(ids)))              # operationId únicos
        try:
            from openapi_spec_validator import validate
            validate(oa)
        except ImportError:
            pass
        def rd(rel):
            with open(os.path.join(tmp, rel), encoding="utf-8") as f:
                return f.read()
        llms, full = rd("llms.txt"), rd("llms-full.txt")
        for needle in ("openapi.json", "llms-full.txt", "find/index.json", "Nunca olvidar", "Never invent", "#s=", "#p=", "ODbL"):
            self.assertIn(needle, llms, needle)
        for needle in ("fold(", "people_prefix", "sources[]", "CC0", "ODbL", "Nunca olvidar", "no consta"):
            self.assertIn(needle, full, needle)
        link = load_json(os.path.join(tmp, ".well-known", "api-catalog"))["linkset"][0]
        self.assertTrue(any(h["href"].endswith("llms-full.txt") for h in link["service-doc"]))


class TestStaticSiteFiles(unittest.TestCase):
    def read(self, rel):
        with open(os.path.join(REPO_ROOT, rel), encoding="utf-8") as f:
            return f.read()

    def test_robots(self):
        r = self.read("robots.txt")
        for bot in ("GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended", "CCBot", "OAI-SearchBot"):
            self.assertRegex(r, r"User-agent: %s\nAllow: /\n" % re.escape(bot))
        self.assertIn("Sitemap: https://roquena71-a11y.github.io/kauffmann-list/sitemap.xml", r)
        self.assertNotRegex(r, r"(?im)^\s*Disallow:\s*/\s*$")

    def test_index_html_links_and_jsonld(self):
        h = self.read("index.html")
        for rel in ('rel="service-desc"', 'rel="api-catalog"', 'href="llms.txt"', 'href="api/v1/openapi.json"'):
            self.assertIn(rel, h)
        m = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)
        ld = json.loads(m.group(1))
        self.assertEqual(ld, load_json(os.path.join(REPO_ROOT, "kauffmann-list.jsonld")))
        types = [n["@type"] for n in ld["@graph"]]
        self.assertIn("WebAPI", types)
        self.assertNotIn("../exports", h)
        ns = re.search(r"<noscript><style>(.*?)</style></noscript>", h, re.S)       # sin JS no hay intro que tape el texto
        self.assertTrue(ns and ".intro" in ns.group(1) and "display:none" in ns.group(1))
        self.assertIn('<section class="noscript"', h)

    def test_sitemap_wellformed(self):
        import xml.etree.ElementTree as ET
        t = ET.fromstring(self.read("sitemap.xml"))
        locs = [e.text for e in t.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertIn("https://roquena71-a11y.github.io/kauffmann-list/llms.txt", locs)
        self.assertEqual(len(locs), len(set(locs)))


if __name__ == "__main__":
    unittest.main()


class TestDoorCheckDetectsAlterations(BuildCase):
    """F1/F3: tests/ai-door-check.py tiene que detectar un nombre, un año o una licencia alterados en find/,
    y una fila de nombre con 6 columnas (el esquema del OpenAPI tiene 7: token primero)."""

    CHECK = os.path.join(REPO_ROOT, "tests", "ai-door-check.py")

    def run_check(self, root):
        env = dict(os.environ, REQUIRE_OAV="")
        res = subprocess.run([sys.executable, self.CHECK, root, "--solo-find"], capture_output=True, text=True, env=env)
        return res.returncode, res.stdout

    def mutate(self, root, rel, fn):
        path = os.path.join(root, "api", "v1", rel)
        d = load_json(path)
        fn(d)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)

    @staticmethod
    def drop_row(d):
        d["rows"].pop()
        d["count"] = len(d["rows"])

    def first(self, root, sub):
        base = os.path.join(root, "api", "v1", "odbl", "find", sub)
        return sub + "/" + sorted(f for f in os.listdir(base) if f != "index.json" and f.endswith(".json"))[0]

    def setUp(self):
        super().setUp()
        self.tmp, sources = self.env(partner=False)
        run_build(sources, self.tmp)

    def mutated_copy(self):
        dst = tempfile.mkdtemp(prefix="kl-mut-")
        self.tmps.append(dst)
        shutil.copytree(self.tmp, dst, dirs_exist_ok=True)
        return dst

    def test_baseline_is_clean(self):
        code, out = self.run_check(self.tmp)
        self.assertEqual(code, 0, out)

    def test_altered_name_year_license(self):
        cases = {
            "nombre": ("odbl/find/" + self.first(self.tmp, "name"), lambda d: d["rows"][0].__setitem__(2, "Nombre Falso"), "fila alterada"),
            "año": ("odbl/find/" + self.first(self.tmp, "year/death"), lambda d: d["rows"][0].__setitem__(3, 1111), "fila alterada"),
            "licencia en un archivo": ("odbl/find/" + self.first(self.tmp, "name"), lambda d: d["meta"].__setitem__("license", "CC0-1.0"), "meta.license"),
            "licencia en find/index.json": ("odbl/find/index.json", lambda d: d["meta"].__setitem__("license", "CC0-1.0"), "meta.license"),
            "atribución": ("odbl/find/index.json", lambda d: d["meta"].__setitem__("attribution", ["otra"]), "meta.attribution"),
            "fila borrada en year": ("odbl/find/" + self.first(self.tmp, "year/death"), self.drop_row, "faltan 1 filas"),
            "fila borrada en city": ("odbl/find/" + self.first(self.tmp, "city/de"), self.drop_row, "faltan 1 filas"),
            "fila con 6 columnas": ("odbl/find/" + self.first(self.tmp, "name"), lambda d: d["rows"][0].pop(0), "esquema"),
        }
        for label, (rel, fn, needle) in cases.items():
            root = self.mutated_copy()
            self.mutate(root, rel, fn)
            code, out = self.run_check(root)
            self.assertEqual(code, 1, "%s: no detectado\n%s" % (label, out))
            self.assertIn(needle, out, "%s: %s" % (label, out))
