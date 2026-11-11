import io
import json
import os
import shutil
import unittest
from contextlib import redirect_stderr

from pipeline import build, inscription
from pipeline.adapters import generic_tabular, overpass, wikidata_sparql
from pipeline.config import ConfigError, load_sources, validate_source
from pipeline.adapters import ADAPTERS
from pipeline.jsonschema_lite import Validator
from pipeline.merge import merge_family, possible_duplicates
from pipeline.util import (PIPELINE_DIR, REPO_ROOT, fold, load_json, normalize_date, person_shard, slugify,
                           surname_key)
from pipeline.validate import validate

from .helpers import FIX, make_env, people, read_all

SCHEMA = load_json(os.path.join(PIPELINE_DIR, "schema", "person.schema.json"))


def run_build(sources, tmp, **kw):
    out = os.path.join(tmp, "api", "v1")
    with redirect_stderr(io.StringIO()):
        res = build.run(sources=sources, out=out, site_root=tmp, suppressed=kw.pop("suppressed", []),
                        reports_dir=os.path.join(tmp, "reports"),
                        source_ids=kw.pop("source_ids", None), **kw)
    return out, res


def rec(rid, source="s1", qid=None, name="Anna Muster", birth=None, gb=None, death=None, fate="unknown"):
    return {"id": "st-" + rid, "name": name, "birth_date": birth, "death_date": death, "fate": fate,
            "identifiers": {"wikidata": qid, "gedenkbuch": gb or []},
            "sources": [{"source_id": source, "record_id": rid, "license": "CC0-1.0", "attribution": "x"}],
            "memorials": [], "links": [], "places": [], "deportations": [], "_variants": {}}


class TestNormalization(unittest.TestCase):
    def test_surname_key(self):
        self.assertEqual(surname_key("Müller"), "muller")
        self.assertEqual(surname_key("Mueller"), "muller")
        self.assertEqual(surname_key("MÜLLER"), "muller")
        self.assertEqual(surname_key("Weiß"), "weiss")
        self.assertEqual(surname_key("von Ossietzky"), "ossietzky")
        self.assertEqual(surname_key("Łódź-Kowalski"), "lodzkowalski")
        self.assertEqual(surname_key("Ça"), "ca")
        self.assertEqual(surname_key(""), "")

    def test_fold_matches_frontend(self):
        self.assertEqual(fold("Ritterstraße 5"), "ritterstrasse 5")
        self.assertEqual(fold("Görlitzer"), "gorlitzer")

    def test_sort_surname_and_prefix(self):
        self.assertEqual(build.sort_surname({"name": "Dr. Werner Josef Walbaum"}), "walbaum")
        self.assertEqual(build.sort_surname({"name": "Max Siegfried 'Friedel' Schlösser"}), "schlosser")
        self.assertEqual(build.sort_surname({"name": "X", "family_name": "van Dijk"}), "dijk")
        pre = build.assign_prefixes(["schmidt"] * 5 + ["sander", "a", ""], max_per=4)
        self.assertIn("schmid", pre)                       # se divide hasta 6 letras si hace falta
        self.assertEqual(build.lookup_prefix("schmidt", pre), "schmid")
        self.assertEqual(build.lookup_prefix("sander", pre), "sa")
        self.assertEqual(build.lookup_prefix("", pre), "_")

    def test_dates_slug_shard(self):
        self.assertEqual(normalize_date("1910-00-00"), "1910")
        self.assertEqual(normalize_date("19.2.1943"), "1943-02-19")
        self.assertEqual(normalize_date("1942-05"), "1942-05")
        self.assertEqual(normalize_date("Jg. 1887"), "1887")
        self.assertEqual(normalize_date("15. Februar 2010"), "2010-02-15")
        self.assertIsNone(normalize_date("unbekannt"))
        self.assertEqual(slugify("Frankfurt am Main"), "frankfurt-am-main")
        self.assertEqual(slugify("Mühringen"), "muhringen")
        self.assertEqual(person_shard("st-n10010972992"), "92")
        self.assertEqual(person_shard("yv-A.b"), "_b")


