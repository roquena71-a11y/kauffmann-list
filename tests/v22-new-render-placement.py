#!/usr/bin/env python3
"""Verify rendered (_dla/_dlo) placement of all Batch-1 stones against complete OSM buildings
(including relation multipolygons), OSM highways (with width/est_width across <=80 m), all 73,950
existing rendered stones, and rigid 1.85 m intra-group grid. Blocks kl-contador and *.workers.dev.
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import pickle
import sys
import time
from collections import defaultdict
from pathlib import Path
from playwright.async_api import async_playwright

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "pipeline" / "tools"))

import sidewalk20 as SW  # noqa: E402
import roadway20 as RWY  # noqa: E402
from geo import to_xy, hav, M_LAT  # noqa: E402
from shapely.geometry import Point, Polygon, LineString  # noqa: E402

COL_HALF = 0.60
MARGIN = 0.50
COL_GAP = 1.55
COL_STEP = 1.85
GRID_TOL = 0.08
MAXMOVE = 25.0
ROAD_Q_RC = 4
ROAD_RAD = 80.0
BLOCK_HOSTS = ("kl-contador", "workers.dev")
V22_SRCS = {
    "moenchengladbach", "denhaag", "krefeld", "monza", "viersen",
    "memmingen", "moers", "grevenbroich", "firenze", "xanten",
    "dresden", "erkrath", "dormagen",
}


def resolve_near_dir() -> Path:
    if os.environ.get("V22_NEAR_DIR"):
        return Path(os.environ["V22_NEAR_DIR"])
    if os.environ.get("V22_DATA"):
        return Path(os.environ["V22_DATA"]) / "near"
    raise SystemExit("FAIL: set V22_DATA or V22_NEAR_DIR pointing to OSM geometry pickles")


def expected_new_count() -> int:
    total = 0
    for src in sorted(V22_SRCS):
        p = R / "data" / f"{src}-added-20261121.json"
        if p.exists():
            total += len(json.load(open(p))["stones"])
    return total


def dist_eq(la1, lo1, la2, lo2):
    return math.hypot((la1 - la2) * M_LAT, (lo1 - lo2) * M_LAT * math.cos(math.radians((la1 + la2) / 2)))


def dist_cons(la1, lo1, la2, lo2):
    return max(hav(la1, lo1, la2, lo2), dist_eq(la1, lo1, la2, lo2))


def load_near_pkl(path: Path, cc: str) -> SW.Near:
    if not path.exists():
        raise SystemExit(f"FAIL: missing near pickle {path}")
    d = pickle.load(open(path, "rb"))
    rel_buildings = sum(1 for bid in d["buildings"] if str(bid).startswith("r"))
    width_tags = sum(1 for _, t in d["highways"].values() if "width" in t or "est_width" in t)
    if rel_buildings == 0:
        raise SystemExit(f"FAIL: {path} has 0 relation multipolygon buildings (incomplete OSM extract)")
    if cc == "IT" and len(d["buildings"]) < 200000:
        raise SystemExit(f"FAIL: {path} has only {len(d['buildings'])} buildings (expected >=200000 complete IT extract)")
    if width_tags == 0:
        raise SystemExit(f"FAIL: {path} has 0 highways with width/est_width tags")

    N = SW.Near()
    N.ts = d.get("osm_timestamp")
    for bid, (o, i, t) in d["buildings"].items():
        N.add_b(bid, o, i, t)
    for hid, (p, t) in d["highways"].items():
        N.add_h(hid, p, t)
    return N


def square(x, y, ang=0.0, half=COL_HALF):
    c, s = math.cos(ang), math.sin(ang)
    return Polygon([(x + c * dx - s * dy, y + s * dx + c * dy)
                    for dx, dy in ((-half, -half), (half, -half), (half, half), (-half, half))])


async def dump(url, expect_total):
    t0 = time.time()
    blocked, allowed, errs = [], set(), []
    chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/google-chrome")
    launch_kw = {
        "headless": True,
        "args": [
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--ignore-gpu-blocklist", "--disable-dev-shm-usage",
        ],
    }
    if Path(chrome_bin).exists():
        launch_kw["executable_path"] = chrome_bin

    async with async_playwright() as p:
        browser = await p.chromium.launch(**launch_kw)
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
            f"typeof DATA!=='undefined' && DATA.length>={expect_total} && DATA.every(s=>s._dla!==undefined || s._aliasOf) && (!window.KLAlign || KLAlign.ready)",
            timeout=600000,
        )
        rows = await page.evaluate("""() => DATA.map(s => ({
          id: String(s.id), src: s.src||null, cc: s.cc||'DE', n: s.n||null, a: s.a||null,
          sla: s.sla??null, slo: s.slo??null, la: s.la, lo: s.lo,
          _dla: s._dla, _dlo: s._dlo, _ang: s._ang||0, alias: s._aliasOf||null
        }))""")
        print(f"  dumped v22: n={len(rows)} blocked={len(blocked)} errs={len(errs)} t={round(time.time()-t0,1)}s", flush=True)
        if any("kl-contador" in h or "workers.dev" in h for h in allowed):
            raise SystemExit(f"FAIL: forbidden host {sorted(allowed)}")
        if errs:
            raise SystemExit(f"FAIL: page errors {errs[:3]}")
        await browser.close()
    return rows


async def main():
    if len(sys.argv) < 2:
        print("usage: v22-new-render-placement.py <url_v22>", file=sys.stderr)
        sys.exit(2)
    near_dir = resolve_near_dir()
    expect_new = expected_new_count()
    assert expect_new > 0, "no Batch-1 data files found"
    url = sys.argv[1].rstrip("/") + "/index.html?intro=0&lang=es"
    rows = await dump(url, 73950 + expect_new)
    vis_new = [r for r in rows if r.get("src") in V22_SRCS and not r.get("alias") and r.get("_dla") is not None]
    vis_old = [r for r in rows if r.get("src") not in V22_SRCS and not r.get("alias") and r.get("_dla") is not None]
    assert len(vis_new) == expect_new, f"expected {expect_new}, got {len(vis_new)}"

    nears = {
        "DE": load_near_pkl(near_dir / "DE-batch1.pkl", "DE"),
        "NL": load_near_pkl(near_dir / "NL-denhaag.pkl", "NL"),
        "IT": load_near_pkl(near_dir / "IT-batch1.pkl", "IT"),
    }

    cell = 8.0
    def kxy(la, lo):
        return (math.floor(la * M_LAT / cell), math.floor(lo * M_LAT / cell))

    g_old = defaultdict(list)
    for r in vis_old:
        g_old[kxy(r["_dla"], r["_dlo"])].append(r)
    g_new = defaultdict(list)
    for r in vis_new:
        g_new[kxy(r["_dla"], r["_dlo"])].append(r)

    ng = SW.groups_of([dict(r, la=r["_dla"], lo=r["_dlo"]) for r in vis_new])
    gid = {s["id"]: gi for gi, g in enumerate(ng) for s in g}

    pos_seen = defaultdict(list)
    for r in vis_new:
        pos_seen[(round(r["_dla"], 7), round(r["_dlo"], 7))].append(r["id"])
    stacked = [v for v in pos_seen.values() if len(v) > 1]

    inside, col, road, gap_old, gap_new, over25, grid_fail = [], [], [], [], [], [], []
    for r in vis_new:
        la, lo = r["_dla"], r["_dlo"]
        sla = r["sla"] if r.get("sla") is not None else r["la"]
        slo = r["slo"] if r.get("slo") is not None else r["lo"]
        mv = dist_cons(sla, slo, la, lo)
        if mv > MAXMOVE + 1e-6:
            over25.append((r["id"], round(mv, 4)))

        i, j = kxy(la, lo)
        for di in range(-3, 4):
            for dj in range(-3, 4):
                for o in g_old.get((i + di, j + dj), ()):
                    d = dist_eq(la, lo, o["_dla"], o["_dlo"])
                    if d < COL_GAP - 1e-6:
                        gap_old.append((r["id"], o["id"], round(d, 3)))
                for o in g_new.get((i + di, j + dj), ()):
                    if o["id"] <= r["id"] or gid.get(o["id"]) == gid.get(r["id"]):
                        continue
                    d = dist_eq(la, lo, o["_dla"], o["_dlo"])
                    if d < COL_GAP - 1e-6:
                        gap_new.append((r["id"], o["id"], round(d, 3)))

        N = nears[r.get("cc") or "DE"]
        PB, *_ = SW.local_geom(N, la, lo, rad=80)
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
        o = (la, lo)
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
        if d_center >= RWY.BLD_EXEMPT_NEAR and rd_clear < -1e-6:
            road.append((r["id"], round(rd_clear, 3), round(d_center, 3)))

    for g in ng:
        if len(g) >= 2:
            ds = [dist_eq(g[i]["_dla"], g[i]["_dlo"], g[j]["_dla"], g[j]["_dlo"])
                  for i in range(len(g)) for j in range(i + 1, len(g))]
            if min(ds) < COL_STEP - GRID_TOL or not any(abs(d - COL_STEP) <= GRID_TOL for d in ds):
                grid_fail.append((g[0]["id"], len(g), round(min(ds), 3)))

    print(f"Checked {len(vis_new)} Batch-1 rendered stones (vs {len(vis_old)} existing visible):")
    print(f"  stacked={len(stacked)} inside={len(inside)} col<0.5={len(col)} road={len(road)} gap_old={len(gap_old)} gap_new={len(gap_new)} over25={len(over25)} grid_fail={len(grid_fail)}")
    if any([stacked, inside, col, road, gap_old, gap_new, over25, grid_fail]):
        print("FAIL details:", stacked[:3], inside[:3], col[:3], road[:3], gap_old[:3], gap_new[:3], over25[:3], grid_fail[:3])
        sys.exit(1)
    print("OK: v22-new-render-placement passed with 0 violations")


if __name__ == "__main__":
    asyncio.run(main())
