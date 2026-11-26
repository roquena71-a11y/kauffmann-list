"""v37 (auditoría A3): fechas y totales del sitio sacados de los datos, nunca a mano.

Reescribe en el sitio (index.html, kauffmann-list.jsonld, sitemap.xml):
- JSON-LD: dateModified del conjunto (= fecha más reciente de meta.generated de los datos del mapa), dateModified de cada
  fuente de isBasedOn (OSM/Wikidata: instantáneas de data/stones.json; listas municipales: input.retrieved de pipeline/sources),
  variableMeasured (placas ODbL, placas del mapa, campos), la frase «Status …» con los totales, y el número de países.
- <meta name="description">, og:description, twitter:description y subtítulo: «Alemania y otros N países».
- sitemap.xml: lastmod del mapa/2D/JSON-LD = fecha de los datos; llms*.txt y api/ = fecha del build (generated).
Lo llama agents.write_site_files en cada build; a mano: python3 -m pipeline.sitefacts [--check] [raíz]."""
import glob
import json
import os
import re
import sys

from .config import load_sources

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDED_RE = re.compile(r"^data/([a-z0-9]+)-added-\d+\.json$")
DATE_RE = re.compile(r"\d{4}-\d\d-\d\d")
COUNTRY_EN = {"DE": "Germany", "NL": "the Netherlands", "IT": "Italy", "AT": "Austria", "FR": "France", "BE": "Belgium",
              "CZ": "Czechia", "PL": "Poland", "CH": "Switzerland", "LU": "Luxembourg"}
VAR_KEYS = (("with name", "n"), ("with inscription", "i"), ("with address", "a"), ("with birth date", "b"),
            ("with death date", "d"), ("with Wikimedia Commons photo", "img"), ("with Bundesarchiv Gedenkbuch ID", "gb"),
            ("with USHMM ID", "us"), ("with Yad Vashem ID", "yv"))