class TestInscription(unittest.TestCase):
    def test_fate(self):
        self.assertEqual(inscription.fate_from_text("deportiert 1941 Riga ermordet 1942")[0], "murdered")
        self.assertEqual(inscription.fate_from_text("FLUCHT IN DEN TOD 1941")[0], "suicide")
        self.assertEqual(inscription.fate_from_text("Flucht 1938 England")[0], "fled")
        self.assertEqual(inscription.fate_from_text("Flucht 1939 überlebt")[0], "survived")
        self.assertEqual(inscription.fate_from_text("tot in Theresienstadt")[0], "died_in_persecution")
        self.assertEqual(inscription.fate_from_text("HIER WOHNTE X")[0], "unknown")

    def test_names_and_events(self):
        self.assertEqual(inscription.split_name("Amanda Wachtel geb. Brandt"), ("Amanda Wachtel", "Brandt"))
        self.assertEqual(inscription.birth_name_from("FANNY FELDSTEIN GEB. KATZENSTEIN JG. 1865"), "Katzenstein")
        ev = inscription.deportations_from("deportiert 1943 Theresienstadt 1944 Auschwitz", "s")
        self.assertEqual([(e["date"], e["place"]) for e in ev], [("1943", "Theresienstadt"), ("1944", "Auschwitz")])
        self.assertEqual(inscription.death_place_from("ERMORDET IN AUSCHWITZ"), "Auschwitz")
        self.assertTrue(inscription.has_survivor_marker("FLUCHT 1939 ENGLAND"))
        self.assertTrue(inscription.has_survivor_marker("entkam 1944"))
        self.assertFalse(inscription.has_survivor_marker("Flucht in den Tod"))


class TestSurvivalVsDeath(unittest.TestCase):
    """Auditoría 1: supervivencia como prefijo; 'Tod'/'Todesmarsch' no son muerte si hay marca de supervivencia."""

    def test_real_cases(self):
        f = inscription.fate_from_text
        # wd-Q132139110 (Jg. 1925)
        self.assertEqual(f("HIER WOHNTE FRED BACHNER JG. 1925 AUSGEWIESEN JUNI 1939 POLEN GHETTO CHRZANÓW 1943 "
                           "ZWANGSARBEIT GRADITZ 1944 AUSCHWITZ TODESMARSCH 1945 DACHAU BEFREIT")[0], "survived")
        # st-n13625639423/24/27/28
        self.assertEqual(f("Hier überlebte 1943-1945 Ursula Giessler, versteckt/gerettet vor Deportation und Tod "
                           "von Pater Heinrich Middendorf SCJ")[0], "survived")

    def test_prefixes_and_rules(self):
        f = inscription.fate_from_text
        self.assertEqual(f("ueberlebte Theresienstadt")[0], "survived")
        self.assertEqual(f("versteckt 1943-1945")[0], "survived")
        self.assertEqual(f("gerettet 1944")[0], "survived")
        self.assertEqual(f("Flucht 1938 England")[0], "fled")
        self.assertEqual(f("Flucht 1939 Frankreich tot 1942 Gurs")[0], "died_in_persecution")   # muerte con fecha
        self.assertEqual(f("befreit tot an den Folgen 11.10.1945")[0], "died_in_persecution")
        self.assertEqual(f("versteckt gelebt deportiert 1943 Auschwitz ermordet")[0], "murdered")  # asesinato explícito
        self.assertEqual(f("versuchte / Flucht in den Tod / überlebt")[0], "survived")          # intento ≠ suicidio
        self.assertEqual(f("FLUCHT IN DEN TOD 1941")[0], "suicide")
        self.assertEqual(f("tot in Theresienstadt")[0], "died_in_persecution")                  # sin marca de supervivencia
        for t in ("überlebte", "gerettet", "versteckt", "befreiten", "Fluchtweg", "entkam"):
            self.assertTrue(inscription.has_survivor_marker(t), t)
        self.assertFalse(inscription.has_survivor_marker("Flucht in den Tod"))


