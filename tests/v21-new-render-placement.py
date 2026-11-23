#!/usr/bin/env python3
"""Comprueba las reglas de colocación en la posición DIBUJADA de las placas nuevas de v21:

- columna 1,2 m (COL_HALF=0,60) y chincheta 2D a ≥0,5 m de toda fachada OSM
- centro nunca dentro de un edificio
- centro fuera de la calzada (regla de roadway20.py; exención si hay edificio a <6 m;
  las documentadas en calzada-v21.csv se aceptan)
- ≥1,55 m respecto a cualquier placa visible de v20 (posición dibujada) y a otros
  grupos nuevos
- desplazamiento ≤25 m salvo excepción en excepciones-25m-v21*.csv
- las nuevas de un mismo grupo forman una malla de paso 1,85 m (mínimo ≥1,85−0,08 m
  y al menos un lado ≈1,85 m); no basta con que no compartan el mismo punto a 7 decimales
- la calzada usa el tag OSM width (o est_width) de todas las vías vehiculares cuyo eje
  queda a ≤80 m; no se omite una vía por el radio del índice ni por d_center >25 m.
  Exención de fachada solo si hay edificio a <6 m. Las de calzada-v21.csv se aceptan.
- se comprueban las 1.840 nuevas
- v29: posición DIBUJADA = con la alineación con la calle (data/align-v24.json) ya aplicada; las de v20 se toman
  de este mismo cliente (no de b142fa48, porque también se alinean)

Uso:
  python3 tests/v21-new-render-placement.py <url_v21> [--v20-json FILE] [--v20-url URL]
  KL_HTTP / Playwright; bloquea kl-contador y *.workers.dev.
  --from-files  comprueba el dla/dlo de data/*-added-*.json (equivalente si el cliente
                clava al archivo) y --v20-json.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "pipeline" / "tools"))
# shapely vive en venv-se en esta máquina
_sp = Path("/workspace/venv-se/lib/python3.13/site-packages")
if _sp.exists() and str(_sp) not in sys.path:
    sys.path.insert(0, str(_sp))

from geo import to_xy, hav, M_LAT  # noqa: E402
import roadway20 as RWY  # noqa: E402

COL_HALF = 0.60
MARGIN = 0.50
COL_GAP = 1.55
COL_STEP = 1.85
GRID_TOL = 0.08
MAXMOVE = 25.0
ROAD_Q_RC = 4
ROAD_RAD = 80.0
EXPECT_NEW = 1840
# Canario de C ronda 3: esta vía tiene width=11; si el test no la ve, el chequeo está roto.
WIDTH_CANARY_WAY = "w4490370"
WIDTH_CANARY_VALUE = "11"
BLOCK_HOSTS = ("kl-contador", "workers.dev")
NEW_RE = re.compile(r"^(ber-|koeln-)")


def dist_eq(la1, lo1, la2, lo2):
    return math.hypot((la1 - la2) * M_LAT, (lo1 - lo2) * M_LAT * math.cos(math.radians((la1 + la2) / 2)))


def dist_cons(la1, lo1, la2, lo2):
    return max(hav(la1, lo1, la2, lo2), dist_eq(la1, lo1, la2, lo2))


def is_added(r):
    src = r.get("src") or ""
    i = str(r.get("id") or "")
    return src in ("berlin", "koeln") or bool(NEW_RE.match(i))


def exceptions_25():
    ids = set()
    for p in R.glob("excepciones-25m-v21*.csv"):
        with p.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("id"):
                    ids.add(row["id"])
    return ids


def calzada_exc():
    ids = set()
    p = R / "calzada-v21.csv"
    if p.exists():
        with p.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("id"):
                    ids.add(row["id"])
    return ids


def tags_extra_path():
    env = os.environ.get("HIGHWAY_TAGS_EXTRA")
    if env:
        return Path(env)
    v20 = Path(os.environ.get("V20_DATA", "/workspace/v21-data/place"))
    cands = [
        v20.resolve().parent / "near" / "highway-tags-extra.json",
        Path("/workspace/v21-data/near/highway-tags-extra.json"),
    ]
    for p in cands:
        if p.is_file():
            return p
    return cands[0]


def enrich_highway_tags(N):
    """Añade width/est_width/sidewalk* del PBF oficial. El extracto near los descarta."""
    path = tags_extra_path()
    if not path.is_file():
        print(f"FAIL: falta el sidecar de tags OSM ({path}). Sin width el chequeo de calzada "
              f"no habría pillado w4490370 (width=11).", file=sys.stderr)
        sys.exit(1)
    extra = json.loads(path.read_text())
    n = 0
    for hid, (_pts, t) in N.h.items():
        if hid in extra:
            t.update(extra[hid])
            n += 1
    sample = extra.get(WIDTH_CANARY_WAY) or (N.h[WIDTH_CANARY_WAY][1] if WIDTH_CANARY_WAY in N.h else None)
    return n, sample


async def dump(url, expect_min, label):
    from playwright.async_api import async_playwright

    t0 = time.time()
    blocked, allowed, errs = [], set(), []
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader",
                  "--ignore-gpu-blocklist", "--disable-dev-shm-usage"],
        )
        ctx = await browser.new_context(viewport={"width": 1280, "height": 800},
                                        service_workers="block", locale="es-ES")
        page = await ctx.new_page()
        page.on("pageerror", lambda e: errs.append(str(e)))

        async def route_handler(route):
            u = route.request.url
            host = ""
            try:
                host = u.split("/")[2]
            except Exception:
                pass
            if any(b in u or b in host for b in BLOCK_HOSTS):
                blocked.append(u)
                await route.abort()
                return
            if u.startswith("http"):
                allowed.add(host)
            await route.continue_()

        await page.route("**/*", route_handler)
        await page.goto(url, wait_until="load", timeout=120000)
        await page.wait_for_function(
            f"typeof DATA!=='undefined' && DATA.length>={expect_min} && DATA.every(s=>s._dla!==undefined || s._aliasOf) && (!window.KLAlign || KLAlign.ready)",
            timeout=600000,
        )
        rows = await page.evaluate("""() => DATA.map(s => ({
          id: String(s.id), src: s.src||null, n:s.n||null, a:s.a||null,
          sla:s.sla??null, slo:s.slo??null, la:s.la, lo:s.lo,
          dla_file:s.dla??null, dlo_file:s.dlo??null,
          _dla:s._dla, _dlo:s._dlo, _ang:s._ang||0, alias:s._aliasOf||null
        }))""")
        print(f"  dumped {label}: n={len(rows)} blocked={len(blocked)} errs={len(errs)} "
              f"hosts={sorted(allowed)} t={round(time.time()-t0,1)}s", flush=True)
        if any("kl-contador" in h or "workers.dev" in h for h in allowed):
            raise SystemExit(f"FAIL {label}: host prohibido {sorted(allowed)}")
        if errs:
            print("  page errors:", errs[:6], flush=True)
        await browser.close()
    return rows


def rows_from_files():
    rows = []
    for fn in sorted((R / "data").glob("berlin-added-*.json")) + sorted((R / "data").glob("koeln-added-*.json")):
        data = json.loads(fn.read_text())
        for s in data["stones"]:
            la = s["dla"] if s.get("dla") is not None else s["la"]
            lo = s["dlo"] if s.get("dlo") is not None else s["lo"]
            rows.append({
                "id": s["id"], "src": s.get("src"), "n": s.get("n"), "a": s.get("a"),
                "sla": s["la"], "slo": s["lo"], "la": la, "lo": lo,
                "dla_file": s.get("dla"), "dlo_file": s.get("dlo"),
                "_dla": la, "_dlo": lo, "_ang": 0, "alias": None,
            })
    return rows


def load_v20(path):
    d = json.loads(Path(path).read_text())
    rows = d["rows"] if isinstance(d, dict) and "rows" in d else d
    return [r for r in rows if not r.get("alias") and r.get("_dla") is not None]


def square(x, y, ang=0.0, half=COL_HALF):
    from shapely.geometry import Polygon
    c, s = math.cos(ang), math.sin(ang)
    return Polygon([(x + c * dx - s * dy, y + s * dx + c * dy)
                    for dx, dy in ((-half, -half), (half, -half), (half, half), (-half, half))])


def addr_key(s):
    a = (s.get("a") or "").lower().replace("ß", "ss").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
    a = re.sub(r"\b\d{5}\b", "", a)
    a = re.sub(r"\b(deutschland|germany)\b", "", a)
    a = re.sub(r"[.,;/]", " ", a)
    a = re.sub(r"\bstr(?:asse)?\.", "strasse ", a)
    a = re.sub(r"([a-z])str\b", r"\1strasse", a)
    a = re.sub(r"\bstr\b", "strasse", a)
    a = re.sub(r"\s+", " ", a).strip()
    m = re.match(r"^(.*?)(\d+\s*[a-z]?)(?:\s+|$)", a)
    if m:
        a = re.sub(r"\s+", " ", (m.group(1) + m.group(2))).strip()
    return a


def groups_of_drawn(vis):
    """Agrupa como el cliente, pero con la/lo ya = posición de dibujo de archivo."""
    byk, no = defaultdict(list), []
    for r in vis:
        k = addr_key(r)
        (byk[k] if k else no).append(r)

    def cluster(lst, maxd):
        n = len(lst)
        if n <= 1:
            return [lst[:]] if n else []
        par = list(range(n))

        def find(i):
            while par[i] != i:
                par[i] = par[par[i]]
                i = par[i]
            return i
        for i in range(n):
            for j in range(i + 1, n):
                if dist_eq(lst[i]["la"], lst[i]["lo"], lst[j]["la"], lst[j]["lo"]) <= maxd:
                    a, b = find(i), find(j)
                    if a != b:
                        par[a] = b
        m = defaultdict(list)
        for i, s in enumerate(lst):
            m[find(i)].append(s)
        return list(m.values())

    clusters = []
    for k, lst in byk.items():
        clusters += cluster(lst, 15 if re.search(r"\d", k) else 8)
    clusters += cluster(no, 3.5)
    # merge centroids <0.8 m
    cents = [(sum(s["la"] for s in g) / len(g), sum(s["lo"] for s in g) / len(g)) for g in clusters]
    par = list(range(len(clusters)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    cell = 0.00002

    def key(la, lo):
        return (math.floor(la / cell), math.floor(lo / cell))
    grid = defaultdict(list)
    for i, c in enumerate(cents):
        grid[key(*c)].append(i)
    for i, c in enumerate(cents):
        a0, b0 = key(*c)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                for j in grid.get((a0 + di, b0 + dj), ()):
                    if j <= i:
                        continue
                    if dist_eq(c[0], c[1], cents[j][0], cents[j][1]) < 0.8:
                        a, b = find(i), find(j)
                        if a != b:
                            par[a] = b
    merged = defaultdict(list)
    for i, g in enumerate(clusters):
        merged[find(i)].extend(g)
    return list(merged.values())


def check(new_rows, v20_rows):
    from shapely.geometry import Point, LineString
    import sidewalk20 as SW

    os.environ.setdefault("V20_DATA", os.environ.get("V20_DATA", "/workspace/v21-data/place"))
    N = SW.load_near("DE")
    n_enr, sample = enrich_highway_tags(N)
    canary = (N.h.get(WIDTH_CANARY_WAY) or (None, {}))[1]
    print(f"  near buildings={len(N.b)} highways={len(N.h)} ts={N.ts} "
          f"enriched={n_enr} {WIDTH_CANARY_WAY}={canary}", flush=True)
    if str(canary.get("width") or "") != WIDTH_CANARY_VALUE:
        print(f"FAIL: {WIDTH_CANARY_WAY} no tiene width={WIDTH_CANARY_VALUE} tras enriquecer "
              f"(tags={canary}, sidecar={sample}). El chequeo de calzada no usaría el width de OSM.",
              file=sys.stderr)
        return False
    if len(new_rows) != EXPECT_NEW:
        print(f"FAIL: se esperaban {EXPECT_NEW} nuevas, hay {len(new_rows)}", file=sys.stderr)
        return False

    exc25, calz = exceptions_25(), calzada_exc()
    vis_new = [r for r in new_rows if not r.get("alias") and r.get("_dla") is not None]
    v20_vis = [r for r in v20_rows if not r.get("alias") and r.get("_dla") is not None]

    # stacked new (same drawn point, different id)
    pos = defaultdict(list)
    for r in vis_new:
        pos[(round(r["_dla"], 7), round(r["_dlo"], 7))].append(r["id"])
    stacked = {i for v in pos.values() if len(v) > 1 for i in v}

    # groups among all visible (new+v20) using post-load la/lo — same as auditor C
    # For v20, la in a dump is file drawing; for our v20-json we stored la as post-load.
    # Inter-group uses _dla. We also enforce vs all v20 _dla regardless of clustering
    # (that's the hard requirement: ≥1,55 m from existing groups as drawn).
    cell = 8.0

    def kxy(la, lo):
        return (math.floor(la * M_LAT / cell), math.floor(lo * M_LAT / cell))

    g20 = defaultdict(list)
    for r in v20_vis:
        g20[kxy(r["_dla"], r["_dlo"])].append(r)
    gnew = defaultdict(list)
    for r in vis_new:
        gnew[kxy(r["_dla"], r["_dlo"])].append(r)

    # new-new groups: cluster only new stones on drawn coords / addr
    ng = groups_of_drawn(vis_new)
    gid = {}
    for i, g in enumerate(ng):
        for s in g:
            gid[s["id"]] = i

    inside, col, road, gap20, gapn, over25 = [], [], [], [], [], []
    for r in vis_new:
        la, lo = r["_dla"], r["_dlo"]
        src_la = r["sla"] if r.get("sla") is not None else r["la"]
        src_lo = r["slo"] if r.get("slo") is not None else r["lo"]
        if r.get("dla_file") is not None and r.get("sla") is not None:
            src_la, src_lo = r["sla"], r["slo"]
        mv = dist_cons(src_la, src_lo, la, lo)
        if mv > MAXMOVE + 1e-6 and r["id"] not in exc25:
            over25.append((r["id"], round(mv, 4)))

        i, j = kxy(la, lo)
        best, who = 1e9, None
        for di in range(-3, 4):
            for dj in range(-3, 4):
                for o in g20.get((i + di, j + dj), ()):
                    d = dist_eq(la, lo, o["_dla"], o["_dlo"])
                    if d < best:
                        best, who = d, o["id"]
        if best < COL_GAP - 1e-6:
            gap20.append((r["id"], who, round(best, 3)))
        for di in range(-3, 4):
            for dj in range(-3, 4):
                for o in gnew.get((i + di, j + dj), ()):
                    if o["id"] <= r["id"]:
                        continue
                    if gid.get(o["id"]) == gid.get(r["id"]):
                        continue
                    d = dist_eq(la, lo, o["_dla"], o["_dlo"])
                    if d < COL_GAP - 1e-6:
                        gapn.append((r["id"], o["id"], round(d, 3)))

        o = (la, lo)
        PB, *_ = SW.local_geom(N, la, lo, rad=80)
        from shapely.geometry import Point, LineString
        pt = Point(0, 0)
        d_center = 99.0
        if PB is not None and not PB.is_empty:
            if PB.contains(pt) or PB.intersects(pt):
                inside.append(r["id"])
                d_center = 0.0
            else:
                d_center = PB.distance(pt)
            sq = square(0, 0, r.get("_ang") or 0)
            d_sq = 0.0 if PB.intersects(sq) else PB.distance(sq)
            if d_sq < MARGIN - 1e-6:
                col.append((r["id"], round(d_center, 3), round(d_sq, 3)))
        rd_clear = 99.0
        # Todas las vías vehiculares a ≤80 m, con semiwidth que honra el tag width.
        # No se recorta el índice a rc=1 ni se omite la vía si d_center > 25 m.
        for hid in N.around(N.hi, la, lo, ROAD_Q_RC):
            pts, t = N.h[hid]
            if not RWY.is_vehicular(t) or len(pts) < 2:
                continue
            ls = LineString([to_xy(a, c, o) for a, c in pts])
            if ls.distance(pt) > ROAD_RAD:
                continue
            dd = ls.distance(pt) - RWY.semiwidth(t)
            if dd < rd_clear:
                rd_clear = dd
        # Exención oficial: solo edificio a <6 m. C no salta cuando d_center > 25 m.
        if d_center >= RWY.BLD_EXEMPT_NEAR and rd_clear < -1e-6:
            if r["id"] not in calz:
                road.append((r["id"], round(rd_clear, 3), round(d_center, 3)))

    # Malla intra-grupo: paso 1,85 m (pilla apiladas a 0,067 m y mallas irregulares ~1 m).
    grid_fail = []
    for g in ng:
        if len(g) < 2:
            continue
        ds = []
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                ds.append(dist_eq(g[i]["_dla"], g[i]["_dlo"], g[j]["_dla"], g[j]["_dlo"]))
        if min(ds) < COL_STEP - GRID_TOL or not any(abs(d - COL_STEP) <= GRID_TOL for d in ds):
            ids = [s["id"] for s in g]
            grid_fail.append((g[0].get("a"), len(g), round(min(ds), 3), ids[:8]))

    ok = True
    print(f"nuevas comprobadas: {len(new_rows)} (visibles sin alias {len(vis_new)}; v20 visibles {len(v20_vis)})")
    if stacked:
        ok = False
        print(f"FAIL: {len(stacked)} placas nuevas comparten dla/dlo con otra (no hay malla), p.ej. {sorted(stacked)[:8]}")
    else:
        print("OK: ninguna placa nueva comparte el punto de dibujo con otra")
    if inside:
        ok = False
        print(f"FAIL: {len(inside)} centros dentro de un edificio: {inside[:8]}")
    else:
        print("OK: ningún centro nuevo dentro de un edificio")
    if col:
        ok = False
        print(f"FAIL: {len(col)} columnas o chinchetas a <0,5 m de un edificio, p.ej. {col[:6]}")
    else:
        print("OK: huella de columna 1,2 m y chincheta a ≥0,5 m de toda fachada")
    if road:
        ok = False
        print(f"FAIL: {len(road)} sobre la calzada sin exención ni ficha en calzada-v21.csv, p.ej. {road[:6]}")
    else:
        print("OK: ninguna nueva sobre la calzada (o documentada)")
    if gap20:
        ok = False
        print(f"FAIL: {len(gap20)} nuevas a <1,55 m de una de v20, p.ej. {gap20[:6]}")
    else:
        print("OK: ≥1,55 m entre nuevas y grupos de v20 dibujados")
    if gapn:
        ok = False
        print(f"FAIL: {len(gapn)} pares nuevos–nuevos de grupos distintos a <1,55 m, p.ej. {gapn[:6]}")
    else:
        print("OK: ≥1,55 m entre grupos nuevos distintos")
    if over25:
        ok = False
        print(f"FAIL: {len(over25)} con desplazamiento >25 m sin excepción, p.ej. {over25[:6]}")
    else:
        print("OK: ninguna nueva a >25 m sin excepción documentada")
    if grid_fail:
        ok = False
        print(f"FAIL: {len(grid_fail)} grupos nuevos sin malla de paso 1,85 m, p.ej. {grid_fail[:6]}")
    else:
        print("OK: malla intra-grupo de paso 1,85 m en todos los grupos de 2 o más")
    return ok


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url_v21", nargs="?", default=None)
    ap.add_argument("--v20-json", default=os.environ.get("V20_RENDERED_JSON", "/workspace/v21-data/out/v20-rendered-vis.json"))
    ap.add_argument("--v20-url", default=None)
    ap.add_argument("--from-files", action="store_true")
    ap.add_argument("--dump-out", default=None)
    args = ap.parse_args()

    if args.from_files:
        new_rows = rows_from_files()
        print(f"from files: {len(new_rows)} nuevas", flush=True)
    else:
        if not args.url_v21:
            print("uso: v21-new-render-placement.py <url_v21> | --from-files", file=sys.stderr)
            sys.exit(2)
        url = args.url_v21.rstrip("/") + "/index.html?intro=0&lang=es"
        print("START v21", url, flush=True)
        all_rows = await dump(url, 72110, "v21")
        new_rows = [r for r in all_rows if is_added(r)]
        if args.dump_out:
            Path(args.dump_out).write_text(json.dumps({"n": len(all_rows), "rows": all_rows}))

    if not args.from_files:
        # v29: las placas de v20 ya no están donde las dejó b142fa48 (alineación con la calle, data/align-v24.json):
        # la separación de 1,55 m se comprueba contra su posición DIBUJADA ahora en este mismo cliente.
        v20_rows = [r for r in all_rows if not is_added(r) and not r.get("alias") and r.get("_dla") is not None]
        print(f"v20 dibujadas en este cliente (con alineación): {len(v20_rows)} visibles", flush=True)
    elif args.v20_url and not Path(args.v20_json).exists():
        url = args.v20_url.rstrip("/") + "/index.html?intro=0&lang=es"
        print("START v20", url, flush=True)
        v20_rows = await dump(url, 72110, "v20")
    elif Path(args.v20_json).exists():
        v20_rows = load_v20(args.v20_json)
        print(f"v20 json: {len(v20_rows)} visibles ({args.v20_json})", flush=True)
    else:
        print("FAIL: no hay --v20-json ni --v20-url para las 72.110 dibujadas", file=sys.stderr)
        sys.exit(1)

    ok = check(new_rows, v20_rows)
    if not ok:
        sys.exit(1)
    print("OK: v21-new-render-placement")


if __name__ == "__main__":
    asyncio.run(main())
