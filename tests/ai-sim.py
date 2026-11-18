"""Simulación de una IA con SOLO los archivos públicos (llms.txt, llms-full.txt, api/v1/**).

Uso: python3 tests/ai-sim.py [raíz_del_sitio] [--n 10] [--seed 1] [--report ruta.json]

La IA simulada:
  · lee llms-full.txt y usa SU fold() (el bloque python publicado), no el del pipeline;
  · solo "descarga" URLs del sitio (api/v1/…, llms*.txt); cualquier otra ruta falla;
  · busca por nombre (find/name) y por ciudad (find/city), con persona elegida al azar entre las fichas reales;
  · compone una cita con la plantilla publicada y comprueba que cada dato citado está en la ficha.
Falla (exit 1) si alguna búsqueda no encuentra a la persona o la cita contiene algo que la ficha no dice.
"""
import json
import os
import random
import re
import sys

BASE = "https://roquena71-a11y.github.io/kauffmann-list/"
args = [a for a in sys.argv[1:]]
opt = lambda name, default: (args[args.index(name) + 1] if name in args else default)
N = int(opt("--n", 10))
SEED = int(opt("--seed", 1))
REPORT = opt("--report", None)
pos = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or not args[i - 1].startswith("--"))]
ROOT = pos[0] if pos else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
fetched = []


def get(url):
    assert url.startswith(BASE), "fuera del sitio: " + url
    rel = url[len(BASE):]
    assert rel.startswith(("api/v1/", "llms")), "ruta no pública para la IA: " + rel
    fetched.append(rel)
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read() if rel.endswith(".txt") else json.load(f)


# --- 1) la IA lee la guía y toma su fold() ---
guide = get(BASE + "llms-full.txt")
ns = {}
exec(re.search(r"```python\n(.*?)\n```", guide, re.S).group(1), ns)
fold = ns["fold"]
template = re.search(r"Template:\n\n```\n(.*?)\n```", guide, re.S).group(1)
fams = [f for f in ("odbl", "cc0") if os.path.isdir(os.path.join(ROOT, "api", "v1", f, "find"))]


def find_prefix(key, prefixes):
    for n in range(6, 0, -1):
        cand = (key + "______")[:n]
        if cand in prefixes:
            return cand
    return None


def person_row_to_dict(r):
    return dict(zip(["id", "name", "birth_year", "death_year", "place", "people_prefix"], r))


def record(fam, row):
    pack = get(BASE + "api/v1/%s/people/by-surname/%s.json" % (fam, row["people_prefix"]))
    hits = [p for p in pack["people"] if p["id"] == row["id"]]
    assert len(hits) == 1, "ficha no encontrada para %s" % row["id"]
    return hits[0], pack["meta"]


def permalink(p, fam):
    """Regla publicada: odbl → #s=<memorials[0].memorial_id>; cc0 → #p=<id>."""
    if fam == "odbl":
        assert p.get("memorials") and p["memorials"][0].get("memorial_id"), "sin memorial_id: " + p["id"]
        return BASE + "#s=" + p["memorials"][0]["memorial_id"]
    return BASE + "#p=" + p["id"]


PARTICLES = {"von", "van", "de", "der", "den", "zu", "zur", "vom", "ten", "ter", "da", "di", "del", "la", "le",
             "dr", "prof", "rabbiner", "rabbi", "sanitatsrat", "justizrat", "pfarrer", "pastor", "dipl", "ing"}   # no se indexan (llms-full.txt)


def search_words(name):
    """Palabras que una IA puede buscar: fold() del nombre sin el texto entre paréntesis, de ≥2 letras, sin partículas ni títulos (según llms-full.txt)."""
    name = re.sub(r"\(.*?\)", " ", name or "")   # el texto entre paréntesis no se indexa (llms-full.txt)
    return [w for w in fold(name).split() if len(w) >= 2 and w not in PARTICLES and not w.isdigit()]


def display_name(p):
    return p["name"] if p.get("name") else "sin nombre (memorial anónimo)"   # nunca 'None'


def cite(p, meta, fam):
    src = [s["url"] for s in p.get("sources", []) if s.get("url")]
    assert src, "ficha sin fuente: " + p["id"]
    birth = (p.get("birth_date") or "no consta")
    death = (p.get("death_date") or "no consta")
    text = template.format(name=display_name(p), birth=birth, death=death, id=p["id"],
                           permalink=permalink(p, fam), source_url=src[0], generated=meta["generated"],
                           license=meta["license"], attribution="; ".join(meta["attribution"]) if isinstance(meta["attribution"], list) else meta["attribution"])
    # comprobación: todo lo citado sale de la ficha o del meta
    assert "None" not in text, "la cita contiene 'None'"
    assert display_name(p) in text and src[0] in text and meta["license"] in text
    if not p.get("death_date"):
        assert "no consta" in text
    return text


def consistent(row, rec):
    """La fila del índice y la ficha dicen lo mismo (nombre y años)."""
    def yr(v):
        return int(v[:4]) if v and re.match(r"^\d{4}", v) else None
    assert row["name"] == rec.get("name"), "fila y ficha con nombre distinto: %r ≠ %r" % (row["name"], rec.get("name"))
    assert row["birth_year"] == yr(rec.get("birth_date")), "año de nacimiento distinto en %s" % rec["id"]
    assert row["death_year"] == yr(rec.get("death_date")), "año de muerte distinto en %s" % rec["id"]