class TestGenericMapping(unittest.TestCase):
    def setUp(self):
        self.cfg = load_sources()["yadvashem"]

    def test_specs(self):
        row = {"A": " x ", "B": "y", "N": {"deep": "z"}, "L": "1; 2;3", "F": "Murdered"}
        R = generic_tabular.resolve
        self.assertEqual(R("A", row), "x")
        self.assertEqual(R("N.deep", row), "z")
        self.assertEqual(R({"concat": ["A", "B"], "sep": "-"}, row), "x-y")
        self.assertEqual(R({"template": "u/{B}/{A}"}, row), "u/y/ x ")
        self.assertIsNone(R({"template": "u/{missing}"}, row))
        self.assertEqual(R({"column": "L", "split": ";"}, row), ["1", "2", "3"])
        self.assertEqual(R({"column": "F", "map": {"murdered": "murdered"}, "default": "unknown"}, row), "murdered")
        self.assertEqual(R({"column": "F", "map": {"x": "y"}, "default": "unknown"}, row), "unknown")
        self.assertEqual(R({"first": ["missing", "B"]}, row), "y")
        self.assertEqual(R({"const": "DE"}, row), "DE")
        self.assertEqual(R({"column": "B", "template": "https://h/{value}"}, row), "https://h/y")

    def test_csv_rows(self):
        self.cfg["input"]["path"] = os.path.join(FIX, "partner_sample.csv")

        class Ctx:
            offline, limit, today = True, None, "2026-11-11"

            def note(self, *a, **k):
                pass
        recs = list(generic_tabular.fetch(self.cfg, Ctx()))
        self.assertEqual(len(recs), 2)  # la fila sin id se descarta
        r = recs[0]
        self.assertEqual(r["id"], "yv-YV-1")
        self.assertEqual(r["name"], "Martha Schwarz")
        self.assertEqual(r["birth_date"], "1897")
        self.assertEqual(r["fate"], "murdered")
        self.assertEqual(r["identifiers"], {"wikidata": "Q900000010", "yad_vashem": ["YV-1"]})
        self.assertEqual(r["deportations"][0]["place"], "Riga")
        self.assertEqual(r["deportations"][0]["from"], "Stuttgart")
        self.assertEqual({p["role"] for p in r["places"]}, {"residence", "birth", "death"})
        self.assertEqual([p["country"] for p in r["places"] if p["role"] == "residence"], ["DE"])
        self.assertEqual(r["sources"][0]["license"], "LicenseRef-permiso-pendiente")
        self.assertTrue(r["links"][0]["url"].startswith("https://collections.yadvashem.org/en/names/YV-1"))
        self.assertEqual(recs[1]["birth_date"], "1901-03-12")
        self.assertEqual(recs[1]["birth_name"], "Muster")

    def test_config_rules(self):
        bad = dict(self.cfg, license_family="odbl")
        self.assertTrue(any("partners/yadvashem" in e for e in validate_source(bad, ADAPTERS)))
        bad = dict(self.cfg)
        del bad["license"]
        self.assertTrue(validate_source(bad, ADAPTERS))
        self.assertEqual(validate_source(self.cfg, ADAPTERS), [])


class TestMerge(unittest.TestCase):
    def test_merge_by_qid_keeps_provenance(self):
        a = rec("a", "s1", qid="Q1", birth="1897")
        b = rec("b", "s2", qid="Q1", birth="1897-04-03", death="1942", fate="murdered")
        b["name"] = "Anna M."
        report = {}
        ps = merge_family([a, b], {"s1": 1, "s2": 2}, report)
        self.assertEqual(len(ps), 1)
        p = ps[0]
        self.assertEqual(p["id"], "wd-Q1")
        self.assertEqual(p["birth_date"], "1897-04-03")          # más precisa y compatible
        self.assertEqual(p["field_sources"]["birth_date"], ["s1", "s2"])
        self.assertEqual(p["name"], "Anna Muster")               # prioridad s1
        self.assertEqual(p["variants"]["name"], [{"value": "Anna M.", "source_id": "s2"}])
        self.assertEqual(p["field_sources"]["death_date"], ["s2"])
        self.assertEqual(p["fate"], "murdered")
        self.assertEqual(sorted(s["source_id"] for s in p["sources"]), ["s1", "s2"])
        self.assertEqual(p["alternate_ids"], ["st-a", "st-b"])

    def test_merge_by_external_id(self):
        ps = merge_family([rec("a", gb=["9"], birth="1880"), rec("b", gb=["9"], birth="1880")], {}, {})
        self.assertEqual(len(ps), 1)

    def test_never_by_name_only(self):
        ps = merge_family([rec("a", birth="1897"), rec("b", birth="1897")], {}, {})
        self.assertEqual(len(ps), 2)
        self.assertEqual(possible_duplicates(ps), [{"name_key": "anna muster", "birth_year": 1897, "ids": ["st-a", "st-b"]}])

    def test_blocked_merges(self):
        report = {}
        ps = merge_family([rec("a", qid="Q1", gb=["9"]), rec("b", qid="Q2", gb=["9"])], {}, report)
        self.assertEqual(len(ps), 2)
        self.assertEqual(report["blocked_merges"][0]["reason"], "different_wikidata")
        report = {}
        ps = merge_family([rec("a", gb=["9"], birth="1880"), rec("b", gb=["9"], birth="1920")], {}, report)
        self.assertEqual(len(ps), 2)
        self.assertEqual(report["blocked_merges"][0]["reason"], "birth_year_mismatch")


