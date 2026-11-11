"""Entorno de prueba aislado: mini data/stones.json + data/bio y configuraciones de fuente."""
import copy
import json
import os
import tempfile

from pipeline.config import load_sources

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "fixtures")

STONES = [
    {"id": "n1", "la": 48.4, "lo": 8.75, "src": "osm", "n": "Martha Schwarz", "p": "Q900000010", "gb": ["111"],
     "i": "HIER WOHNTE MARTHA SCHWARZ JG. 1897 DEPORTIERT 1941 RIGA ERMORDET 1942", "a": "Dorfstraße 1, Mühringen",
     "c": "Mühringen", "b": "1897"},
    {"id": "n2", "la": 48.5, "lo": 8.8, "src": "osm", "n": "Martha Schwarz", "p": "Q900000010",
     "i": "HIER ARBEITETE MARTHA SCHWARZ JG. 1897 ERMORDET 1942 IN RIGA", "a": "Marktplatz 2, Horb", "c": "Horb",
     "b": "1897-04-03", "d": "1942"},
    {"id": "n3", "la": 52.5, "lo": 13.4, "src": "osm", "n": "Kurt Lebend",
     "i": "HIER WOHNTE KURT LEBEND JG. 1930 FLUCHT 1939 ENGLAND", "a": "Teststraße 3, Berlin", "c": "Berlin", "b": "1930"},
    {"id": "n4", "la": 52.5, "lo": 13.41, "src": "osm", "n": "Eva Flucht", "gb": ["222"], "d": "1990-01-01",
     "i": "HIER WOHNTE EVA FLUCHT JG. 1920 FLUCHT 1939 ENGLAND ÜBERLEBT", "a": "Teststraße 4, Berlin", "c": "Berlin",
     "b": "1920"},
    {"id": "n5", "la": 52.5, "lo": 13.42, "src": "osm", "n": "Max Alt",
     "i": "HIER WOHNTE MAX ALT JG. 1900 DEPORTIERT 1942", "a": "Teststraße 5, Berlin", "c": "Berlin", "b": "1900"},
    {"id": "n6", "la": 50.1, "lo": 8.6, "src": "osm", "n": "Martha Schwarz",
     "i": "HIER WOHNTE MARTHA SCHWARZ JG. 1897 ERMORDET 1943", "a": "Hauptstraße 6, Frankfurt am Main",
     "c": "Frankfurt am Main", "b": "1897"},
    {"id": "Q7", "la": 51.3, "lo": 9.48, "src": "wd", "wd": "Q7", "n": "Paul Gebe", "gb": ["333"],
     "i": "HIER WOHNTE PAUL GEBE JG. 1880 ERMORDET 1942", "a": "Ring 7, Kassel", "c": "Kassel"},
    {"id": "n8", "la": 51.31, "lo": 9.49, "src": "osm", "n": "Paul Gebe", "gb": ["333"], "b": "1880",
     "i": "HIER LERNTE PAUL GEBE JG. 1880 ERMORDET 1942", "a": "Schulweg 8, Kassel", "c": "Kassel"},
]

BIO = {"muhringen": {"n1": {"insc": {"birth": "1897", "deportation": "deportiert 1941 Riga", "death": "ermordet 1942"},
                            "links": {"berlin": "https://www.stolpersteine-berlin.de/biografie/1"}}},
       "berlin": {"n4": {"insc": {"birth": "1920"}, "links": {"describedAt": ["https://example.org/eva"]}}}}


def make_env(partner_publish=False, partner=True, wikidata=False, stones=None):
    tmp = tempfile.mkdtemp(prefix="kl-test-")
    data = os.path.join(tmp, "data")
    os.makedirs(os.path.join(data, "bio"))
    with open(os.path.join(data, "stones.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": {"generated": "2026-11-07T06:55+01:00", "osm_snapshot": "2026-11-04T21:21:03Z"},
                   "stones": stones if stones is not None else STONES}, f, ensure_ascii=False)
    for city, recs in BIO.items():
        with open(os.path.join(data, "bio", city + ".json"), "w", encoding="utf-8") as f:
            json.dump(recs, f, ensure_ascii=False)
    real = load_sources()
    sources = {}
    st = copy.deepcopy(real["stolpersteine_de"])
    st["input"] = {"stones": os.path.join(data, "stones.json"), "bio_dir": os.path.join(data, "bio")}
    sources[st["id"]] = st
    if partner:
        yv = copy.deepcopy(real["yadvashem"])
        yv["enabled"] = True
        yv["publish_allowed"] = partner_publish
        yv["input"]["path"] = os.path.join(FIX, "partner_sample.csv")
        sources[yv["id"]] = yv
    if wikidata:
        sources["wikidata_holocaust_victims"] = copy.deepcopy(real["wikidata_holocaust_victims"])
    return tmp, sources


def read_all(out):
    """Devuelve {ruta_relativa: texto} de todo lo generado."""
    res = {}
    for dirpath, _, files in os.walk(out):
        for fn in files:
            p = os.path.join(dirpath, fn)
            with open(p, "r", encoding="utf-8") as f:
                res[os.path.relpath(p, out)] = f.read()
    return res


def people(out, family="odbl"):
    base = os.path.join(out, family, "people", "by-surname")
    res = {}
    if not os.path.isdir(base):
        return res
    for fn in sorted(os.listdir(base)):
        with open(os.path.join(base, fn), encoding="utf-8") as f:
            for p in json.load(f)["people"]:
                res[p["id"]] = p
    return res
