#!/usr/bin/env python3
"""Compare rendered positions (_dla/_dlo/_ang) of ALL 73,950 stones from v21 (990ddc10)
between v22 and v21, and verify all 1,135 Batch-1 stones render pinned to file dla/dlo.
Blocks kl-contador and *.workers.dev.
"""
from __future__ import annotations

import asyncio
import math
import sys
import time
from playwright.async_api import async_playwright

M_LAT = 111320.0
TOL_M = 0.01
TOL_ANG_DEG = 0.5
BLOCK_HOSTS = ("kl-contador", "workers.dev")
V21_N = 73950
NEW_N = 1135
V22_SRCS = {
    "moenchengladbach", "denhaag", "krefeld", "monza", "viersen",
    "memmingen", "moers", "grevenbroich", "firenze", "xanten",
    "dresden", "erkrath", "dormagen",
}


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
            f"typeof DATA!=='undefined' && DATA.length>={expect_min} && DATA.every(s=>s._dla!==undefined || s._aliasOf)",
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


async def main():
    if len(sys.argv) < 3:
        print("usage: v22-render-compare.py <url_v22> <url_v21>", file=sys.stderr)
        sys.exit(2)
    url_v22 = sys.argv[1].rstrip("/") + "/index.html?intro=0&lang=es"
    url_v21 = sys.argv[2].rstrip("/") + "/index.html?intro=0&lang=es"
    v21, e21 = await dump(url_v21, V21_N, "v21")
    v22, e22 = await dump(url_v22, V21_N + NEW_N, "v22")

    assert len(v21) == V21_N, f"expected {V21_N} in v21, got {len(v21)}"
    assert len(v22) == V21_N + NEW_N, f"expected {V21_N + NEW_N} in v22, got {len(v22)}"

    moved, ang_only = [], []
    for iid, a in v21.items():
        b = v22.get(iid)
        if not b:
            moved.append((999.0, iid, "missing"))
            continue
        if a.get("_dla") is None or b.get("_dla") is None:
            if not (a.get("alias") and b.get("alias")):
                moved.append((999.0, iid, "missing _dla"))
            continue
        d = dist_m(a["_dla"], a["_dlo"], b["_dla"], b["_dlo"])
        axis_deg, raw_deg = ang_diff_deg(a["_ang"], b["_ang"])
        if d > TOL_M:
            moved.append((d, iid, axis_deg))
        elif axis_deg > TOL_ANG_DEG or raw_deg > TOL_ANG_DEG:
            ang_only.append((raw_deg, axis_deg, iid))

    added = [r for r in v22.values() if r.get("src") in V22_SRCS]
    pin_fail = []
    for r in added:
        if r.get("_dla") is None or r.get("dla_file") is None:
            pin_fail.append((r["id"], "missing _dla/dla_file"))
            continue
        if dist_m(r["_dla"], r["_dlo"], r["dla_file"], r["dlo_file"]) > TOL_M:
            pin_fail.append((r["id"], "not pinned to dla_file"))
        if r.get("alias"):
            pin_fail.append((r["id"], "unexpected alias"))

    print(f"Compared existing 73,950 stones: moved={len(moved)} ang_only={len(ang_only)}")
    print(f"Checked {len(added)} Batch-1 stones pinned to file dla/dlo: pin_fail={len(pin_fail)}")
    if moved or ang_only or pin_fail or e21 or e22:
        print("FAIL:", moved[:5], ang_only[:5], pin_fail[:5], e21[:3], e22[:3])
        sys.exit(1)
    print("OK: all 73,950 existing stones render identically to 990ddc10 and all 1,135 Batch-1 stones are pinned")


if __name__ == "__main__":
    asyncio.run(main())