class TestSchemaValidator(unittest.TestCase):
    def test_validator(self):
        v = Validator(SCHEMA)
        good = {"id": "st-n1", "name": "A", "fate": "unknown", "field_sources": {"name": ["s"]},
                "sources": [{"source_id": "s", "record_id": "n1", "license": "ODbL-1.0", "attribution": "x"}]}
        self.assertEqual(v.errors(good), [])
        self.assertTrue(v.errors(dict(good, sources=[])))                       # procedencia obligatoria
        bad = dict(good, sources=[{"source_id": "s", "record_id": "n1", "attribution": "x"}])
        self.assertTrue(any("license" in e for e in v.errors(bad)))              # licencia obligatoria
        self.assertTrue(v.errors(dict(good, fate="happy")))
        self.assertTrue(v.errors(dict(good, birth_date="12.3.1900")))
        self.assertTrue(v.errors(dict(good, extra=1)))
        self.assertTrue(v.errors(dict(good, places=[{"role": "x", "label": "y", "source_id": "s"}])))


class BuildCase(unittest.TestCase):
    def setUp(self):
        self.tmps = []

    def tearDown(self):
        for t in self.tmps:
            shutil.rmtree(t, ignore_errors=True)

    def env(self, **kw):
        tmp, sources = make_env(**kw)
        self.tmps.append(tmp)
        return tmp, sources


class TestLicenseGate(BuildCase):
    def test_not_allowed_source_absent(self):
        tmp, sources = self.env(partner_publish=False)
        out, res = run_build(sources, tmp)
        files = read_all(out)
        blob = "\n".join(files.values())
        self.assertNotIn('"source_id":"yadvashem"', blob)
        self.assertNotIn("Yad Vashem – The World", blob)   # ni su atribución (no hay datos suyos)
        self.assertNotIn("YV-1", blob)
        self.assertNotIn("Erna", blob)
        self.assertFalse(os.path.exists(os.path.join(out, "partners")))
        self.assertEqual(res["gate"]["withheld_by_license"]["yadvashem"]["count"], 2)
        self.assertEqual(validate(out=out, sources=sources, suppressed=set())["errors"], [])

    def test_families_never_merged(self):
        """Regla 2: con permiso, la fuente de socio va en partners/<fuente>/ y no se fusiona con ODbL
        aunque comparta Qid; el cruce es solo por id (ids/wikidata.json en cada familia)."""
        tmp, sources = self.env(partner_publish=True)
        out, _ = run_build(sources, tmp)
        odbl = people(out, "odbl")
        partner = people(out, "partners/yadvashem")
        self.assertIn("wd-Q900000010", odbl)
        self.assertIn("yv-YV-1", partner)
        for p in odbl.values():
            self.assertEqual({s["source_id"] for s in p["sources"]}, {"stolpersteine_de"})
        for p in partner.values():
            self.assertEqual({s["source_id"] for s in p["sources"]}, {"yadvashem"})
        self.assertNotIn("deportations", [k for k, v in odbl["wd-Q900000010"].items() if "Stuttgart" in json.dumps(v)])
        meta = load_json(os.path.join(out, "partners", "yadvashem", "index.json"))["meta"]
        self.assertEqual(meta["license"], "LicenseRef-permiso-pendiente")
        idx_o = load_json(os.path.join(out, "odbl", "ids", "wikidata.json"))["rows"]
        idx_p = load_json(os.path.join(out, "partners", "yadvashem", "ids", "wikidata.json"))["rows"]
        self.assertIn(["Q900000010", "wd-Q900000010"], idx_o)
        self.assertIn(["Q900000010", "yv-YV-1"], idx_p)
        self.assertEqual(validate(out=out, sources=sources, suppressed=set())["errors"], [])