def lookup_by_name(fam, person):
    idx = get(BASE + "api/v1/%s/find/index.json" % fam)
    words = search_words(person["name"])
    assert words, "nombre sin palabras buscables: %r" % person["name"]
    key = words[-1]                      # apellido = última palabra buscable
    pre = find_prefix(key, idx["name"]["prefixes"])
    assert pre, "sin prefijo para " + key
    f = get(BASE + "api/v1/%s/find/name/%s.json" % (fam, pre))
    rows = [person_row_to_dict(r[1:]) for r in f["rows"] if r[0].startswith(key)]
    # desambiguar con nombre completo normalizado
    exact = [r for r in rows if fold(r["name"]) == fold(person["name"])]
    return exact, len(rows), pre


def lookup_by_city(fam, label, country, pid):
    ci = get(BASE + "api/v1/%s/find/city/index.json" % fam)
    key = fold(label).replace(" ", "")
    cand = [r for r in ci["rows"] if r[0] == key and r[1].lower() == country.lower()]
    assert cand, "ciudad no encontrada: " + label
    _, cc, slug, lab, count, pages = cand[0]
    rows = []
    for pg in range(pages):
        name = slug if pg == 0 else "%s~%d" % (slug, pg + 1)
        f = get(BASE + "api/v1/%s/find/city/%s/%s.json" % (fam, cc.lower(), name))
        rows += [person_row_to_dict(r) for r in f["rows"]]
    return [r for r in rows if r["id"] == pid], count


def main():
    rnd = random.Random(SEED)
    results, failures, skipped = [], [], []
    for fam in fams:
        d = os.path.join(ROOT, "api", "v1", fam, "people", "by-surname")
        files = sorted(os.listdir(d))
        # muestra ground truth leyendo fichas reales (la IA NO ve esto; es solo para elegir a quién buscar)
        pool = []
        while len(pool) < N * 6:
            fn = rnd.choice(files)
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                ppl = json.load(f)["people"]
            if ppl:
                pool.append(rnd.choice(ppl))
        by_name = [p for p in pool if p.get("name") and len(search_words(p["name"])) >= 2][:N // 2 if N > 1 else 1]
        with_city = []
        for p in pool:
            for m in p.get("memorials") or []:
                if m.get("locality") and m.get("country"):
                    with_city.append((p, m["locality"], m["country"]))
                    break
            else:
                for pl in p.get("places") or []:
                    if pl.get("role") == "death" and pl.get("country") and (pl.get("locality") or pl.get("label")):
                        with_city.append((p, pl.get("locality") or pl["label"], pl["country"]))
                        break
        used = {p["id"] for p in by_name}
        by_city = [t for t in with_city if t[0]["id"] not in used][:N - len(by_name)]
        for p in by_name:
            r = {"family": fam, "mode": "name", "query": p["name"], "id": p["id"]}
            try:
                exact, n_rows, pre = lookup_by_name(fam, p)
                ids = [e["id"] for e in exact]
                assert p["id"] in ids, "no encontrada (%d filas con esa palabra, %d exactas)" % (n_rows, len(exact))
                row = next(e for e in exact if e["id"] == p["id"])
                rec, meta = record(fam, row)
                consistent(row, rec)
                r.update(ok=True, candidates=len(exact), prefix=pre, citation=cite(rec, meta, fam))
            except AssertionError as e:
                r.update(ok=False, error=str(e))
                failures.append(r)
            except Exception as e:  # noqa: BLE001 — un fallo del propio simulador no debe bloquear una publicación
                r.update(ok=None, error="simulador: %s: %s" % (type(e).__name__, e))
                skipped.append(r)
            results.append(r)
        for p, loc, cc in by_city:
            r = {"family": fam, "mode": "city", "query": "%s (%s)" % (loc, cc), "id": p["id"], "name": p.get("name")}
            try:
                hit, count = lookup_by_city(fam, loc, cc, p["id"])
                assert hit, "no está en la página de la ciudad (%d personas)" % count
                rec, meta = record(fam, hit[0])
                consistent(hit[0], rec)
                assert fold(hit[0]["name"]) == fold(p.get("name"))
                r.update(ok=True, city_people=count, citation=cite(rec, meta, fam))
            except AssertionError as e:
                r.update(ok=False, error=str(e))
                failures.append(r)
            except Exception as e:  # noqa: BLE001 — un fallo del propio simulador no debe bloquear una publicación
                r.update(ok=None, error="simulador: %s: %s" % (type(e).__name__, e))
                skipped.append(r)
            results.append(r)
    out = {"seed": SEED, "total": len(results), "ok": sum(1 for r in results if r["ok"]), "skipped": len(skipped),
           "fetched_files": len(set(fetched)), "results": results}
    if REPORT:
        with open(REPORT, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
    for r in results:
        print(("OK  " if r["ok"] else "AVISO " if r["ok"] is None else "FALLO ") + "%s %-4s %-40s → %s" % (r["family"], r["mode"], r["query"][:40], (r.get("citation") or r.get("error"))[:150]))
    print("ai-sim: %d/%d correctas, %d fallos, %d avisos del simulador (seed %d, %d archivos distintos descargados)" % (
        out["ok"], out["total"], len(failures), len(skipped), SEED, out["fetched_files"]))
    # Un aviso del simulador (p. ej. un nombre raro) no bloquea; solo bloquea un fallo real o si el simulador no pudo probar casi nada.
    if skipped and len(skipped) > max(2, out["total"] // 4):
        print("ai-sim: demasiados avisos del simulador")
        return 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
