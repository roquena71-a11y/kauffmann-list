"""Regenera llms.txt y llms-full.txt (y la nota de familias vacías en api/v1/index.json) desde los índices YA generados de api/v1/,
sin reconstruir api/ (para trabajar en local con poco disco). En CI lo hace `python3 -m pipeline build`.
Uso: python3 tests/regen-agent-texts.py [--check]   (--check: solo compara, no escribe; sale 1 si difiere)"""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, ROOT)
from pipeline import agents  # noqa: E402
from pipeline.config import load_sources, load_families  # noqa: E402

def main():
    check = "--check" in sys.argv
    cat = json.load(open(os.path.join(ROOT, "api/v1/index.json"), encoding="utf-8"))
    generated = cat["generated"]
    sources = load_sources()
    families = load_families(sources=sources)
    fam_indexes = {}
    for fid in cat["families"]:
        fam_indexes[fid] = json.load(open(os.path.join(ROOT, "api/v1", fid, "index.json"), encoding="utf-8"))
    out = {"llms.txt": agents.llms_txt(fam_indexes, families, generated),
           "llms-full.txt": agents.llms_full_txt(fam_indexes, families, generated)}
    # api/v1/index.json: solo la nota de familias sin fichas (igual que agents.write_catalog), sin tocar nada más
    from pipeline.util import write_json
    import tempfile
    cat2 = json.loads(json.dumps(cat))
    for fid, f in cat2["families"].items():
        f.pop("note_zero_people", None)
        if not f["count_people"]:
            f["note_zero_people"] = agents.zero_people_note(fid, sources)
    tmp = tempfile.mktemp()
    write_json(tmp, cat2)
    out["api/v1/index.json"] = open(tmp, encoding="utf-8").read()
    os.unlink(tmp)
    bad = []
    for rel, txt in out.items():
        p = os.path.join(ROOT, rel)
        cur = open(p, encoding="utf-8").read()
        if cur != txt:
            bad.append(rel)
            if not check:
                open(p, "w", encoding="utf-8").write(txt)
    print(("difiere: " if check else "reescrito: ") + (", ".join(bad) or "nada"))
    return 1 if (check and bad) else 0

if __name__ == "__main__":
    sys.exit(main())