class TestPolicy(BuildCase):
    def test_living_and_survivor_rules(self):
        tmp, sources = self.env(partner=False)
        out, res = run_build(sources, tmp)
        ps = people(out)
        names = {p["name"] for p in ps.values()}
        self.assertNotIn("Kurt Lebend", names)            # 1930, sin indicio de muerte → fuera
        self.assertIn("Max Alt", names)                   # 1900 (> 110 años) → dentro
        eva = next(p for p in ps.values() if p["name"] == "Eva Flucht")
        self.assertEqual(eva.get("links", []), [])        # superviviente ≥1916: sin enlaces a fichas
        self.assertNotIn("gedenkbuch", eva.get("identifiers", {}))
        self.assertEqual(eva["restrictions"], ["survivor_minimization"])
        blob = "\n".join(read_all(out).values())
        self.assertNotIn("example.org/eva", blob)
        self.assertNotIn("Kurt Lebend", blob)
        # El índice de placas (data/search) sí muestra la placa, sin ficha en la API
        plaques = "\n".join(read_all(os.path.join(tmp, "data", "search")).values())
        self.assertIn('"n3","Kurt Lebend"', plaques)
        self.assertIn('"1930",null]', plaques)
        self.assertEqual(res["policy"]["odbl"]["possibly_living_excluded"], 1)

    def test_unknown_birth_without_death_excluded(self):
        tmp, sources = self.env(partner=False, stones=[
            {"id": "n9", "la": 1, "lo": 1, "src": "osm", "n": "Ohne Jahr", "i": "HIER WOHNTE OHNE JAHR DEPORTIERT"},
            {"id": "n10", "la": 1, "lo": 1, "src": "osm", "n": "Tot Ohne Jahr", "i": "HIER WOHNTE X ERMORDET"}])
        out, _ = run_build(sources, tmp)
        self.assertEqual([p["name"] for p in people(out).values()], ["Tot Ohne Jahr"])


