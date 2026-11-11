"""CLI: python3 -m pipeline build|validate (desde la raíz del repo)."""
import argparse
import os
import sys

from . import build as build_mod
from .validate import validate


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python3 -m pipeline", description="Pipeline de datos abiertos de la Lista Kauffmann")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Genera api/v1 (y llms.txt, .well-known, data/search)")
    b.add_argument("--sources", help="ids separados por comas (por defecto: las fuentes con enabled:true)")
    b.add_argument("--limit", type=int, help="máximo de registros por fuente (pruebas)")
    b.add_argument("--offline", action="store_true", help="sin red: solo caché local (pipeline/cache)")
    b.add_argument("--out", help="directorio de salida (por defecto api/v1)")
    b.add_argument("--no-site", action="store_true", help="no escribir llms.txt, .well-known ni data/search")
    b.add_argument("--fixture", action="append", default=[], metavar="FUENTE=RUTA",
                   help="usar un archivo de prueba en lugar de la red para una fuente")
    b.add_argument("--strict", action="store_true", help="fallar si una fuente no se puede leer")
    b.add_argument("--generated", help="fecha de datos (por defecto: la del snapshot más reciente)")
    b.add_argument("--shard-chars", type=int, default=2, help="caracteres finales del id para el fragmento (2 o 3)")
    v = sub.add_parser("validate", help="Valida la salida publicada")
    v.add_argument("--out", help="directorio a validar (por defecto api/v1)")
    args = ap.parse_args(argv)
    if args.cmd == "build":
        fixtures = dict(f.split("=", 1) for f in args.fixture)
        res = build_mod.run(source_ids=args.sources.split(",") if args.sources else None, limit=args.limit,
                            offline=args.offline, out=args.out, fixtures=fixtures, strict=args.strict,
                            generated=args.generated, shard_chars=args.shard_chars, write_site=not args.no_site)
        files = res["files"]
        print("generated=%s" % res["generated"])
        for fid, pol in sorted(res["policy"].items()):
            print("familia %-28s %s" % (fid, " ".join("%s=%s" % kv for kv in sorted(pol.items()))))
        print("api: %d archivos, %d bytes, máximo %d bytes (%s)" % (
            len(files), sum(files.values()), max(files.values()) if files else 0,
            max(files, key=files.get) if files else "-"))
        if res["site_files"]:
            sf = res["site_files"]
            print("sitio: %d archivos, %d bytes, máximo %d bytes" % (len(sf), sum(sf.values()), max(sf.values())))
        if res["report"]["failures"]:
            print("FALLOS: %s" % res["report"]["failures"])
        if res["gate"].get("withheld_by_license"):
            print("retenidos por licencia: %s" % {k: v["count"] for k, v in res["gate"]["withheld_by_license"].items()})
        return 0
    res = validate(out=args.out)
    for w in res["warnings"][:50]:
        print("AVISO: " + w)
    for e in res["errors"][:100]:
        print("ERROR: " + e)
    print("validate: %d archivos, %d fichas, %d bytes, máximo %d bytes (%s), %d errores, %d avisos" % (
        res["files"], res["people"], res.get("bytes", 0), res.get("max_bytes", 0), res.get("max_file"),
        len(res["errors"]), len(res["warnings"])))
    return 1 if res["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