def _load(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return json.load(f)


def _dates(v):
    return DATE_RE.findall(json.dumps(v)) if not isinstance(v, str) else DATE_RE.findall(v)


def facts(root=ROOT, generated=None, sources=None):
    """Cifras y fechas reales de los datos del mapa (data/stones.json + las listas municipales que carga el mapa)."""
    sources = sources if sources is not None else load_sources()
    st = _load(root, "data/stones.json")
    S, meta = st["stones"], st["meta"]
    by_cc = {}
    for s in S:
        cc = s.get("cc") or "DE"
        by_cc[cc] = by_cc.get(cc, 0) + 1
    added, added_cc, data_dates, retrieved = {}, {}, _dates(meta.get("generated", "")), {}
    for sid in sorted(sources):
        cfg = sources[sid]
        path = (cfg.get("input") or {}).get("path") or ""
        m = ADDED_RE.match(path)
        if not m:
            continue
        d = _load(root, path)
        rows = d.get("stones") or []
        added[m.group(1)] = len(rows)
        for r in rows:
            cc = r.get("cc") or "DE"
            added_cc[cc] = added_cc.get(cc, 0) + 1
        data_dates += _dates((d.get("meta") or {}).get("generated", ""))
        if cfg.get("homepage"):
            retrieved[cfg["homepage"]] = (cfg.get("input") or {}).get("retrieved")
    for extra in sorted(glob.glob(os.path.join(root, "data", "photos-added-*.json"))):   # fotos de Commons que aplica el mapa (v34)
        with open(extra, encoding="utf-8") as f:
            data_dates += _dates((json.load(f).get("meta") or {}).get("generated", ""))
    osm = [meta.get("osm_snapshot", "")] + [v.get("snapshot_osm", "") for v in meta.values() if isinstance(v, dict)]
    wd = [meta.get("wikidata_snapshot", "")] + [v.get("snapshot_wikidata", v.get("snapshot", "")) for v in meta.values() if isinstance(v, dict)]
    all_cc = dict(by_cc)
    for cc, n in added_cc.items():
        all_cc[cc] = all_cc.get(cc, 0) + n
    if generated is None:
        try:
            generated = _load(root, "api/v1/index.json")["generated"]
        except (OSError, KeyError, ValueError):
            generated = max(data_dates)
    return {
        "odbl": len(S), "added": added, "added_total": sum(added.values()), "map_total": len(S) + sum(added.values()),
        "lists": len(added), "countries": len(all_cc), "by_cc": all_cc, "odbl_by_cc": by_cc, "added_cc": added_cc,
        "data_date": max(data_dates), "generated": generated[:10],
        "osm_date": max(x for s in osm for x in _dates(s)), "wikidata_date": max(x for s in wd for x in _dates(s)),
        "retrieved": retrieved, "fields": {lab: sum(1 for s in S if s.get(k)) for lab, k in VAR_KEYS},
    }


def _sub(pat, repl, s, n_expected, what, flags=0):
    s2, n = re.subn(pat, repl, s, flags=flags)
    if n != n_expected and not (n_expected == "+" and n > 0):
        raise ValueError("sitefacts: %s: %d coincidencias (esperadas %s)" % (what, n, n_expected))
    return s2


def apply_jsonld_text(x, F, what):
    """Cambia fechas y totales en un texto que contiene el JSON-LD del Dataset (index.html o kauffmann-list.jsonld)."""
    based = dict(F["retrieved"], **{"https://www.openstreetmap.org": F["osm_date"], "https://www.wikidata.org": F["wikidata_date"]})

    def based_date(m):
        u = m.group(2)
        if u not in based or not based[u]:
            raise ValueError("sitefacts: %s: fuente sin fecha %s" % (what, u))
        return m.group(1) + based[u] + '"'
    x = _sub(r'("url": "([^"]+)",\s*"license": "[^"]+",\s*"dateModified": ")\d{4}-\d\d-\d\d"', based_date, x, "+", what + " isBasedOn")
    x = _sub(r'("dateModified": )"\d{4}-\d\d-\d\d"(,\s*"variableMeasured")', lambda m: m.group(1) + '"%s"' % F["data_date"] + m.group(2), x, 1, what + " dateModified")
    x = _sub(r'("name": "Stolpersteine in dataset \(ODbL, OSM\+Wikidata\)",\s*"value": )\d+', lambda m: m.group(1) + str(F["odbl"]), x, 1, what + " odbl")
    x = _sub(r'("name": "Stolpersteine on the map \(ODbL plus )\d+( municipal open-data lists\)",\s*"value": )\d+',
             lambda m: m.group(1) + str(F["lists"]) + m.group(2) + str(F["map_total"]), x, 1, what + " map total")
    for lab, n in F["fields"].items():
        x = _sub(r'("name": "%s",\s*"value": )\d+' % re.escape(lab), lambda m, n=n: m.group(1) + str(n), x, 1, what + " " + lab)
    a, c = F["added"], F["countries"]
    others = F["added_total"] - a.get("berlin", 0) - a.get("koeln", 0)
    extra = "; ".join("{:,} in {}".format(F["by_cc"][cc], COUNTRY_EN.get(cc, cc)) for cc in sorted(F["added_cc"], key=lambda k: -F["added_cc"][k]) if cc != "DE")
    status = ("Status {d}, in preparation, not published: {odbl:,} stones (ODbL, OpenStreetMap + Wikidata) plus {be:,} from Berlin Open Data, "
              "{ko:,} from Köln Open.NRW, and {ot:,} from {nl} municipal open-data lists added in v22 (map total {tot:,}) in {c} countries "
              "({de:,} in Germany, of which {deo:,} are in the ODbL dataset{extra})").format(
        d=F["data_date"], odbl=F["odbl"], be=a.get("berlin", 0), ko=a.get("koeln", 0), ot=others, nl=F["lists"] - 2,
        tot=F["map_total"], c=c, de=F["by_cc"].get("DE", 0), deo=F["odbl_by_cc"].get("DE", 0), extra=("; " + extra) if extra else "")
    x = _sub(r"Status \d{4}-\d\d-\d\d, in preparation, not published: [\d,]+ stones \(ODbL, OpenStreetMap \+ Wikidata\) plus .*? in \d+ countries \([\d,]+ in Germany, of which [\d,]+ are in the ODbL dataset[^)]*\)",
             lambda m: status, x, 1, what + " status")
    x = _sub(r"Germany and \d+ other European countries", "Germany and %d other European countries" % (c - 1), x, "+", what + " países (en)")
    return x


def apply_html_meta(h, F):
    k = F["countries"] - 1
    h = _sub(r"Alemania y otros \d+ países", "Alemania y otros %d países" % k, h, "+", "index.html países (es)")
    h = _sub(r"Deutschland und \d+ weiteren Ländern", "Deutschland und %d weiteren Ländern" % k, h, "+", "index.html países (de)")
    return h


def apply_sitemap(t, F):
    def lm(m):
        loc = m.group(1)
        rel = loc.split("/kauffmann-list/", 1)[1]
        if rel.startswith("proyecto/"):
            return m.group(0)                       # textos del proyecto: no dependen de los datos
        d = F["generated"] if (rel.startswith("api/") or rel.startswith("llms")) else F["data_date"]
        return m.group(0)[:m.start(2) - m.start(0)] + d + m.group(0)[m.end(2) - m.start(0):]
    return _sub(r"<loc>([^<]+)</loc>\s*<lastmod>(\d{4}-\d\d-\d\d)</lastmod>", lm, t, "+", "sitemap")


def apply(root=ROOT, generated=None, check=False, sources=None):
    """Aplica las cifras a los archivos del sitio. Devuelve la lista de archivos que cambian (con check=True no escribe)."""
    if not all(os.path.exists(os.path.join(root, p)) for p in ("index.html", "kauffmann-list.jsonld", "sitemap.xml", "data/stones.json")):
        return []
    F = facts(root, generated, sources)
    changed = []
    for rel, fn in (("index.html", lambda t: apply_html_meta(apply_jsonld_text(t, F, "index.html"), F)),
                    ("kauffmann-list.jsonld", lambda t: apply_jsonld_text(t, F, "kauffmann-list.jsonld")),
                    ("sitemap.xml", lambda t: apply_sitemap(t, F))):
        p = os.path.join(root, rel)
        with open(p, encoding="utf-8") as f:
            cur = f.read()
        new = fn(cur)
        if new != cur:
            changed.append(rel)
            if not check:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(new)
    return changed


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    chk = "--check" in sys.argv
    root = os.path.abspath(args[0]) if args else ROOT
    F = facts(root)
    print(json.dumps({k: v for k, v in F.items() if k not in ("retrieved",)}, ensure_ascii=False, sort_keys=True))
    ch = apply(root, check=chk)
    print(("difiere: " if chk else "reescrito: ") + (", ".join(ch) or "nada"))
    sys.exit(1 if (chk and ch) else 0)