class TestAuditFixes(BuildCase):
    def test_hidden_child_excluded_from_api_but_plaque_kept(self):
        tmp, sources = self.env(partner=False, stones=[
            {"id": "n20", "la": 52, "lo": 7.6, "src": "osm", "n": "Ursula Test",
             "i": "Hier überlebte 1943-1945 Ursula Test, versteckt/gerettet vor Deportation und Tod", "b": "1935",
             "a": "Weg 1, Münster", "c": "Münster", "gb": ["777"]}])
        out, res = run_build(sources, tmp)
        self.assertEqual(people(out), {})                                   # posible viva: fuera de la API
        man = load_json(os.path.join(tmp, "data", "search", "manifest.json"))
        self.assertEqual(man["prefixes"], ["t"])
        rows = load_json(os.path.join(tmp, "data", "search", "index-t.json"))["rows"]
        # jg = None: la placa no lleva "Jg."; el año 1935 es una etiqueta OSM, no texto de la placa
        self.assertEqual(rows, [["n20", "Ursula Test", "Weg 1, Münster", "Münster", 52, 7.6, None, None]])
        self.assertNotIn("http", json.dumps(rows))                           # sin enlaces en las filas
        blob = "\n".join(read_all(os.path.join(tmp, "data", "search")).values())
        self.assertNotIn("777", blob)                                         # ni ids de registros

    def test_scope_statements(self):
        tmp, sources = self.env(partner=False)
        out, _ = run_build(sources, tmp)
        idx = load_json(os.path.join(out, "index.json"))
        self.assertIn("NO son fichas de personas", idx["scope"])
        self.assertIn("TODAS las placas", idx["scope"])
        self.assertIn("no una base de fichas de personas", idx["full_database"]["note"])
        with open(os.path.join(tmp, "llms.txt"), encoding="utf-8") as fh:
            llms = fh.read()
        self.assertIn("NO tiene valor jurídico propio", llms)
        self.assertIn("NO son fichas de personas", llms)
        self.assertIn("ODbL", llms)

    def test_quality_flags(self):
        tmp, sources = self.env(partner=False, stones=[
            {"id": "n30", "la": 1, "lo": 1, "src": "osm", "n": "Anna Datum", "b": "1950", "d": "1942-01-01",
             "i": "HIER WOHNTE ANNA DATUM ERMORDET"},
            {"id": "n31", "la": 1, "lo": 1, "src": "osm", "n": "Otto Alt", "b": "1020", "i": "HIER WOHNTE OTTO ALT ERMORDET"},
            {"id": "n32", "la": 1, "lo": 1, "src": "osm", "n": "Ida Gut", "b": "1890", "d": "1942",
             "i": "HIER WOHNTE IDA GUT ERMORDET 1942"}])
        out, _ = run_build(sources, tmp)
        ps = {p["name"]: p for p in people(out).values()}
        self.assertEqual(ps["Anna Datum"]["quality_flags"], ["birth_after_death"])
        self.assertEqual(ps["Anna Datum"]["birth_date"], "1950")                # se marca, no se corrige
        self.assertEqual(ps["Otto Alt"]["quality_flags"], ["birth_before_1800"])
        self.assertNotIn("quality_flags", ps["Ida Gut"])
        rows = load_json(os.path.join(out, "odbl", "quality", "date-flags.json"))["rows"]
        self.assertEqual(sorted(r[1] for r in rows), ["Anna Datum", "Otto Alt"])
        st = load_json(os.path.join(out, "odbl", "stats.json"))["stats"]["quality_flags"]
        self.assertEqual(st, {"birth_after_death": 1, "birth_before_1800": 1})

    def test_tests_do_not_touch_repo_reports(self):
        rep = os.path.join(PIPELINE_DIR, "reports")
        before = {f: os.path.getmtime(os.path.join(rep, f)) for f in os.listdir(rep)} if os.path.isdir(rep) else {}
        tmp, sources = self.env(partner=False)
        run_build(sources, tmp)
        after = {f: os.path.getmtime(os.path.join(rep, f)) for f in os.listdir(rep)} if os.path.isdir(rep) else {}
        self.assertEqual(before, after)
        self.assertTrue(os.path.exists(os.path.join(tmp, "reports", "build.json")))

    def test_wikidata_source_scope(self):
        cfg = load_sources()["wikidata_holocaust_victims"]
        self.assertFalse(any("P9805" in x for x in cfg["selectors"]))
        self.assertNotIn("P9805", cfg["identifier_properties"])
        self.assertTrue(any("P4130" in x for x in cfg["selectors"]))           # USHMM se mantiene
        self.assertNotIn("víctimas de", cfg["name"].lower())
        b = {"item": {"value": "http://www.wikidata.org/entity/Q5000"}, "label1": {"value": "U S"},
             "ids_P4130": {"value": "1"}, "birth": {"value": "1880-01-01T00:00:00Z"}, "birth_prec": {"value": "11"}}
        r = wikidata_sparql.binding_to_record(b, cfg, "2026-11-11")
        self.assertEqual(r["fate"], "unknown")                                  # tener id USHMM no implica víctima


