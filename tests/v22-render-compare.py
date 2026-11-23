#!/usr/bin/env python3
"""Compare rendered positions (_dla/_dlo/_ang) of ALL 73,950 stones from v21 (990ddc10)
between v22 and v21, and verify all Batch-1 stones render pinned to file dla/dlo.
v29: two passes. With ?alignoff=1 (v28 layout) everything must be identical to 990ddc10 as before; with the
street alignment the expected position is the one in data/align-v24.json (tests/align_expected.py) for listed
stones and the old one otherwise. Placement rules: tests/v24-align-check.py.
Blocks kl-contador and *.workers.dev.
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import sys
import time
from pathlib import Path
from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import align_expected as AE  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
M_LAT = 111320.0
TOL_M = 0.01
TOL_ANG_DEG = 0.5
BLOCK_HOSTS = ("kl-contador", "workers.dev")
V21_N = 73950
V22_SRCS = {
    "moenchengladbach", "denhaag", "krefeld", "monza", "viersen",
    "memmingen", "moers", "grevenbroich", "firenze", "xanten",
    "dresden", "erkrath", "dormagen",
}


def expected_new_count() -> int:
    total = 0
    for src in sorted(V22_SRCS):
        p = ROOT / "data" / f"{src}-added-20261121.json"
        if p.exists():
            total += len(json.load(open(p))["stones"])
    return total


def dist_m(la1, lo1, la2, lo2):
    return math.hypot((la1 - la2) * M_LAT, (lo1 - lo2) * M_LAT * math.cos(math.radians((la1 + la2) / 2)))


def ang_diff_deg(a, b):
    da = abs((a or 0) - (b or 0))
    raw = math.degrees(min(da, abs(da - 2 * math.pi)))
    d = abs((a or 0) - (b or 0)) % math.pi
    d = min(d, math.pi - d)
    return math.degrees(d), raw


async def dump(url, expect_min, label):
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
            f"typeof DATA!=='undefined' && DATA.length>={expect_min} && DATA.every(s=>s._dla!==undefined || s._aliasOf) && (!window.KLAlign || KLAlign.ready)",
            timeout=600000,
        )
        rows = await page.evaluate("""() => DATA.map(s => ({
          id: String(s.id),
          src: s.src || null,
          cc: s.cc || null,
          sla: s.sla ?? null, slo: s.slo ?? null,
          la: s.la, lo: s.lo,
          dla_file: s.dla ?? null, dlo_file: s.dlo ?? null,
          _dla: s._dla, _dlo: s._dlo, _ang: s._ang || 0,
          alias: s._aliasOf || null
        }))""")
        print(f"  dumped {label}: n={len(rows)} blocked={len(blocked)} errs={len(errs)} hosts={sorted(allowed)} t={round(time.time()-t0,1)}s", flush=True)
        if any("kl-contador" in h or "workers.dev" in h for h in allowed):
            raise SystemExit(f"FAIL {label}: forbidden host {sorted(allowed)}")
        await browser.close()
    return {r["id"]: r for r in rows}, errs


def compare(v21, v22, EXP, label, new_n):
    """v29: posición esperada = data/align-v24.json si la placa está alineada; si no, la de 990ddc10 (y las de Lote 1, su dla/dlo de archivo).
    Con EXP vacío (?alignoff=1) es exactamente la comprobación de v22."""
    moved, ang_only = [], []
    n_al = 0
    for iid, a in v21.items():
        b = v22.get(iid)
        if not b:
            moved.append((999.0, iid, "missing"))
            continue
        if a.get("_dla") is None or b.get("_dla") is None:
            if not (a.get("alias") and b.get("alias")):
                moved.append((999.0, iid, "missing _dla"))
            continue
        e = EXP.get(b.get("alias") or iid)
        if e is not None:
            n_al += 1
            a = dict(a, _dla=e[0], _dlo=e[1], _ang=e[2])
        d = dist_m(a["_dla"], a["_dlo"], b["_dla"], b["_dlo"])
        axis_deg, raw_deg = ang_diff_deg(a["_ang"], b["_ang"])
        if d > TOL_M:
            moved.append((d, iid, axis_deg))
        elif axis_deg > TOL_ANG_DEG or raw_deg > TOL_ANG_DEG:
            ang_only.append((raw_deg, axis_deg, iid))

    added = [r for r in v22.values() if r.get("src") in V22_SRCS]
    pin_fail = []
    n_al_new = 0
    for r in added:
        if r.get("_dla") is None or r.get("dla_file") is None:
            pin_fail.append((r["id"], "missing _dla/dla_file"))
            continue
        if r.get("alias"):
            pin_fail.append((r["id"], "unexpected alias"))
        e = EXP.get(r["id"])
        if e is not None:
            n_al_new += 1
            if dist_m(r["_dla"], r["_dlo"], e[0], e[1]) > TOL_M or ang_diff_deg(r["_ang"], e[2])[1] > TOL_ANG_DEG:
                pin_fail.append((r["id"], "not at aligned position"))
            continue
        if dist_m(r["_dla"], r["_dlo"], r["dla_file"], r["dlo_file"]) > TOL_M:
            pin_fail.append((r["id"], "not pinned to dla_file"))

    print(f"[{label}] Compared existing 73,950 stones: moved={len(moved)} ang_only={len(ang_only)} (expected at aligned position: {n_al})")
    print(f"[{label}] Checked {len(added)} Batch-1 stones: pin_fail={len(pin_fail)} (expected at aligned position: {n_al_new}, pinned to file: {len(added) - n_al_new})")
    ok = not (moved or ang_only or pin_fail)
    if not ok:
        print(f"FAIL [{label}]:", moved[:5], ang_only[:5], pin_fail[:5])
    else:
        print(f"OK [{label}]: all 73,950 existing stones and all {new_n} Batch-1 stones render at their expected position")
    return ok


async def main():
    if len(sys.argv) < 3:
        print("usage: v22-render-compare.py <url_v22> <url_v21>", file=sys.stderr)
        sys.exit(2)
    new_n = expected_new_count()
    assert new_n > 0, "no Batch-1 data files found"
    url_v22 = sys.argv[1].rstrip("/") + "/index.html?intro=0&lang=es"
    url_v21 = sys.argv[2].rstrip("/") + "/index.html?intro=0&lang=es"
    v21, e21 = await dump(url_v21, V21_N, "v21")
    v22, e22 = await dump(url_v22, V21_N + new_n, "v22")

    assert len(v21) == V21_N, f"expected {V21_N} in v21, got {len(v21)}"
    assert len(v22) == V21_N + new_n, f"expected {V21_N + new_n} in v22, got {len(v22)}"

    v22off, e22o = await dump(url_v22 + "&alignoff=1", V21_N + new_n, "v22-alignoff")
    assert len(v22off) == V21_N + new_n, f"expected {V21_N + new_n} in v22 (alignoff), got {len(v22off)}"
    ok1 = compare(v21, v22off, {}, "sin alineación = v28", new_n)
    ok2 = compare(v21, v22, AE.load(), "con alineación", new_n)
    if not (ok1 and ok2) or e21 or e22 or e22o:
        print("FAIL:", e21[:3], e22[:3], e22o[:3])
        sys.exit(1)
    print(f"OK: sin alineación todo idéntico a 990ddc10; con alineación cada placa en su posición de data/align-v24.json o, si no está, la de antes")


if __name__ == "__main__":
    asyncio.run(main())