class TestSuppressed(BuildCase):
    def test_suppressed_ids_removed_everywhere(self):
        tmp, sources = self.env(partner=False)
        out, res = run_build(sources, tmp, suppressed=["n5", "Q900000010"])
        blob = "\n".join(read_all(out).values()) + "\n".join(read_all(os.path.join(tmp, "data", "search")).values())
        self.assertNotIn("Max Alt", blob)
        self.assertNotIn("Q900000010", blob)
        self.assertNotIn("Dorfstraße 1", blob)
        self.assertIn("Paul Gebe", blob)
        self.assertEqual(validate(out=out, sources=sources, suppressed={"n5", "Q900000010"})["errors"], [])

    def test_suppressed_by_external_id_and_memorial(self):
        tmp, sources = self.env(partner=False)
        out, _ = run_build(sources, tmp, suppressed=["gedenkbuch:333", "n6"])
        names = [p["name"] for p in people(out).values()]
        self.assertNotIn("Paul Gebe", names)                 # retirado por id del Gedenkbuch
        self.assertEqual(names.count("Martha Schwarz"), 1)   # n6 (Frankfurt) retirado por id de placa
        plaques = "\n".join(read_all(os.path.join(tmp, "data", "search")).values())
        self.assertNotIn("Paul Gebe", plaques)

    def test_suppressed_by_person_id(self):
        tmp, sources = self.env(partner=False)
        out, _ = run_build(sources, tmp, suppressed=["st-n8"])  # id alternativo de una persona fusionada
        self.assertFalse([p for p in people(out).values() if p["name"] == "Paul Gebe"])


class TestBuildOffline(BuildCase):
    def test_mini_build_contents(self):
        tmp, sources = self.env(partner=False)
        out, _ = run_build(sources, tmp)
        ps = people(out)
        martha = ps["wd-Q900000010"]
        self.assertEqual(len(martha["memorials"]), 2)               # dos placas, misma persona (Qid)
        self.assertEqual(martha["birth_date"], "1897-04-03")
        self.assertEqual(martha["fate"], "murdered")
        paul = [p for p in ps.values() if p["name"] == "Paul Gebe"]
        self.assertEqual(len(paul), 1)                               # unión por id del Gedenkbuch
        self.assertEqual(sorted(s["license"] for s in paul[0]["sources"]), ["CC0-1.0", "ODbL-1.0"])
        dups = load_json(os.path.join(out, "odbl", "quality", "possible-duplicates.json"))["groups"]
        self.assertEqual(len(dups), 1)                               # Martha Schwarz de Frankfurt: no fusionada
        for rel, text in read_all(out).items():
            if rel.endswith(".json") and rel not in ("openapi.json", os.path.join("schema", "person.schema.json")):
                meta = json.loads(text)["meta"]
                for k in ("license", "attribution", "source_url", "generated"):
                    self.assertTrue(meta.get(k), "%s sin meta.%s" % (rel, k))
        self.assertTrue(os.path.exists(os.path.join(tmp, "llms.txt")))
        self.assertTrue(os.path.exists(os.path.join(tmp, ".well-known", "api-catalog")))
        oa = load_json(os.path.join(out, "openapi.json"))
        self.assertEqual(oa["openapi"], "3.1.0")

    def test_deterministic(self):
        tmp, sources = self.env(partner=False)
        out, _ = run_build(sources, tmp)
        first = read_all(out)
        out, _ = run_build(sources, tmp)
        self.assertEqual(first, read_all(out))

    def test_real_stones_limited(self):
        """Build offline desde el data/stones.json real del repo (primeros 1500 registros)."""
        tmp = __import__("tempfile").mkdtemp(prefix="kl-real-")
        self.tmps.append(tmp)
        sources = load_sources()
        out, res = run_build(sources, tmp, source_ids=["stolpersteine_de"], limit=1500, offline=True)
        self.assertEqual(res["report"]["sources"]["stolpersteine_de"]["records"], 1500)
        v = validate(out=out, sources=sources, suppressed=set())
        self.assertEqual(v["errors"], [])
        self.assertGreater(v["people"], 1000)

    def test_safe_reset_refuses_foreign_dir(self):
        tmp, sources = self.env(partner=False)
        foreign = os.path.join(tmp, "foreign")
        os.makedirs(foreign)
        open(os.path.join(foreign, "keep.txt"), "w").close()
        with self.assertRaises(RuntimeError):
            build.safe_reset(foreign)
        self.assertTrue(os.path.exists(os.path.join(foreign, "keep.txt")))


class TestNetworkAdapters(BuildCase):
    def test_wikidata_fixture_family_cc0(self):
        tmp, sources = self.env(partner=False, wikidata=True)
        out, res = run_build(sources, tmp, fixtures={"wikidata_holocaust_victims": os.path.join(FIX, "wikidata_sample.json")})
        cc0 = people(out, "cc0")
        self.assertIn("wd-Q104424595", cc0)
        berta = cc0["wd-Q104424595"]
        self.assertEqual(berta["birth_date"], "1868-02-25")
        self.assertNotIn("family_name", berta)                 # dos apellidos distintos: no se elige
        self.assertEqual(berta["identifiers"]["gedenkbuch"], ["851018"])
        rosenthal = cc0["wd-Q105388305"]
        self.assertNotIn("death_date", rosenthal)              # precisión de década: no se inventa año
        self.assertNotIn("wd-Q900000001", cc0)                 # nacido 1925 sin muerte → fuera
        self.assertEqual(load_json(os.path.join(out, "cc0", "index.json"))["meta"]["license"], "CC0-1.0")
        for p in people(out, "odbl").values():
            self.assertEqual({s["source_id"] for s in p["sources"]}, {"stolpersteine_de"})

    def test_wikidata_queries(self):
        q = wikidata_sparql.build_list_query("?item wdt:P7571 ?_gb", 10, 20)
        self.assertIn("LIMIT 10 OFFSET 20", q)
        d = wikidata_sparql.build_detail_query(["Q1", "Q2"], {"P7571": "gedenkbuch"}, ["de", "en", "mul"])
        self.assertIn("VALUES ?item { wd:Q1 wd:Q2 }", d)
        self.assertIn("?ids_P7571", d)

    def test_overpass_element(self):
        cfg = load_sources()["osm_stolpersteine_europe"]
        data = load_json(os.path.join(FIX, "overpass_sample.json"))
        r = overpass.element_to_record(data["elements"][0], "AT", cfg, "2026-11-11")
        self.assertEqual(r["id"], "osm-n900000001")
        self.assertEqual(r["fate"], "murdered")
        self.assertEqual(r["memorials"][0]["country"], "AT")
        self.assertEqual(r["sources"][0]["license"], "ODbL-1.0")

    def test_http_cache_and_retry(self):
        import urllib.error
        from pipeline.http import HttpClient, OfflineCacheMiss
        tmp, _ = self.env(partner=False)
        calls = []

        class Resp(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def opener(req, timeout=None):
            calls.append(req.get_header("User-agent"))
            if len(calls) == 1:
                raise urllib.error.HTTPError(req.full_url, 503, "busy", {}, None)
            return Resp(b'{"ok": 1}')
        c = HttpClient("t", cache_dir=tmp, min_interval=0, sleep=lambda s: None, opener=opener)
        self.assertEqual(c.get_json("https://example.org/x", {"a": 1}), {"ok": 1})
        self.assertEqual(calls, ["KauffmannList-pipeline/1.0"] * 2)
        off = HttpClient("t", cache_dir=tmp, offline=True)
        self.assertEqual(off.get_json("https://example.org/x", {"a": 1}), {"ok": 1})   # desde caché
        with self.assertRaises(OfflineCacheMiss):
            off.get_json("https://example.org/otro")


class TestRepoConfig(unittest.TestCase):
    def test_all_sources_valid_and_phase2_closed(self):
        srcs = load_sources()
        self.assertEqual(sorted(srcs), ["arolsen", "bundesarchiv_gedenkbuch", "osm_stolpersteine_europe",
                                        "stolpersteine_de", "ushmm", "wikidata_holocaust_victims", "yadvashem"])
        for s in srcs.values():
            if s["phase"] == 2:
                self.assertFalse(s["publish_allowed"])
                self.assertFalse(s["enabled"])
                self.assertEqual(s["license_family"], "partners/" + s["id"])
        self.assertFalse(srcs["osm_stolpersteine_europe"]["enabled"])

    def test_suppressed_file_only_ids(self):
        data = load_json(os.path.join(PIPELINE_DIR, "suppressed.json"))
        self.assertIsInstance(data["ids"], list)
        for x in data["ids"]:
            self.assertIsInstance(x, str)


if __name__ == "__main__":
    unittest.main()
